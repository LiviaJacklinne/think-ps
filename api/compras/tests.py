import json
from unittest.mock import patch

from bson import ObjectId
from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.roles import MANAGER, USER, assign_role


User = get_user_model()


class InsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class UpdateOneResult:
    def __init__(self, modified_count):
        self.modified_count = modified_count


class FakeCollection:
    def __init__(self, docs=None):
        self.docs = docs or []

    def insert_one(self, doc):
        inserted = {**doc, "_id": ObjectId()}
        self.docs.append(inserted)
        return InsertOneResult(inserted["_id"])

    def find_one(self, filtro):
        for doc in self.docs:
            if self._matches(doc, filtro):
                return doc

        return None

    def update_one(self, filtro, update, upsert=False):
        doc = self.find_one(filtro)

        if doc is None and upsert:
            doc = {**filtro}
            self.docs.append(doc)

        if doc is None:
            return UpdateOneResult(0)

        for key, value in update.get("$setOnInsert", {}).items():
            doc.setdefault(key, value)

        for key, value in update.get("$set", {}).items():
            doc[key] = value

        for key, value in update.get("$inc", {}).items():
            doc[key] = doc.get(key, 0) + value

        return UpdateOneResult(1)

    def _matches(self, doc, filtro):
        for key, value in filtro.items():
            if isinstance(value, dict) and "$gte" in value:
                if doc.get(key, 0) < value["$gte"]:
                    return False
                continue

            if doc.get(key) != value:
                return False

        return True


class ComprasApiTests(TestCase):
    def test_manager_cria_produto(self):
        manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="12345678",
        )
        assign_role(manager, MANAGER)
        self.client.force_login(manager)
        produtos_collection = FakeCollection()

        with patch("compras.api_views.produtos_collection", produtos_collection):
            response = self.client.post(
                "/api/compras/produtos/",
                data=json.dumps(
                    {
                        "nome": "Mouse",
                        "quantidade": 5,
                        "valor": 99.9,
                    }
                ),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["nome"], "Mouse")
        self.assertEqual(response.json()["quantidade"], 5)
        self.assertEqual(len(produtos_collection.docs), 1)

    def test_user_adiciona_item_ao_carrinho(self):
        user = User.objects.create_user(
            username="usuario",
            email="usuario@example.com",
            password="12345678",
        )
        assign_role(user, USER)
        self.client.force_login(user)

        produto_id = ObjectId()
        produtos_collection = FakeCollection(
            [
                {
                    "_id": produto_id,
                    "nome": "Teclado",
                    "quantidade": 10,
                    "valor": 150.0,
                }
            ]
        )
        compras_collection = FakeCollection()

        with patch("compras.api_views.produtos_collection", produtos_collection), patch(
            "compras.api_views.compras_collection", compras_collection
        ):
            response = self.client.post(
                f"/api/compras/produtos/{produto_id}/comprar/",
                data=json.dumps({"quantidade": 2}),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mensagem"], "Produto adicionado ao carrinho.")
        self.assertEqual(produtos_collection.docs[0]["quantidade"], 8)
        self.assertEqual(len(compras_collection.docs), 1)
        self.assertEqual(compras_collection.docs[0]["quantidade"], 2)
        self.assertEqual(compras_collection.docs[0]["usuario_id"], user.id)
