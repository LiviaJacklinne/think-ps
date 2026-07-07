import json

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST


User = get_user_model()


def _json_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


@csrf_exempt
@require_POST
def cadastro(request):
    data = _json_body(request)

    if data is None:
        return JsonResponse({"erro": "JSON invalido."}, status=400)

    username = data.get("username")
    email = data.get("email", "")
    password = data.get("password")

    if not username or not password:
        return JsonResponse(
            {"erro": "Informe username e password."},
            status=400,
        )

    if User.objects.filter(username=username).exists():
        return JsonResponse({"erro": "Username ja cadastrado."}, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )

    return JsonResponse(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
        status=201,
    )


@csrf_exempt
@require_POST
def login_usuario(request):
    data = _json_body(request)

    if data is None:
        return JsonResponse({"erro": "JSON invalido."}, status=400)

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JsonResponse(
            {"erro": "Informe username e password."},
            status=400,
        )

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({"erro": "Credenciais invalidas."}, status=401)

    login(request, user)

    return JsonResponse(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    )


@csrf_exempt
@require_POST
def logout_usuario(request):
    logout(request)
    return JsonResponse({"mensagem": "Logout realizado com sucesso."})


@require_GET
def usuario_atual(request):
    if not request.user.is_authenticated:
        return JsonResponse({"autenticado": False}, status=401)

    return JsonResponse(
        {
            "autenticado": True,
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
        }
    )
