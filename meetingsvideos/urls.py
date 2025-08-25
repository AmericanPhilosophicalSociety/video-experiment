from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.Landing.as_view(), name='landing_page'),
    path("index/", views.IndexView.as_view(), name="index"),
    path("meetings/", views.MeetingsList.as_view(), name="meetings"),
    path("meetings/<slug:slug>/", views.MeetingDetail.as_view(), name="meeting_detail"),
    path("videos/<slug:slug>/", views.VideoDetail.as_view(), name="video_detail"),
    path("headings", views.HeadingsView.as_view(), name="headings"),
    path("headings/<slug:slug>/", views.HeadingDetail.as_view(), name="heading_detail"),
    path("symposia/", views.SymposiumList.as_view(), name="symposia"),
    path(
        "symposia/<slug:slug>/", views.SymposiumDetail.as_view(), name="symposium_detail"
    ),
    path("disciplines/", views.DisciplineList.as_view(), name="disciplines"),
    path(
        "disciplines/<slug:slug>/",
        views.DisciplineDetail.as_view(),
        name="discipline_detail",
    ),
    path("departments/", views.DepartmentList.as_view(), name="departments"),
    path(
        "departments/<slug:slug>/",
        views.DepartmentDetail.as_view(),
        name="department_detail",
    ),
    path("speakers/", views.SpeakersView.as_view(), name="speakers"),
    path("speakers/<slug:slug>/", views.SpeakerDetail.as_view(), name="speaker_detail"),
    path("search/", views.search, name="search"),
    path("search_results/", views.search_results, name="search_results"),
    path(
        "search_results_advanced/",
        views.search_results_advanced,
        name="search_results_advanced",
    ),
    path('hello-webpack/', TemplateView.as_view(template_name='hello_webpack.html'))
]
