from django.urls import path
from . import views 

urlpatterns = [
    path('criacao/', views.create,  name="create_fixed"),
    path('listagem/', views.list_fix,  name="list_fixed"),
]