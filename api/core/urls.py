from django.http import JsonResponse
from django.urls import include, path

from .openapi import openapi_schema, swagger_ui


def health_check(_request):
    return JsonResponse({"status": "ok", "service": "think-ps-api"})


urlpatterns = [
    path("", health_check, name="health_check"),
    path("api/schema/", openapi_schema, name="openapi_schema"),
    path("api/docs/", swagger_ui, name="swagger_ui"),
    path("api/auth/", include("accounts.urls")),
    path("api/compras/", include("compras.api_urls")),
]
