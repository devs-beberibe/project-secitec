from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('criar/', views.create_page, name='create_page'),
    path('criar/add/', views.create, name='create'),
    path('encerrar/<int:id_call>', views.close, name='close'),
    path('listar/<str:stts>/<int:page>/', views.list, name='list'),
    path('consultar/', views.query, name='query'),
    path('consultar/detales', views.detail, name='detail'),
    path('consultar/editar/<int:id>/<str:status>', views.edit_status, name='edit'),
]