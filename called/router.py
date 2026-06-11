from rest_framework import routers

from .viewset import *

router = routers.DefaultRouter()

router.register(r"abrir-chamados", CreateCallViewSet, basename="abrir-chamados")

router.register(r"tecnico", TecnicoViewSet, basename="tecnico")

router.register(r"secretaria-setor", SecretaryViewSet, basename="secretaria-setor")

router.register(
    r"atualizar-chamados", UptdateCallViewSet, basename="atualizar-chamados"
)
