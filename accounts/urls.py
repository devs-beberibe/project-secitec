from django.urls import path
from .views import *

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegistrationView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("user-info/", UserInfoView.as_view(), name="user_info"),
]
