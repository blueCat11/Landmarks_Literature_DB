import django_tables2 as tables
from django.utils.html import format_html

from .models import *



class ActionColumn(tables.Column):
    def render(self, value):
        form = '<form action="/LM_DB/enterData/" method="post" class="action_form">' \
               ' <input type="hidden" name="paper_id" value="{}">' \
               '<p uk-margin>' \
               '<input class="button uk-button uk-button-primary uk-button-small" type="submit" name="editStart" value="Edit"/>' \
               '</p>' \
               '<p uk-margin>' \
               '<input class="button uk-button uk-button-primary uk-button-small" type="submit" name="downloadPaper" value="Download"/>' \
               '</p>' \
               '</form>'
        return format_html(form, value)


class PaperTable(tables.Table):
    actions = ActionColumn()
    doi = tables.Column()
    bibtex = tables.Column()
    cite_command = tables.Column()
    title = tables.Column()
    year = tables.Column()
    authors = tables.Column()
    abstract = tables.Column()
    is_fulltext_in_repo = tables.Column()
    concept_name = tables.Column()
    core_attributes = tables.Column()
    links = tables.Column()
    keywords = tables.Column()
    categories = tables.Column()
    purpose = tables.Column()
    creation = tables.Column()
    last_edit = tables.Column()

    class Meta:
        template_name = 'django_tables2/table.html'
        attrs = {'class': 'uk-table uk-table-striped'}


