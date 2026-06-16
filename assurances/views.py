from rest_framework import generics, permissions

from .models import (
    InsuranceProduct,
    InsuranceSubscription,
)

from .serializers import (
    InsuranceProductSerializer,
    InsuranceSubscriptionSerializer,
    InsuranceSubscriptionListSerializer,
)


class InsuranceProductListView(generics.ListAPIView):
    """
    Catalogue des assurances
    """

    queryset = InsuranceProduct.objects.all()
    serializer_class = InsuranceProductSerializer
    permission_classes = [permissions.IsAuthenticated]


class InsuranceSubscriptionCreateView(generics.CreateAPIView):
    """
    Souscrire à une assurance
    """

    serializer_class = InsuranceSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {
            "request": self.request
        }


class InsuranceSubscriptionListView(generics.ListAPIView):
    """
    Liste des souscriptions
    """

    serializer_class = InsuranceSubscriptionListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role in ["ADMIN", "AGENT"]:
            return InsuranceSubscription.objects.all()

        return InsuranceSubscription.objects.filter(
            client=user
        )


class InsuranceSubscriptionDetailView(
    generics.RetrieveAPIView
):

    serializer_class = InsuranceSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role in ["ADMIN", "AGENT"]:
            return InsuranceSubscription.objects.all()

        return InsuranceSubscription.objects.filter(
            client=user
        )