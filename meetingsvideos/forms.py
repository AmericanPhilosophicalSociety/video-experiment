from django import forms
from .models import APSDepartment, AcademicDiscipline

class AdvancedSearchForm(forms.Form):
    title = forms.CharField(max_length=100, label="Title", required=False)
    abstract = forms.CharField(max_length=100, label="Abstract", required=False)
    speaker = forms.CharField(max_length=100, label="Speaker", required=False)
    subject = forms.CharField(max_length=100, label="Subject", required=False)
    discipline = forms.ModelMultipleChoiceField(label="Academic discipline", queryset=AcademicDiscipline.objects.all(), required=False)
    department = forms.ModelMultipleChoiceField(label="APS department", queryset=APSDepartment.objects.all(), required=False)
    
    ADMIN_CATEGORY_CHOICES = {
        "ARCHIVES": "APS Archives",
        "INDUCTION": "Member Induction",
        "AWARDS": "Presentation of Awards",
        "CONCERT": "Concert",
        "LECTURE": "Lecture",
        "CONVERSATION": "In Conversation",
        "PANEL": "Panel Discussion",
        "OTHER": "Other",
    }
    category = forms.MultipleChoiceField(choices=ADMIN_CATEGORY_CHOICES, widget=forms.CheckboxSelectMultiple, initial=[value for value in ADMIN_CATEGORY_CHOICES], required=False)