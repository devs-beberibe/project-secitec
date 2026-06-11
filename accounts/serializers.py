from .models import *
from rest_framework import serializers
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email")


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("email", "username", "password")

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    def validate(self, data):
        user = authenticate(username=data["email"], password=data["password"])

        if user and user.is_active:
            return user
        else:
            raise serializers.ValidationError("Email ou senha invalidos!")
