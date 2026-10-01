from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

router.register("chamados", CallViewSet, basename="chamados")

urlpatterns = router.urls