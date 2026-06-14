# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [

    # ==========================
    # ADMIN
    # ==========================

    path("admin/", admin.site.urls),

    # ==========================
    # API SCHEMA
    # ==========================

    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    # ==========================
    # SWAGGER
    # ==========================

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui",
    ),

    # ==========================
    # REDOC
    # ==========================

    path(
        "api/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema"
        ),
        name="redoc",
    ),

    # ==========================
    # APPLICATIONS
    # ==========================

    path(
        "api/accounts/",
        include("accounts.urls"),
    ),

    path(
        "api/credits/",
        include("credits.urls"),
    ),

    path(
        "api/remboursements/",
        include("remboursements.urls"),
    ),

    path(
        "api/assurances/",
        include("assurances.urls"),
    ),

    path(
        "api/notifications/",
        include("notifications.urls"),
    ),

    path(
        "api/dashboard/",
        include("dashboard.urls"),
    ),

    path(
        "api/chat/",
        include("support_chat.urls"),
    ),
]

# ==========================
# MEDIA FILES
# ==========================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
