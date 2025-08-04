from django import forms

class AdvancedSearchForm(forms.Form):
    title = forms.CharField(max_length=100, label="Title", required=False)
    abstract = forms.CharField(max_length=100, label="Abstract", required=False)
    speaker = forms.CharField(max_length=100, label="Speaker", required=False)
    subject = forms.CharField(max_length=100, label="Subject", required=False)
    term_1 = forms.CharField(max_length=50, 
                             label = "Search term 1", 
                             error_messages={'required': "You must enter at least one search term"})
    term_2 = forms.CharField(max_length=50, 
                             required=False, 
                             label = "Search term 2 (optional)")
    exclude = forms.CharField(max_length=50, 
                              required=False, 
                              label = "Enter a term to exclude")
    exclude_from_sentence = forms.BooleanField(label = "Sentence results",
                                               initial=True,
                                               required=False)
    exclude_from_text = forms.BooleanField(label = "Text results",
                                           initial=True,
                                           required=False)
    distance = forms.IntegerField(help_text = "Enter a whole number", 
                                  required=False, min_value=0, 
                                  label = "Search term 1 must appear within X words of search term 2.")