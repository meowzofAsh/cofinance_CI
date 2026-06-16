from datetime import date, timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from credits.models import Credit
from remboursements.models import Remboursement, RepaymentSchedule
from assurances.models import InsuranceSubscription
from support_chat.models import Conversation

from .serializers import DashboardSerializer

User = get_user_model()


class DashboardView(APIView):
    """
    Tableau de bord administrateur — enrichi
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role not in ["ADMIN", "AGENT"]:
            return self._client_data(user)

        # Filtres
        periode = request.query_params.get("periode", "")
        region = request.query_params.get("region", "")

        credit_qs = Credit.objects.all()
        remb_qs = Remboursement.objects.all()
        sub_qs = InsuranceSubscription.objects.all()

        if periode:
            try:
                jours = int(periode)
                debut = date.today() - timedelta(days=jours)
                credit_qs = credit_qs.filter(created_at__gte=debut)
                remb_qs = remb_qs.filter(created_at__gte=debut)
                sub_qs = sub_qs.filter(created_at__gte=debut)
            except ValueError:
                pass

        if region:
            clients_ids = User.objects.filter(
                role=User.CLIENT, region=region
            ).values_list("id", flat=True)
            credit_qs = credit_qs.filter(client_id__in=list(clients_ids))
            remb_qs = remb_qs.filter(credit__client_id__in=list(clients_ids))
            sub_qs = sub_qs.filter(client_id__in=list(clients_ids))

        soumis = credit_qs.filter(status=Credit.SOUMISE).count()
        en_analyse = credit_qs.filter(status=Credit.EN_ANALYSE).count()
        approuves = credit_qs.filter(status=Credit.APPROUVEE).count()
        rejetes = credit_qs.filter(status=Credit.REJETEE).count()
        decaisses = credit_qs.filter(status=Credit.DECAISSEE).count()

        montant_total_prete = sum(
            c.approved_amount
            for c in credit_qs.filter(status=Credit.DECAISSEE)
        )
        total_rembourse = sum(r.amount_paid for r in remb_qs)

        # Évolution mensuelle 6 mois
        today = date.today()
        evolution = []
        from datetime import datetime
        for i in range(5, -1, -1):
            m = today.month - i
            y = today.year
            if m < 1:
                m += 12
                y -= 1
            d1 = timezone.make_aware(datetime(y, m, 1))
            d2 = timezone.make_aware(datetime(y + 1, 1, 1)) if m == 12 else timezone.make_aware(datetime(y, m + 1, 1))
            evolution.append({
                "mois": f"{m:02d}/{y}",
                "credits": Credit.objects.filter(created_at__gte=d1, created_at__lt=d2).count(),
                "remboursements": Remboursement.objects.filter(created_at__gte=d1, created_at__lt=d2).count(),
                "souscriptions": InsuranceSubscription.objects.filter(created_at__gte=d1, created_at__lt=d2).count(),
            })

        regions_list = list(
            User.objects.filter(role=User.CLIENT)
            .values_list("region", flat=True)
            .distinct()
        )

        data = {
            "total_clients": User.objects.filter(role=User.CLIENT).count(),
            "total_agents": User.objects.filter(role=User.AGENT).count(),
            "total_credits": credit_qs.count(),
            "soumis": soumis,
            "en_analyse": en_analyse,
            "approuves": approuves,
            "rejetes": rejetes,
            "decaisses": decaisses,
            "montant_total_prete": f"{montant_total_prete:,.0f}",
            "total_rembourse": f"{total_rembourse:,.0f}",
            "taux_approbation": int((approuves / credit_qs.count() * 100)) if credit_qs.count() else 0,
            "taux_recouvrement": int((total_rembourse / montant_total_prete * 100)) if montant_total_prete else 0,
            "assurances_actives": sub_qs.filter(status="ACTIVE").count(),
            "conversations_ouvertes": Conversation.objects.filter(status=Conversation.OPEN).count(),
            "evolution": evolution,
            "regions": regions_list,
        }

        serializer = DashboardSerializer(data)
        return Response(serializer.data)

    def _client_data(self, user):
        credits_client = Credit.objects.filter(client=user)
        montant_total = sum(
            c.approved_amount
            for c in credits_client.filter(status=Credit.DECAISSEE)
        )
        total_paye = sum(
            r.amount_paid
            for r in Remboursement.objects.filter(credit__client=user)
        )
        prochaine_echeance = None
        echeances = RepaymentSchedule.objects.filter(
            credit__client=user, status=RepaymentSchedule.EN_ATTENTE
        ).order_by("due_date")
        if echeances.exists():
            s = echeances.first()
            prochaine_echeance = {
                "credit": s.credit.pk,
                "due_date": s.due_date,
                "amount_due": str(s.amount_due),
            }

        data = {
            "credits_actifs": credits_client.exclude(status=Credit.REJETEE).count(),
            "montant_total": f"{montant_total:,.0f}",
            "total_rembourse": f"{total_paye:,.0f}",
            "reste": f"{montant_total - total_paye:,.0f}",
            "assurances_actives": InsuranceSubscription.objects.filter(
                client=user, status="ACTIVE"
            ).count(),
            "prochaine_echeance": prochaine_echeance,
            "mes_credits": list(
                credits_client.values("id", "amount", "status", "purpose")
            ),
        }
        return Response(data)
