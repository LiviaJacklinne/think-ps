import json

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .roles import (
    MANAGER,
    USER,
    ROLE_CHOICES,
    assign_role,
    bootstrap_roles,
    get_role,
    is_manager,
)


User = get_user_model()


def _user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": get_role(user),
    }


def _json_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _manager_required(request):
    bootstrap_roles(User)

    if not request.user.is_authenticated:
        return JsonResponse({"erro": "Login obrigatorio."}, status=401)

    if not is_manager(request.user):
        return JsonResponse({"erro": "Apenas managers podem acessar este recurso."}, status=403)

    return None


@csrf_exempt
@require_http_methods(["POST"])
def cadastro(request):
    bootstrap_roles(User)
    is_first_user = not User.objects.exists()
    can_create_user = is_first_user or (
        request.user.is_authenticated and is_manager(request.user)
    )

    data = _json_body(request)
    if data is None:
        return JsonResponse({"erro": "JSON invalido."}, status=400)

    if not can_create_user:
        return JsonResponse({"erro": "Apenas managers podem cadastrar usuarios."}, status=403)

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return JsonResponse({"erro": "Informe username e password."}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"erro": "Username ja cadastrado."}, status=400)

    if email and User.objects.filter(email=email).exists():
        return JsonResponse({"erro": "E-mail ja cadastrado."}, status=400)

    role = MANAGER if is_first_user else data.get("role", USER)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )
    assign_role(user, role)

    if is_first_user:
        login(request, user)

    return JsonResponse(_user_payload(user), status=201)


@csrf_exempt
@require_http_methods(["GET"])
def usuarios(request):
    blocked = _manager_required(request)
    if blocked:
        return blocked

    users = User.objects.all().order_by("username")
    return JsonResponse({"usuarios": [_user_payload(user) for user in users]})


@csrf_exempt
@require_http_methods(["PATCH"])
def usuario_detalhe(request, user_id):
    blocked = _manager_required(request)
    if blocked:
        return blocked

    data = _json_body(request)
    if data is None:
        return JsonResponse({"erro": "JSON invalido."}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"erro": "Usuario nao encontrado."}, status=404)

    username = data.get("username", user.username).strip()
    email = data.get("email", user.email).strip()
    password = data.get("password", "")
    role = data.get("role", get_role(user))

    if not username:
        return JsonResponse({"erro": "Informe o nome de usuario."}, status=400)

    if User.objects.filter(username=username).exclude(id=user.id).exists():
        return JsonResponse({"erro": "Usuario ja cadastrado."}, status=400)

    if email and User.objects.filter(email=email).exclude(id=user.id).exists():
        return JsonResponse({"erro": "E-mail ja cadastrado."}, status=400)

    if role not in ROLE_CHOICES:
        return JsonResponse({"erro": "Role invalida."}, status=400)

    user.username = username
    user.email = email

    if password:
        user.set_password(password)

    user.save()
    assign_role(user, role)

    return JsonResponse(_user_payload(user))


@csrf_exempt
@require_http_methods(["POST"])
def login_usuario(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"erro": "JSON invalido."}, status=400)

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JsonResponse({"erro": "Informe username e password."}, status=400)

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({"erro": "Credenciais invalidas."}, status=401)

    login(request, user)
    bootstrap_roles(User)

    return JsonResponse(_user_payload(user))


@csrf_exempt
@require_POST
def logout_usuario(request):
    logout(request)
    return JsonResponse({"mensagem": "Logout realizado com sucesso."})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def usuario_atual(request):
    bootstrap_roles(User)

    if not request.user.is_authenticated:
        return JsonResponse({"autenticado": False}, status=401)

    if request.method == "POST":
        user = request.user
        data = _json_body(request)

        if data is None:
            return JsonResponse({"erro": "JSON invalido."}, status=400)

        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")

        if not username:
            return JsonResponse({"erro": "Informe o nome de usuario."}, status=400)

        if User.objects.filter(username=username).exclude(id=user.id).exists():
            return JsonResponse({"erro": "Usuario ja cadastrado."}, status=400)

        if email and User.objects.filter(email=email).exclude(id=user.id).exists():
            return JsonResponse({"erro": "E-mail ja cadastrado."}, status=400)

        user.username = username
        user.email = email

        if password:
            user.set_password(password)

        user.save()

        if password:
            login(request, user)

        return JsonResponse(_user_payload(user))

    return JsonResponse(
        {
            "autenticado": True,
            **_user_payload(request.user),
        }
    )
