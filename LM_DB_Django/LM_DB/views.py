from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

#This View displays all current database entries in a table format
from LM_DB.forms import PaperForm
from LM_DB.models import Papers


class ViewData(View):
    def get(self, request):
        #https://stackoverflow.com/questions/3319632/join-tables-with-django
        #join data here, so all the info about one paper is in one "row", e.g. categories stringified, and concatenated with commas between them

        all_papers = Papers.objects.all()
        paper_list = []
        for paper in all_papers:
            paper_info = get_dict_of_all_data_on_one_paper(paper)
            paper_list.append(paper_info)
            print(paper_info)
        columns = get_list_of_included_columns()
        context_dict = {"papers":paper_list, "included_columns": columns}
        return render(request, "LM_DB/ViewData.html", context_dict)

    #maybe we don't need a post here
    def post(self, request):
        pass

#This View allows entering new data and editing data by means of forms
class EnterData(View):
    def get(self, request):
        paper_form = PaperForm(prefix="paper")
        # get more forms here, multiple model form in one form template, use prefixes
        # save infos for template (like forms etc) to contextDict

        context_dict = {"original_form_name": "newSave",
                        "type_of_edit": "New Entry", "paper_form": paper_form}

        return render(request, "LM_DB/EnterData.html", context_dict)

    # get form data, see https://stackoverflow.com/questions/2770810/multiple-models-in-a-single-django-modelform
    def post(self, request):
        request_data = request.POST
        if request_data.get('editStart', -1)!=-1:
            #TODO: pass data to the template to render the fields with data in them
            context_dict = {"original_form_name": "editSave"}
            pass
        elif request_data.get('editSave', -1)!=-1:
            #TODO: get corresponding data-object(s) from DB, make changes to it and save changes
            return redirect("LM_DB:viewData")
        elif request_data.get('newSave', -1)!= 1:
            # TODO: make new object(s) and save those to DB
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
                    current_paper = Papers(doi=doi, bibtex=bibtex, cite_command=cite_command, title=title, abstract=abstract)
                    current_paper.save()


                return redirect("LM_DB:viewData")




# This method is necessary because django gets the value of empty text fields as '' and not as None, but we want null
# for all empty fields in the DB, so you can check: How many papers do not have a saved bibTex or similiar queries
# Pass all data-gets for textfields to this method, so that their empty values are converted to None
def convert_empty_string_to_none(aString):
    if aString in [None, '']:
        return None
    else:
        return aString

# This method returns all information on one paper in form of a dictionary, to be used for display in view-data-template
def get_dict_of_all_data_on_one_paper(paper):
    paper_data = {"pk":paper.pk, "doi":paper.doi, "bibtex":paper.bibtex,
                  "cite_command":paper.cite_command, "title":paper.title, "abstract":paper.abstract}
    return paper_data
    #as long as there are no relations connected to paper:


def get_list_of_included_columns():
    included_columns = ["pk", "doi", "bibtex", "cite_command", "title", "abstract"]
    return included_columns

