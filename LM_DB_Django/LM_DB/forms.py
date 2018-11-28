
from django import forms
from django.forms import ClearableFileInput, Textarea

from LM_DB.models import *


# form for main information on paper
class PaperForm (forms.ModelForm):
    paper_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    doi = forms.CharField(max_length=50)
    bibtex = forms.CharField(widget=forms.Textarea, required=False,)
    don_t_overwrite = forms.BooleanField(label="don't overwrite when bibtex is updated", required=False)
    cite_command = forms.CharField(max_length=50, required=False)
    title = forms.CharField(max_length=500, required=False)
    abstract = forms.CharField(widget=forms.Textarea, required=False)
    year = forms.IntegerField(required=False)


    class Meta:
        model = Papers
        fields = ('paper_id', 'doi', 'bibtex', 'don_t_overwrite', 'cite_command', 'title', 'abstract', "year")


class FileForm (forms.ModelForm):
    file_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    file_name = forms.CharField(max_length=50, required=False)
    complete_file_path = forms.FileField(widget=forms.ClearableFileInput, label="File", required=False)
    year = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Files
        fields = ('file_id', 'complete_file_path', 'file_name', 'year')


class ConceptNameForm (forms.ModelForm):
    concept_name_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    concept_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = ConceptNames
        fields = ('concept_name_id', 'concept_name')


class PaperConceptNameForm (forms.Form):
    paper_concept_name = forms.ModelMultipleChoiceField(label="",
                                                        queryset=ConceptNames.objects.all().order_by('concept_name'),
                                                        widget=forms.CheckboxSelectMultiple, required=False)


class CoreAttributeForm (forms.ModelForm):
    core_attribute_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    core_attribute = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 1}), required=False)
    is_literal_quotation = forms.BooleanField(required=False)
    page_num = forms.CharField(required=False)
    delete_this_core_attribute = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = CoreAttributes
        fields = ('core_attribute_id', 'core_attribute', 'is_literal_quotation', 'page_num')


class LinkForm (forms.ModelForm):
    link_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    link_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 1}), required=False)
    is_local_link = forms.BooleanField(required=False)
    delete_this_link = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Links
        fields = ('link_id', 'link_text', 'is_local_link')



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
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 2}), required=False)
    super_category = forms.ModelChoiceField(queryset=SuperCategories.objects.all().order_by('name'),
                                            widget=forms.RadioSelect, required=False)

    class Meta:
        model = Categories
        exclude = ('ref_category_to_super_category',)


class PaperCategoryForm(forms.Form):
    paper_categories = forms.ModelMultipleChoiceField(label="",
                                                      queryset=Categories.objects.all().order_by('category_name'),
                                                      widget=forms.CheckboxSelectMultiple, required=False)


class PurposeForm(forms.ModelForm):
    purpose_id = models.AutoField(primary_key=True)
    purpose = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 1}), required=False)
    delete_this_purpose = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = Purposes
        fields = ('purpose_id', 'purpose',)


# Done delete PaperAuthorForm where used
class PaperAuthorForm(forms.Form):
    paper_authors = forms.ModelMultipleChoiceField(label="", queryset=Authors.objects.all().order_by('last_name'),
                                                   widget=forms.CheckboxSelectMultiple, required=False)


class AuthorOrderForm(forms.Form):
    paper_author_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length =100, required=False)
    author_order_on_paper = forms.IntegerField(label="order for paper", required=False)
    delete_this_author = forms.BooleanField(required=False, initial=True)


# Done delete AuthorForm where used
class AuthorForm(forms.ModelForm):
    author_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    last_name = forms.CharField(max_length=100, required=False)
    first_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Authors
        fields = ('author_id', 'last_name', 'first_name')
