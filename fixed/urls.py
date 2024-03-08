from django.urls import path
from . import views 

urlpatterns = [
    path('criacao/', views.create,  name="create_fixed"),
]