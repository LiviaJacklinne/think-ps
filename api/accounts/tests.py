import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from .roles import USER, assign_role, get_role


User = get_user_model()


class AccountsApiTests(TestCase):
    def test_criar_primeira_conta_define_manager(self):
        response = self.client.post(
            "/api/auth/cadastro/",
            data=json.dumps(
                {
                    "username": "livia",
                    "email": "livia@example.com",
                    "password": "12345678",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "livia")
        self.assertEqual(response.json()["role"], "manager")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(get_role(User.objects.get(username="livia")), "manager")

    def test_validar_email_unico_ao_editar_perfil(self):
        user = User.objects.create_user(
            username="usuario",
            email="usuario@example.com",
            password="12345678",
        )
        other_user = User.objects.create_user(
            username="outro",
            email="outro@example.com",
            password="12345678",
        )
        assign_role(user, USER)
        assign_role(other_user, USER)
        self.client.force_login(user)

        response = self.client.post(
            "/api/auth/me/",
            data=json.dumps(
                {
                    "username": "usuario",
                    "email": "outro@example.com",
                    "password": "",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["erro"], "E-mail ja cadastrado.")
        user.refresh_from_db()
        self.assertEqual(user.email, "usuario@example.com")
