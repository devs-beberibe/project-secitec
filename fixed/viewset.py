import json
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import *
from .serializers import *


class SectorViewSet(viewsets.ModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [AllowAny]


class MaintenanceSheetViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceSheet.objects.all()
    serializer_class = MaintenanceSheetSerializer
    permission_classes = [AllowAny]


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.all()
    serializer_class = ComponentSeriliazer
    permission_classes = [AllowAny]


class ComponentStatusViewSet(viewsets.ModelViewSet):
    queryset = ComponentStatus.objects.all()
    serializer_class = ComponentStatusSerializer
    permission_classes = [AllowAny]
