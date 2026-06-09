from rest_framework import serializers

from .models import *



class AdministracaoFichaSerializer(serializers.ModelSerializer):
    receipt_date = serializers.DateField(read_only=True)
    serial_number = serializers.CharField(read_only=True)
    left_by = serializers.CharField
    receipt = serializers.CharField(source="receipt.username", read_only=True)
    secretary_sector = serializers.CharField(source="secretary_sector.name", read_only=True)
    pc_responsible = serializers.CharField(read_only=True)
    problem_description = serializers.CharField(read_only=True)
    contact = serializers.CharField(read_only=True)
    observation = serializers.CharField(read_only=True)
    realized_service = serializers.CharField(read_only=True)
    search_by = serializers.CharField
    delivered_by = serializers.CharField(source="delivered_by.username")
    report = serializers.CharField(read_only=True)
    delivery_date = serializers.DateField
    technician = serializers.CharField(source="technician.name", read_only=True)
    class Meta:
        model = MaintenanceSheet
        fields = "__all__"

class FichaEntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceSheet
        fields = ("receipt_date","serial_number","left_by","receipt","secretary_sector","pc_responsible","problem_description","contact")

class FichaSaidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceSheet
        fields = ("observation","realized_service","search_by","delivered_by","report","delivery_date","technician")



class ComponentSeriliazer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = "__all__"


class StatusComponentesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentStatus
        fields = "__all__"
