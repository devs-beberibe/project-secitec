from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", admin.site.urls),
    path("api/v1/called/", include("called.urls")),
    path("api/v1/fixed/", include("fixed.urls")),
]
