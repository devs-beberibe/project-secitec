from django.urls import path, include
from . import views

from .router import router


urlpatterns = [
    path("entrada/", views.create, name="create_fixed"),
    path("<str:id>/saida/", views.update, name="update_fixed"),
    path("listagem/", views.list_fix, name="list_fixed"),
]

urlpatterns += router.urls