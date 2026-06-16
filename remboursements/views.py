from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Remboursement, RepaymentSchedule
from .serializers import (
    RemboursementSerializer,
    RemboursementListSerializer,
    RepaymentScheduleSerializer,
)


# ---- Remboursements ----


class RemboursementCreateView(generics.CreateAPIView):
    """
    Enregistrer un remboursement
    """

    serializer_class = RemboursementSerializer
    permission_classes = [permissions.IsAuthenticated]


class RemboursementListView(generics.ListAPIView):
    """
    Liste des remboursements
    """

    serializer_class = RemboursementListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "AGENT"]:
            return Remboursement.objects.all().order_by("-payment_date")
        return Remboursement.objects.filter(
            credit__client=user
        ).order_by("-payment_date")


class RemboursementDetailView(generics.RetrieveAPIView):
    """
    Détail d'un remboursement
    """

    serializer_class = RemboursementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "AGENT"]:
            return Remboursement.objects.all()
        return Remboursement.objects.filter(credit__client=user)


class RemboursementUpdateView(generics.UpdateAPIView):
    """
    Modifier un remboursement
    """

    serializer_class = RemboursementSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Remboursement.objects.all()


class RemboursementDeleteView(generics.DestroyAPIView):
    """
    Supprimer un remboursement
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = Remboursement.objects.all()


# ---- Échéancier ----


class RepaymentScheduleListView(generics.ListAPIView):
    """
    Liste des échéances
    """

    serializer_class = RepaymentScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        credit_pk = self.request.query_params.get("credit")

        if user.role in ["ADMIN", "AGENT"]:
            qs = RepaymentSchedule.objects.all()
        else:
            qs = RepaymentSchedule.objects.filter(credit__client=user)

        if credit_pk:
            qs = qs.filter(credit__pk=credit_pk)

        return qs.order_by("due_date")


class RepaymentScheduleDetailView(generics.RetrieveAPIView):
    """
    Détail d'une échéance
    """

    serializer_class = RepaymentScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "AGENT"]:
            return RepaymentSchedule.objects.all()
        return RepaymentSchedule.objects.filter(credit__client=user)
