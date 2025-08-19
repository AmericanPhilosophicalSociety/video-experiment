from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path("index/", views.IndexView.as_view(), name="index"),
    path("meetings/", views.meetings, name="meetings"),
    path("meetings/<int:meeting_id>/", views.meeting_detail, name="meeting_detail"),
    path("videos/<int:video_id>/", views.video_detail, name="video_detail"),
    path("headings", views.headings, name="headings"),
    path("headings/<int:pk>/", views.heading_detail, name="heading_detail"),
    path("headings/topics/", views.topics, name="topics"),
    path("headings/names/", views.names, name="names"),
    path("headings/corporate/", views.corporate, name="corporate"),
    path("headings/geographic/", views.geographic, name="geographic"),
    path("symposia/", views.symposia, name="symposia"),
    path(
        "symposia/<int:symposium_id>/", views.symposium_detail, name="symposium_detail"
    ),
    path("disciplines/", views.disciplines, name="disciplines"),
    path(
        "disciplines/<int:discipline_id>/",
        views.discipline_detail,
        name="discipline_detail",
    ),
    path("departments/", views.departments, name="departments"),
    path(
        "departments/<int:department_id>/",
        views.department_detail,
        name="department_detail",
    ),
    path("speakers/", views.speakers, name="speakers"),
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
