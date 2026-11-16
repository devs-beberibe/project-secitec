from rest_framework import routers

from .views import MaintenanceSheetViewSet


router = routers.DefaultRouter()

router.register(
    "ficha-manutencao",
    MaintenanceSheetViewSet,
    basename="ficha-manutencao",
)