from rest_framework import serializers

from .models import *


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = "__all__"


class MaintenanceSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceSheet
        fields = "__all__"


class ComponentSeriliazer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = "__all__"


class ComponentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentStatus
        fields = "__all__"
