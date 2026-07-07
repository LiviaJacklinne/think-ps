try:
    from pymongo.errors import PyMongoError
except ImportError:
    PyMongoError = Exception

from .mongo import produtos_collection


MONGO_ERRORS = (PyMongoError, RuntimeError)

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


def normalizar_produto(produto):
    produto["id"] = str(produto.get("_id", produto.get("id", "")))
    produto["valor"] = float(produto.get("valor", 0))
    produto["quantidade"] = int(produto.get("quantidade", 0))
    produto["subtotal"] = produto["valor"] * produto["quantidade"]
    return produto


def seed_produtos():
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


def listar_produtos(termo):
    try:
        seed_produtos()
        filtro = {}

        if termo:
            filtro = {"nome": {"$regex": termo, "$options": "i"}}

        produtos = produtos_collection.find(filtro).sort("nome", 1)
        return [normalizar_produto(produto) for produto in produtos], False
    except MONGO_ERRORS:
        produtos = [
            normalizar_produto({"id": f"mock-{index}", **produto})
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
