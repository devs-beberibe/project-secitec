from rest_framework import serializers

from .models import *


class SecretarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SecretarySector
        fields = "__all__"


class PublicCallSerialzier(serializers.ModelSerializer):
    problem = serializers.CharField(max_length=255, write_only=True)
    requester = serializers.CharField(max_length=125, write_only=True)
    class Meta:
        model = Call
        fields = ("secretary_sector","problem","requester")


class AdminCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = "__all__"

class AdministracaoCallSerializer(serializers.ModelSerializer):
    problem = serializers.CharField(max_length=255, write_only=True)
    requester = serializers.CharField(max_length=125, write_only=True)
    solution = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = Call
        fields = ("secretary_sector","problem","requester","solution")

class TecnicoCallSerializer(serializers.ModelSerializer):
    problem = serializers.CharField(max_length=255, read_only=True)
    requester = serializers.CharField(max_length=125, read_only=True)
    solution = serializers.CharField(max_length=255, write_only=True)
    status = serializers.ChoiceField(choices=Call.STATUS_CALLED)
    class Meta:
        model = Call
        fields = ("secretary_sector","problem","requester","solution","status","date_end")

class TecnicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technician
        fields = "__all__"
