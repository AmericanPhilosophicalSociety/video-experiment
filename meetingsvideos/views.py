from django.shortcuts import render, get_object_or_404, redirect
from .forms import AdvancedSearchForm
from django.views.generic import ListView

from random import sample
from string import ascii_uppercase

from .models import (
    Video,
    Meeting,
    LCSH,
    Symposium,
    AcademicDiscipline,
    APSDepartment,
    Speaker,
)

from .service import basic_search, advanced_search


class TopicView(ListView):
    context_object_name = "topics"
    paginate_by = 25

    def get_template_names(self, *args, **kwargs):
        if self.request.htmx:
            return "meetingsvideos/item-list.html"
        else:
            return self.template_name


class FilterView(TopicView):
    queryset_method = None

    def get_queryset(self):
        queryset = self.queryset_method()
        param = self.request.GET.getlist('q')
        if param:
            queryset = queryset.filter(category__in=param)

        return queryset


class Landing(ListView):
    template_name = "meetingsvideos/landing-page.html"
    context_object_name = "videos"

    def get_queryset(self):
        # get all pks that exist - don't call object into memory
        pks = Video.objects.values_list('pk', flat=True)
        # choose three random pks
        random_pks = sample(list(pks), 3)
        # call selected object into memory
        queryset = Video.objects.filter(pk__in=random_pks)
        return queryset


class IndexView(ListView):
    # model = Video
    template_name = "meetingsvideos/index.html"
    context_object_name = "videos"
    paginate_by = 10

    def get_queryset(self):
        queryset = Video.objects.exclude_inductions()
        return queryset

    def get_template_names(self, *args, **kwargs):
        if self.request.htmx:
            return "meetingsvideos/video-list.html"
        else:
            return self.template_name


class HeadingsView(FilterView):
    queryset_method = LCSH.objects.only_topics
    template_name = "meetingsvideos/headings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["link_template"] = "heading_detail"
        return context


class SpeakersView(FilterView):
    queryset_method = Speaker.objects.with_first_letter
    template_name = "meetingsvideos/speakers.html"
    alpha_list = list(ascii_uppercase)
    available_letters = set(Speaker.objects.with_first_letter().values_list('category', flat=True))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["alphabet"] = self.alpha_list
        context["available_letters"] = self.available_letters
        context["link_template"] = "speaker_detail"
        return context


class MeetingsList(ListView):
    model = Meeting
    template_name = "meetingsvideos/meetings.html"
    context_object_name = "meetings"
    paginate_by = 10

    def get_template_names(self, *args, **kwargs):
        if self.request.htmx:
            return "meetingsvideos/meetings-list.html"
        else:
            return self.template_name


class SymposiumList(ListView):
    model = Symposium
    template_name = "meetingsvideos/symposia.html"
    context_object_name = "symposia"
    paginate_by = 10

    def get_template_names(self, *args, **kwargs):
        if self.request.htmx:
            return "meetingsvideos/symposium-list.html"
        else:
            return self.template_name


class DisciplineList(ListView):
    model = AcademicDiscipline
    template_name = "meetingsvideos/disciplines.html"
    context_object_name = "topics"


def meeting_detail(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    return render(request, "meetingsvideos/meeting_detail.html", {"meeting": meeting})


def video_detail(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    return render(request, "meetingsvideos/video_detail.html", {"video": video})


def heading_detail(request, pk):
    lcsh = get_object_or_404(LCSH, pk=pk)

    # returns separate lists of videos tagged with this LCSH and videos whose
    # speaker corresponds to this LCSH
    videos_with_topic = lcsh.video_set.all()
    videos_by_speaker = Video.objects.filter(speakers__lcsh=lcsh)

    return render(
        request,
        "meetingsvideos/heading_detail.html",
        {
            "lcsh": lcsh,
            "videos_with_topic": videos_with_topic,
            "videos_by_speaker": videos_by_speaker,
        },
    )


def symposium_detail(request, symposium_id):
    symposium = get_object_or_404(Symposium, pk=symposium_id)
    return render(
        request, "meetingsvideos/symposium_detail.html", {"symposium": symposium}
    )


def symposia(request):
    symposia = Symposium.objects.all()
    return render(request, "meetingsvideos/symposia.html", {"symposia": symposia})


def discipline_detail(request, discipline_id):
    discipline = get_object_or_404(AcademicDiscipline, pk=discipline_id)
    return render(
        request, "meetingsvideos/discipline_detail.html", {"discipline": discipline}
    )


def disciplines(request):
    disciplines = AcademicDiscipline.objects.all()
    return render(
        request, "meetingsvideos/disciplines.html", {"disciplines": disciplines}
    )


def department_detail(request, department_id):
    department = get_object_or_404(APSDepartment, pk=department_id)
    return render(
        request, "meetingsvideos/department_detail.html", {"department": department}
    )


def departments(request):
    departments = APSDepartment.objects.all()
    return render(
        request, "meetingsvideos/departments.html", {"departments": departments}
    )


def speaker_detail(request, speaker_id):
    speaker = get_object_or_404(Speaker, pk=speaker_id)
    return render(request, "meetingsvideos/speaker_detail.html", {"speaker": speaker})


def search(request):
    context = {}
    context["advanced_search"] = AdvancedSearchForm()
    return render(request, "meetingsvideos/search.html", context)


def search_results(request):
    if request.method == "POST":
        query = request.POST["q"]
        videos, speakers, subjects, disciplines, departments = basic_search(query)
        return render(
            request,
            "meetingsvideos/search_results.html",
            {
                "query": query,
                "videos": videos,
                "speakers": speakers,
                "subjects": subjects,
                "disciplines": disciplines,
                "departments": departments,
            },
        )
    else:
        return redirect("search")


def search_results_advanced(request):
    if request.method == "POST":
        # TODO: remove this once everything is working
        query = request.POST
        form = AdvancedSearchForm(request.POST)
        if form.is_valid():
            videos = advanced_search(form)
            return render(
                request,
                "meetingsvideos/search_results_advanced.html",
                {"query": query, "videos": videos},
            )
        # TODO: does anything else need to happen if form not valid?
        else:
            return redirect("search")
    else:
        return redirect("search")
