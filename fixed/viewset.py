import json
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from accounts.permissions import IsAdministracao, IsTecnico
from .models import *
from .serializers import *



class FichaEntradaViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceSheet.objects.all()
    serializer_class = FichaEntradaSerializer
    permission_classes = [IsTecnico]

class FichaSaidaViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceSheet.objects.all()
    serializer_class = FichaSaidaSerializer
    permission_classes = [IsTecnico]


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.all()
    serializer_class = ComponentSeriliazer
    permission_classes = [IsAdminUser]

class AdministracaoFichaViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceSheet.objects.all()
    serializer_class = AdministracaoFichaSerializer
    permission_classes = [IsAdministracao]

class StatusComponentesViewSet(viewsets.ModelViewSet):
    queryset = ComponentStatus.objects.all()
    serializer_class = StatusComponentesSerializer
    permission_classes = [IsAdminUser]
