import json
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from .models import *
from .serializers import *
from accounts.permissions import IsAdministracao, IsTecnico


class SecretaryViewSet(viewsets.ModelViewSet):
    queryset = SecretarySector.objects.all()
    serializer_class = SecretarySerializer
    permission_classes = [IsAdminUser]

        
class PublicCallViewSet(viewsets.ModelViewSet):
    serializer_class = PublicCallSerialzier
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name__startswith="Tecnico").exists():
            return Call.objects.all()

        return Call.objects.filter(secretary_sector__user=user)
    
#Viewset de chamados pra administradores da secretaria
class AdministracaoSecCallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all()
    serializer_class = AdministracaoCallSerializer
    permission_classes = [IsAdministracao]


class TechnicianCallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all()
    serializer_class = TecnicoCallSerializer
    permission_classes = [IsTecnico]


#Viewset de chamados para administradores do sistema
class AdminViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all()
    serializer_class = AdminCallSerializer
    permission_classes = [IsAdminUser]

class TechnicianViewSet(viewsets.ModelViewSet):
    queryset = Technician.objects.all()
    serializer_class = TecnicoSerializer
    permission_classes = [IsAdminUser]
