from rest_framework import routers

from .viewset import *

router = routers.DefaultRouter()

router.register(r"chamados", PublicCallViewSet, basename="chamados")

router.register(r"technician", TechnicianViewSet, basename="technician")

router.register(r"secretary-sector", SecretaryViewSet, basename="secretary-sector")

router.register(r"adminsec-chamados", AdministracaoSecCallViewSet, basename="adminsec-chamados")

router.register(r"admin-chamados", AdminViewSet, basename="admin-chamados")

router.register(r"tecnico-chamados", TechnicianCallViewSet, basename="tecnico-chamados")