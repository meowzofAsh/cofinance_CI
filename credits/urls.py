# credits/urls.py


from django.urls import path

from .views import (
    CreditCreateView,
    CreditListView,
    CreditDetailView,
    CreditUpdateView,
    CreditDeleteView,
    ChangeCreditStatusView,
)

urlpatterns = [

    # ==========================
    # CREATION D'UNE DEMANDE
    # ==========================

    path(
        "",
        CreditCreateView.as_view(),
        name="credit-create",
    ),

    # ==========================
    # LISTE DES CREDITS
    # ==========================

    path(
        "list/",
        CreditListView.as_view(),
        name="credit-list",
    ),

    # ==========================
    # DETAIL
    # ==========================

    path(
        "<int:pk>/",
        CreditDetailView.as_view(),
        name="credit-detail",
    ),

    # ==========================
    # MODIFICATION
    # ==========================

    path(
        "<int:pk>/update/",
        CreditUpdateView.as_view(),
        name="credit-update",
    ),

    # ==========================
    # SUPPRESSION
    # ==========================

    path(
        "<int:pk>/delete/",
        CreditDeleteView.as_view(),
        name="credit-delete",
    ),

    # ==========================
    # CHANGEMENT DE STATUT
    # ==========================

    path(
        "<int:pk>/status/",
        ChangeCreditStatusView.as_view(),
        name="credit-status",
    ),

]

