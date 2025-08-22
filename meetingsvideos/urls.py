from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.Landing.as_view(), name='landing_page'),
    path("index/", views.IndexView.as_view(), name="index"),
    path("meetings/", views.MeetingsList.as_view(), name="meetings"),
    path("meetings/<int:pk>/", views.MeetingDetail.as_view(), name="meeting_detail"),
    path("videos/<int:pk>/", views.VideoDetail.as_view(), name="video_detail"),
    path("headings", views.HeadingsView.as_view(), name="headings"),
    path("headings/<int:pk>/", views.heading_detail, name="heading_detail"),
    path("symposia/", views.SymposiumList.as_view(), name="symposia"),
    path(
        "symposia/<int:symposium_id>/", views.symposium_detail, name="symposium_detail"
    ),
    path("disciplines/", views.DisciplineList.as_view(), name="disciplines"),
    path(
        "disciplines/<int:discipline_id>/",
        views.discipline_detail,
        name="discipline_detail",
    ),
    path("departments/", views.DepartmentList.as_view(), name="departments"),
    path(
        "departments/<int:department_id>/",
        views.department_detail,
        name="department_detail",
    ),
    path("speakers/", views.SpeakersView.as_view(), name="speakers"),
    path("speakers/<int:speaker_id>/", views.speaker_detail, name="speaker_detail"),
    path("search/", views.search, name="search"),
    path("search_results/", views.search_results, name="search_results"),
    path(
        "search_results_advanced/",
        views.search_results_advanced,
        name="search_results_advanced",
    ),
    path('hello-webpack/', TemplateView.as_view(template_name='hello_webpack.html'))
]
