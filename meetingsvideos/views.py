from django.shortcuts import render, get_object_or_404, redirect
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

from .service import basic_search


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
    headings = LCSH.objects.filter(video__isnull=False).distinct()
    return render(request, "meetingsvideos/headings.html", {"headings": headings})


def heading_detail(request, pk):
    lcsh = get_object_or_404(LCSH, pk=pk)
    videos_with_topic = lcsh.video_set.all()
    videos_by_speaker = Video.objects.filter(speakers__lcsh=lcsh)
    
    # if len(lcsh.speaker_set.all()) > 0:
    #     videos_by_speaker = Video.objects.filter(speakers__lcsh=lcsh)
    # else:
    #     videos_by_speaker = None
        
    return render(request, "meetingsvideos/heading_detail.html", {"lcsh": lcsh, "videos_with_topic": videos_with_topic, "videos_by_speaker": videos_by_speaker})


def topics(request):
    headings = LCSH.objects.filter(Q(category="TOPIC") | Q(category="COMPLEX_SUBJECT"))
    return render(
        request,
        "meetingsvideos/heading_category.html",
        {"headings": headings, "lcsh_type": "Topic"},
    )


def names(request):
    headings = LCSH.objects.filter(Q(category="PERSONAL_NAME") & Q(video__isnull=False))
    return render(
        request,
        "meetingsvideos/heading_category.html",
        {"headings": headings, "lcsh_type": "Names"},
    )


def corporate(request):
    headings = LCSH.objects.filter(Q(category="CORPORATE_NAME") & Q(video__isnull=False))
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


def search(request):
    context = {}
    # context['advanced_search'] = AdvancedSearchForm()
    return render(request, "meetingsvideos/search.html", context)


def search_results(request):
    if request.method == "POST":
        query = request.POST['q']
        videos, speakers, subjects = basic_search(query)
        return render(request, "meetingsvideos/search_results.html", {"query": query, "videos": videos, "speakers": speakers, "subjects": subjects})
    else:
        return redirect("search")