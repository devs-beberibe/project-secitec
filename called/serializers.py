from rest_framework import serializers

from .models import *
from core.models import Tecs, User_sec



class SecretarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Secretary
        fields = "__all__"

class SectorSerializer(serializers.ModelSerializer):
    secretary = SecretarySerializer(
        read_only=True,
    )
    class Meta:
        model = Sector
        fields = "__all__"

class TechnicianSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Tecs
        fields = ["id", "user", "name"]

    def get_name(self, obj):
        return (
            obj.user.get_full_name().strip()
            or obj.user.get_username()
        )
    
class OpenCallSerializer(serializers.ModelSerializer):
    
    sector = SectorSerializer(
        read_only=True,
    )
    
    id_sector = serializers.PrimaryKeyRelatedField(
        source="sector",
        queryset=Sector.objects.all(),
        write_only=True,
    )
    
    date_start = models.DateField(
        default=timezone.localdate,
    )
    class Meta:
        model = Call
        fields = (
            "problem",
            "requester",
            "sector",
            "id_sector",
            "status",
            "priority",
            "date_start",
            "description",
        )
        
class FinishCallSerializer(serializers.ModelSerializer):
    
    tecs = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tecs.objects.all(),
    )
    
    class Meta:
        model = Call
        fields = (
            "status",
            "tecs",
            "date_end",
            "solution",
        )
        
class CallSerializer(serializers.ModelSerializer):
    
    sector_name = serializers.CharField(
        source="sector.sector_name",
        read_only=True,
    )
    
    tecs = TechnicianSerializer(
        many=True,
        read_only=True,
    )
    
    class Meta:
        model = Call
        fields = "__all__"
        
class UpdatePrioritySerializer(serializers.ModelSerializer):
    priority = serializers.ChoiceField(
        choices=Call.PRIORITY,
        required=True,
    )

    class Meta:
        model = Call
        fields = ("priority",)

    def validate(self, attrs):
        if "priority" not in attrs:
            raise serializers.ValidationError({
                "priority": "Informe a nova prioridade."
            })
        return attrs

    def update(self, instance, validated_data):
        instance.priority = validated_data["priority"]
        instance.save(update_fields=["priority"])
        return instance