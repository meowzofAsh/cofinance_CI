# credits/views.py 

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Credit
from .serializers import (
    CreditSerializer,
    CreditStatusSerializer,
    CreditListSerializer,
)


class CreditCreateView(generics.CreateAPIView):
    """
    Création d'une demande de crédit
    """

    serializer_class = CreditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}


class CreditListView(generics.ListAPIView):
    """
    Liste des crédits
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreditListSerializer

    def get_queryset(self):

        user = self.request.user

        if user.role in ["ADMIN", "AGENT"]:
            return Credit.objects.all().order_by("-created_at")

        return Credit.objects.filter(
            client=user
        ).order_by("-created_at")


class CreditDetailView(generics.RetrieveAPIView):
    """
    Détail d'un crédit
    """

    serializer_class = CreditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role in ["ADMIN", "AGENT"]:
            return Credit.objects.all()

        return Credit.objects.filter(client=user)


class CreditUpdateView(generics.UpdateAPIView):
    """
    Modification d'une demande
    """

    serializer_class = CreditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role in ["ADMIN", "AGENT"]:
            return Credit.objects.all()

        return Credit.objects.filter(client=user)


class CreditDeleteView(generics.DestroyAPIView):
    """
    Suppression
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role == "ADMIN":
            return Credit.objects.all()

        return Credit.objects.filter(client=user)


class ChangeCreditStatusView(APIView):
    """
    Changement du statut
    """

    permission_classes = [permissions.IsAuthenticated]

    ALLOWED_STATUS = [
        "SOUMISE",
        "EN_ANALYSE",
        "APPROUVEE",
        "REJETEE",
        "DECAISSEE",
    ]

    def patch(self, request, pk):

        if request.user.role not in ["ADMIN", "AGENT"]:
            return Response(
                {
                    "detail": "Permission refusée."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            credit = Credit.objects.get(pk=pk)

        except Credit.DoesNotExist:

            return Response(
                {
                    "detail": "Crédit introuvable."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = request.data.get("status")

        if new_status not in self.ALLOWED_STATUS:

            return Response(
                {
                    "detail": "Statut invalide."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CreditStatusSerializer(
            credit,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )