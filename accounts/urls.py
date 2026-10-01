from django.urls import path
from .views import *

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("usuario/", UsuarioView.as_view(), name="usuario"),
    path("alterar-senha", AlterarSenhaView.as_view(), name="alterar-senha"),
]
