from .models import *
from rest_framework import serializers
from accounts.models import CustomUser
from called.models import SecretarySector
from accounts.serializers import UserSerializer
from called.serializers import SecretarySerializer


class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Components
        fields = "__all__"


class ComponentStatusSerializer(serializers.ModelSerializer):
    component = ComponentSerializer(read_only=True)

    component_id = serializers.PrimaryKeyRelatedField(
        queryset=Components.objects.all(), source="component", write_only=True
    )

    class Meta:
        model = ComponentStatus
        fields = (
            "component",
            "component_id",
            "status",
            "description_report",
        )


class ReceiveFixSerializer(serializers.ModelSerializer):

    # Serializador para leitura usuario(GET)
    receipt = UserSerializer(read_only=True)

    # Serializador para escrita usuario(POST)
    receipt_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source="receipt", write_only=True
    )

    # Serializador para leitura secretaria(GET)
    secretary_sector = SecretarySerializer(read_only=True)

    # Serializador para escrita secretaria(POST)
    secretary_sector_id = serializers.PrimaryKeyRelatedField(
        queryset=SecretarySector.objects.all(),
        source="secretary_sector",
        write_only=True,
    )

    class Meta:
        model = MaintenanceSheet
        fields = (
            "id",
            "receipt_date",
            "serial_number",
            "left_by",
            "receipt",
            "receipt_id",
            "secretary_sector",
            "secretary_sector_id",
            "pc_responsible",
            "problem_description",
            "contact",
        )


class MaintenanceSerializer(serializers.ModelSerializer):

    # Serializador para leitura componentes da ficha de manutenção(GET)
    components_status = ComponentStatusSerializer(many=True)

    # Serializador para leitura secretaria(GET)
    secretary_sector = SecretarySerializer(read_only=True)

    class Meta:
        model = MaintenanceSheet
        fields = (
            "id",
            "receipt_date",
            "serial_number",
            "left_by",
            "receipt",
            "secretary_sector",
            "pc_responsible",
            "problem_description",
            "contact",
            "components_status",
        )

    def create(self, validated_data):
        components_status_data = validated_data.pop("components_status", [])

        maintenance_sheet = MaintenanceSheet.objects.create(**validated_data)

        for component_status_data in components_status_data:
            ComponentStatus.objects.create(
                sheet=maintenance_sheet, **component_status_data
            )

        return maintenance_sheet

    def update(self, instance, validated_data):
        components_status_data = validated_data.pop("components_status", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if components_status_data is not None:
            instance.components_status.all().delete()

            for component_status_data in components_status_data:
                ComponentStatus.objects.create(sheet=instance, **component_status_data)

        return instance


class CloseFixSerializer(serializers.ModelSerializer):

    # Serializador para leitura componentes da ficha de manutenção(GET)
    components_status = ComponentStatusSerializer(many=True, read_only=True)

    # Serializador para leitura secretaria(GET)
    secretary_sector = SecretarySerializer(read_only=True)

    # Serializador para leitura usuario(GET)
    delivered_by = UserSerializer(read_only=True)

    # Serializador para escrita usuario(POST)
    delivered_by_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source="delivered_by", write_only=True
    )

    # Serializador para leitura do tecnico(GET)
    technician = UserSerializer(read_only=True)

    # Serializador para escrita do tecnico(POST)
    technician_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source="technician", write_only=True
    )

    class Meta:
        model = MaintenanceSheet
        fields = (
            "id",
            "receipt_date",
            "serial_number",
            "left_by",
            "receipt",
            "receipt_id",
            "secretary_sector",
            "pc_responsible",
            "problem_description",
            "contact",
            "components_status",
            "delivered_by",
            "delivered_by_id",
            "technician",
            "technician_id",
            "observation",
            "realized_service",
            "search_by",
            "report",
            "delivery_date",
        )
