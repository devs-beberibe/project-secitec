from django.urls import path, include

from . import views
from .router import router

from rest_framework import routers

urlpatterns = [

]

urlpatterns += router.urls
