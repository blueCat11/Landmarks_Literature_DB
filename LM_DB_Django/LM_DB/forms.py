
from django import forms

from LM_DB.models import *

# form for main information on paper
class PaperForm (forms.ModelForm):
    paper_id = forms.IntegerField(widget=forms.HiddenInput())
    doi = forms.CharField(max_length=50)
    bibtex = forms.CharField(widget=forms.Textarea, required=False)
    cite_command = forms.CharField(max_length=50, required=False)
    title = forms.CharField(widget=forms.Textarea, required=False)
    abstract = forms.CharField(widget=forms.Textarea, required=False)
    is_fulltext_in_repo = forms.BooleanField(required=False)


    class Meta:
        model = Papers
        fields = ('paper_id', 'doi', 'bibtex', 'cite_command', 'title', 'abstract')


class CoreAttributeForm (forms.ModelForm):
    core_attribute_id = forms.IntegerField(widget=forms.HiddenInput())
    core_attribute = forms.CharField(widget=forms.Textarea, required=False)
    is_literal_quotation = forms.BooleanField(required=False)
    page_num = forms.IntegerField(required=False)

    class Meta:
        model = CoreAttributes
        fields = ('core_attribute_id', 'core_attribute', 'is_literal_quotation', 'page_num')


class LinkForm (forms.ModelForm):
    link_id = forms.IntegerField(widget=forms.HiddenInput())
    link_text = forms.CharField(widget=forms.Textarea, required=False)
    is_local_link = forms.BooleanField(required=False)

    class Meta:
        model=Links
        fields=('link_id', 'link_text', 'is_local_link')
