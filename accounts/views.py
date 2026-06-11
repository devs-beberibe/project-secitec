from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *


class UserInfoView(RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class LoginView(APIView):

    parser_classes = [
        JSONParser,
        FormParser,
        MultiPartParser,
    ]
    renderer_classes = [
        JSONRenderer,
        BrowsableAPIRenderer,
    ]

    def post(self, request):

        serializer = UserLoginSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():

            validated_data = serializer.validated_data
            if isinstance(validated_data, dict):
                user = validated_data.get("user")
            else:
                user = validated_data

            if user is None:
                return Response(
                    {"erro": "Usuário inválido"}, status=status.HTTP_400_BAD_REQUEST
                )

            refresh = RefreshToken.for_user(user)  # type: ignore[arg-type]

            access_token = str(refresh.access_token)

            response = Response(
                {
                    "mensagem": "Login realizado com sucesso!",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,
                samesite="Lax",
            )

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=False,
                samesite="Lax",
            )

            print("COOKIE ACCESS:", access_token)
            print("COOKIES SETADOS:", response.cookies)

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenRefreshView(TokenRefreshView):

    def post(self, request):

        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:

            return Response(
                {"erro": "Refresh token não encontrado"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:

            refresh = RefreshToken(refresh_token)

            access_token = str(refresh.access_token)

            response = Response(
                {"mensagem": "Token atualizado"}, status=status.HTTP_200_OK
            )

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,
                samesite="Lax",
            )

            return response

        except (InvalidToken, TokenError):

            return Response(
                {"erro": "Token inválido ou expirado"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:

            try:

                refresh = RefreshToken(refresh_token)

                refresh.blacklist()

            except TokenError:

                return Response(
                    {"erro": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST
                )

        response = Response(
            {"mensagem": "Logout realizado com sucesso!"}, status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class RegistrationView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]
