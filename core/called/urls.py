from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('criar/', views.create_page, name='create_page'),
    path('criar/add/', views.create, name='create'),
    path('consultar/<int:call_id>/', views.query, name='query'),
]