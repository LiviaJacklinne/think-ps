from django.urls import path

from . import api_views


urlpatterns = [
    path("produtos/", api_views.produtos, name="api_produtos"),
    path("produtos/<str:produto_id>/", api_views.produto_detalhe, name="api_produto_detalhe"),
    path("produtos/<str:produto_id>/comprar/", api_views.comprar_produto, name="api_comprar_produto"),
    path("carrinho/", api_views.carrinho, name="api_carrinho"),
    path("carrinho/<str:compra_id>/", api_views.item_carrinho, name="api_item_carrinho"),
]
