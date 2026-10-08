from .models import *
from rest_framework import serializers
from core.models import *
from called.models import Sector
from called.serializers import TechnicianSerializer, SectorSerializer

class UserSecretariaSerializer(serializers.ModelSerialzier):
    class Meta:
        model = User_sec
        fields = "__all__"

class MaintenanceSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceSheet
        fields = "__all__"
    
class InitialMaintenanceSheetSerializer(serializers.ModelSerializer):
    
    receipt = UserSecretariaSerializer(
        read_only=True,
    )
    
    id_receipt = serializers.PrimaryKeyRelatedField(
        source="receipt",
        queryset=User_sec.objects.all(),
        write_only=True,
    )
    
    technician = TechnicianSerializer(
        read_only=True,
    )
    
    id_technician = serializers.PrimaryKeyRelatedField(
        source="technician",
        queryset=Tecs.objects.all(),
        write_only=True,
    )
    
    secretary_sector = SectorSerializer(
            read_only=True,
        )
        
    id_secretary_sector = serializers.PrimaryKeyRelatedField(
        source="secretary_sector",
        queryset=Sector.objects.all(),
        write_only=True,
    )
    
    class Meta:
        model = MaintenanceSheet
        fields = [
            "receipt_date",
            "serial_number",
            "receipt",
            "id_receipt",
            "technician",
            "id_technician",
            "secretary_sector",
            "id_secretary_sector",
            "pc_responsible",
            "problem_description",
            "contact",
        ]
        
class FinalMaintenanceSheetSerializer(serializers.ModelSerializer):

    delivered_by = UserSecretariaSerializer(
        read_only=True,
    )
    
    id_delivered_by = serializers.PrimaryKeyRelatedField(
        source="receipt",
        queryset=User_sec.objects.all(),
        write_only=True,
    )


    class Meta:
        model = MaintenanceSheet
        fields = [
            "observation",
            "realizerd_service",
            "search_by",
            "delivered_by",
            "id_delivered_by",
            "report",
            "delivery_date",
        ]
        

class ComponentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Components
        fields = "__all__"

class ComponentsStatusSerializer(serializers.ModelSerializer):
    
    sheet = MaintenanceSheetSerializer(
        read_only=True,
    )
    
    id_component = serializers.PrimaryKeyRelatedField(
        source="component",
        queryset=Components.objects.all(),
        write_only=True,
    )
    
    component = ComponentsSerializer(
        read_only=True,
    )
    
    id_delivered_by = serializers.PrimaryKeyRelatedField(
        source="receipt",
        queryset=User_sec.objects.all(),
        write_only=True,
    )

    
    
    class Meta:
        model = ComponentStatus
        fields = [
            "sheet",
            "id_sheet",
            "status",
            "description_report",
        ]
