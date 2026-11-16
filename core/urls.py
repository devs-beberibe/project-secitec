from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", admin.site.urls),
    path("api/v1/called/", include("called.urls")),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/fixed/", include("fixed.urls")),
    path("entrar/", views.login_page, name="login-page"),
    path("chamados/dashboard/", views.home, {"dashboard_page": True}, name="dashboard",),
    path("fichas/manutencao/",views.maintenance_page,name="maintenance-page"),
    ]
