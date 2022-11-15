from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('criar/', views.create_page, name='create_page'),
    path('criar/add/', views.create, name='create'),
    path('listar/<str:stts>', views.list, name='list'),
    path('consultar/', views.query, name='query'),
    path('consultar/detales', views.detail, name='detail'),
    path('consultar/editar/<int:id>', views.edit_status, name='edit'),
]