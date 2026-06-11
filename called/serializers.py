from rest_framework import serializers

from .models import *


class SecretarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SecretarySector
        fields = "__all__"


class CreateCallSerializer(serializers.ModelSerializer):
    # Serializador para leitura (GET)
    secretary_sector = SecretarySerializer(read_only=True)

    # Serializador para escrita (POST)
    secretary_sector_id = serializers.PrimaryKeyRelatedField(
        queryset=SecretarySector.objects.all(),
        source="secretary_sector",
        write_only=True,
    )

    problem = serializers.CharField
    requester = serializers.CharField

    class Meta:
        model = Call
        fields = (
            "id",
            "secretary_sector_id",
            "secretary_sector",
            "problem",
            "requester",
        )


class UpdateCallSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Call.STATUS_CALLED)
    solution = serializers.CharField()
    date_end = serializers.DateField()
    technician = serializers.PrimaryKeyRelatedField(
        queryset=Technician.objects.all(), many=True
    )

    class Meta:
        model = Call
        fields = ("status", "solution", "date_end", "technician")


class TecnicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technician
        fields = "__all__"
