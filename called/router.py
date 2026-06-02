from rest_framework import routers

from .viewset import (SecretaryViewSet,CallViewSet,TechnicianViewSet,)

router = routers.DefaultRouter()

router.register(r"secretary", SecretaryViewSet, basename="secretary")

router.register(r"call", CallViewSet, basename="call")

router.register(r"technician", TechnicianViewSet, basename="technician")
