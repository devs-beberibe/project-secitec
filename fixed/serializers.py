from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.reverse import reverse

from core.models import Tecs, User_sec

from .models import ComponentStatus, Components, MaintenanceSheet


class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Components
        fields = ("id", "name", "display_order")


class ComponentStatusReadSerializer(serializers.ModelSerializer):
    component = ComponentSerializer(read_only=True)
    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = ComponentStatus
        fields = (
            "id",
            "component",
            "status",
            "status_label",
            "description_report",
        )


class ComponentStatusWriteSerializer(serializers.Serializer):
    component = serializers.PrimaryKeyRelatedField(
        queryset=Components.objects.filter(active=True),
    )
    status = serializers.ChoiceField(choices=ComponentStatus.CASE)
    description_report = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        default="",
    )


class UserSecLabelField(serializers.RelatedField):
    def to_representation(self, value):
        user = getattr(value, "user", None)
        if user:
            return user.get_full_name().strip() or user.get_username()
        return str(value)


class TechnicianLabelField(serializers.RelatedField):
    def to_representation(self, value):
        user = getattr(value, "user", None)
        if user:
            return user.get_full_name().strip() or user.get_username()
        return str(value)


class MaintenanceSheetSerializer(serializers.ModelSerializer):
    components_status = ComponentStatusReadSerializer(many=True, read_only=True)
    receipt_name = UserSecLabelField(source="receipt", read_only=True)
    technician_name = TechnicianLabelField(source="technician", read_only=True)
    delivered_by_name = UserSecLabelField(source="delivered_by", read_only=True)
    sector_name = serializers.CharField(
        source="secretary_sector.sector_name",
        read_only=True,
    )
    secretary_name = serializers.CharField(
        source="secretary_sector.secretary.secretary_name",
        read_only=True,
    )
    situation = serializers.CharField(read_only=True)
    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    report_available = serializers.SerializerMethodField()
    report_url = serializers.SerializerMethodField()

    def get_report_available(self, obj):
        return bool(obj.technical_report)

    def get_report_url(self, obj):
        if not obj.technical_report:
            return None
        return reverse("ficha-manutencao-laudo", kwargs={"pk": obj.pk})

    class Meta:
        model = MaintenanceSheet
        fields = (
            "id",
            "situation",
            "status",
            "status_label",
            "receipt_date",
            "serial_number",
            "receipt",
            "receipt_name",
            "technician",
            "technician_name",
            "secretary_sector",
            "sector_name",
            "secretary_name",
            "pc_responsible",
            "problem_description",
            "contact",
            "observation",
            "realized_service",
            "components_status",
            "search_by",
            "delivered_by",
            "delivered_by_name",
            "delivery_date",
            "report_available",
            "report_url",
            "report_generated_at",
        )


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceSheet
        fields = (
            "receipt_date",
            "serial_number",
            "receipt",
            "secretary_sector",
            "pc_responsible",
            "problem_description",
            "contact",
        )

    def create(self, validated_data):
        return MaintenanceSheet.objects.create(
            status=MaintenanceSheet.RECEIVED,
            **validated_data,
        )


class MaintenanceSerializer(serializers.ModelSerializer):
    components_status = ComponentStatusWriteSerializer(many=True)

    class Meta:
        model = MaintenanceSheet
        fields = (
            "technician",
            "observation",
            "realized_service",
            "components_status",
        )
        extra_kwargs = {
            "technician": {"required": True, "allow_null": False},
            "realized_service": {"required": True, "allow_blank": False},
        }

    def validate_components_status(self, value):
        active_ids = set(
            Components.objects.filter(active=True).values_list("id", flat=True)
        )
        submitted_ids = [item["component"].id for item in value]
        submitted_set = set(submitted_ids)

        if len(submitted_ids) != len(submitted_set):
            raise serializers.ValidationError(
                "Cada componente deve aparecer apenas uma vez."
            )
        missing = active_ids - submitted_set
        extra = submitted_set - active_ids
        if missing or extra:
            raise serializers.ValidationError(
                "Informe o estado de todos os componentes ativos."
            )
        return value

    @transaction.atomic
    def validate(self, attrs):
        if self.instance.status != MaintenanceSheet.RECEIVED:
            raise serializers.ValidationError(
                "Somente fichas recebidas podem iniciar a manutenção."
            )
        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        statuses = validated_data.pop("components_status")
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.status = MaintenanceSheet.IN_MAINTENANCE
        instance.save(update_fields=(
            "technician",
            "observation",
            "realized_service",
            "status",
        ))
        # Fichas criadas pelo fluxo antigo podem já possuir a conferência.
        # Nesse caso atualizamos os registros, evitando violar a constraint
        # de um único status por ficha/componente.
        for item in statuses:
            component = item.pop("component")
            ComponentStatus.objects.update_or_create(
                sheet=instance,
                component=component,
                defaults=item,
            )
        return instance


class DeliverySerializer(serializers.ModelSerializer):
    delivered_by = serializers.PrimaryKeyRelatedField(
        queryset=User_sec.objects.all(),
    )

    class Meta:
        model = MaintenanceSheet
        fields = (
            "search_by",
            "delivered_by",
            "delivery_date",
        )
        extra_kwargs = {
            "search_by": {"required": True, "allow_blank": False},
            "delivery_date": {"required": True, "allow_null": False},
        }

    def validate_delivery_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError(
                "A data de entrega não pode estar no futuro."
            )
        return value

    def validate(self, attrs):
        if self.instance.status == MaintenanceSheet.DELIVERED:
            raise serializers.ValidationError(
                "Esta ficha já possui uma entrega registrada."
            )
        if self.instance.status != MaintenanceSheet.IN_MAINTENANCE:
            raise serializers.ValidationError(
                "A manutenção precisa ser realizada antes da entrega."
            )
        if (
            self.instance
            and attrs.get("delivery_date")
            and attrs["delivery_date"] < self.instance.receipt_date
        ):
            raise serializers.ValidationError(
                "A entrega não pode ocorrer antes do recebimento."
            )
        return attrs

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.status = MaintenanceSheet.DELIVERED
        instance.save(update_fields=(
            "search_by",
            "delivered_by",
            "delivery_date",
            "status",
        ))
        return instance


class PublicTrackingSerializer(serializers.ModelSerializer):
    components_status = ComponentStatusReadSerializer(many=True, read_only=True)
    sector_name = serializers.CharField(
        source="secretary_sector.sector_name",
        read_only=True,
    )
    situation = serializers.CharField(read_only=True)
    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    technician_name = TechnicianLabelField(
        source="technician",
        read_only=True,
    )
    report_available = serializers.SerializerMethodField()
    report_url = serializers.SerializerMethodField()

    def get_report_available(self, obj):
        return bool(obj.technical_report)

    def get_report_url(self, obj):
        if not obj.technical_report:
            return None
        return reverse("ficha-manutencao-laudo-publico", kwargs={"pk": obj.pk})

    class Meta:
        model = MaintenanceSheet
        fields = (
            "id",
            "situation",
            "status",
            "status_label",
            "receipt_date",
            "serial_number",
            "sector_name",
            "technician_name",
            "problem_description",
            "realized_service",
            "observation",
            "components_status",
            "delivery_date",
            "report_available",
            "report_url",
        )
