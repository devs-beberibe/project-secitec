from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from accounts.permissions import IsAdministracao, IsTecnico
from .models import *
from .serializers import *
from rest_framework.response import Response

