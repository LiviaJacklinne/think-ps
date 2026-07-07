from django.urls import path

from . import views


urlpatterns = [
    path("", views.lista_produtos, name="lista_produtos"),
    path("carrinho/", views.carrinho, name="carrinho"),
    path("carrinho/<str:compra_id>/atualizar/", views.atualizar_item_carrinho, name="atualizar_item_carrinho"),
    path("carrinho/<str:compra_id>/excluir/", views.excluir_item_carrinho, name="excluir_item_carrinho"),
    path("produtos/<str:produto_id>/comprar/", views.comprar_produto, name="comprar_produto"),
    path("produtos/novo/", views.cadastrar_produto, name="cadastrar_produto"),
    path("produtos/<str:produto_id>/editar/", views.editar_produto, name="editar_produto"),
]
