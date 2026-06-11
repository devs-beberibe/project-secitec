import json
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from accounts.permissions import IsAdministracao, IsTecnico
from .models import *
from .serializers import *


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Components.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [IsTecnico | IsAdministracao]


class FichaEntradaViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceSheet.objects.all()
    serializer_class = ReceiveFixSerializer
    permission_classes = [IsTecnico | IsAdministracao]


class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceSheet.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [IsTecnico | IsAdministracao]


class FichaSaidaViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceSheet.objects.all()
    serializer_class = CloseFixSerializer
    permission_classes = [IsTecnico | IsAdministracao]
