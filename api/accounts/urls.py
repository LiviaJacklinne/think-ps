from django.urls import path

from . import views


urlpatterns = [
    path("cadastro/", views.cadastro, name="cadastro"),
    path("usuarios/", views.usuarios, name="usuarios"),
    path("usuarios/<int:user_id>/", views.usuario_detalhe, name="usuario_detalhe"),
    path("login/", views.login_usuario, name="login_usuario"),
    path("logout/", views.logout_usuario, name="logout_usuario"),
    path("menu/", views.menu, name="menu"),
    path("me/", views.usuario_atual, name="usuario_atual"),
]
