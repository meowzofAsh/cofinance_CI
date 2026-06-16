from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NPSSurvey
from .serializers import NPSSurveySerializer


class NPSSurveyCreateView(generics.CreateAPIView):
    serializer_class = NPSSurveySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NPSSurveyListView(generics.ListAPIView):
    serializer_class = NPSSurveySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "AGENT"]:
            return NPSSurvey.objects.all().order_by("-created_at")
        return NPSSurvey.objects.filter(user=user).order_by("-created_at")


class NPSDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role not in ["ADMIN", "AGENT"]:
            return Response({"detail": "Accès réservé."}, status=status.HTTP_403_FORBIDDEN)

        all_surveys = NPSSurvey.objects.all()
        total = all_surveys.count()

        if total == 0:
            return Response({
                "total_responses": 0,
                "nps_score": None,
                "promoters": 0,
                "passives": 0,
                "detractors": 0,
                "promoters_pct": 0,
                "detractors_pct": 0,
                "recent": [],
            })

        promoters = all_surveys.filter(score__gte=9).count()
        passives = all_surveys.filter(score__gte=7, score__lte=8).count()
        detractors = all_surveys.filter(score__lte=6).count()

        promoters_pct = (promoters / total) * 100
        detractors_pct = (detractors / total) * 100
        nps_score = round(promoters_pct - detractors_pct, 1)

        recent = list(
            all_surveys.select_related("user").order_by("-created_at")[:10].values(
                "user__username", "score", "comment", "context_type", "created_at"
            )
        )

        return Response({
            "total_responses": total,
            "nps_score": nps_score,
            "promoters": promoters,
            "passives": passives,
            "detractors": detractors,
            "promoters_pct": round(promoters_pct, 1),
            "detractors_pct": round(detractors_pct, 1),
            "recent": recent,
        })
