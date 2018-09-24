from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

# This View displays all current database entries in a table format
from LM_DB.forms import *
from LM_DB.models import *


class ViewData(View):
    def get(self, request):
        # how to form queryset into list: https://stackoverflow.com/questions/7811556/how-do-i-convert-a-django-queryset-into-list-of-dicts
        all_papers = Papers.objects.all()
        paper_list = []
        for paper in all_papers:
            paper_data = get_dict_of_all_data_on_one_paper(paper.pk)
            paper_list.append(paper_data)

        columns = get_list_of_included_columns()
        context_dict = {"papers": paper_list, "included_columns": columns}
        return render(request, "LM_DB/ViewData.html", context_dict)

    # maybe we don't need a post here
    def post(self, request):
        pass


# This View allows entering new data and editing data by means of forms
# To add forms to formsets dynamically:
# https://stackoverflow.com/questions/501719/dynamically-adding-a-form-to-a-django-formset-with-ajax
class EnterData(View):
    CoreAttributeFormset = formset_factory(CoreAttributeForm)
    LinkFormset = formset_factory(LinkForm)


    def get(self, request):
        paper_form = PaperForm(prefix="paper")
        # get more forms here, multiple model form in one form template, use prefixes
        # save info for template (like forms etc) to contextDict

        core_attribute_formset = self.CoreAttributeFormset(prefix="core_attribute")
        links_formset = self.LinkFormset(prefix="link")
        keyword_form = KeywordForm(prefix="new_keyword")
        paper_keywords_form = PaperKeywordForm(prefix="paper_keywords")

        context_dict = {"original_form_name": "newSave",
                        "type_of_edit": "New Entry", "paper_form": paper_form,
                        "core_attribute_forms": core_attribute_formset, "link_forms": links_formset,
                        "keyword_form":keyword_form, "paper_keywords_form":paper_keywords_form
                        }

        return render(request, "LM_DB/EnterData.html", context_dict)

    # get form data
    # src: https://stackoverflow.com/questions/2770810/multiple-models-in-a-single-django-modelform
    def post(self, request):
        request_data = request.POST

        if request_data.get('editStart', -1)!=-1:
            print("editStart")
            # pass data to the template to render the fields with data in them
            # src: https: // docs.djangoproject.com / en / dev / ref / forms / api /  # dynamic-initial-values
            current_paper_pk = request_data["paper_id"]
            all_table_data = get_dict_for_enter_data(current_paper_pk)
            paper_data = all_table_data["paper"]
            paper_form = PaperForm(prefix="paper", initial=paper_data)

            link_data = all_table_data["link"]
            link_formset = self.LinkFormset(prefix="link", initial=link_data)

            core_attribute_data = all_table_data["core_attribute"]
            core_attribute_formset = self.CoreAttributeFormset(prefix="core_attribute", initial=core_attribute_data)

            keyword_form = KeywordForm(prefix="new_keyword")
            paper_keyword_data = all_table_data["paper_keyword"]
            print(paper_keyword_data)
            paper_keywords_form = PaperKeywordForm(prefix="paper_keywords", initial = {
                'paper_keywords': all_table_data["paper_keyword"]}
                                                   )
            print(paper_keywords_form)


            context_dict = {"original_form_name": "editSave", "type_of_edit": "Edit Entry", "paper_form": paper_form,
                            "core_attribute_forms": core_attribute_formset, "link_forms": link_formset,
                            "paper_keywords_form":paper_keywords_form, "keyword_form": keyword_form}
            return render(request, "LM_DB/EnterData.html", context_dict)

        elif request_data.get('editSave', -1)!=-1:
            print("editSave")
            # get corresponding data-object(s) from DB, make changes to it and save changes
            # src: https://docs.djangoproject.com/en/2.1/ref/forms/api/#checking-which-form-data-has-changed
            current_paper_pk = request_data["paper-paper_id"]
            all_table_data = get_dict_for_enter_data(current_paper_pk)
            paper_data = all_table_data["paper"]
            paper_form = PaperForm(request_data, prefix="paper", initial=paper_data)
            print(request_data)

            link_data = all_table_data["link"]
            link_formset = self.LinkFormset(request_data, prefix="link", initial=link_data)

            core_attribute_data = all_table_data["core_attribute"]
            core_attribute_formset = self.CoreAttributeFormset(request_data, prefix="core_attribute", initial=core_attribute_data)

            if paper_form.has_changed() or link_formset.has_changed() or core_attribute_formset.has_changed(): # add other forms into this if-clause with or later
                if paper_form.is_valid() and link_formset.is_valid() and core_attribute_formset.is_valid():

                    if paper_form.has_changed():
                        current_paper = get_current_paper(current_paper_pk)
                        if paper_form.is_valid():
                            data = paper_form.cleaned_data
                            for entry in paper_form.changed_data:
                                if entry == "doi":
                                    current_paper.doi = convert_empty_string_to_none(data.get('doi', None))
                                elif entry == "bibtex":
                                    current_paper.bibtex = convert_empty_string_to_none(data.get('bibtex', None))
                                elif entry == "cite_command":
                                    current_paper.cite_command = convert_empty_string_to_none(data.get('cite_command', None))
                                elif entry == "title":
                                    current_paper.title =  convert_empty_string_to_none(data.get('title', None))
                                elif entry == "abstract":
                                    current_paper.abstract = convert_empty_string_to_none(data.get('abstract', None))
                                elif entry == "is_fulltext_in_repo":
                                    current_paper.is_fulltext_in_repo = data['is_fulltext_in_repo']
                            current_paper.save()
                        else:
                            # error display is managed in outside else-clause, all have to be valid to get here
                            pass
                    if link_formset.has_changed():
                        print("linkformset changed")
                        if link_formset.is_valid():
                            print("link formset valid")
                            current_paper = get_current_paper(current_paper_pk)
                            for link_form in link_formset:
                                if link_form.is_valid():
                                    print("link form valid")
                                    data = link_form.cleaned_data
                                    if data.get("link_id", None) is not None:
                                        current_link_id = data["link_id"]
                                        current_link = Links.objects.get(link_id=current_link_id)
                                        for entry in link_form.changed_data:
                                            if entry == "link_text":
                                                current_link.link_text = convert_empty_string_to_none(data.get('link_text', None))
                                            elif entry == "is_local_link":
                                                current_link.is_local_link = data['is_local_link']
                                        current_link.save()
                                        print("link saved")
                                    else:
                                        link_text = convert_empty_string_to_none(data.get("link_text", None))
                                        is_local_link = data.get("is_local_link", None)
                                        Links.objects.create(link_text=link_text,
                                                             is_local_link=is_local_link,
                                                             ref_link_to_paper=current_paper
                                                             )
                                else:
                                    # error handling done in outside else clause
                                    pass
                        else:
                            print("link_formset_not_valid")
                            print(link_formset.errors)
                        if core_attribute_formset.has_changed():
                            if core_attribute_formset.is_valid():
                                current_paper = get_current_paper(current_paper_pk)
                                for core_attribute_form in core_attribute_formset:
                                    if core_attribute_form.is_valid():
                                        data = core_attribute_form.cleaned_data
                                        if data.get("core_attribute_id", None) is not None:
                                            current_core_attribute_id = data["core_attribute_id"]
                                            current_core_attribute = CoreAttributes.objects.get(core_attribute_id= current_core_attribute_id)
                                            for entry in core_attribute_form.changed_data:
                                                if entry == "core_attribute":
                                                    current_core_attribute.core_attribute = convert_empty_string_to_none(
                                                        data.get('core_attribute', None))
                                                elif entry == "is_literal_quotation":
                                                    current_core_attribute.is_literal_quotation = data['is_literal_quotation']
                                                elif entry == "page_num":
                                                    current_core_attribute.page_num = convert_empty_string_to_none(data['page_num'])
                                            current_core_attribute.save()
                                        else:
                                            core_attribute = convert_empty_string_to_none(data.get("core_attribute", None))
                                            is_literal_quotation = data.get("is_literal_quotation", None)
                                            page_num = data.get("page_num", None)
                                            CoreAttributes.objects.create(core_attribute=core_attribute,
                                                                          is_literal_quotation=is_literal_quotation,
                                                                          page_num=page_num,
                                                                          ref_core_attribute_to_paper=current_paper)
                                    else:
                                        # error handling done in outside else-clause
                                        pass
                else:
                    error_dict = {}
                    if not paper_form.is_valid():
                        error_dict["paper"]=True
                    if not core_attribute_formset.is_valid():
                        error_dict["core_attribute_forms"] =True
                    if not link_formset.is_valid():
                        error_dict["link_forms"]=True
                    context_dict = {"original_form_name": "editSave", "type_of_edit": "Edit Entry",
                                    "paper_form": paper_form,
                                    "core_attribute_forms": core_attribute_formset, "link_forms": link_formset,
                                    "errors":error_dict}
                    return render(request, "LM_DB/enterData.html", context_dict)
            return redirect("LM_DB:viewData")

        elif request_data.get("isNewKeyword", -1) != -1:
            print("isNewKeyword")
            #print(request_data)
            keyword = request_data['keyword']
            is_not_unique = Keywords.objects.filter(keyword=keyword).exists()
            if not is_not_unique:
                new_keyword = Keywords(keyword=keyword)
                new_keyword.save()
                print("keyword saved")
                response_data = {"result": "Create keyword successful!", "keyword": keyword, "keyword_id": new_keyword.pk}
            else:
                response_data = {"result": "Keyword not unique!", "error":"This keyword already exists."}
            json_response = JsonResponse(response_data)
            return json_response

        elif request_data.get('newSave', -1) != 1:
            print("newSave")
            # make new object(s) and save those to DB
            # construct forms from data here
            paper_form = PaperForm(request_data, prefix="paper")
            link_formset = self.LinkFormset(request_data, prefix="link")
            core_attribute_formset = self.CoreAttributeFormset(request_data, prefix="core_attribute")
            paper_keywords_form = PaperKeywordForm(request_data, prefix="paper_keywords")

            #check if all forms are valid, add further forms to the if-clause later
            if paper_form.is_valid() and link_formset.is_valid() and core_attribute_formset.is_valid() and \
                    paper_keywords_form.is_valid():
                # save data from the forms here
                if paper_form.is_valid():
                    data = paper_form.cleaned_data
                    #print(data)
                    doi = data['doi']
                    bibtex = convert_empty_string_to_none(data.get('bibtex', None))
                    cite_command = convert_empty_string_to_none(data.get('cite_command', None))
                    title = convert_empty_string_to_none(data.get('title', None))
                    abstract = convert_empty_string_to_none(data.get('abstract', None))
                    is_in_repo = data.get('is_fulltext_in_repo', None)
                    current_paper = Papers(doi=doi, bibtex=bibtex, cite_command=cite_command, title=title,
                                           abstract=abstract, is_fulltext_in_repo=is_in_repo)
                    current_paper.save()

                    if link_formset.is_valid():
                        for link_form in link_formset:
                            # save links here
                            if link_form.is_valid():
                                data = link_form.cleaned_data
                                link_text = convert_empty_string_to_none(data.get('link_text', None))
                                is_local_link = data.get('is_local_link', None)
                                current_link = Links(link_text=link_text, is_local_link=is_local_link,
                                                     ref_link_to_paper=current_paper)
                                current_link.save()

                    if core_attribute_formset.is_valid():
                        for core_attribute_form in core_attribute_formset:
                            # save core attributes here!
                            if core_attribute_form.is_valid():
                                data = core_attribute_form.cleaned_data
                                core_attribute = convert_empty_string_to_none(data.get('core_attribute', None))
                                is_literal_quotation = data.get('is_literal_quotation', None)
                                page_num = data.get('is_literal_quotation', None) # TODO add empty string to none later, after has been converted to char-field
                                current_core_attribute = CoreAttributes(core_attribute=core_attribute,
                                                                        is_literal_quotation=is_literal_quotation,
                                                                        page_num=page_num,
                                                                        ref_core_attribute_to_paper= current_paper)
                                current_core_attribute.save()

                    if paper_keywords_form.is_valid():
                        data = paper_keywords_form.cleaned_data
                        print("paper keywords")
                        print(data)
                        ref_paper = current_paper
                        for keyword in data.get("paper_keywords", None):
                            current_paper_keyword = PaperKeyword(ref_paper_keyword_to_paper=ref_paper, ref_paper_keyword_to_keyword=keyword)
                            current_paper_keyword.save()
                    else:
                        print("paper keywords not valid")

                else:
                    # paper form is not valid
                    print("paper form not valid")


                return redirect("LM_DB:viewData")
            else:
                pass
                # TODO: error handling


        else:
            print("default")
            pass


# This method is necessary because django gets the value of empty text fields as '' and not as None, but we want null
# for all empty fields in the DB, so you can check: How many papers do not have a saved bibTex or similiar queries
# Pass all data-gets for textfields to this method, so that their empty values are converted to None
def convert_empty_string_to_none(a_string):
    if a_string in [None, '']:
        return None
    else:
        return a_string


# This method returns all information on one paper in form of a dictionary, to be used for display in EnterData-View
# information for different forms is stored in different dictionaries
# some contain more than one object e.g. core attributes
def get_dict_for_enter_data(current_paper_pk):
    paper = Papers.objects.filter(pk=current_paper_pk)
    all_table_data = {}
    paper_data = paper.values()[0]
    all_table_data["paper"] = paper_data

    current_core_attributes = CoreAttributes.objects.filter(ref_core_attribute_to_paper=current_paper_pk)
    core_attributes_data = current_core_attributes.values()
    all_table_data["core_attribute"] = core_attributes_data

    current_links = Links.objects.filter(ref_link_to_paper=current_paper_pk)
    links_data = current_links.values()
    all_table_data["link"] = links_data

    current_paper_keywords = Keywords.objects.filter(paperkeyword__ref_paper_keyword_to_paper=current_paper_pk)
    paper_keywords_data = current_paper_keywords.values_list('keyword_id', flat=True)
    all_table_data["paper_keyword"] = paper_keywords_data
    # TODO: add version for keywords (many-to-many) Don't know yet how...
    # paper_data = {"pk":paper.pk, "doi":paper.doi, "bibtex":paper.bibtex, "cite_command":paper.cite_command, "title":paper.title, "abstract":paper.abstract}
    return all_table_data
    # as long as there are no relations connected to paper:


# This method returns all information on one paper in form of a dictionary, to be used in ViewData-View
# for each column per paper, the data is in String-form
def get_dict_of_all_data_on_one_paper(current_paper_pk):
    paper = Papers.objects.filter(pk=current_paper_pk)
    paper_data = paper.values()[0]

    current_core_attributes = CoreAttributes.objects.filter(ref_core_attribute_to_paper=current_paper_pk)
    core_attributes_data = ''
    for core_attribute in current_core_attributes:
        core_attributes_data += str(core_attribute) + "; "
    paper_data['core_attributes'] = core_attributes_data

    current_links = Links.objects.filter(ref_link_to_paper=current_paper_pk)
    links_data = ''
    for link in current_links:
        links_data += str(link) + "; "
    paper_data['links'] = links_data

    # the keywords that are linked to a paper
    current_keywords = Keywords.objects.filter(paperkeyword__ref_paper_keyword_to_paper=current_paper_pk)
    keywords_data = ''
    for keyword in current_keywords:
        keywords_data += str(keyword) + ", "
    paper_data['keywords'] = keywords_data

    # old version:
    # paper_data = {"paper_id":paper.pk, "doi":paper.doi, "bibtex":paper.bibtex, "cite_command":paper.cite_command,
    # "title":paper.title, "abstract":paper.abstract}
    return paper_data

    # TODO: with other tables being displayed in relation, this dictionary needs to be updated
    # TODO: missing: purposes, categories, conceptname


# This method gets a list of the columns which should be displayed in ViewData-View,
# currently they are generated hard-coded :(
def get_list_of_included_columns():
    # first column empty because in table, the edit button should not have a heading
    included_columns = ["", "pk", "doi", "bibtex", "cite_command", "title", "abstract", "is_fulltext_in_repo",
                        "core_attributes", "links", "keywords"]
    return included_columns


# Gets the paper which is being currently edited
def get_current_paper(pk):
    return Papers.objects.get(pk=pk)

