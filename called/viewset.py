import json
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from .models import *
from .serializers import *
from accounts.permissions import IsAdministracao, IsTecnico


class SecretaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SecretarySector.objects.all()
    serializer_class = SecretarySerializer
    permission_classes = [IsAuthenticated]


class CreateCallViewSet(viewsets.ModelViewSet):
    serializer_class = CreateCallSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name__startswith="Tecnico").exists():
            return Call.objects.all()

        return Call.objects.filter(secretary_sector__user=user)


class UptdateCallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all()
    serializer_class = UpdateCallSerializer
    permission_classes = [IsTecnico]


class TecnicoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Technician.objects.all()
    serializer_class = TecnicoSerializer
    permission_classes = [IsAuthenticated]
