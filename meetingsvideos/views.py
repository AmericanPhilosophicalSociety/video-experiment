from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import (
    Video,
    Meeting,
    LCSH,
    Symposium,
    AcademicDiscipline,
    APSDepartment,
    Speaker
)


# Create your views here.
def index(request):
    videos = Video.objects.all()
    return render(request, "meetingsvideos/index.html", {"videos": videos})


def meeting_detail(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    return render(request, "meetingsvideos/meeting_detail.html", {"meeting": meeting})


def meetings(request):
    meetings = Meeting.objects.all()
    return render(request, "meetingsvideos/meetings.html", {"meetings": meetings})


def video_detail(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    return render(request, "meetingsvideos/video_detail.html", {"video": video})


def headings(request):
    headings = LCSH.objects.all()
    return render(request, "meetingsvideos/headings.html", {"headings": headings})


def heading_detail(request, pk):
    lcsh = get_object_or_404(LCSH, pk=pk)
    if len(lcsh.speaker_set.all()) > 0:
        videos_by_speaker = Video.objects.filter(speakers__lcsh=lcsh)
    else:
        videos_by_speaker = None
        
    return render(request, "meetingsvideos/heading_detail.html", {"lcsh": lcsh, "videos_by_speaker": videos_by_speaker})


def topics(request):
    headings = LCSH.objects.filter(Q(category="TOPIC") | Q(category="COMPLEX_SUBJECT"))
    return render(
        request,
        "meetingsvideos/heading_category.html",
        {"headings": headings, "lcsh_type": "Topic"},
    )


def names(request):
    headings = LCSH.objects.filter(category="PERSONAL_NAME")
    return render(
        request,
        "meetingsvideos/heading_category.html",
        {"headings": headings, "lcsh_type": "Names"},
    )


def corporate(request):
    headings = LCSH.objects.filter(category="CORPORATE_NAME")
    return render(
        request,
        "meetingsvideos/heading_category.html",
        {"headings": headings, "lcsh_type": "Corporate Entities"},
    )


def geographic(request):
    headings = LCSH.objects.filter(category="GEOGRAPHIC")
    return render(
        request,
        "meetingsvideos/heading_category.html",
        {"headings": headings, "lcsh_type": "Geographic Entities"},
    )


def symposium_detail(request, symposium_id):
    symposium = get_object_or_404(Symposium, pk=symposium_id)
    return render(request, "meetingsvideos/symposium_detail.html", {"symposium": symposium})


def symposia(request):
    symposia = Symposium.objects.all()
    return render(request, "meetingsvideos/symposia.html", {"symposia": symposia})


def discipline_detail(request, discipline_id):
    discipline = get_object_or_404(AcademicDiscipline, pk=discipline_id)
    return render(request, "meetingsvideos/discipline_detail.html", {"discipline": discipline})


def disciplines(request):
    disciplines = AcademicDiscipline.objects.all()
    return render(request, "meetingsvideos/disciplines.html", {"disciplines": disciplines})


def department_detail(request, department_id):
    department = get_object_or_404(APSDepartment, pk=department_id)
    return render(request, "meetingsvideos/department_detail.html", {"department": department})


def departments(request):
    departments = APSDepartment.objects.all()
    return render(request, "meetingsvideos/departments.html", {"departments": departments})


def speakers(request):
    speakers = Speaker.objects.all().order_by('lcsh')
    return render(request, "meetingsvideos/speakers.html", {"speakers": speakers})


def speaker_detail(request, speaker_id):
    speaker = get_object_or_404(Speaker, pk=speaker_id)
    return render(request, "meetingsvideos/speaker_detail.html", {"speaker": speaker})