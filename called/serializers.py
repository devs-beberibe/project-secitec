from rest_framework import serializers

from .models import *


class SecretarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Secretary
        fields = "__all__"


class CallSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = "__all__"


class TechnicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technician
        fields = "__all__"
