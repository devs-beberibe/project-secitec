from django.shortcuts import render
from rest_framework.exceptions import AuthenticationFailed

from called.models import Secretary, Sector
from core.models import Tecs
from accounts.authentication import CookieJWTAuthentication
def home(request, dashboard_page=False):
    try:
        authentication = CookieJWTAuthentication().authenticate(
            request
        )
    except AuthenticationFailed:
        authentication = None

    return render(
        request,
        "core/home.html",
        
        {
            "secretarias": (
                Secretary.objects.order_by("secretary_name")
            ),
            "setores": (
                Sector.objects
                .select_related("secretary")
                .order_by("sector_name")
            ),
            "tecnicos": (
                Tecs.objects.all()
                if authentication
                else []
            ),
            "dashboard_page": dashboard_page,
        },
    )


def login_page(request):
    return render(request, "accounts/login.html")