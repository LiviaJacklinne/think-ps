import json

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .roles import (
    MANAGER,
    USER,
    ROLE_CHOICES,
    assign_role,
    bootstrap_roles,
    ensure_roles,
    get_role,
    is_manager,
)


User = get_user_model()


def _json_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _wants_json(request):
    return (
        request.content_type == "application/json"
        or "application/json" in request.headers.get("Accept", "")
    )


@csrf_exempt
@require_http_methods(["GET", "POST"])
def cadastro(request):
    bootstrap_roles(User)
    is_first_user = not User.objects.exists()
    can_create_user = is_first_user or (
        request.user.is_authenticated and is_manager(request.user)
    )
    template_context = {
        "can_choose_role": not is_first_user,
        "is_first_user": is_first_user,
        "roles": ROLE_CHOICES,
    }

    if request.method == "GET":
        if not can_create_user:
            if request.user.is_authenticated:
                messages.error(request, "Apenas managers podem cadastrar usuarios.")
                return redirect("menu")

            return redirect("login_usuario")

        return render(request, "accounts/cadastro.html", template_context)

    data = _json_body(request)
    if not _wants_json(request):
        data = request.POST

    if data is None:
        return JsonResponse({"erro": "JSON invalido."}, status=400)

    username = data.get("username")
    email = data.get("email", "")
    password = data.get("password")

    if not can_create_user:
        if not _wants_json(request):
            messages.error(request, "Apenas managers podem cadastrar usuarios.")
            return redirect("menu" if request.user.is_authenticated else "login_usuario")

        return JsonResponse({"erro": "Apenas managers podem cadastrar usuarios."}, status=403)

    if not username or not password:
        if not _wants_json(request):
            messages.error(request, "Informe usuario e senha.")
            return render(request, "accounts/cadastro.html", template_context, status=400)

        return JsonResponse(
            {"erro": "Informe username e password."},
            status=400,
        )

    if User.objects.filter(username=username).exists():
        if not _wants_json(request):
            messages.error(request, "Usuario ja cadastrado.")
            return render(request, "accounts/cadastro.html", template_context, status=400)

        return JsonResponse({"erro": "Username ja cadastrado."}, status=400)

    if email and User.objects.filter(email=email).exists():
        if not _wants_json(request):
            messages.error(request, "E-mail ja cadastrado.")
            return render(request, "accounts/cadastro.html", template_context, status=400)

        return JsonResponse({"erro": "E-mail ja cadastrado."}, status=400)

    role = MANAGER if is_first_user else data.get("role", USER)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )
    assign_role(user, role)

    if not _wants_json(request):
        if is_first_user:
            login(request, user)
        else:
            messages.success(request, "Usuario cadastrado com sucesso.")

        return redirect("menu")

    return JsonResponse(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": get_role(user),
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["GET", "POST"])
def login_usuario(request):
    if request.method == "GET":
        return render(request, "accounts/login.html")

    data = _json_body(request)
    if not _wants_json(request):
        data = request.POST

    if data is None:
        return JsonResponse({"erro": "JSON invalido."}, status=400)

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        if not _wants_json(request):
            messages.error(request, "Informe usuario e senha.")
            return render(request, "accounts/login.html", status=400)

        return JsonResponse(
            {"erro": "Informe username e password."},
            status=400,
        )

    user = authenticate(request, username=username, password=password)

    if user is None:
        if not _wants_json(request):
            messages.error(request, "Credenciais invalidas.")
            return render(request, "accounts/login.html", status=401)

        return JsonResponse({"erro": "Credenciais invalidas."}, status=401)

    login(request, user)
    bootstrap_roles(User)

    if not _wants_json(request):
        return redirect("menu")

    return JsonResponse(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": get_role(user),
        }
    )


@csrf_exempt
@require_POST
def logout_usuario(request):
    logout(request)

    if not _wants_json(request):
        return redirect("login_usuario")

    return JsonResponse({"mensagem": "Logout realizado com sucesso."})


@login_required
def menu(request):
    bootstrap_roles(User)
    return render(request, "accounts/menu.html", {"role": get_role(request.user)})


@require_http_methods(["GET", "POST"])
def usuario_atual(request):
    bootstrap_roles(User)

    if not request.user.is_authenticated:
        if not _wants_json(request):
            return redirect("login_usuario")

        return JsonResponse({"autenticado": False}, status=401)

    if request.method == "POST":
        user = request.user
        data = _json_body(request) if _wants_json(request) else request.POST

        if data is None:
            return JsonResponse({"erro": "JSON invalido."}, status=400)

        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")

        if not username:
            if not _wants_json(request):
                messages.error(request, "Informe o nome de usuario.")
                return render(request, "accounts/me.html", status=400)

            return JsonResponse({"erro": "Informe o nome de usuario."}, status=400)

        if User.objects.filter(username=username).exclude(id=user.id).exists():
            if not _wants_json(request):
                messages.error(request, "Usuario ja cadastrado.")
                return render(request, "accounts/me.html", status=400)

            return JsonResponse({"erro": "Usuario ja cadastrado."}, status=400)

        if email and User.objects.filter(email=email).exclude(id=user.id).exists():
            if not _wants_json(request):
                messages.error(request, "E-mail ja cadastrado.")
                return render(request, "accounts/me.html", status=400)

            return JsonResponse({"erro": "E-mail ja cadastrado."}, status=400)

        user.username = username
        user.email = email

        if password:
            user.set_password(password)

        user.save()

        if password:
            login(request, user)

        if not _wants_json(request):
            messages.success(request, "Perfil atualizado com sucesso.")
            return redirect("usuario_atual")

        return JsonResponse(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": get_role(user),
            }
        )

    if not _wants_json(request):
        return render(request, "accounts/me.html", {"role": get_role(request.user)})

    return JsonResponse(
        {
            "autenticado": True,
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "role": get_role(request.user),
        }
    )
