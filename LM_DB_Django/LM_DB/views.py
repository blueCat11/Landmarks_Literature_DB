from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

#This View displays all current database entries in a table format
from LM_DB.forms import PaperForm
from LM_DB.models import Papers


class ViewData(View):
    def get(self, request):
        # https://stackoverflow.com/questions/3319632/join-tables-with-django
        # join data here, so all the info about one paper is in one "row", e.g. categories stringified, and concatenated with commas between them
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

#This View allows entering new data and editing data by means of forms
class EnterData(View):
    def get(self, request):
        paper_form = PaperForm(prefix="paper")
        # get more forms here, multiple model form in one form template, use prefixes
        # save info for template (like forms etc) to contextDict

        context_dict = {"original_form_name": "newSave",
                        "type_of_edit": "New Entry", "paper_form": paper_form}

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
            context_dict = {"original_form_name": "editSave", "paper_form": paper_form}
            return render(request, "LM_DB/EnterData.html", context_dict)
        elif request_data.get('editSave', -1)!=-1:
            print("editSave")
            # TODO: get corresponding data-object(s) from DB, make changes to it and save changes
            # TODO: Test the code below!
            # src: https://docs.djangoproject.com/en/2.1/ref/forms/api/#checking-which-form-data-has-changed
            current_paper_pk = request_data["paper-paper_id"]
            all_table_data = get_dict_for_enter_data(current_paper_pk)
            paper_data = all_table_data["paper"]
            paper_form = PaperForm(request_data, prefix="paper", initial=paper_data)
            if paper_form.has_changed(): # add other forms into this if-clause with or later
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
                        # TODO: save errors in a context_dict and pass that back to EnterData-View
                        pass

            return redirect("LM_DB:viewData")

        elif request_data.get('newSave', -1)!= 1:
            print("newSave")
            # make new object(s) and save those to DB
            # construct forms from data here
            paper_form = PaperForm(request_data, prefix="paper")

            #check if all forms are valid, add further forms to the if-clause later
            if paper_form.is_valid():
                # save data from the forms here
                if paper_form.is_valid():
                    data = paper_form.cleaned_data
                    print(data)
                    doi = data['doi']
                    bibtex = convert_empty_string_to_none(data.get('bibtex', None))
                    cite_command = convert_empty_string_to_none(data.get('cite_command', None))
                    title = convert_empty_string_to_none(data.get('title', None))
                    abstract = convert_empty_string_to_none(data.get('abstract', None))
                    is_in_repo = data['is_fulltext_in_repo']
                    current_paper = Papers(doi=doi, bibtex=bibtex, cite_command=cite_command, title=title,
                                           abstract=abstract, is_fulltext_in_repo=is_in_repo)
                    current_paper.save()

                return redirect("LM_DB:viewData")
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
def get_dict_for_enter_data(current_paper_pk):
    paper = Papers.objects.filter(pk=current_paper_pk)
    all_table_data = {}
    paper_data = paper.values()[0]
    all_table_data["paper"]= paper_data

    # paper_data = {"pk":paper.pk, "doi":paper.doi, "bibtex":paper.bibtex, "cite_command":paper.cite_command, "title":paper.title, "abstract":paper.abstract}
    return all_table_data
    # as long as there are no relations connected to paper:


# This method returns all information on one paper in form of a dictionary, to be used for display in EnterData-View
# information for different forms is stored in different dictionaries
def get_dict_of_all_data_on_one_paper(current_paper_pk):
    paper = Papers.objects.filter(pk=current_paper_pk)
    paper_data = paper.values()[0]
    # TODO: with other tables being displayed in relation, this dictionary needs to be updated
    # paper_data = {"paper_id":paper.pk, "doi":paper.doi, "bibtex":paper.bibtex, "cite_command":paper.cite_command,
    # "title":paper.title, "abstract":paper.abstract}
    return paper_data


# This method gets a list of the columns which should be displayed in ViewData-View,
# currently they are generated hard-coded :(
def get_list_of_included_columns():
    # first column empty because in table, the edit button should not have a heading
    included_columns = ["", "pk", "doi", "bibtex", "cite_command", "title", "abstract"]
    return included_columns


# Gets the paper which is being currently edited
def get_current_paper(pk):
    return Papers.objects.get(pk=pk)
