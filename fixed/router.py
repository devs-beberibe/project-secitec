from rest_framework import routers
from rest_framework.routers import DefaultRouter

from .viewset import *

router = DefaultRouter()

router.register(r"componentes", ComponentViewSet, basename="componentes")

router.register(r"manutencao", MaintenanceViewSet, basename="manutencao")

router.register(
    r"ficha-saida",
    FichaSaidaViewSet,
    basename="ficha-saida",
)

router.register(
    r"ficha-entrada",
    FichaEntradaViewSet,
    basename="ficha-entrada",
)
