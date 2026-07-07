from django.urls import path

from . import views


urlpatterns = [
    path("cadastro/", views.cadastro, name="cadastro"),
    path("login/", views.login_usuario, name="login_usuario"),
    path("logout/", views.logout_usuario, name="logout_usuario"),
    path("me/", views.usuario_atual, name="usuario_atual"),
]
