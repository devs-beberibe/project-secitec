from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('criar/', views.create, name='create'),
    path('consultar/', views.query, name='query'),
]