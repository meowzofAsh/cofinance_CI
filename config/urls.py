from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from core import views

urlpatterns = [

    # -------------------
    # SITE WEB
    # -------------------

    path("", views.login_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("credits/", views.credits, name="credit_list"),
    path("credits/create/", views.credit_create, name="credit_create"),
    path("credits/<int:pk>/", views.credit_detail, name="credit_detail"),
    path("credits/<int:pk>/edit/", views.credit_update, name="credit_update"),
    path("remboursements/", views.remboursements, name="remboursement_list"),
    path("assurances/", views.assurances, name="assurance_list"),
    path("assurances/<int:pk>/subscribe/", views.assurance_subscribe, name="assurance_subscribe"),
    path("notifications/", views.notifications, name="notification_list"),
    path("notifications/mark-all/", views.notification_mark_all, name="notification_mark_all"),
    path("chat/", views.chat_conversations, name="chat_conversations"),
    path("chat/<int:pk>/", views.support_chat, name="chat_room"),
    path("nps/submit/", views.nps_submit, name="nps_submit"),

    # -------------------
    # ADMIN
    # -------------------

    path("admin/", admin.site.urls),

    # -------------------
    # API
    # -------------------

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/accounts/", include("accounts.urls")),
    path("api/credits/", include("credits.urls")),
    path("api/remboursements/", include("remboursements.urls")),
    path("api/assurances/", include("assurances.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/chat/", include("support_chat.urls")),
    path("api/surveys/", include("surveys.urls")),
    
    # -------------------
    # ADMIN PANEL ROUTES
    # -------------------
    path("admin-panel/users/", views.admin_users, name="admin_users"),
    path("admin-panel/credits/", views.admin_credits, name="admin_credits"),
    path("credits/<int:pk>/status/", views.credit_change_status, name="credit_change_status"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)