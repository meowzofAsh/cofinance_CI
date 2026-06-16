# accounts/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, ChangePasswordView, UserListView, UserDetailView

urlpatterns = [

    path("register/", RegisterView.as_view(), name="api_register"),
    path("login/", TokenObtainPairView.as_view(), name="api_login"),
    path("refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),
    path("profile/", ProfileView.as_view(), name="api_profile"),
    path("change-password/", ChangePasswordView.as_view(), name="api_change_password"),
    path("users/", UserListView.as_view(), name="api_users"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="api_user_detail"),
]