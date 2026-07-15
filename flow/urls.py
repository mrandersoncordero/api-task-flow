"""URL configuration for flow project."""

# Django
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from account.views import DashBoardView

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # API v1
    path("api/v1/", include("api.urls", namespace="api")),
    # Web App
    path("account/", include("apps.account.urls", namespace="account")),
    # Dashboard
    path("", DashBoardView.as_view(), name="dashboard"),
    # Petitions
    path("", include("petitions.urls", namespace="petitions")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns