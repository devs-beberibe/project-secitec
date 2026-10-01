from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import *

def set_access_cookie(response, access_token):
    response.set_cookie(
        key=settings.JWT_ACCESS_COOKIE,
        value=access_token,
        max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/",
    )


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key=settings.JWT_REFRESH_COOKIE,
        value=refresh_token,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/",
    )

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "detail": "Login realizado com sucesso.",
                "usuario": UsuarioSerializer(
                    user,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_200_OK,
        )

        set_access_cookie(
            response,
            str(refresh.access_token),
        )

        set_refresh_cookie(
            response,
            str(refresh),
        )

        response["Cache-Control"] = "no-store"

        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)

        if not refresh_token:
            raise AuthenticationFailed("Refresh token não encontrado.")

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)

        tokens = serializer.validated_data

        response = Response(
            {"detail": "Token renovado com sucesso."},
            status=status.HTTP_200_OK,
        )

        set_access_cookie(
            response,
            tokens["access"],
        )

        # Quando ROTATE_REFRESH_TOKENS=True,
        # um novo refresh token também será retornado.
        if "refresh" in tokens:
            set_refresh_cookie(
                response,
                tokens["refresh"],
            )

        response["Cache-Control"] = "no-store"

        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)

        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass

        response = Response(
            {"detail": "Logout realizado com sucesso."},
            status=status.HTTP_200_OK,
        )

        response.delete_cookie(
            key=settings.JWT_ACCESS_COOKIE,
            path="/",
            samesite=settings.JWT_COOKIE_SAMESITE,
        )

        response.delete_cookie(
            key=settings.JWT_REFRESH_COOKIE,
            path="/",
            samesite=settings.JWT_COOKIE_SAMESITE,
        )

        response["Cache-Control"] = "no-store"

        return response


class AlterarSenhaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AlterarSenhaSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)

        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass

        response = Response(
            {"detail": ("Senha alterada com sucesso. " "Faça login novamente.")},
            status=status.HTTP_200_OK,
        )

        response.delete_cookie(
            key=settings.JWT_ACCESS_COOKIE,
            path="/",
            samesite=settings.JWT_COOKIE_SAMESITE,
        )

        response.delete_cookie(
            key=settings.JWT_REFRESH_COOKIE,
            path="/",
            samesite=settings.JWT_COOKIE_SAMESITE,
        )

        response["Cache-Control"] = "no-store"

        return response
    

class UsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)