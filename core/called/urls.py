from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('criar/', views.create_page, name='create_page'),
    path('criar/add/', views.create, name='create'),
    path('consultar/', views.query, name='query'),
    path('consultar/<int:call_id>/detalhes', views.detail, name='detail'),
    
]