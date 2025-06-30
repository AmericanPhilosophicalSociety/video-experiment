from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("meetings/", views.meetings, name="meetings"),
    path("meetings/<int:meeting_id>/", views.meeting, name="meeting"),
    path("videos/<int:video_id>/", views.video, name="video"),
    path("headings", views.headings, name="headings"),
    path("headings/topics/", views.topics, name="topics"),
    path("headings/topics/<int:pk>/", views.topic_detail, name="topic_detail"),
    path("headings/names/", views.names, name="names"),
    path("headings/names/<int:pk>", views.name_detail, name="name_detail"),
    path("headings/corporate/", views.corporate, name="corporate"),
    path("headings/corporate/<int:pk>", views.corporate_detail, name="corporate_detail"),
    path("headings/geographic/", views.geographic, name="geographic"),
    path("headings/geographic/<int:pk>", views.geographic_detail, name="geographic_detail"),
    path("headings/temporal/", views.temporal, name="temporal"),
    path("headings/temporal/<int:pk>", views.temporal_detail, name="temporal_detail"),
    path("symposia/", views.symposia, name="symposia"),
    path("symposia/<int:symposium_id>/", views.symposium, name="symposium"),
    path("disciplines/", views.disciplines, name="disciplines"),
    path("disciplines/<int:discipline_id>/", views.discipline_detail, name="discipline_detail"),
    path("departments/", views.departments, name="departments"),
    path("departments/<int:department_id>/", views.department_detail, name="department_detail"),
]