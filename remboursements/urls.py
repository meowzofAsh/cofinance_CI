from django.urls import path

from .views import (
    RemboursementCreateView,
    RemboursementListView,
    RemboursementDetailView,
    RemboursementUpdateView,
    RemboursementDeleteView,
    RepaymentScheduleListView,
    RepaymentScheduleDetailView,
)

urlpatterns = [
    # Remboursements
    path("", RemboursementCreateView.as_view(), name="remboursement-create"),
    path("list/", RemboursementListView.as_view(), name="remboursement-list"),
    path("<int:pk>/", RemboursementDetailView.as_view(), name="remboursement-detail"),
    path("<int:pk>/update/", RemboursementUpdateView.as_view(), name="remboursement-update"),
    path("<int:pk>/delete/", RemboursementDeleteView.as_view(), name="remboursement-delete"),
    # Échéancier
    path("schedules/", RepaymentScheduleListView.as_view(), name="schedule-list"),
    path("schedules/<int:pk>/", RepaymentScheduleDetailView.as_view(), name="schedule-detail"),
]
