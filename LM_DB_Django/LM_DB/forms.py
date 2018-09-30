
from django import forms

from LM_DB.models import *

# form for main information on paper
class PaperForm (forms.ModelForm):
    paper_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    doi = forms.CharField(max_length=50)
    bibtex = forms.CharField(widget=forms.Textarea, required=False)
    cite_command = forms.CharField(max_length=50, required=False)
    title = forms.CharField(widget=forms.Textarea, required=False)
    abstract = forms.CharField(widget=forms.Textarea, required=False)
    is_fulltext_in_repo = forms.BooleanField(required=False)


    class Meta:
        model = Papers
        fields = ('paper_id', 'doi', 'bibtex', 'cite_command', 'title', 'abstract')


class ConceptNameForm (forms.ModelForm):
    concept_name_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    concept_name = forms.CharField(widget=forms.Textarea, required=False)
    delete_this_concept_name = forms.BooleanField(required=False)

    class Meta:
        model=ConceptNames
        fields = ('concept_name_id', 'concept_name')


class CoreAttributeForm (forms.ModelForm):
    core_attribute_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    core_attribute = forms.CharField(widget=forms.Textarea, required=False)
    is_literal_quotation = forms.BooleanField(required=False)
    page_num = forms.CharField(required=False)
    delete_this_core_attribute = forms.BooleanField(required=False)

    class Meta:
        model = CoreAttributes
        fields = ('core_attribute_id', 'core_attribute', 'is_literal_quotation', 'page_num')


class LinkForm (forms.ModelForm):
    link_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    link_text = forms.CharField(widget=forms.Textarea, required=False)
    is_local_link = forms.BooleanField(required=False)
    delete_this_link = forms.BooleanField(required=False)

    class Meta:
        model=Links
        fields=('link_id', 'link_text', 'is_local_link')


class KeywordForm(forms.ModelForm):
    keyword_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    keyword = forms.CharField(max_length=60, required=False)

    class Meta:
        model = Keywords
        exclude = ()


class PaperKeywordForm(forms.Form):
    paper_keywords = forms.ModelMultipleChoiceField(label="", queryset=Keywords.objects.all().order_by('keyword'),
                                                   widget=forms.CheckboxSelectMultiple, required=False)


class CategoryForm(forms.ModelForm):
    category_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    category_name = forms.CharField(max_length=50, required=False)
    shortcut = forms.CharField(max_length=10, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    #TODO super_category_choices should be generated from DB if possible
    # first part of tuple is unique id of super category, second part is name of super category
    super_category_choices = (
        (1, 'environment'),
        (2, 'type of paper'),
        (3, 'size of landmark'),
    )
    super_category = forms.ChoiceField(choices=super_category_choices)

    class Meta:
        model = Categories
        exclude = ('ref_category_to_super_category',)


class PaperCategoryForm(forms.Form):
    paper_categories = forms.ModelMultipleChoiceField(label="", queryset=Categories.objects.all().order_by('category_name'),
                                                    widget=forms.CheckboxSelectMultiple, required=False)