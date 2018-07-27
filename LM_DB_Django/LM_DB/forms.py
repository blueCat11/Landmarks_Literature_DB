
from django import forms

from LM_DB.models import *


class PaperForm (forms.ModelForm):
    doi = forms.CharField(max_length=50)
    bibtex = forms.CharField(widget=forms.Textarea, required=False)
    cite_command = forms.CharField(max_length=50, required=False)
    title = forms.CharField(widget=forms.Textarea, required=False)
    abstract = forms.CharField(widget=forms.Textarea, required=False)
    is_fulltext_in_repo = forms.BooleanField(required=False)

    class Meta:
        model = Papers
        fields = ('doi', 'bibtex', 'cite_command', 'title', 'abstract')

