import json
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from accounts.permissions import IsAdministracao, IsTecnico
from .models import *
from .serializers import *


