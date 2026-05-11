from django import forms
from .models import APSDepartment, AcademicDiscipline, LCSH
from django.db.models import Count

from .models import Speaker, Video, Affiliation


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


class AffiliationForm(forms.ModelForm):
    class Meta:
        model = Affiliation
        fields = ["meetings", "position", "institution"]
        widgets = {
            "meetings": forms.SelectMultiple(attrs={"class": "form-select"}),
            "position": forms.TextInput(attrs={"class": "form-control"}),
            "institution": forms.TextInput(attrs={"class": "form-control"}),
        }


AffiliationFormSet = forms.inlineformset_factory(
    Speaker, Affiliation, form=AffiliationForm, can_delete=False, extra=0
)

class SpeakerForm(forms.ModelForm):
    class Meta:
        model = Speaker
        fields = [
            'display_name',
            'label',
            'lcsh',
        ]

        widgets = {
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
            "label": forms.TextInput(attrs={"class": "form-control"}),
            "lcsh": forms.Select(attrs={"class": "form-select"}),
        }


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            "display_notes",
            "admin_notes",
            "title",
            "lecture_additional_info",
            "date",
            "order_in_day",
            "abstract",
            "doi",
            "proceedings_title",
            "node",
            "service_file",
            "admin_category",
            # "lcsh",
            # "aps_departments",
            # "academic_disciplines",
        ]
        widgets = {
            "display_notes": forms.Textarea(attrs={"class": "form-control"}),
            "admin_notes": forms.Textarea(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "lecture_additional_info": forms.TextInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "order_in_day": forms.NumberInput(attrs={"class": "form-control"}),
            "abstract": forms.Textarea(attrs={"class": "form-control"}),
            "doi": forms.URLInput(attrs={"class": "form-control"}),
            "proceedings_title": forms.TextInput(attrs={"class": "form-control"}),
            "node": forms.NumberInput(attrs={"class": "form-control"}),
            "service_file": forms.URLInput(attrs={"class": "form-control"}),
            "admin_category": forms.Select(attrs={"class": "form-select"}),
            # "lcsh": ,
            # "aps_departments",
            # "academic_disciplines",
        }


SpeakerFormSet = forms.modelformset_factory(
    Speaker,
    fields=["display_name", "lcsh", "label"],
    extra=0,
    widgets={
        "display_name": forms.TextInput(attrs={"class": "form-control"}),
        "lcsh": forms.Select(attrs={"class": "form-select"}),
        "label": forms.TextInput(attrs={"class": "form-control"}),
    }
)
