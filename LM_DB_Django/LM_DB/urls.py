from django.contrib.auth.decorators import login_required
from django.urls import path, include, re_path

from LM_DB.views import * # Index, StartSurvey, Interests, Questionnaire, Demographics, InterestValues
from LM_DB_Django import settings
from . import views

app_name = 'LM_DB'
# name nur bei Verwendung von Links aus anderen Seiten relevant

# DONE decomment this for production, it restricts access to views
urlpatterns = [
    re_path(r'^viewData/$', login_required(ViewData.as_view()), name="viewData"),
    re_path(r'^enterData/$', login_required(EnterData.as_view()), name="enterData")

]
#urlpatterns = [  # DONE leave this commented for production
#    re_path(r'^viewData/$', ViewData.as_view(), name="viewData"),
#    re_path(r'^enterData/$', EnterData.as_view(), name="enterData")


#]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
