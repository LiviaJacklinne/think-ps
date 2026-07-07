from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

try:
    from pymongo.errors import PyMongoError
except ImportError:
    PyMongoError = Exception

try:
    from bson import ObjectId
    from bson.errors import InvalidId
except ImportError:
    ObjectId = None
    InvalidId = ValueError

from accounts.roles import get_role, is_manager
from .mongo import compras_collection, produtos_collection


MOCK_PRODUTOS = [
    {
        "nome": "Pneu",
        "quantidade": 4,
        "valor": 389.9,
    },
    {
        "nome": "Televisao",
        "quantidade": 2,
        "valor": 2199.0,
    },
    {
        "nome": "Cafe",
        "quantidade": 10,
        "valor": 18.5,
    },
]

OLD_MOCK_NAMES = {"Arroz integral", "Cafe especial", "Sabonete liquido"}


def _produto_context(request, **extra):
    context = {"role": get_role(request.user)}
    context.update(extra)
    return context


def _normalizar_produto(produto):
    produto["id"] = str(produto.get("_id", produto.get("id", "")))
    produto["valor"] = float(produto.get("valor", 0))
    produto["quantidade"] = int(produto.get("quantidade", 0))
    produto["subtotal"] = produto["valor"] * produto["quantidade"]
    return produto


def _seed_produtos():
    total = produtos_collection.count_documents({})

    if total == 0:
        produtos_collection.insert_many(MOCK_PRODUTOS)
        return

    nomes = {
        produto.get("nome")
        for produto in produtos_collection.find({}, {"nome": 1})
    }

    if nomes and nomes.issubset(OLD_MOCK_NAMES):
        produtos_collection.delete_many({})
        produtos_collection.insert_many(MOCK_PRODUTOS)
        return

    for produto in MOCK_PRODUTOS:
        produtos_collection.update_one(
            {"nome": produto["nome"]},
            {"$setOnInsert": produto},
            upsert=True,
        )


def _listar_produtos(termo):
    try:
        _seed_produtos()
        filtro = {}

        if termo:
            filtro = {"nome": {"$regex": termo, "$options": "i"}}

        produtos = produtos_collection.find(filtro).sort("nome", 1)
        return [_normalizar_produto(produto) for produto in produtos], False
    except PyMongoError:
        produtos = [
            _normalizar_produto({"id": f"mock-{index}", **produto})
            for index, produto in enumerate(MOCK_PRODUTOS, start=1)
        ]

        if termo:
            termo_normalizado = termo.lower()
            produtos = [
                produto
                for produto in produtos
                if termo_normalizado in produto["nome"].lower()
            ]

        return produtos, True


def _manager_required(request):
    if is_manager(request.user):
        return None

    messages.error(request, "Apenas managers podem cadastrar ou editar produtos.")
    return redirect("lista_produtos")


def _buscar_produto_por_id(produto_id):
    if produto_id.startswith("mock-"):
        try:
            index = int(produto_id.split("-", 1)[1]) - 1
            return _normalizar_produto({"id": produto_id, **MOCK_PRODUTOS[index]})
        except (IndexError, ValueError):
            return None

    if ObjectId is None:
        return None

    try:
        produto = produtos_collection.find_one({"_id": ObjectId(produto_id)})
    except (InvalidId, PyMongoError):
        return None

    if not produto:
        return None

    return _normalizar_produto(produto)


def _buscar_compra_do_usuario(compra_id, user):
    if ObjectId is None:
        return None, None

    try:
        object_id = ObjectId(compra_id)
    except InvalidId:
        return None, None

    try:
        compra = compras_collection.find_one(
            {
                "_id": object_id,
                "usuario_id": user.id,
            }
        )
    except PyMongoError:
        return None, None

    return object_id, compra


@login_required
def lista_produtos(request):
    termo = request.GET.get("q", "").strip()
    produtos, usando_mock = _listar_produtos(termo)

    return render(
        request,
        "compras/produtos.html",
        _produto_context(
            request,
            produtos=produtos,
            termo=termo,
            usando_mock=usando_mock,
        ),
    )


@login_required
@require_http_methods(["POST"])
def comprar_produto(request, produto_id):
    if is_manager(request.user):
        messages.error(request, "Managers nao possuem carrinho.")
        return redirect("lista_produtos")

    produto = _buscar_produto_por_id(produto_id)

    if not produto:
        messages.error(request, "Produto nao encontrado.")
        return redirect("lista_produtos")

    try:
        quantidade = int(request.POST.get("quantidade") or 1)
    except ValueError:
        messages.error(request, "Quantidade invalida.")
        return redirect("lista_produtos")

    if quantidade < 1:
        messages.error(request, "Selecione pelo menos 1 unidade.")
        return redirect("lista_produtos")

    if quantidade > produto["quantidade"]:
        messages.error(request, "Quantidade maior que o estoque disponivel.")
        return redirect("lista_produtos")

    compra = {
        "usuario_id": request.user.id,
        "usuario": request.user.username,
        "produto_id": produto["id"],
        "nome": produto["nome"],
        "valor": produto["valor"],
        "quantidade": quantidade,
        "comprado_em": timezone.now(),
    }

    estoque_decrementado = False

    try:
        if ObjectId is None or produto_id.startswith("mock-"):
            messages.error(request, "Nao foi possivel atualizar o estoque no MongoDB agora.")
            return redirect("lista_produtos")

        object_id = ObjectId(produto_id)
        result = produtos_collection.update_one(
            {
                "_id": object_id,
                "quantidade": {"$gte": quantidade},
            },
            {"$inc": {"quantidade": -quantidade}},
        )

        if result.modified_count == 0:
            messages.error(request, "Estoque insuficiente para essa compra.")
            return redirect("lista_produtos")

        estoque_decrementado = True
        compras_collection.update_one(
            {
                "usuario_id": request.user.id,
                "produto_id": produto["id"],
            },
            {
                "$set": {
                    "usuario": request.user.username,
                    "nome": produto["nome"],
                    "valor": produto["valor"],
                    "atualizado_em": timezone.now(),
                },
                "$setOnInsert": {
                    "comprado_em": timezone.now(),
                },
                "$inc": {
                    "quantidade": quantidade,
                },
            },
            upsert=True,
        )
        messages.success(request, "Compra adicionada ao carrinho.")
    except PyMongoError:
        if estoque_decrementado:
            try:
                produtos_collection.update_one(
                    {"_id": object_id},
                    {"$inc": {"quantidade": quantidade}},
                )
            except PyMongoError:
                pass

        messages.error(request, "Nao foi possivel registrar a compra agora.")

    return redirect("lista_produtos")


@login_required
@require_http_methods(["POST"])
def atualizar_item_carrinho(request, compra_id):
    if is_manager(request.user):
        messages.error(request, "Managers nao possuem carrinho.")
        return redirect("lista_produtos")

    object_id, compra = _buscar_compra_do_usuario(compra_id, request.user)

    if not compra:
        messages.error(request, "Item do carrinho nao encontrado.")
        return redirect("carrinho")

    try:
        nova_quantidade = int(request.POST.get("quantidade") or 1)
    except ValueError:
        messages.error(request, "Quantidade invalida.")
        return redirect("carrinho")

    if nova_quantidade < 1:
        messages.error(request, "Selecione pelo menos 1 unidade.")
        return redirect("carrinho")

    quantidade_atual = int(compra.get("quantidade", 0))
    diferenca = nova_quantidade - quantidade_atual

    if diferenca == 0:
        messages.success(request, "Quantidade mantida.")
        return redirect("carrinho")

    produto_id = compra.get("produto_id")

    if ObjectId is None:
        messages.error(request, "Nao foi possivel atualizar o carrinho agora.")
        return redirect("carrinho")

    try:
        produto_object_id = ObjectId(produto_id)
    except InvalidId:
        messages.error(request, "Produto invalido.")
        return redirect("carrinho")

    estoque_alterado = False

    try:
        if diferenca > 0:
            result = produtos_collection.update_one(
                {
                    "_id": produto_object_id,
                    "quantidade": {"$gte": diferenca},
                },
                {"$inc": {"quantidade": -diferenca}},
            )

            if result.modified_count == 0:
                messages.error(request, "Estoque insuficiente para essa quantidade.")
                return redirect("carrinho")

            estoque_alterado = True
        else:
            produtos_collection.update_one(
                {"_id": produto_object_id},
                {"$inc": {"quantidade": abs(diferenca)}},
            )
            estoque_alterado = True

        compras_collection.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "quantidade": nova_quantidade,
                    "atualizado_em": timezone.now(),
                }
            },
        )
        messages.success(request, "Quantidade atualizada.")
    except PyMongoError:
        if estoque_alterado:
            try:
                produtos_collection.update_one(
                    {"_id": produto_object_id},
                    {"$inc": {"quantidade": diferenca}},
                )
            except PyMongoError:
                pass

        messages.error(request, "Nao foi possivel atualizar o carrinho agora.")

    return redirect("carrinho")


@login_required
@require_http_methods(["POST"])
def excluir_item_carrinho(request, compra_id):
    if is_manager(request.user):
        messages.error(request, "Managers nao possuem carrinho.")
        return redirect("lista_produtos")

    object_id, compra = _buscar_compra_do_usuario(compra_id, request.user)

    if not compra:
        messages.error(request, "Item do carrinho nao encontrado.")
        return redirect("carrinho")

    produto_id = compra.get("produto_id")
    quantidade = int(compra.get("quantidade", 0))

    try:
        if ObjectId is not None:
            produtos_collection.update_one(
                {"_id": ObjectId(produto_id)},
                {"$inc": {"quantidade": quantidade}},
            )

        compras_collection.delete_one({"_id": object_id})
        messages.success(request, "Item removido do carrinho.")
    except (InvalidId, PyMongoError):
        messages.error(request, "Nao foi possivel excluir o item agora.")

    return redirect("carrinho")


@login_required
def carrinho(request):
    if is_manager(request.user):
        messages.error(request, "Managers nao possuem carrinho.")
        return redirect("lista_produtos")

    try:
        compras = list(
            compras_collection.find({"usuario_id": request.user.id}).sort("comprado_em", -1)
        )
        compras = [_normalizar_produto(compra) for compra in compras]
        usando_mock = False
    except PyMongoError:
        compras = []
        usando_mock = True

    total = sum(compra["valor"] * compra["quantidade"] for compra in compras)

    return render(
        request,
        "compras/carrinho.html",
        _produto_context(
            request,
            compras=compras,
            total=total,
            usando_mock=usando_mock,
        ),
    )


@login_required
@require_http_methods(["GET", "POST"])
def cadastrar_produto(request):
    bloqueio = _manager_required(request)

    if bloqueio:
        return bloqueio

    if request.method == "POST":
        produto = {
            "nome": request.POST.get("nome", "").strip(),
            "quantidade": int(request.POST.get("quantidade") or 0),
            "valor": float(request.POST.get("valor") or 0),
        }

        if not produto["nome"]:
            messages.error(request, "Informe o nome do produto.")
            return render(
                request,
                "compras/produto_form.html",
                _produto_context(request, produto=produto, modo="Cadastrar"),
                status=400,
            )

        try:
            produtos_collection.insert_one(produto)
            messages.success(request, "Produto cadastrado com sucesso.")
        except PyMongoError:
            messages.error(request, "Nao foi possivel salvar no MongoDB agora.")

        return redirect("lista_produtos")

    return render(
        request,
        "compras/produto_form.html",
        _produto_context(request, produto={}, modo="Cadastrar"),
    )


@login_required
@require_http_methods(["GET", "POST"])
def editar_produto(request, produto_id):
    bloqueio = _manager_required(request)

    if bloqueio:
        return bloqueio

    if ObjectId is None:
        messages.error(request, "Instale o pymongo no ambiente para editar produtos.")
        return redirect("lista_produtos")

    try:
        object_id = ObjectId(produto_id)
    except InvalidId:
        messages.error(request, "Produto invalido.")
        return redirect("lista_produtos")

    try:
        produto = produtos_collection.find_one({"_id": object_id})
    except PyMongoError:
        messages.error(request, "Nao foi possivel consultar o MongoDB agora.")
        return redirect("lista_produtos")

    if not produto:
        messages.error(request, "Produto nao encontrado.")
        return redirect("lista_produtos")

    produto = _normalizar_produto(produto)

    if request.method == "POST":
        dados = {
            "nome": request.POST.get("nome", "").strip(),
            "quantidade": int(request.POST.get("quantidade") or 0),
            "valor": float(request.POST.get("valor") or 0),
        }

        if not dados["nome"]:
            messages.error(request, "Informe o nome do produto.")
            produto.update(dados)
            return render(
                request,
                "compras/produto_form.html",
                _produto_context(request, produto=produto, modo="Editar"),
                status=400,
            )

        try:
            produtos_collection.update_one({"_id": object_id}, {"$set": dados})
            messages.success(request, "Produto atualizado com sucesso.")
        except PyMongoError:
            messages.error(request, "Nao foi possivel atualizar no MongoDB agora.")

        return redirect("lista_produtos")

    return render(
        request,
        "compras/produto_form.html",
        _produto_context(request, produto=produto, modo="Editar"),
    )
