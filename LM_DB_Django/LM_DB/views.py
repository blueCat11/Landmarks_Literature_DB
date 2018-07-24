from django.shortcuts import render

# Create your views here.
from django.views import View

#This View displays all current database entries in a table format
class Table(View):
    def get(self, request):
        pass

    def post(self, request):
        pass

#This View allows entering new data or changing data by means of forms
class EnterData(View):
    def get(self, request):
        pass

    def post(self, request):
        pass