from django.contrib import messages
from django.forms import formset_factory
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render, redirect, render_to_response
import bibtexparser  # for bibtex
from datetime import datetime, timezone  # for edit and creation times

from django_tables2 import RequestConfig
from pyparsing import ParseException

from LM_DB.display_methods import *
from LM_DB.general import *
from django.views import View

from LM_DB.tables import PaperTable
from LM_DB_Django.settings import MEDIA_ROOT
from LM_DB.forms import *

CONTEXT_NEW_SAVE = "newSave"
CONTEXT_EDIT = "editSave"
CONTEXT_FOR_DB = "db"
CONTEXT_FOR_VIEW = "view"

# custom message level
ANCHOR_ID = 21


# DONE see https://simpleisbetterthancomplex.com/tips/2016/09/06/django-tip-14-messages-framework.html
# To-Dos
# DONE authentification: http://www.tangowithdjango.com/book17/chapters/login.html;
# DONE user permissions # https://docs.djangoproject.com/en/2.1/topics/auth/default/#topic-authorization
# DONE enable file uploading: https://docs.djangoproject.com/en/2.1/topics/http/file-uploads/
# DONE display file as field with "is_file_in_repo", false when empty, path-string when true
# DONE integrate separate file form -> currently only possible for new papers, not in edit mode
# DONE change concept name to many-to-many relation
# DONE empty core attributes and links are added for new papers, should not be (must be something specific to new,
# because they can be deleted using edit)
# DONE add css to make layout better, i.e. navbar: https://getuikit.com/docs/navbar
# DONE add UI-Kit notification instead of alert https://getuikit.com/docs/notification
# DONE test cite-command + title updates
# DONE update author from bibtex
# DONE update keywords from bibtex
# DONE check where files are uploaded
# DONE sticky table header
# DONE: TEST set checkmark (bibtex) automatically, after first bibtex update
# DONE make new Author relation Paper_Author mediator table
# DONE incorporate author-paper many-to-many relationship into code
# DONE add possibility to specify order of author for given paper
# Done add field "verified by" to paper (needs to be different user than created)
# Done add boolean field "need for discussion" to paper
# DONE: Bug fix: updating bibtex again authors: empty forms again and again, and first author delete-this-checked
# DONE: Bug fix page numbers get displayed as True and False
# DONE: after verify or download or needForDiscussion, return to previous table row (anchor link jumping)
# DONE get abstract-column wider (https://stackoverflow.com/questions/19847371/django-how-to-change-the-column-width-in-django-tables2)
# DONE visualize spaces after each item for categories, links, etc
# DONE: test whether keywords still work
# DONE: check whether file of this name is already in media folder (ensure it's not overwriting) -> default behavior
# TODO: hide "add new xyz" from view default because uses up lots of space which you have to scroll down
# DONE: update file-year-field whenever paper-year-field gets changed, and once at document load
# DONE: save default name of file, if user doesn't enter anything into the field.
# (default name is entered, if deleted, then still none saved)
# DONE: if no doi: display help -> current no_doi_[number] - currently only [number] is displayed
# DONE add logout in navbar
# DONE: add field for experiment design
# TODO: do something about performance
# TODO: make papers appear sorted alphabetically (in the long run)
# DONE: distinguish current page (at the bottom of table) visibly (maybe underline)
# DONE: add padding to heading
# DONE: make link field larger
# DONE: uniqueness-check before adding first attempting paper-save

# This View displays all current database entries in a table format
class ViewData(View):
    def get(self, request):
        # how to form queryset into list: https://stackoverflow.com/questions/7811556/how-do-i-convert-a-django-queryset-into-list-of-dicts
        all_papers = Papers.objects.order_by('-creation_timestamp')
        paper_list = []
        for paper in all_papers:
            paper_data = get_dict_of_all_data_on_one_paper(paper.pk)
            paper_list.append(paper_data)

        columns = get_list_of_included_columns()
        table = PaperTable(paper_list)
        RequestConfig(request).configure(table)
        context_dict = {"papers": paper_list, "included_columns": columns, 'table': table}
        return render(request, "LM_DB/ViewData.html", context_dict)


# This view deals with user actions for a single paper, that concern issues where several users interact
# need for discussion can be set and paper a different user entered can be verifiedpga
class UserInteraction(View):

    def post(self, request):
        request_data = request.POST
        user = get_current_auth_user(request.user)
        if request_data.get('needForDiscussion', -1) != -1:
            paper_id = request_data["paper_id"]
            current_paper = get_current_paper(paper_id)
            isNeedForDiscussion = current_paper.is_need_for_discussion
            if isNeedForDiscussion:
                current_paper.is_need_for_discussion = None
                messages.success(request, 'Need for discussion resolved.')
            elif isNeedForDiscussion is None:
                current_paper.is_need_for_discussion = True
                messages.success(request, 'Need for discussion saved.')
            messages.add_message(request, ANCHOR_ID, str(paper_id))
            current_paper.save()
            return redirect(request.META['HTTP_REFERER'])

        elif request_data.get('verifyPaper', -1) != -1:
            paper_id = request_data["paper_id"]
            current_paper = get_current_paper(paper_id)
            creation_user = current_paper.creation_user
            if user == creation_user:
                messages.error(request, 'The user who verifies a paper cannot be the same user who created this paper. Ask a differnt user to verify this paper.')
                messages.add_message(request, ANCHOR_ID, str(paper_id))
                return redirect(request.META['HTTP_REFERER'])
            else:
                current_paper.verified_user = user
                current_paper.verified_timestamp = get_current_time()
                current_paper.save()
                messages.success(request, 'Paper verified.')
                messages.add_message(request, ANCHOR_ID, str(paper_id))
                return redirect(request.META['HTTP_REFERER'])


# This View allows entering new data and editing data by means of forms
# To add forms to formsets dynamically:
# https://stackoverflow.com/questions/501719/dynamically-adding-a-form-to-a-django-formset-with-ajax
class EnterData(View):
    CoreAttributeFormset = formset_factory(CoreAttributeForm)
    LinkFormset = formset_factory(LinkForm)
    PurposeFormset = formset_factory(PurposeForm)
    AuthorOrderFormset = formset_factory(AuthorOrderForm)

    def get(self, request):
        paper_form = PaperForm(prefix="paper")
        file_form = FileForm(prefix="file")
        concept_name_form= ConceptNameForm(prefix="concept_name")
        purpose_formset = self.PurposeFormset(prefix="purpose")
        paper_concept_name_form = PaperConceptNameForm(prefix="new_concept_name")
        core_attribute_formset = self.CoreAttributeFormset(prefix="core_attribute")
        links_formset = self.LinkFormset(prefix="link")
        keyword_form = KeywordForm(prefix="new_keyword")
        paper_keywords_form = PaperKeywordForm(prefix="paper_keywords")
        category_form = CategoryForm(prefix="new_category")
        paper_categories_forms = PaperCategoryForm(prefix="paper_categories")
        author_order_formset = self.AuthorOrderFormset(prefix="author")

        context_dict = {"original_form_name": "newSave",
                        "type_of_edit": "New Entry"}

        context_dict = add_forms_to_context_dict(context_dict, paper=paper_form, file=file_form,
                                                 concept_name=concept_name_form, paper_concept_name=paper_concept_name_form,
                                                 purpose=purpose_formset, core_attribute=core_attribute_formset,
                                                 links=links_formset,
                                                 keyword=keyword_form, paper_keywords=paper_keywords_form,
                                                 category=category_form, paper_categories=paper_categories_forms,
                                                 author_order=author_order_formset,
                                                 )

        return render(request, "LM_DB/EnterData.html", context_dict)

    # get form data
    # src: https://stackoverflow.com/questions/2770810/multiple-models-in-a-single-django-modelform
    def post(self, request):
        request_data = request.POST
        user = get_current_auth_user(request.user)

        if request_data.get('downloadPaper', -1) != -1:
            # https://stackoverflow.com/questions/1156246/having-django-serve-downloadable-files
            current_paper_pk = request_data["paper_id"]
            file = get_file_for_paper(current_paper_pk)
            return serve_file(file, request)

        elif request_data.get('uniqueness_check', -1) != -1:
            doi = request_data.get("doi", -1)
            bibtex = request_data.get("bibtex", -1)
            cite_command = request_data.get("cite_command", -1)
            context = request_data.get("context", -1)
            paper_id = request_data.get("current_paper_id", -1)
            if paper_id != -1 and paper_id != "":
                current_paper = get_current_paper(int(paper_id))
            else:
                current_paper = None
            are_errors = uniqueness_check(doi=doi, bibtex=bibtex, cite_command=cite_command, current_paper=current_paper, context=context)
            if not are_errors.get("is_unique", False):  # if there are uniqueness errors
                error_text = ""
                for key, value in are_errors.items():
                    if key == "is_unique":
                        continue
                    else:
                        error_text += value
                response_data = {"result": "Something is not unique", "error": error_text}
                json_response = JsonResponse(response_data)
                return json_response
            else:
                response_data = {"result": "Everything unique"}
                json_response = JsonResponse(response_data)
                return json_response

        elif request_data.get('needForDiscussion', -1) != -1:
            current_paper = get_current_paper(request_data["paper_id"])
            isNeedForDiscussion = current_paper.is_need_for_discussion
            if isNeedForDiscussion:
                current_paper.is_need_for_discussion = None
                messages.success(request, 'Need for discussion resolved.')
            elif isNeedForDiscussion is None:
                current_paper.is_need_for_discussion = True
                messages.success(request, 'Need for discussion saved.')
            current_paper.save()
            return redirect(request.META['HTTP_REFERER'])

        elif request_data.get('verifyPaper', -1) != -1:
            current_paper = get_current_paper(request_data["paper_id"])
            creation_user = current_paper.creation_user
            if user == creation_user:
                messages.error(request, 'The user who verifies a paper cannot be the same user who created this paper. Ask a differnt user to verify this paper.')
                return redirect(request.META['HTTP_REFERER'])
            else:
                current_paper.verified_user = user
                current_paper.verified_timestamp = get_current_time()
                current_paper.save()
                messages.success(request, 'Paper verified.')
                return redirect(request.META['HTTP_REFERER'])

        elif request_data.get('editStart', -1) != -1:
            print("editStart")
            # pass data to the template to render the fields with data in them
            # src: https: // docs.djangoproject.com / en / dev / ref / forms / api /  # dynamic-initial-values
            current_paper_pk = request_data["paper_id"]
            all_table_data = get_dict_for_enter_data(current_paper_pk)
            paper_data = all_table_data["paper"]
            paper_form = PaperForm(prefix="paper", initial=paper_data)

            file_data = all_table_data["file"]
            file_pk = file_data.get('file_id', None)
            if file_pk is not None:
                file = Files.objects.filter(pk=file_data['file_id'])[0]
            else:
                file = None
            file_form = FileForm(prefix="file", instance=file)

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

            category_form = CategoryForm(prefix="new_category")
            paper_category_data = all_table_data["paper_category"]
            paper_categories_form = PaperCategoryForm(prefix="paper_categories", initial={
                'paper_categories': paper_category_data})

            concept_name_form = ConceptNameForm(prefix="new_concept_name")
            paper_concept_name_data = all_table_data["paper_concept_name"]
            paper_concept_names_form = PaperConceptNameForm(prefix="paper_concept_names", initial={
                'paper_concept_names': paper_concept_name_data})

            #author_form = AuthorForm(prefix="new_author")
            author_data = all_table_data["author"]
            author_order_formset = self.AuthorOrderFormset(prefix="author", initial=author_data)

            context_dict = {"original_form_name": "editSave", "type_of_edit": "Edit Entry"}
            context_dict = add_forms_to_context_dict(context_dict, paper=paper_form, file=file_form,
                                                     concept_name=concept_name_form,
                                                     paper_concept_name=paper_concept_names_form,
                                                     purpose=purpose_formset, core_attribute=core_attribute_formset,
                                                     links=link_formset,
                                                     keyword=keyword_form, paper_keywords=paper_keywords_form,
                                                     category=category_form, paper_categories=paper_categories_form,
                                                     author_order=author_order_formset,
                                                     )
            return render(request, "LM_DB/EnterData.html", context_dict)

        elif request_data.get('editSave_viewData', -1) != -1 or request_data.get('editSave_enterData',-1) != -1:
            print("editSave")

            # get corresponding data-object(s) from DB, make changes to it and save changes
            # src: https://docs.djangoproject.com/en/2.1/ref/forms/api/#checking-which-form-data-has-changed
            current_paper_pk = request_data["paper-paper_id"]
            all_table_data = get_dict_for_enter_data(current_paper_pk)
            paper_data = all_table_data["paper"]
            paper_form = PaperForm(request_data, prefix="paper", initial=paper_data)

            file_data = all_table_data["file"]
            file_pk = file_data.get('file_id', None)
            if file_pk is not None:
                file = Files.objects.filter(pk=file_data['file_id'])[0]
            else:
                file = None
            file_form = FileForm(request_data, request.FILES, prefix="file", instance=file)

            purpose_data = all_table_data["purpose"]
            purpose_formset = self.PurposeFormset(request_data, prefix="purpose", initial=purpose_data)

            link_data = all_table_data["link"]
            link_formset = self.LinkFormset(request_data, prefix="link", initial=link_data)

            core_attribute_data = all_table_data["core_attribute"]
            core_attribute_formset = self.CoreAttributeFormset(request_data, prefix="core_attribute", initial=core_attribute_data)

            paper_keyword_data = all_table_data["paper_keyword"]
            paper_keywords_form = PaperKeywordForm(request_data, prefix="paper_keywords", initial={
                'paper_keywords': paper_keyword_data})

            paper_category_data = all_table_data["paper_category"]
            paper_categories_form = PaperCategoryForm(request_data, prefix="paper_categories",
                                                    initial={'paper_categories': paper_category_data})

            paper_concept_name_data = all_table_data["paper_concept_name"]
            paper_concept_names_form = PaperConceptNameForm(request_data, prefix="paper_concept_names",
                                                           initial={'paper_concept_names': paper_concept_name_data})

            keyword_form = KeywordForm(prefix="new_keyword")
            category_form = CategoryForm(prefix="new_category")
            concept_name_form = ConceptNameForm(prefix="new_concept_name")

            author_order_data = all_table_data["author"]
            author_order_formset = self.AuthorOrderFormset(request_data, prefix="author", initial=author_order_data)


            if paper_form.has_changed() or file_form.has_changed() or link_formset.has_changed() or\
                    core_attribute_formset.has_changed() or paper_keywords_form.has_changed() or \
                    purpose_formset.has_changed() or paper_categories_form.has_changed() or \
                    paper_concept_names_form.has_changed() or author_order_formset.has_changed():
                # add other forms into this if-clause with or later
                if paper_form.is_valid() and file_form.is_valid() and link_formset.is_valid() and \
                        core_attribute_formset.is_valid() and paper_keywords_form.is_valid() and \
                        purpose_formset.is_valid() and paper_categories_form.is_valid() and \
                        paper_concept_names_form.is_valid() and author_order_formset.is_valid():
                    print("everything valid")
                    current_paper = get_current_paper(current_paper_pk)
                    update_last_edit(current_paper, user)
                    if paper_form.has_changed():
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
                                    current_paper.title = convert_empty_string_to_none(data.get('title', None))
                                elif entry == "abstract":
                                    current_paper.abstract = convert_empty_string_to_none(data.get('abstract', None))
                                elif entry == "authors":
                                    current_paper.authors = convert_empty_string_to_none(data.get('authors', None))
                                elif entry == "year":
                                    current_paper.year = data.get('year', None)
                                elif entry == "experiment_design":
                                    current_paper.experiment_design = convert_empty_string_to_none(data.get('experiment_design', None))

                            are_errors = uniqueness_check(bibtex=current_paper.bibtex, doi=current_paper.doi,
                                                              cite_command=current_paper.cite_command,
                                                              context=CONTEXT_EDIT, current_paper=current_paper)
                            if not are_errors.get("is_unique", False):  # if there are uniqueness errors
                                context_dict = {"original_form_name": "editSave", "type_of_edit": "Edit Entry",
                                                "uniqueness_errors": are_errors}
                                context_dict = add_forms_to_context_dict(context_dict, paper=paper_form,
                                                                         file=file_form,
                                                                         concept_name=concept_name_form,
                                                                         paper_concept_name=paper_concept_names_form,
                                                                         purpose=purpose_formset,
                                                                         core_attribute=core_attribute_formset,
                                                                         links=link_formset,
                                                                         keyword=keyword_form,
                                                                         paper_keywords=paper_keywords_form,
                                                                         category=category_form,
                                                                         paper_categories=paper_categories_form,
                                                                         author_order=author_order_formset,
                                                                         )

                                return render(request, "LM_DB/enterData.html", context_dict)
                            else:
                                current_paper.save()
                        else:
                            print("error display should be managed in outside else-clause.")
                            # error display is managed in outside else-clause, all have to be valid to get here
                            pass
                    if file_form.has_changed():
                        data = file_form.cleaned_data
                        if data['complete_file_path'] == False:
                            print("delete file")
                            current_file = Files.objects.get(file_id=data['file_id'], ref_file_to_paper=current_paper_pk)
                            current_file.delete()
                        else:
                            data = file_form.cleaned_data
                            if data.get('file_id', None) is not None:#changing old file
                                current_file = Files.objects.get(file_id=data['file_id'])
                                for entry in file_form.changed_data:
                                    if entry == "year":
                                        current_file.year = convert_empty_string_to_none(data['year'])
                                    elif entry == "file_name":
                                        current_file.file_name = convert_empty_string_to_none(data['file_name'])
                                    elif entry == "complete_file_path":
                                        current_file.complete_file_path = request.FILES["file-complete_file_path"]
                                current_file.save()
                            else:# new file
                                file_name = convert_empty_string_to_none(data.get('file_name', None))
                                file = request.FILES.get("file-complete_file_path", False)
                                if file != False:
                                    if file_name is None:
                                        file_name = file.name
                                    year = data["year"]
                                    current_file = Files(file_name=file_name, complete_file_path=file, year=year,
                                                         ref_file_to_paper_id=current_paper_pk)
                                    current_file.save()
                        pass
                    if author_order_formset.has_changed():
                        print("author changed")
                        if author_order_formset.is_valid():
                            print("author order formset valid")
                            for author_form in author_order_formset.forms:
                                if author_form.is_valid():
                                    print("author form valid")
                                    data = author_form.cleaned_data
                                    if data.get("paper_author_id", None) is not None:
                                        current_paper_author_id = data["paper_author_id"]
                                        current_paper_author = PaperAuthor.objects.get(paper_author_id=current_paper_author_id)
                                        is_to_be_deleted = False
                                        for entry in author_form.changed_data:
                                            if entry == "delete_this_author":
                                                is_to_be_deleted = data["delete_this_author"]
                                            elif entry == "author_order_on_paper":
                                                current_paper_author.author_order_on_paper = data["author_order_on_paper"]
                                            elif entry == "first_name" or entry == "last_name":
                                                current_paper_author = save_authors_information(data, current_paper_author, current_paper)
                                        if is_to_be_deleted:
                                            current_paper_author.delete()
                                            print("paper_author deleted")
                                        else:
                                            current_paper_author.save()
                                            print("paper_author saved")
                                    else:
                                        # what happens, when adding a new paper_author
                                        print("new paper_author")
                                        if data.get("delete_this_author", "none") == False:
                                            current_paper_author = save_authors_information(data, None, current_paper)
                                            current_paper_author.save()
                                            print("paper author saved")
                                        else:
                                            print("paper author not saved")

                    if purpose_formset.has_changed():
                        print("purpose changed")
                        if purpose_formset.is_valid():
                            print("purpose formset valid")
                            for purpose_form in purpose_formset.forms:
                                if purpose_form.is_valid():
                                    print("purpose form valid")
                                    data = purpose_form.cleaned_data
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
                                            print("link deleted")
                                        else:
                                            current_link.save()
                                        print("link saved")
                                    else:
                                        #handles cases, when there's no link-id yet (= new links)
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
                    if core_attribute_formset.has_changed():
                        if core_attribute_formset.is_valid():
                            current_paper = get_current_paper(current_paper_pk)
                            for core_attribute_form in core_attribute_formset:
                                if core_attribute_form.is_valid():
                                    data = core_attribute_form.cleaned_data
                                    if data.get("core_attribute_id", None) is not None:
                                        current_core_attribute_id = data["core_attribute_id"]
                                        current_core_attribute = CoreAttributes.objects.get(core_attribute_id= current_core_attribute_id)
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
                                        #handles cases in which id was not given yet (= new core attributes)
                                        if data.get("delete_this_core_attribute", "None") == False:
                                            core_attribute = convert_empty_string_to_none(data.get("core_attribute", None))
                                            is_literal_quotation = data.get("is_literal_quotation", None)
                                            page_num = convert_empty_string_to_none(data.get("page_num", None))
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
                            keywords_before = Keywords.objects.filter(paperkeyword__ref_paper_keyword_to_paper=current_paper_pk)
                            keywords_after = paper_keywords_form.cleaned_data['paper_keywords']
                            for keyword in keywords_after:
                                if keyword not in keywords_before:
                                    # in after, not before
                                    # add relation to paper_keywords relation
                                    keyword_id = keyword.keyword_id
                                    PaperKeyword.objects.create(ref_paper_keyword_to_keyword_id =keyword_id, ref_paper_keyword_to_paper_id=current_paper_pk)
                            for keyword in keywords_before:
                                if keyword not in keywords_after:
                                    # in before, now not anymore
                                    # delete appropriate entry in paper_keywords
                                    keyword_id = keyword.keyword_id
                                    PaperKeyword.objects.get(ref_paper_keyword_to_keyword_id=keyword_id, ref_paper_keyword_to_paper_id=current_paper_pk).delete()

                            print("valid cleaned paper keywords")
                    if paper_concept_names_form.has_changed():
                        print("paper concept names changed")
                        if paper_concept_names_form.is_valid():

                            concept_names_before = ConceptNames.objects.filter(paperconceptname__ref_paper_concept_name_to_paper=current_paper_pk)
                            concept_names_after = paper_concept_names_form.cleaned_data['paper_concept_name']
                            for concept_name in concept_names_after:
                                if concept_name not in concept_names_before:
                                    # in after, not before
                                    # add relation to paper_keywords relation
                                    concept_name_id = concept_name.concept_name_id
                                    PaperConceptName.objects.create(ref_paper_concept_name_to_concept_name_id =concept_name_id,
                                                                    ref_paper_concept_name_to_paper_id=current_paper_pk)
                            for concept_name in concept_names_before:
                                if concept_name not in concept_names_after:
                                    # in before, now not anymore
                                    # delete appropriate entry in paper_keywords
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
                    print("errors")
                    error_dict = {}  # TODO check whether the errors are displayed correctly for each (is the key right)
                    if not paper_form.is_valid():
                        error_dict["paper"] = True
                    if not file_form.is_valid():
                        error_dict["file"] = True
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

                    context_dict = {"original_form_name": "editSave", "type_of_edit": "Edit Entry", "errors":error_dict}
                    context_dict = add_forms_to_context_dict(context_dict, paper=paper_form,
                                                             file=file_form,
                                                             concept_name=concept_name_form,
                                                             paper_concept_name=paper_concept_names_form,
                                                             purpose=purpose_formset,
                                                             core_attribute=core_attribute_formset,
                                                             links=link_formset,
                                                             keyword=keyword_form,
                                                             paper_keywords=paper_keywords_form,
                                                             category=category_form,
                                                             paper_categories=paper_categories_form,
                                                             author_order = author_order_formset,

                                                             )

                    return render(request, "LM_DB/enterData.html", context_dict)
            return disambiguate_submit_button(request_data)#redirect("LM_DB:viewData")

        elif request_data.get("isNewKeyword", -1) != -1:
            print("isNewKeyword")
            keyword = request_data['keyword'].lower()
            is_not_unique = Keywords.objects.filter(keyword=keyword).exists()
            if not is_not_unique:
                new_keyword = Keywords(keyword=keyword)
                new_keyword.save()
                print("keyword saved")
                response_data = {"result": "Create keyword successful!", "keyword": keyword, "keyword_id": new_keyword.pk}
            else:
                response_data = {"result": "Creating keyword not successful!", "error": "This keyword already exists."}
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
                response_data = {"result": "Creating concept name not successful!",
                                 "error": "This concept name already exists."}
            json_response = JsonResponse(response_data)
            return json_response

        elif request_data.get("isNewAuthor", -1) != -1:
            print("isNewAuthor")
            first_name = request_data["first_name"]
            last_name = request_data["last_name"]
            is_not_unique = Authors.objects.filter(first_name=first_name, last_name=last_name)
            if not is_not_unique:
                new_author = Authors(first_name=first_name, last_name=last_name)
                new_author.save()
                print("author saved")
                response_data = {"result": "Create author sucessful!", "last_name": last_name, "first_name":first_name,
                                 "author_id":new_author.pk}
            else:
                response_data = {"result": "Creating author not sucessful!", "error": "This author already exists."}
            json_response = JsonResponse(response_data)
            return json_response


        elif request_data.get("isYearFromBibtex", -1) != -1:
            json_response = get_info_from_bibtex(request_data)
            return json_response

        elif request_data.get('newSave_viewData', -1) != 1 or request_data.get('newSave_enterData', -1) != -1:
            print("newSave")
            # make new object(s) and save those to DB
            # construct forms from data here
            paper_form = PaperForm(request_data, prefix="paper")
            file_form = FileForm(request_data, request.FILES, prefix="file")
            purpose_formset = self.PurposeFormset(request_data, prefix="purpose")
            link_formset = self.LinkFormset(request_data, prefix="link")
            core_attribute_formset = self.CoreAttributeFormset(request_data, prefix="core_attribute")
            paper_keywords_form = PaperKeywordForm(request_data, prefix="paper_keywords")
            paper_categories_form = PaperCategoryForm(request_data, prefix="paper_categories")
            paper_concept_names_form = PaperConceptNameForm(request_data, prefix="paper_concept_names")
            keyword_form = KeywordForm(prefix="new_keyword")
            category_form = CategoryForm(prefix="new_category")
            concept_name_form = ConceptNameForm(prefix="new_concept_name")
            author_form = AuthorForm(prefix="new_author")
            author_order_formset = self.AuthorOrderFormset(request_data, prefix="author")
            paper_author_form = PaperAuthorForm(request_data, prefix="paper_authors")

            # check if all forms are valid, add further forms to the if-clause later
            if paper_form.is_valid() and file_form.is_valid() and link_formset.is_valid() and\
                    core_attribute_formset.is_valid() and paper_keywords_form.is_valid() and \
                    purpose_formset.is_valid and paper_categories_form.is_valid() and \
                    paper_concept_names_form.is_valid() and author_order_formset.is_valid:
                # save data from the forms here
                if paper_form.is_valid():
                    data = paper_form.cleaned_data
                    doi = data['doi']
                    bibtex = convert_empty_string_to_none(data.get('bibtex', None))
                    cite_command = convert_empty_string_to_none(data.get('cite_command', None))
                    title = convert_empty_string_to_none(data.get('title', None))
                    abstract = convert_empty_string_to_none(data.get('abstract', None))
                    authors = convert_empty_string_to_none(data.get('authors', None))
                    year = data.get('year', None)
                    experiment_design = convert_empty_string_to_none(data.get('experiment_design', None))

                    are_errors = uniqueness_check(bibtex=bibtex, doi=doi, cite_command=cite_command,
                                                  context=CONTEXT_NEW_SAVE, current_paper=None)
                    if not are_errors.get("is_unique", False):

                        context_dict = {"original_form_name": "newSave", "type_of_edit": "New Entry",
                                        "uniqueness_errors": are_errors}
                        context_dict = add_forms_to_context_dict(context_dict, paper=paper_form,
                                                                 file=file_form,
                                                                 concept_name=concept_name_form,
                                                                 paper_concept_name=paper_concept_names_form,
                                                                 purpose=purpose_formset,
                                                                 core_attribute=core_attribute_formset,
                                                                 links=link_formset,
                                                                 keyword=keyword_form,
                                                                 paper_keywords=paper_keywords_form,
                                                                 category=category_form,
                                                                 paper_categories=paper_categories_form,

                                                                 author_order=author_order_formset,

                                                                 )

                        return render(request, "LM_DB/enterData.html", context_dict)

                    current_paper = Papers(doi=doi, bibtex=bibtex, cite_command=cite_command, title=title,
                                           abstract=abstract, authors=authors, year=year,
                                           experiment_design=experiment_design)
                    set_creation_meta_data(current_paper, user)
                    current_paper.save()

                    if file_form.is_valid():
                        data = file_form.cleaned_data
                        file_name = convert_empty_string_to_none(data.get('file_name', None))
                        file = request.FILES.get("file-complete_file_path", None)
                        if file is not None:
                            # file_data = handle_uploaded_file(file, bibtex, file_name)
                            # file_name = file_data["file_name"]
                            year = data["year"]
                            current_file = Files(file_name=file_name, complete_file_path=file, year=year,
                                                 ref_file_to_paper=current_paper)
                            current_file.save()

                    if author_order_formset.is_valid():
                        for author_form in author_order_formset:
                            if author_form.is_valid():
                                data = author_form.cleaned_data
                                if data.get("delete_this_author", "None") == False:
                                    current_paper_author = save_authors_information(data, None, current_paper)
                                    current_paper_author.save()

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
                                    page_num = convert_empty_string_to_none(data.get('page_num', None))
                                    current_core_attribute = CoreAttributes(core_attribute=core_attribute,
                                                                            is_literal_quotation=is_literal_quotation,
                                                                            page_num=page_num,
                                                                            ref_core_attribute_to_paper= current_paper)
                                    current_core_attribute.save()

                    if paper_keywords_form.is_valid():
                        data = paper_keywords_form.cleaned_data
                        ref_paper = current_paper
                        for keyword in data.get("paper_keywords", None):
                            current_paper_keyword = PaperKeyword(ref_paper_keyword_to_paper=ref_paper,
                                                                 ref_paper_keyword_to_keyword=keyword)
                            current_paper_keyword.save()
                    else:
                        print("paper keywords not valid")

                    if paper_categories_form.is_valid():
                        data = paper_categories_form.cleaned_data
                        for category in data.get("paper_categories", None):
                            current_paper_category = PaperCategory(ref_paper_category_to_paper=current_paper,
                                                                   ref_paper_category_to_category=category)
                            current_paper_category.save()
                    else:
                        print("paper categories not valid")

                    # paper form is not valid
                    print("paper form not valid")

                return disambiguate_submit_button(request_data)
            else:
                context_dict = {"original_form_name": "newSave", "type_of_edit": "New Entry",
                                }
                context_dict = add_forms_to_context_dict(context_dict, paper=paper_form,
                                                         file=file_form,
                                                         concept_name=concept_name_form,
                                                         paper_concept_name=paper_concept_names_form,
                                                         purpose=purpose_formset,
                                                         core_attribute=core_attribute_formset,
                                                         links=link_formset,
                                                         keyword=keyword_form,
                                                         paper_keywords=paper_keywords_form,
                                                         category=category_form,
                                                         paper_categories=paper_categories_form,
                                                         author_order=author_order_formset,
                                                         )

                return render(request, "LM_DB/enterData.html", context_dict)
                # Done: error handling

        else:
            print("default")
            pass


# This method is necessary because django gets the value of empty text fields as '' and not as None, but we want null
# for all empty fields in the DB, so you can check: How many papers do not have a saved bibTex or similar queries
# Pass all data-gets for text fields to this method, so that their empty values are converted to None
def convert_empty_string_to_none(a_string):
    if a_string in [None, '']:
        return None
    else:
        return a_string


def add_forms_to_context_dict(context_dict, paper, file, concept_name, paper_concept_name, core_attribute,
                             links, paper_keywords, paper_categories, purpose, keyword, category,
                              author_order):
    context_dict["paper_form"] = paper
    context_dict["file_form"] = file
    context_dict["concept_name_form"] = concept_name
    context_dict["paper_concept_names_form"] = paper_concept_name
    context_dict["core_attribute_forms"] = core_attribute
    context_dict["link_forms"] = links
    context_dict["keyword_form"] = keyword
    context_dict["paper_keywords_form"] = paper_keywords
    context_dict["category_form"] = category
    context_dict["paper_categories_form"] = paper_categories
    context_dict["purpose_forms"] = purpose
    context_dict["author_order_forms"] = author_order
    return context_dict


# the attributes of user who performed the last edit on data related to a paper and time of the edit are updated
# to current user and time
def update_last_edit(current_paper, current_user):
    current_date_time = get_current_time()

    current_paper.last_edit_user = current_user
    current_paper.last_edit_timestamp = current_date_time
    current_paper.save() # TODO check if this is necessary and can't just return current_paper


def set_creation_meta_data(current_paper, current_user):

    current_date_time = get_current_time()

    current_paper.creation_user = current_user
    current_paper.creation_timestamp = current_date_time

    # maybe calling the method again is a bit slower than
    update_last_edit(current_paper, current_user)


def get_current_auth_user(current_user):
    return AuthUser.objects.get(id=current_user.id)


# tries to extract stuff from a given bibtex and returns a json response
def get_info_from_bibtex(request_data):
    print("new file upload - bibtex processing")
    bibtex_str = request_data['bibtex']
    if bibtex_str is None or bibtex_str == "":
        year = "unknown_year"
        title = ""
        cite_command = ""
        authors = ""
        keywords = ""
        doi = ""
        abstract = ""

        error = "No bibtex is present."
        response_data = {"result": " ", "year": "", "year_for_file": year, "title": title, "cite_command": cite_command, "author": authors,
                         "doi": doi, "keywords": keywords, "abstract": abstract, "error": error}
    else:
        context = request_data.get("context", -1)
        response_data = called_by_bibtex_upload(bibtex_str, context)
    json_response = JsonResponse(response_data)
    return json_response


# extracts stuff from bibtex
def called_by_bibtex_upload(bibtex_str, context):
    error = ""
    title = ""
    cite_command = ""
    year = ""
    authors = ""
    keywords = ""
    doi = ""
    year_for_file = ""
    abstract = ""
    is_bibtex_correct = False

    try:
        bib = bibtexparser.loads(bibtex_str)
        paper = bib.entries[0]
        is_bibtex_correct = True
    except IndexError as e:
        error = "Error in bibtex: " + str(e)
        print("indexError in Bibtex: " + str(e))
    except KeyError as e:
        error = "Error in bibtex: " + str(e)
        print("keyError in Bibtex: " + str(e))
    except ParseException as e:
        error = "Error in bibtex: " + str(e)
        print ("ParseException during parsing bibtex: "+str(e))

    if is_bibtex_correct:
        try:
            title = paper['title']
        except KeyError as e:
            error += "\n Could not find title. "
            print(e)

        try:
            authors = get_authors_from_bibtex(paper['author'])
        except KeyError as e:
            error += "\n Could not find authors. "
            print(e)

        try:
            cite_command = str(paper["ID"])
        except KeyError as e:
            error += "\n Could not find cite-command. "
            print(e)

        try:
            abstract = str(paper["abstract"])
        except KeyError as e:
            error += "\n Could not find abstract. "
            print(e)

        try:
            keywords_random_case = get_keywords_list(str(paper["keywords"]))
            # for uniformity (some bibtex-files have upper, some lower)
            keywords = [keyword.lower() for keyword in keywords_random_case]

        except KeyError as e:
            error += "\n Could not find keywords. "
            print(e)

        try:
            doi = str(paper["doi"])
        except KeyError as e:
            no_doi_number = str(int(get_non_doi_number())+1)
            no_doi_help = 'no_doi_'+no_doi_number
            no_doi_text = "If there is no doi for this paper, please enter '"+no_doi_help+"'. "
            error += "\n Could not find doi. "+ no_doi_text
            doi = no_doi_help

            print(e)

        try:
            year = paper["year"]
            year_for_file = str(year)
        except KeyError as e:
            if context == "file_upload":
                error = "\n Could not find year. Saving to folder 'unknown_year' instead. "
                year_for_file = "unknown_year"
            else:
                error += "\n Could not find year. "
                year_for_file = "unknown_year"
            print(e)

    response_data = {"result": "year extracted from bibtex! ", "title": title, "cite_command": cite_command,
                     "year": year, "year_for_file": year_for_file, "author": authors, "doi": doi, "keywords": keywords,
                     "abstract": abstract}
    if error != "":
        response_data["error"] = error

    return response_data


# make files available for download (are automatically saved in temp folder)
def serve_file(file, request):
    if not file:
        # handle case when file = False, that is to say the given paper doesn't have a file
        # return render_to_response('LM_DB/EnterData.html', message='This paper does not have an associated file.')
        messages.error(request, 'This paper does not have an associated file.')
        return redirect(request.META['HTTP_REFERER'])
    else:
        file_path = os.path.join(MEDIA_ROOT, str(file.complete_file_path))
        # file is saved in temporary folder. If downloaded repeatedly, it's name is counted up
        with open(file_path, 'rb') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            file_name = file.file_name
            response['Content-Disposition']= "attachment; filename={0}".format(file_name)
            return response


def get_file_for_paper(current_paper_pk):
    files = Files.objects.filter(ref_file_to_paper__paper_id=current_paper_pk)
    if len(files) > 0:
        return files[0]
    else:
        return False


# db unique-constraints don't work (none values should be possible for bibtex and cite-command), so checking myself
def uniqueness_check(bibtex, doi, cite_command, context, current_paper):
    bibtex_unique = is_bibtex_unique(bibtex, context, current_paper)
    doi_unique = is_doi_unique(doi, context, current_paper)
    cite_command_unique = is_cite_command_unique(cite_command, context, current_paper)
    context_dict = {}
    if bibtex_unique and doi_unique and cite_command_unique:
        context_dict["is_unique"] = True
    else:
        context_dict["is_unique"] = False
        if not bibtex_unique:
            context_dict["bibtex_unique"] = "Bibtex not unique. A paper with this bibtex is already in the database."
        if not cite_command_unique:
            context_dict["cite_command_unique"] = "Cite-command not unique. A paper with this cite-command is already in the database."
        if not doi_unique:
            context_dict["doi_unique"] = "Doi not unique. A paper with this doi is already in the database."

    return context_dict


def is_bibtex_unique(bibtex_str, context, current_paper):
    if bibtex_str == "" or bibtex_str is None:
        return True
    poss_other_bibtex = Papers.objects.filter(bibtex=bibtex_str)
    if context == CONTEXT_NEW_SAVE:
        return is_unique_for_new_data(poss_other_bibtex)
    else:
        return is_unique_for_edit_data(poss_other_bibtex, current_paper)


def is_doi_unique(doi_str, context, current_paper):
    if doi_str == "" or doi_str is None:
        return True
    poss_other_doi = Papers.objects.filter(doi=doi_str)
    if context == CONTEXT_NEW_SAVE:
        return is_unique_for_new_data(poss_other_doi)
    else:
        return is_unique_for_edit_data(poss_other_doi, current_paper)


def is_cite_command_unique(cite_command_str, context, current_paper):
    print("inside cite_command")
    if cite_command_str == "" or cite_command_str is None:
        return True
    poss_other_cite_command = Papers.objects.filter(cite_command=cite_command_str)
    if context == CONTEXT_NEW_SAVE:
        return is_unique_for_new_data(poss_other_cite_command)
    else:
        return is_unique_for_edit_data(poss_other_cite_command, current_paper)


def is_unique_for_edit_data(queryset, current_paper):
    if len(queryset) == 0:
        return True
    elif len(queryset) == 1:
        if queryset[0] == current_paper:
            return True
        else:
            return False
    else:
        return False


def is_unique_for_new_data(queryset):
    if len(queryset) == 0:
        return True
    else:
        return False


def get_keywords_list(keywords_from_bibtex):
    return keywords_from_bibtex.split(", ")


# gets authors info from form and if no author for that info is in db, creates a new author
# otherwise references an old one
# returns an instance of the through table, PaperAuthors, which then still needs to be saved
def save_authors_information(data, current_paper_author, current_paper):
    first_name = convert_empty_string_to_none(data.get("first_name", None))
    last_name = convert_empty_string_to_none(data.get("last_name", None))
    order = data.get("author_order_on_paper", None)

    authors = Authors.objects.filter(first_name=first_name, last_name=last_name)
    if len(authors) !=0:  # author is in database
        # if yes, change ref_paper_author_to_author
        current_author = authors[0]
        return update_current_paper_author(current_paper_author, current_author, current_paper, order)
    else:  # author is not in database
        current_author = Authors.objects.create(first_name=first_name, last_name=last_name)
        return update_current_paper_author(current_paper_author, current_author, current_paper, order)


def update_current_paper_author(current_paper_author, current_author, current_paper, order):
    if current_paper_author is not None:
        current_paper_author.ref_paper_author_to_author = current_author
    else:
        current_paper_author = PaperAuthor(ref_paper_author_to_paper=current_paper, author_order_on_paper=order,
                                       ref_paper_author_to_author=current_author)
    return current_paper_author


def get_current_time():
    current_time = datetime.now().astimezone()
    print (current_time)
    return datetime.now().astimezone()


# This method determines which submit button in enterData-view was clicked (and which view to return to)
def disambiguate_submit_button(request_data):
    relevant_keys = [key for key, value in request_data.items() if 'Save_' in key]
    relevant_key = ""
    if len(relevant_keys) != 0:
        relevant_key = relevant_keys[0]

    if "Save_enterData" in relevant_key:
        print("back to enterData")
        return redirect("LM_DB:enterData")
    elif "Save_viewData" in relevant_key:
        print("back to viewData")
        return redirect("LM_DB:viewData")
    else:
        print("else")
        return redirect("LM_DB:viewData")
