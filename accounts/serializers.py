from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


User = get_user_model()

class GrupoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ["id", "name"]

class UsuarioSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(
        source="first_name",
        read_only=True,
    )
    sobrenome = serializers.CharField(
        source="last_name",
        read_only=True,
    )
    grupos = GrupoSerializer(
        source="groups",
        many=True,
        read_only=True,
    )
    
    class Meta:
        model = User
        fields = [
            "id",
            "nome",
            "sobrenome",
            "grupos",
            "username",
        ]
        read_only_fields = [
            "id",
            "nome",
            "sobrenome",
            "grupos",
            "username",
        ]

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
    )

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    def validate(self, attributes):
        request = self.context.get("request")

        user = authenticate(
            request=request,
            username=attributes["username"],
            password=attributes["password"],
        )

        if user is None:
            raise serializers.ValidationError({"detail": "Usuário ou senha inválidos."})

        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "Este usuário está desativado."}
            )

        attributes["user"] = user
        return attributes
    

class AlterarSenhaSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    nova_senha = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    confirmar_nova_senha = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    def validate_senha_atual(self, senha_atual):
        user = self.context["request"].user

        if not user.check_password(senha_atual):
            raise serializers.ValidationError("A senha atual está incorreta.")

        return senha_atual

    def validate(self, attributes):
        senha_atual = attributes["senha_atual"]
        nova_senha = attributes["nova_senha"]
        confirmacao = attributes["confirmar_nova_senha"]

        if nova_senha != confirmacao:
            raise serializers.ValidationError(
                {
                    "confirmar_nova_senha": (
                        "A confirmação não corresponde à nova senha."
                    )
                }
            )

        if senha_atual == nova_senha:
            raise serializers.ValidationError(
                {"nova_senha": ("A nova senha deve ser diferente da senha atual.")}
            )

        user = self.context["request"].user

        try:
            validate_password(nova_senha, user=user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"nova_senha": list(error.messages)})

        return attributes

    def save(self):
        user = self.context["request"].user

        user.set_password(self.validated_data["nova_senha"])
        user.save(update_fields=["password"])

        return user