from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('criar/', views.create, name='create'),
    path('encerrar/<int:id_call>', views.close, name='close'),
    path('listar/', views.list, name='list'),
    path('consultar/', views.query, name='query'),
    path('consultar/detales', views.detail, name='detail'),
    path('consultar/editar/<int:id>/<str:status>', views.edit_status, name='edit'),
]