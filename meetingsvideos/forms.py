from django import forms
from .models import APSDepartment, AcademicDiscipline, LCSH
from django.db.models import Count

from .models import Speaker


class AdvancedSearchForm(forms.Form):
    title = forms.CharField(max_length=100, label="Title", required=False)
    abstract = forms.CharField(max_length=100, label="Abstract", required=False)
    speaker = forms.CharField(max_length=100, label="Speaker", required=False)
    subject = forms.CharField(max_length=100, label="Subject", required=False)
    discipline = forms.ModelMultipleChoiceField(
        label="Academic discipline",
        queryset=AcademicDiscipline.objects.all(),
        required=False,
    )
    department = forms.ModelMultipleChoiceField(
        label="APS department", queryset=APSDepartment.objects.all(), required=False
    )

    # ADMIN_CATEGORY_CHOICES = {
    #     "ARCHIVES": "APS Archives",
    #     "INDUCTION": "Member Induction",
    #     "AWARDS": "Presentation of Awards",
    #     "CONCERT": "Concert",
    #     "LECTURE": "Lecture",
    #     "CONVERSATION": "In Conversation",
    #     "PANEL": "Panel Discussion",
    #     "OTHER": "Other",
    # }
    ADMIN_CATEGORY_CHOICES = {
        "LECTURE": "Lectures and Panels",
        "CONCERT": "Concerts",
        "INDUCTION": "Member Inductions",
        "AWARDS": "Presentation of Awards",
        "OTHER": "Other",
    }
    category = forms.MultipleChoiceField(
        choices=ADMIN_CATEGORY_CHOICES,
        label="Video category",
        widget=forms.CheckboxSelectMultiple,
        initial=[value for value in ADMIN_CATEGORY_CHOICES],
        required=False,
    )

    start_date = forms.DateField(
        label="Start date",
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"],
        required=False,
    )
    end_date = forms.DateField(
        label="End date",
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"],
        required=False,
    )


class SubjectModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj[0] + " ({})".format(obj[1])

    def prepare_value(self, value):
        if value is not None:
            return value[0]
        return super().prepare_value(value)


class FacetForm(forms.Form):
    template_name = "meetingsvideos/facet-form.html"
    lcsh = SubjectModelChoiceField(
        queryset=None,
        required=False,
        label="Subject",
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="Choose...",
    )
    discipline = SubjectModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="Choose...",
    )
    start = forms.IntegerField(
        min_value=2003,
        max_value=2025,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-select"}),
    )
    end = forms.IntegerField(
        min_value=2003,
        max_value=2025,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-select"}),
    )

    def __init__(self, object_list, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sub_query = (
            LCSH.objects.filter(video__in=object_list)
            .annotate(n=Count("heading"))
            .values_list("heading", "n")
            .order_by("-n")[:20]
        )

        discipline_query = (
            AcademicDiscipline.objects.filter(video__in=object_list)
            .annotate(n=Count("name"))
            .values_list("name", "n")
            .order_by("-n")[:20]
        )

        self.fields["lcsh"].queryset = sub_query
        self.fields["discipline"].queryset = discipline_query


SpeakerFormSet = forms.modelformset_factory(
    Speaker, fields=["display_name", "lcsh", "label"], extra=0
)
