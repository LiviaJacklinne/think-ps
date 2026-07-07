import json

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

try:
    from bson import ObjectId
    from bson.errors import InvalidId
except ImportError:
    ObjectId = None
    InvalidId = ValueError

try:
    from pymongo.errors import PyMongoError
except ImportError:
    PyMongoError = Exception

MONGO_ERRORS = (PyMongoError, RuntimeError)
INVALID_MONGO_ERRORS = (InvalidId,) + MONGO_ERRORS

from accounts.roles import get_role, is_manager
from .mongo import compras_collection, produtos_collection
from .services import MOCK_PRODUTOS, listar_produtos, normalizar_produto


def _body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _auth_required(request):
    if not request.user.is_authenticated:
        return JsonResponse({"erro": "Nao autenticado."}, status=401)

    return None


def _serialize(produto):
    produto = normalizar_produto(produto)
    return {
        "id": produto["id"],
        "nome": produto.get("nome", ""),
        "quantidade": produto["quantidade"],
        "valor": produto["valor"],
        "subtotal": produto["subtotal"],
    }


def _produto_por_id(produto_id):
    if produto_id.startswith("mock-"):
        try:
            index = int(produto_id.split("-", 1)[1]) - 1
            return normalizar_produto({"id": produto_id, **MOCK_PRODUTOS[index]})
        except (IndexError, ValueError):
            return None

    if ObjectId is None:
        return None

    try:
        produto = produtos_collection.find_one({"_id": ObjectId(produto_id)})
    except INVALID_MONGO_ERRORS:
        return None

    return normalizar_produto(produto) if produto else None


@csrf_exempt
@require_http_methods(["GET", "POST"])
def produtos(request):
    auth = _auth_required(request)

    if auth:
        return auth

    if request.method == "GET":
        termo = request.GET.get("q", "").strip()
        produtos_lista, usando_mock = listar_produtos(termo)
        return JsonResponse(
            {
                "role": get_role(request.user),
                "usando_mock": usando_mock,
                "produtos": [_serialize(produto) for produto in produtos_lista],
            }
        )

    if not is_manager(request.user):
        return JsonResponse({"erro": "Apenas managers podem cadastrar produtos."}, status=403)

    data = _body(request)

    if data is None:
        return JsonResponse({"erro": "JSON invalido."}, status=400)

    produto = {
        "nome": data.get("nome", "").strip(),
        "quantidade": int(data.get("quantidade") or 0),
        "valor": float(data.get("valor") or 0),
    }

    if not produto["nome"]:
        return JsonResponse({"erro": "Informe o nome do produto."}, status=400)

    try:
        result = produtos_collection.insert_one(produto)
    except MONGO_ERRORS:
        return JsonResponse({"erro": "Nao foi possivel salvar no MongoDB."}, status=503)

    produto["_id"] = result.inserted_id
    return JsonResponse(_serialize(produto), status=201)


@csrf_exempt
@require_http_methods(["PATCH"])
def produto_detalhe(request, produto_id):
    auth = _auth_required(request)

    if auth:
        return auth

    if not is_manager(request.user):
        return JsonResponse({"erro": "Apenas managers podem editar produtos."}, status=403)

    if ObjectId is None:
        return JsonResponse({"erro": "pymongo nao esta disponivel."}, status=503)

    data = _body(request)

    if data is None:
        return JsonResponse({"erro": "JSON invalido."}, status=400)

    try:
        object_id = ObjectId(produto_id)
    except InvalidId:
        return JsonResponse({"erro": "Produto invalido."}, status=400)

    dados = {
        "nome": data.get("nome", "").strip(),
        "quantidade": int(data.get("quantidade") or 0),
        "valor": float(data.get("valor") or 0),
    }

    if not dados["nome"]:
        return JsonResponse({"erro": "Informe o nome do produto."}, status=400)

    try:
        produtos_collection.update_one({"_id": object_id}, {"$set": dados})
        produto = produtos_collection.find_one({"_id": object_id})
    except MONGO_ERRORS:
        return JsonResponse({"erro": "Nao foi possivel atualizar o MongoDB."}, status=503)

    if not produto:
        return JsonResponse({"erro": "Produto nao encontrado."}, status=404)

    return JsonResponse(_serialize(produto))


@csrf_exempt
@require_http_methods(["POST"])
def comprar_produto(request, produto_id):
    auth = _auth_required(request)

    if auth:
        return auth

    if is_manager(request.user):
        return JsonResponse({"erro": "Managers nao possuem carrinho."}, status=403)

    data = _body(request)

    if data is None:
        return JsonResponse({"erro": "JSON invalido."}, status=400)

    try:
        quantidade = int(data.get("quantidade") or 1)
    except ValueError:
        return JsonResponse({"erro": "Quantidade invalida."}, status=400)

    produto = _produto_por_id(produto_id)

    if not produto:
        return JsonResponse({"erro": "Produto nao encontrado."}, status=404)

    if quantidade < 1 or quantidade > produto["quantidade"]:
        return JsonResponse({"erro": "Quantidade indisponivel."}, status=400)

    if ObjectId is None or produto_id.startswith("mock-"):
        return JsonResponse({"erro": "MongoDB indisponivel para compra."}, status=503)

    try:
        object_id = ObjectId(produto_id)
        result = produtos_collection.update_one(
            {"_id": object_id, "quantidade": {"$gte": quantidade}},
            {"$inc": {"quantidade": -quantidade}},
        )

        if result.modified_count == 0:
            return JsonResponse({"erro": "Estoque insuficiente."}, status=400)

        compras_collection.update_one(
            {"usuario_id": request.user.id, "produto_id": produto["id"]},
            {
                "$set": {
                    "usuario": request.user.username,
                    "nome": produto["nome"],
                    "valor": produto["valor"],
                    "atualizado_em": timezone.now(),
                },
                "$setOnInsert": {"comprado_em": timezone.now()},
                "$inc": {"quantidade": quantidade},
            },
            upsert=True,
        )
    except INVALID_MONGO_ERRORS:
        return JsonResponse({"erro": "Nao foi possivel registrar a compra."}, status=503)

    return JsonResponse({"mensagem": "Produto adicionado ao carrinho."})


@csrf_exempt
@require_http_methods(["GET"])
def carrinho(request):
    auth = _auth_required(request)

    if auth:
        return auth

    if is_manager(request.user):
        return JsonResponse({"erro": "Managers nao possuem carrinho."}, status=403)

    try:
        compras = list(compras_collection.find({"usuario_id": request.user.id}).sort("comprado_em", -1))
    except MONGO_ERRORS:
        return JsonResponse({"erro": "Nao foi possivel consultar o carrinho."}, status=503)

    itens = [_serialize(compra) for compra in compras]
    total = sum(item["subtotal"] for item in itens)
    return JsonResponse({"itens": itens, "total": total, "role": get_role(request.user)})


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
def item_carrinho(request, compra_id):
    auth = _auth_required(request)

    if auth:
        return auth

    if is_manager(request.user):
        return JsonResponse({"erro": "Managers nao possuem carrinho."}, status=403)

    if ObjectId is None:
        return JsonResponse({"erro": "pymongo nao esta disponivel."}, status=503)

    try:
        object_id = ObjectId(compra_id)
        compra = compras_collection.find_one({"_id": object_id, "usuario_id": request.user.id})
    except INVALID_MONGO_ERRORS:
        return JsonResponse({"erro": "Item invalido."}, status=400)

    if not compra:
        return JsonResponse({"erro": "Item nao encontrado."}, status=404)

    try:
        produto_id = ObjectId(compra["produto_id"])
    except InvalidId:
        return JsonResponse({"erro": "Produto invalido."}, status=400)

    if request.method == "DELETE":
        try:
            produtos_collection.update_one({"_id": produto_id}, {"$inc": {"quantidade": int(compra["quantidade"])}})
            compras_collection.delete_one({"_id": object_id})
        except MONGO_ERRORS:
            return JsonResponse({"erro": "Nao foi possivel excluir o item."}, status=503)

        return JsonResponse({"mensagem": "Item removido."})

    data = _body(request)

    if data is None:
        return JsonResponse({"erro": "JSON invalido."}, status=400)

    try:
        nova_quantidade = int(data.get("quantidade") or 1)
    except ValueError:
        return JsonResponse({"erro": "Quantidade invalida."}, status=400)

    if nova_quantidade < 1:
        return JsonResponse({"erro": "Quantidade invalida."}, status=400)

    atual = int(compra["quantidade"])
    diferenca = nova_quantidade - atual

    try:
        if diferenca > 0:
            result = produtos_collection.update_one(
                {"_id": produto_id, "quantidade": {"$gte": diferenca}},
                {"$inc": {"quantidade": -diferenca}},
            )

            if result.modified_count == 0:
                return JsonResponse({"erro": "Estoque insuficiente."}, status=400)
        elif diferenca < 0:
            produtos_collection.update_one({"_id": produto_id}, {"$inc": {"quantidade": abs(diferenca)}})

        compras_collection.update_one(
            {"_id": object_id},
            {"$set": {"quantidade": nova_quantidade, "atualizado_em": timezone.now()}},
        )
    except MONGO_ERRORS:
        return JsonResponse({"erro": "Nao foi possivel atualizar o item."}, status=503)

    return JsonResponse({"mensagem": "Quantidade atualizada."})
