from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('criar/', views.create, name='create'),
    path('<int:id_call>/encerrar/', views.close, name='close'),
    path('<int:id_call>/detalhes/', views.detail, name='detail'),
    path('listar/', views.list, name='list'),
    path('consultar/', views.query, name='query'),
    path('consultar/detales', views.detail, name='detail'),
    path('consultar/<int:id>/editar/<str:status>', views.edit_status, name='edit'),
]