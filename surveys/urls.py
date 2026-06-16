from django.urls import path

from . import views

urlpatterns = [
    path("", views.NPSSurveyCreateView.as_view(), name="api_nps_create"),
    path("list/", views.NPSSurveyListView.as_view(), name="api_nps_list"),
    path("dashboard/", views.NPSDashboardView.as_view(), name="api_nps_dashboard"),
]
