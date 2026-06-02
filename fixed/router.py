from rest_framework import routers
from rest_framework.routers import DefaultRouter

from .viewset import *

router = DefaultRouter()

router.register(r"components",ComponentViewSet,basename="component",)

router.register(r"components-status",ComponentStatusViewSet,basename="component-status",)

router.register(r"sector",SectorViewSet,basename="sector",)

router.register(r"maintenance-sheet",MaintenanceSheetViewSet,basename="maintenance-sheet",)
