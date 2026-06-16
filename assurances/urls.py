from django.urls import path

from .views import (
    InsuranceProductListView,
    InsuranceSubscriptionCreateView,
    InsuranceSubscriptionListView,
    InsuranceSubscriptionDetailView,
)

urlpatterns = [

    # Catalogue

    path(
        "products/",
        InsuranceProductListView.as_view(),
        name="insurance-products",
    ),

    # Souscription

    path(
        "subscribe/",
        InsuranceSubscriptionCreateView.as_view(),
        name="insurance-subscribe",
    ),

    # Liste

    path(
        "",
        InsuranceSubscriptionListView.as_view(),
        name="insurance-list",
    ),

    # Détail

    path(
        "<int:pk>/",
        InsuranceSubscriptionDetailView.as_view(),
        name="insurance-detail",
    ),

]