from django.shortcuts import render

# Create your views here.
from django.views import View

#This View displays all current database entries in a table format
class Table(View):
    def get(self, request):
        #join data here, so all the info about one paper is in one "row", e.g. categories stringified, and concatenated with commas between them
        return render(request, "ViewData.html")

    #maybe we don't need a post here
    def post(self, request):
        pass

#This View allows entering new data by means of forms
class EnterData(View):
    def get(self, request):
        #get forms here, multiple model form in one form template, use prefixes
        contextDict = {} # save infos for template (like forms etc) to contextDict
        return render(request, "EnterDataBase.html", contextDict)

    def post(self, request):
        # get form data, see https://stackoverflow.com/questions/2770810/multiple-models-in-a-single-django-modelform
       #render
        pass

#this View allows editing data by means of forms. It is called when an Edit-Button is clicked in the Table View
#TODO: Try to reuse stuff from EnterData, validating
class EditData(View):
    def post(self, request):
        # TODO:
        # check if is coming from Table or from EnterData
        # if Table prepopulate the necessary fields in the form with the values from the row, don't save anything to db yet
        # if EnterData: checck if valid, save to DB
        pass