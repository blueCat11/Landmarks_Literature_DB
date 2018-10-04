from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

# This View displays all current database entries in a table format
from LM_DB.forms import *
from LM_DB.old_stuff.models_old import *

#TODO authentification: http://www.tangowithdjango.com/book17/chapters/login.html
#TODO enable file uploading: https://docs.djangoproject.com/en/2.1/topics/http/file-uploads/
# DONE change concept name to many-to-many relation
#DONE empty core attributes and links are added for new papers, should not be (must be something specific to new, because they can be deleted using edit)

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
    PurposeFormset = formset_factory(PurposeForm)

    def get(self, request):
        paper_form = PaperForm(prefix="paper")
        # get more forms here, multiple model form in one form template, use prefixes
        # save info for template (like forms etc) to contextDict

        concept_name_form= ConceptNameForm(prefix="concept_name")
        purpose_formset = self.PurposeFormset(prefix="purpose")
        paper_concept_name_form = PaperConceptNameForm(prefix="concept_name")
        core_attribute_formset = self.CoreAttributeFormset(prefix="core_attribute")
        links_formset = self.LinkFormset(prefix="link")
        keyword_form = KeywordForm(prefix="new_keyword")
        paper_keywords_form = PaperKeywordForm(prefix="paper_keywords")
        category_form = CategoryForm(prefix="new_category")
        paper_categories_forms = PaperCategoryForm(prefix="paper_categories")

        context_dict = {"original_form_name": "newSave",
                        "type_of_edit": "New Entry",
                        "paper_form": paper_form,
                        "concept_name_form": concept_name_form, "paper_concept_names_form":paper_concept_name_form,
                        "core_attribute_forms": core_attribute_formset,
                        "link_forms": links_formset,
                        "keyword_form":keyword_form, "paper_keywords_form":paper_keywords_form,
                        "category_form":category_form, "paper_categories_form":paper_categories_forms,
                        "purpose_forms":purpose_formset
                        }

        return render(request, "LM_DB/EnterData.html", context_dict)

    # get form data
    # src: https://stackoverflow.com/questions/2770810/multiple-models-in-a-single-django-modelform
    def post(self, request):
        request_data = request.POST
        print(request_data)

        if request_data.get('editStart', -1)!=-1:
            print("editStart")
            # pass data to the template to render the fields with data in them
            # src: https: // docs.djangoproject.com / en / dev / ref / forms / api /  # dynamic-initial-values
            current_paper_pk = request_data["paper_id"]
            all_table_data = get_dict_for_enter_data(current_paper_pk)
            paper_data = all_table_data["paper"]
            paper_form = PaperForm(prefix="paper", initial=paper_data)

            purpose_data = all_table_data["purpose"]
            purpose_formset = self.PurposeFormset(prefix="purpose", initial=purpose_data)

            link_data = all_table_data["link"]
            link_formset = self.LinkFormset(prefix="link", initial=link_data)

            core_attribute_data = all_table_data["core_attribute"]
            core_attribute_formset = self.CoreAttributeFormset(prefix="core_attribute", initial=core_attribute_data)

            keyword_form = KeywordForm(prefix="new_keyword")
            paper_keyword_data = all_table_data["paper_keyword"]
            paper_keywords_form = PaperKeywordForm(prefix="paper_keywords", initial={
                'paper_keywords': paper_keyword_data})

            #DONE decomment the category stuff and integrate into context_dict
            category_form = CategoryForm(prefix="new_category")
            paper_category_data = all_table_data["paper_category"]
            paper_categories_form = PaperCategoryForm(prefix="paper_categories", initial={
                'paper_categories': paper_category_data})

            concept_name_form = ConceptNameForm(prefix="new_concept_name")
            paper_concept_name_data = all_table_data["paper_concept_name"]
            paper_concept_names_form = PaperConceptNameForm(prefix="paper_concept_names", initial={
                'paper_concept_names':paper_concept_name_data})

            context_dict = {"original_form_name": "editSave", "type_of_edit": "Edit Entry",
                            "paper_form": paper_form,
                            "purpose_forms": purpose_formset,
                            "core_attribute_forms": core_attribute_formset,
                            "link_forms": link_formset,
                            "paper_keywords_form":paper_keywords_form, "keyword_form": keyword_form,
                            "paper_categories_form":paper_categories_form, "category_form":category_form,
                            "paper_concept_names_form":paper_concept_names_form, "concept_name_form": concept_name_form}
            return render(request, "LM_DB/EnterData.html", context_dict)

        elif request_data.get('editSave', -1)!=-1:
            print("editSave")

            # get corresponding data-object(s) from DB, make changes to it and save changes
            # src: https://docs.djangoproject.com/en/2.1/ref/forms/api/#checking-which-form-data-has-changed
            current_paper_pk = request_data["paper-paper_id"]
            all_table_data = get_dict_for_enter_data(current_paper_pk)
            paper_data = all_table_data["paper"]
            paper_form = PaperForm(request_data, prefix="paper", initial=paper_data)

            purpose_data = all_table_data["purpose"]
            purpose_formset = self.PurposeFormset(request_data, prefix="purpose", initial=purpose_data)

            link_data = all_table_data["link"]
            link_formset = self.LinkFormset(request_data, prefix="link", initial=link_data)

            core_attribute_data = all_table_data["core_attribute"]
            core_attribute_formset = self.CoreAttributeFormset(request_data, prefix="core_attribute", initial=core_attribute_data)

            paper_keyword_data = all_table_data["paper_keyword"]
            paper_keywords_form = PaperKeywordForm(request_data, prefix="paper_keywords", initial={
                'paper_keywords': paper_keyword_data})

            #DONE: decomment the following (category stuff)
            paper_category_data = all_table_data["paper_category"]
            paper_categories_form = PaperCategoryForm(request_data, prefix="paper_categories",
                                                    initial={'paper_categories': paper_category_data})

            paper_concept_name_data = all_table_data["paper_concept_name"]
            paper_concept_names_form = PaperConceptNameForm(request_data, prefix="paper_concept_names",
                                                           initial={'paper_concept_names': paper_concept_name_data})

            keyword_form = KeywordForm(prefix="new_keyword")
            category_form = CategoryForm(prefix="new_category")
            concept_name_form = ConceptNameForm(prefix="new_concept_name")

            if paper_form.has_changed() or link_formset.has_changed() or core_attribute_formset.has_changed() or paper_keywords_form.has_changed() or purpose_formset.has_changed() or paper_categories_form.has_changed() or paper_concept_names_form.has_changed():
                # add other forms into this if-clause with or later
                if paper_form.is_valid() and link_formset.is_valid() and core_attribute_formset.is_valid() and paper_keywords_form.is_valid() and purpose_formset.is_valid() and paper_categories_form.is_valid() and paper_concept_names_form.is_valid():
                    print("everything valid")
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

                    if purpose_formset.has_changed():
                        print("purpose changed")
                        if purpose_formset.is_valid():
                            print("purpose formset valid")
                            for purpose_form in purpose_formset.forms:
                                if purpose_form.is_valid():
                                    print("purpose form valid")
                                    data = purpose_form.cleaned_data
                                    print("data")
                                    print(data)
                                    if data.get("purpose_id", None) is not None:
                                        current_purpose_id = data["purpose_id"]
                                        current_purpose = Purposes.objects.get(purpose_id=current_purpose_id)
                                        is_to_be_deleted = False
                                        for entry in purpose_form.changed_data:
                                            if entry == "delete_this_purpose":
                                                is_to_be_deleted = data["delete_this_purpose"]
                                            elif entry == "purpose":
                                                current_purpose.purpose = convert_empty_string_to_none(data.get('purpose', None))
                                        if is_to_be_deleted:
                                            current_purpose.delete()
                                            print("purpose deleted")
                                        else:
                                            current_purpose.save()
                                            print("purpose saved")
                                    else:
                                        # what happens, when adding a new concept name
                                        print("new purpose")
                                        print(data)
                                        if data.get("delete_this_purpose", "none") == False:
                                            purpose = convert_empty_string_to_none(data.get("purpose", None))
                                            Purposes.objects.create(purpose=purpose,
                                                                        ref_purpose_to_paper_id=current_paper_pk)
                                            print("purpose saved")
                                        else:
                                            print("purpose not saved")

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
                                        is_to_be_deleted = False
                                        for entry in link_form.changed_data:
                                            if entry == "delete_this_link":
                                                is_to_be_deleted = data["delete_this_link"]
                                            elif entry == "link_text":
                                                current_link.link_text = convert_empty_string_to_none(data.get('link_text', None))
                                            elif entry == "is_local_link":
                                                current_link.is_local_link = data['is_local_link']
                                        if is_to_be_deleted:
                                            current_link.delete()
                                        else:
                                            current_link.save()
                                        print("link saved")
                                    else:
                                        #handles cases, when there's no link-id yet (= new links)
                                        print(data)
                                        if data.get("delete_this_link", "none") == False:
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
                                        print(core_attribute_form.changed_data)
                                        is_to_be_deleted=False
                                        for entry in core_attribute_form.changed_data:
                                            if entry == "delete_this_core_attribute":
                                                is_to_be_deleted = data["delete_this_core_attribute"]
                                            elif entry == "core_attribute":
                                                current_core_attribute.core_attribute = convert_empty_string_to_none(
                                                        data.get('core_attribute', None))
                                            elif entry == "is_literal_quotation":
                                                current_core_attribute.is_literal_quotation = data['is_literal_quotation']
                                            elif entry == "page_num":
                                                current_core_attribute.page_num = convert_empty_string_to_none(data['page_num'])
                                        if is_to_be_deleted:
                                            current_core_attribute.delete()
                                        else:
                                            current_core_attribute.save()
                                    else:
                                        print("core attribute data, new")
                                        print (data)
                                        #handles cases in which id was not given yet (= new core attributes)
                                        if data.get("delete_this_core_attribute", "None") == False:
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
                    if paper_keywords_form.has_changed():
                        print("paper keywords changed")
                        if paper_keywords_form.is_valid():
                            data = paper_keywords_form.cleaned_data #not necessary
                            keywords_before = Keywords.objects.filter(paperkeyword__ref_paper_keyword_to_paper=current_paper_pk)
                            list_keywords_before = keywords_before.values_list('keyword_id',flat=True)
                            keywords_after = paper_keywords_form.cleaned_data['paper_keywords']
                            list_keywords_after = keywords_after.values_list('keyword_id', flat=True)
                            for keyword in keywords_after:
                                if keyword not in keywords_before:
                                    #in after, not before
                                    #add relation to paper_keywords relation
                                    keyword_id = keyword.keyword_id
                                    PaperKeyword.objects.create(ref_paper_keyword_to_keyword_id =keyword_id, ref_paper_keyword_to_paper_id=current_paper_pk)
                            for keyword in keywords_before:
                                if keyword not in keywords_after:
                                    #in before, now not anymore
                                    #delete appropriate entry in paper_keywords
                                    keyword_id = keyword.keyword_id
                                    PaperKeyword.objects.get(ref_paper_keyword_to_keyword_id=keyword_id, ref_paper_keyword_to_paper_id=current_paper_pk).delete()

                            print("valid cleaned paper keywords")
                    if paper_concept_names_form.has_changed():
                        print("paper concept names changed")
                        if paper_concept_names_form.is_valid():

                            concept_names_before = ConceptNames.objects.filter(paperconceptname__ref_paper_concept_name_to_paper=current_paper_pk)
                            #list_concept_names_before = concept_names_before.values_list('concept_name_id',flat=True)
                            concept_names_after = paper_concept_names_form.cleaned_data['paper_concept_names']
                            #list_concept_names_after = concept_names_after.values_list('concept_name_id', flat=True)
                            for concept_name in concept_names_after:
                                if concept_name not in concept_names_before:
                                    #in after, not before
                                    #add relation to paper_keywords relation
                                    concept_name_id = concept_name.concept_name_id
                                    PaperConceptName.objects.create(ref_paper_concept_name_to_concept_name_id =concept_name_id,
                                                                    ref_paper_concept_name_to_paper_id=current_paper_pk)
                            for concept_name in concept_names_before:
                                if concept_name not in concept_names_after:
                                    #in before, now not anymore
                                    #delete appropriate entry in paper_keywords
                                    concept_name_id = concept_name.concept_name_id
                                    PaperConceptName.objects.get(ref_paper_concept_name_to_concept_name_id=concept_name_id,
                                                                 ref_paper_concept_name_to_paper_id=current_paper_pk).delete()

                            print("valid cleaned paper concept names")
                    if paper_categories_form.has_changed():
                        print("paper categories changed")
                        if paper_categories_form.is_valid():
                            categories_before = Categories.objects.filter(papercategory__ref_paper_category_to_paper=current_paper_pk)
                            categories_after = paper_categories_form.cleaned_data['paper_categories']
                            for category in categories_after:
                                if category not in categories_before:
                                    #in after, not before
                                    #add relation to paper_categories relation
                                    category_id = category.category_id
                                    PaperCategory.objects.create(ref_paper_category_to_category_id=category_id,
                                                                 ref_paper_category_to_paper_id=current_paper_pk)
                            for category in categories_before:
                                if category not in categories_after:
                                    #in before, now not anymore
                                    #delete appropriate entry in paper_keywords
                                    category_id = category.category_id
                                    PaperCategory.objects.get(ref_paper_category_to_category_id=category_id,
                                                              ref_paper_category_to_paper_id=current_paper_pk).delete()

                            print("valid cleaned paper categories")
                else:
                    error_dict = {}
                    if not paper_form.is_valid():
                        error_dict["paper"] = True
                    if not core_attribute_formset.is_valid():
                        error_dict["core_attribute_forms"] = True
                    if not link_formset.is_valid():
                        error_dict["link_forms"]=True
                    if not paper_keywords_form.is_valid():
                        error_dict["paper_keywords_form"] = True
                    if not purpose_formset.is_valid():
                        error_dict["purpose"] = True
                    if not paper_categories_form.is_valid():
                        error_dict["category"] = True
                    if not paper_concept_names_form.is_valid():
                        error_dict["paper_concept_name"] = True
                    context_dict = {"original_form_name": "editSave", "type_of_edit": "Edit Entry",
                                    "paper_form": paper_form,
                                    "purpose_forms": purpose_formset,
                                    "core_attribute_forms": core_attribute_formset,
                                    "link_forms": link_formset,
                                    "paper_keywords_form":paper_keywords_form, "keyword_form":keyword_form,
                                    "paper_concept_names_form":paper_concept_names_form, "concept_name_form":concept_name_form,
                                    "paper_categories_form":paper_categories_form, "category_form":category_form,
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
                response_data = {"result": "Creating keyword not successful!", "error":"This keyword already exists."}
            json_response = JsonResponse(response_data)
            return json_response

        elif request_data.get("isNewCategory", -1) != -1 :
            print("isNewCategory")
            category_name = request_data['category_name']
            is_not_unique = Categories.objects.filter(category_name=category_name).exists()
            if not is_not_unique:
                shortcut = request_data['shortcut']
                description = request_data['description']
                super_category = request_data['super_category']
                new_category = Categories(category_name=category_name, shortcut=shortcut, description=description,
                                          ref_category_to_super_category_id=super_category)
                new_category.save()
                print("category saved")
                response_data = {"result":"Create category successful!", "category":category_name, "category_id": new_category.pk}
            else:
                response_data = {"result": "Creating category not successful", "error": "This category already exists."}
            json_response = JsonResponse(response_data)
            return json_response

        elif request_data.get("isNewConceptName", -1) != -1 :
            print("isNewConceptName")
            concept_name = request_data['concept_name']
            is_not_unique = ConceptNames.objects.filter(concept_name=concept_name).exists()
            if not is_not_unique:
                new_concept_name = ConceptNames(concept_name=concept_name)
                new_concept_name.save()
                print("concept name saved")
                response_data = {"result": "Create concept name successful!", "concept_name": concept_name,
                                 "concept_name_id": new_concept_name.pk}
            else:
                response_data = {"result": "Creating concept name not successful!", "error": "This concept name already exists."}
            json_response = JsonResponse(response_data)
            return json_response

        elif request_data.get('newSave', -1) != 1:
            print("newSave")
            # make new object(s) and save those to DB
            # construct forms from data here
            paper_form = PaperForm(request_data, prefix="paper")
            purpose_formset = self.PurposeFormset(request_data, prefix="purpose")
            link_formset = self.LinkFormset(request_data, prefix="link")
            core_attribute_formset = self.CoreAttributeFormset(request_data, prefix="core_attribute")
            paper_keywords_form = PaperKeywordForm(request_data, prefix="paper_keywords")

            #check if all forms are valid, add further forms to the if-clause later
            if paper_form.is_valid() and link_formset.is_valid() and core_attribute_formset.is_valid() and \
                    paper_keywords_form.is_valid() and purpose_formset.is_valid:
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

                    if purpose_formset.is_valid():
                        for purpose_form in purpose_formset:
                            if purpose_form.is_valid():
                                data = purpose_form.cleaned_data
                                if data.get("delete_this_purpose", "None") == False:
                                    purpose = convert_empty_string_to_none(data.get('purpose', None))
                                    current_purpose = Purposes(purpose = purpose,
                                                                        ref_purpose_to_paper=current_paper)
                                    current_purpose.save()

                    if link_formset.is_valid():
                        for link_form in link_formset:
                            # save links here
                            if link_form.is_valid():
                                data = link_form.cleaned_data
                                if data.get("delete_this_link", "None") == False:
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
                                if data.get("delete_this_core_attribute", "None") == False:
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

    current_concept_name = ConceptNames.objects.filter(paperconceptname__ref_paper_concept_name_to_paper=current_paper_pk)
    concept_name_data = current_concept_name.values_list('concept_name_id', flat=True)
    # priorly empty forms are automatically set to be deleted
    all_table_data["concept_name"] = concept_name_data

    current_core_attributes = CoreAttributes.objects.filter(ref_core_attribute_to_paper=current_paper_pk)
    core_attributes_data = current_core_attributes.values()
    for core_attribute in core_attributes_data:
        core_attribute['delete_this_core_attribute'] = False
    all_table_data["core_attribute"] = core_attributes_data

    current_links = Links.objects.filter(ref_link_to_paper=current_paper_pk)
    links_data = current_links.values()
    for link in links_data:
        link['delete_this_link']=False # makes default for already there data not deleted automatically
    all_table_data["link"] = links_data

    current_paper_keywords = Keywords.objects.filter(paperkeyword__ref_paper_keyword_to_paper=current_paper_pk)
    paper_keywords_data = current_paper_keywords.values_list('keyword_id', flat=True)
    all_table_data["paper_keyword"] = paper_keywords_data

    current_paper_categories = Categories.objects.filter(papercategory__ref_paper_category_to_paper=current_paper_pk)
    paper_categories_data = current_paper_categories.values_list('category_id', flat=True)
    all_table_data["paper_category"] = paper_categories_data

    current_purposes = Purposes.objects.filter(ref_purpose_to_paper = current_paper_pk)
    purposes_data = current_purposes.values()
    for purpose in purposes_data:
        purpose['delete_this_purpose'] = False
    all_table_data["purpose"] = purposes_data

    return all_table_data


# This method returns all information on one paper in form of a dictionary, to be used in ViewData-View
# for each column per paper, the data is in String-form
def get_dict_of_all_data_on_one_paper(current_paper_pk):
    paper = Papers.objects.filter(pk=current_paper_pk)
    paper_data = paper.values()[0]

    current_concept_name = ConceptNames.objects.filter(paperconceptname__ref_paper_concept_name_to_paper=current_paper_pk)
    concept_name_data = ''
    for concept_name in current_concept_name:
        concept_name_data += str(concept_name)+", "
    paper_data["concept_name"] = concept_name_data

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

    # the categories that are linked to a paper
    current_categories = Categories.objects.filter(papercategory__ref_paper_category_to_paper=current_paper_pk)
    categories_data = ""
    for category in current_categories:
        categories_data += str(category) + ";"
    paper_data['categories'] = categories_data

    current_purposes = Purposes.objects.filter(ref_purpose_to_paper=current_paper_pk)
    purposes_data = ''
    for purpose in current_purposes:
        purposes_data += str(purpose) + "; "
    paper_data['purpose'] = purposes_data

    # old version:
    # paper_data = {"paper_id":paper.pk, "doi":paper.doi, "bibtex":paper.bibtex, "cite_command":paper.cite_command,
    # "title":paper.title, "abstract":paper.abstract}
    return paper_data


# This method gets a list of the columns which should be displayed in ViewData-View,
# currently they are generated hard-coded :(
def get_list_of_included_columns():
    # first column empty because in table, the edit button should not have a heading
    included_columns = ["", "pk", "doi", "bibtex", "cite_command", "title", "abstract", "is_fulltext_in_repo",
                        "concept_name", "core_attributes", "links", "keywords", "categories", "purpose"]
    return included_columns


# Gets the paper which is being currently edited
def get_current_paper(pk):
    return Papers.objects.get(pk=pk)
