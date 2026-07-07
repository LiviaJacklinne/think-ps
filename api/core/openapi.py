from django.http import HttpResponse, JsonResponse


OPENAPI_SCHEMA = {
    "openapi": "3.0.3",
    "info": {
        "title": "Think PS API",
        "version": "1.0.0",
        "description": "API para autenticação, usuários, produtos e carrinho do Think PS.",
    },
    "servers": [
        {
            "url": "http://localhost:8000",
            "description": "Django local",
        },
        {
            "url": "http://localhost:3000",
            "description": "Next.js proxy local",
        },
    ],
    "tags": [
        {"name": "Auth"},
        {"name": "Usuários"},
        {"name": "Produtos"},
        {"name": "Carrinho"},
    ],
    "paths": {
        "/api/auth/login/": {
            "post": {
                "tags": ["Auth"],
                "summary": "Realiza login",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/LoginRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Login realizado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}},
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                },
            }
        },
        "/api/auth/logout/": {
            "post": {
                "tags": ["Auth"],
                "summary": "Realiza logout",
                "responses": {
                    "200": {"description": "Logout realizado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Message"}}}},
                },
            }
        },
        "/api/auth/me/": {
            "get": {
                "tags": ["Auth"],
                "summary": "Retorna o usuário logado",
                "responses": {
                    "200": {"description": "Usuário autenticado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CurrentUser"}}}},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                },
            },
            "post": {
                "tags": ["Auth"],
                "summary": "Atualiza o perfil do usuário logado",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ProfileUpdateRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Perfil atualizado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}},
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                },
            },
        },
        "/api/auth/cadastro/": {
            "post": {
                "tags": ["Usuários"],
                "summary": "Cria um usuário",
                "description": "A primeira conta vira manager. Depois disso, apenas managers podem cadastrar usuários.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/UserCreateRequest"}
                        }
                    },
                },
                "responses": {
                    "201": {"description": "Usuário criado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}},
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "403": {"$ref": "#/components/responses/Forbidden"},
                },
            }
        },
        "/api/auth/usuarios/": {
            "get": {
                "tags": ["Usuários"],
                "summary": "Lista usuários",
                "description": "Apenas managers.",
                "responses": {
                    "200": {"description": "Usuários listados", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UsersResponse"}}}},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "403": {"$ref": "#/components/responses/Forbidden"},
                },
            }
        },
        "/api/auth/usuarios/{user_id}/": {
            "patch": {
                "tags": ["Usuários"],
                "summary": "Edita um usuário",
                "description": "Apenas managers.",
                "parameters": [{"$ref": "#/components/parameters/UserId"}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/UserUpdateRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Usuário atualizado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}},
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "403": {"$ref": "#/components/responses/Forbidden"},
                    "404": {"$ref": "#/components/responses/NotFound"},
                },
            }
        },
        "/api/compras/produtos/": {
            "get": {
                "tags": ["Produtos"],
                "summary": "Lista produtos",
                "parameters": [{"$ref": "#/components/parameters/SearchQuery"}],
                "responses": {
                    "200": {"description": "Produtos listados", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ProductsResponse"}}}},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                },
            },
            "post": {
                "tags": ["Produtos"],
                "summary": "Cria produto",
                "description": "Apenas managers.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ProductRequest"}
                        }
                    },
                },
                "responses": {
                    "201": {"description": "Produto criado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Product"}}}},
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "403": {"$ref": "#/components/responses/Forbidden"},
                    "503": {"$ref": "#/components/responses/ServiceUnavailable"},
                },
            },
        },
        "/api/compras/produtos/{produto_id}/": {
            "patch": {
                "tags": ["Produtos"],
                "summary": "Edita produto",
                "description": "Apenas managers.",
                "parameters": [{"$ref": "#/components/parameters/ProductId"}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ProductRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Produto atualizado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Product"}}}},
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "403": {"$ref": "#/components/responses/Forbidden"},
                    "404": {"$ref": "#/components/responses/NotFound"},
                    "503": {"$ref": "#/components/responses/ServiceUnavailable"},
                },
            }
        },
        "/api/compras/produtos/{produto_id}/comprar/": {
            "post": {
                "tags": ["Carrinho"],
                "summary": "Adiciona produto ao carrinho",
                "description": "Apenas usuários comuns. Managers não possuem carrinho.",
                "parameters": [{"$ref": "#/components/parameters/ProductId"}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/BuyRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Produto adicionado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Message"}}}},
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "403": {"$ref": "#/components/responses/Forbidden"},
                    "404": {"$ref": "#/components/responses/NotFound"},
                    "503": {"$ref": "#/components/responses/ServiceUnavailable"},
                },
            }
        },
        "/api/compras/carrinho/": {
            "get": {
                "tags": ["Carrinho"],
                "summary": "Lista itens do carrinho",
                "responses": {
                    "200": {"description": "Carrinho listado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CartResponse"}}}},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "403": {"$ref": "#/components/responses/Forbidden"},
                    "503": {"$ref": "#/components/responses/ServiceUnavailable"},
                },
            }
        },
        "/api/compras/carrinho/{compra_id}/": {
            "patch": {
                "tags": ["Carrinho"],
                "summary": "Atualiza quantidade de um item do carrinho",
                "parameters": [{"$ref": "#/components/parameters/CartItemId"}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/BuyRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Quantidade atualizada", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Message"}}}},
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "403": {"$ref": "#/components/responses/Forbidden"},
                    "404": {"$ref": "#/components/responses/NotFound"},
                    "503": {"$ref": "#/components/responses/ServiceUnavailable"},
                },
            },
            "delete": {
                "tags": ["Carrinho"],
                "summary": "Remove item do carrinho",
                "parameters": [{"$ref": "#/components/parameters/CartItemId"}],
                "responses": {
                    "200": {"description": "Item removido", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Message"}}}},
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "401": {"$ref": "#/components/responses/Unauthorized"},
                    "403": {"$ref": "#/components/responses/Forbidden"},
                    "404": {"$ref": "#/components/responses/NotFound"},
                    "503": {"$ref": "#/components/responses/ServiceUnavailable"},
                },
            },
        },
    },
    "components": {
        "parameters": {
            "UserId": {"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}},
            "ProductId": {"name": "produto_id", "in": "path", "required": True, "schema": {"type": "string"}},
            "CartItemId": {"name": "compra_id", "in": "path", "required": True, "schema": {"type": "string"}},
            "SearchQuery": {"name": "q", "in": "query", "required": False, "schema": {"type": "string"}},
        },
        "responses": {
            "BadRequest": {"description": "Requisição inválida", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            "Unauthorized": {"description": "Não autenticado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            "Forbidden": {"description": "Sem permissão", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            "NotFound": {"description": "Não encontrado", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            "ServiceUnavailable": {"description": "Serviço indisponível", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
        },
        "schemas": {
            "Error": {
                "type": "object",
                "properties": {"erro": {"type": "string"}},
                "required": ["erro"],
            },
            "Message": {
                "type": "object",
                "properties": {"mensagem": {"type": "string"}},
                "required": ["mensagem"],
            },
            "LoginRequest": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "example": "manager"},
                    "password": {"type": "string", "example": "12345678"},
                },
                "required": ["username", "password"],
            },
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "role": {"type": "string", "enum": ["manager", "user"]},
                },
                "required": ["id", "username", "email", "role"],
            },
            "CurrentUser": {
                "allOf": [
                    {"$ref": "#/components/schemas/User"},
                    {
                        "type": "object",
                        "properties": {"autenticado": {"type": "boolean"}},
                        "required": ["autenticado"],
                    },
                ]
            },
            "UserCreateRequest": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "password": {"type": "string"},
                    "role": {"type": "string", "enum": ["manager", "user"], "default": "user"},
                },
                "required": ["username", "password"],
            },
            "UserUpdateRequest": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "password": {"type": "string"},
                    "role": {"type": "string", "enum": ["manager", "user"]},
                },
                "required": ["username", "role"],
            },
            "ProfileUpdateRequest": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "password": {"type": "string"},
                },
                "required": ["username"],
            },
            "ProductRequest": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "example": "Pneu"},
                    "quantidade": {"type": "integer", "minimum": 0, "example": 4},
                    "valor": {"type": "number", "minimum": 0, "example": 389.9},
                },
                "required": ["nome", "quantidade", "valor"],
            },
            "Product": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "nome": {"type": "string"},
                    "quantidade": {"type": "integer"},
                    "valor": {"type": "number"},
                    "subtotal": {"type": "number"},
                },
                "required": ["id", "nome", "quantidade", "valor", "subtotal"],
            },
            "ProductsResponse": {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "enum": ["manager", "user"]},
                    "usando_mock": {"type": "boolean"},
                    "produtos": {"type": "array", "items": {"$ref": "#/components/schemas/Product"}},
                },
                "required": ["role", "usando_mock", "produtos"],
            },
            "BuyRequest": {
                "type": "object",
                "properties": {"quantidade": {"type": "integer", "minimum": 1, "example": 2}},
                "required": ["quantidade"],
            },
            "CartResponse": {
                "type": "object",
                "properties": {
                    "itens": {"type": "array", "items": {"$ref": "#/components/schemas/Product"}},
                    "total": {"type": "number"},
                    "role": {"type": "string", "enum": ["manager", "user"]},
                },
                "required": ["itens", "total", "role"],
            },
            "UsersResponse": {
                "type": "object",
                "properties": {
                    "usuarios": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}
                },
                "required": ["usuarios"],
            },
        },
    },
}


def openapi_schema(_request):
    return JsonResponse(OPENAPI_SCHEMA)


def swagger_ui(_request):
    html = """
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Think PS API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.ui = SwaggerUIBundle({
        url: "/api/schema/",
        dom_id: "#swagger-ui",
        deepLinking: true,
        persistAuthorization: true
      });
    </script>
  </body>
</html>
"""
    return HttpResponse(html)
