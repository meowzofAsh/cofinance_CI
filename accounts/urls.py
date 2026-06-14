# accounts/urls.py

from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    RegisterView,
    ProfileView,
    ChangePasswordView,
    UserListView,
    UserDetailView,
)

urlpatterns = [

    # ==================================
    # AUTHENTIFICATION
    # ==================================

    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="login",
    ),

    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    # ==================================
    # PROFIL
    # ==================================

    path(
        "profile/",
        ProfileView.as_view(),
        name="profile",
    ),

    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change_password",
    ),

    # ==================================
    # UTILISATEURS
    # ==================================

    path(
        "users/",
        UserListView.as_view(),
        name="users",
    ),

    path(
        "users/<int:pk>/",
        UserDetailView.as_view(),
        name="user_detail",
    ),
]