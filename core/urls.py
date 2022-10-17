from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('chamados/', include('called.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
