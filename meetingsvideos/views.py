from django.shortcuts import render, redirect
from .forms import AdvancedSearchForm
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers

from random import sample
from string import ascii_uppercase
import datetime

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


class HTMXMixin:
    partial_template = None
    content_template = None

    def get_template_names(self, *args, **kwargs):
        if self.request.htmx.target == "video-container":
            return self.content_template
        elif self.request.htmx and not self.request.htmx.history_restore_request:
            return self.partial_template
        else:
            return self.template_name

    @method_decorator(vary_on_headers("HX-Request"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TopicView(HTMXMixin, ListView):
    context_object_name = "topics"
    paginate_by = 25
    link_template = None
    partial_template = "meetingsvideos/item-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["link_template"] = self.link_template
        return context


class AlphaMixin:
    model = None
    alpha_list = list(ascii_uppercase)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["alphabet"] = self.alpha_list
        available_letters = set(
            self.model.objects.with_first_letter().values_list(
                "first_letter", flat=True
            )
        )
        context["available_letters"] = available_letters
        return context


class FilterView(TopicView):
    queryset_method = None

    def get_queryset(self):
        queryset = self.queryset_method()
        param = self.request.GET.getlist("q")
        if param:
            queryset = queryset.filter(category__in=param)

        return queryset


class AlphaFilterView(AlphaMixin, FilterView):
    def get_queryset(self):
        queryset = super().get_queryset()
        first_letter = self.request.GET.get("first_letter")
        if first_letter:
            queryset = queryset.filter(first_letter=first_letter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        param = self.request.GET.getlist("q")
        if param:
            available_letters = set(
                self.queryset_method()
                .filter(category__in=param)
                .values_list("first_letter", flat=True)
            )
            context["available_letters"] = available_letters
        return context


class Landing(ListView):
    template_name = "meetingsvideos/landing-page.html"
    context_object_name = "videos"

    def get_queryset(self):
        # get all pks that exist - don't call object into memory
        pks = Video.objects.values_list("pk", flat=True)
        # choose three random pks
        random_pks = sample(list(pks), 3)
        # call selected object into memory
        queryset = Video.objects.filter(pk__in=random_pks)
        return queryset


class IndexView(HTMXMixin, ListView):
    # model = Video
    template_name = "meetingsvideos/index.html"
    context_object_name = "videos"
    paginate_by = 10
    partial_template = "meetingsvideos/video-list.html"
    content_template = "meetingsvideos/index-content.html"

    def get_queryset(self):
        queryset = Video.objects.exclude_inductions()
        return queryset


class VideoDetail(DetailView):
    model = Video
    context_object_name = "video"
    template_name = "meetingsvideos/video_detail.html"


class HeadingsView(AlphaFilterView):
    model = LCSH
    queryset_method = LCSH.objects.only_topics_with_first_letter
    template_name = "meetingsvideos/headings.html"
    link_template = "heading_detail"
    content_template = "meetingsvideos/heading-content.html"


class HeadingDetail(DetailView):
    model = LCSH
    context_object_name = "lcsh"
    template_name = "meetingsvideos/heading_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        videos_by_speaker = Video.objects.filter(speakers__lcsh=self.get_object().pk)
        context["videos_by_speaker"] = videos_by_speaker
        return context


class SpeakersView(AlphaFilterView):
    model = Speaker
    queryset_method = Speaker.objects.with_first_letter
    template_name = "meetingsvideos/speakers.html"
    link_template = "speaker_detail"
    content_template = "meetingsvideos/speaker-content.html"


class SpeakerDetail(DetailView):
    model = Speaker
    template_name = "meetingsvideos/speaker_detail.html"
    context_object_name = "speaker"


class MeetingsList(HTMXMixin, ListView):
    model = Meeting
    template_name = "meetingsvideos/meetings.html"
    context_object_name = "meetings"
    paginate_by = 10
    partial_template = "meetingsvideos/meetings-list.html"
    content_template = "meetingsvideos/meeting-content.html"


class MeetingDetail(HTMXMixin, DetailView):
    model = Meeting
    context_object_name = "meeting"
    template_name = "meetingsvideos/meeting_detail.html"
    partial_template = "meetingsvideos/meeting-video-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dates = sorted(set(self.get_object().video_set.values_list("date", flat=True)))
        context["dates"] = dates
        param = self.request.GET.get("q")
        if param:
            parsed_param = [int(p) for p in param.split("-")]
            query_date = datetime.date(*parsed_param)
        else:
            try:
                query_date = dates[0]
            except IndexError:
                query_date = None
        context["videos"] = self.get_object().video_set.filter(date=query_date)
        return context


class SymposiumList(HTMXMixin, ListView):
    model = Symposium
    template_name = "meetingsvideos/symposia.html"
    context_object_name = "symposia"
    paginate_by = 10
    partial_template = "meetingsvideos/symposium-list.html"
    content_template = "meetingsvideos/symposium-content.html"


class SymposiumDetail(DetailView):
    model = Symposium
    template_name = "meetingsvideos/symposium_detail.html"
    context_object_name = "symposium"


class DisciplineList(TopicView):
    model = AcademicDiscipline
    template_name = "meetingsvideos/disciplines.html"
    link_template = "discipline_detail"
    content_template = "meetingsvideos/discipline-content.html"


class DisciplineDetail(DetailView):
    model = AcademicDiscipline
    template_name = "meetingsvideos/discipline_detail.html"
    context_object_name = "discipline"


# class DepartmentList(TopicView):
#     model = APSDepartment
#     template_name = "meetingsvideos/departments.html"
#     link_template = "department_detail"
#     content_template = "meetingsvideos/department-content.html"


# class DepartmentDetail(DetailView):
#     model = APSDepartment
#     template_name = "meetingsvideos/department_detail.html"
#     context_object_name = "department"


def search(request):
    context = {}
    context["advanced_search"] = AdvancedSearchForm()
    if request.htmx:
        template_name = "meetingsvideos/search-content.html"
    else:
        template_name = "meetingsvideos/search.html"
    return render(request, template_name, context)


def search_results(request):
    if request.method == "POST":
        query = request.POST["q"]
        videos, speakers, subjects = basic_search(query)
        return render(
            request,
            "meetingsvideos/search_results.html",
            {
                "query": query,
                "videos": videos,
                "speakers": speakers,
                "subjects": subjects,
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
