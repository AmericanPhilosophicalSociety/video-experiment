from django.shortcuts import render, get_object_or_404

from .models import (
    Video,
    Meeting,
    LCSHTopic,
    Symposium,
    LCSHGeographic,
    LCSHTemporal,
    LCSHNamePersonal,
    LCSHNameCorporate,
)


# Create your views here.
def index(request):
    videos = Video.objects.all()
    return render(request, "meetingsvideos/index.html", {"videos": videos})


def meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    return render(request, "meetingsvideos/meeting.html", {"meeting": meeting})


def meetings(request):
    meetings = Meeting.objects.all()
    return render(request, "meetingsvideos/meetings.html", {"meetings": meetings})


def video(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    return render(request, "meetingsvideos/video.html", {"video": video})


def headings(request):
    return render(request, "meetingsvideos/headings.html")


def topics(request):
    headings = LCSHTopic.objects.all()
    return render(
        request,
        "meetingsvideos/lcsh_all.html",
        {"headings": headings, "lcsh_type": "Topics"},
    )


def topic_detail(request, pk):
    lcsh = get_object_or_404(LCSHTopic, pk=pk)
    return render(request, "meetingsvideos/lcsh_single.html", {"lcsh": lcsh})


def names(request):
    headings = LCSHNamePersonal.objects.all()
    return render(
        request,
        "meetingsvideos/lcsh_all.html",
        {"headings": headings, "lcsh_type": "Names"},
    )


def name_detail(request, pk):
    lcsh = get_object_or_404(LCSHNamePersonal, pk=pk)
    return render(request, "meetingsvideos/lcsh_single.html", {"lcsh": lcsh})


def corporate(request):
    headings = LCSHNameCorporate.objects.all()
    return render(
        request,
        "meetingsvideos/lcsh_all.html",
        {"headings": headings, "lcsh_type": "Corporate Entities"},
    )


def corporate_detail(request, pk):
    lcsh = get_object_or_404(LCSHNameCorporate, pk=pk)
    return render(request, "meetingsvideos/lcsh_single.html", {"lcsh": lcsh})


def geographic(request):
    headings = LCSHGeographic.objects.all()
    return render(
        request,
        "meetingsvideos/lcsh_all.html",
        {"headings": headings, "lcsh_type": "Geographic Entities"},
    )


def geographic_detail(request, pk):
    lcsh = get_object_or_404(LCSHGeographic, pk=pk)
    return render(request, "meetingsvideos/lcsh_single.html", {"lcsh": lcsh})


def temporal(request):
    headings = LCSHTemporal.objects.all()
    return render(
        request,
        "meetingsvideos/lcsh_all.html",
        {"headings": headings, "lcsh_type": "Temporal Entities"},
    )


def temporal_detail(request, pk):
    lcsh = get_object_or_404(LCSHTemporal, pk=pk)
    return render(request, "meetingsvideos/lcsh_single.html", {"lcsh": lcsh})


def symposium(request, symposium_id):
    symposium = get_object_or_404(Symposium, pk=symposium_id)
    return render(request, "meetingsvideos/symposium.html", {"symposium": symposium})


def symposia(request):
    symposia = Symposium.objects.all()
    return render(request, "meetingsvideos/symposia.html", {"symposia": symposia})
