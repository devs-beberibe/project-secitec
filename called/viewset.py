import json
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import *
from .serializers import *


class SecretaryViewSet(viewsets.ModelViewSet):
    queryset = Secretary.objects.all()
    serializer_class = SecretarySerializer
    permission_classes = [AllowAny]


class CallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all()
    serializer_class = CallSerialzier
    permission_classes = [AllowAny]


class TechnicianViewSet(viewsets.ModelViewSet):
    queryset = Technician.objects.all()
    serializer_class = TechnicianSerializer
    permission_classes = [AllowAny]
