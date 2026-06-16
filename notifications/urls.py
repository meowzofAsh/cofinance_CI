from django.urls import path

from .views import (
    NotificationListView,
    NotificationDetailView,
    NotificationReadView,
)

urlpatterns = [

    # Liste des notifications

    path(
        "",
        NotificationListView.as_view(),
        name="notification-list",
    ),

    # Détail

    path(
        "<int:pk>/",
        NotificationDetailView.as_view(),
        name="notification-detail",
    ),

    # Marquer comme lu

    path(
        "<int:pk>/read/",
        NotificationReadView.as_view(),
        name="notification-read",
    ),

]