from rest_framework import serializers

from .models import *
from core.models import Tecs

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
    class Meta:
        model = Tecs
        fields = "__all__"
    
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
    class Meta:
        model = Call
        fields = "__all__"