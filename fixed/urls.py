from django.urls import path
from . import views 

urlpatterns = [
    path('entrada/', views.create,  name="create_fixed"),
    path('<str:id>/saida/', views.update,  name="update_fixed"),
    path('listagem/', views.list_fix,  name="list_fixed"),
]