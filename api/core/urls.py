from django.http import JsonResponse
from django.urls import include, path


def health_check(_request):
    return JsonResponse({"status": "ok", "service": "think-ps-api"})


urlpatterns = [
    path("", health_check, name="health_check"),
    path("api/auth/", include("accounts.urls")),
    path("api/compras/", include("compras.api_urls")),
]
