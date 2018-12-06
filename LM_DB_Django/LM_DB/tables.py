import django_tables2 as tables
from django.utils.html import format_html


class ActionColumn(tables.Column):
    def render(self, value):
        form = '<form action="/LM_DB/enterData/" method="post" class="action_form">' \
               ' <input type="hidden" name="paper_id" value="{}">' \
               '<div class="uk-margin-small">' \
               '<input class="button uk-button uk-button-primary uk-button-small" type="submit" name="editStart" value="Edit"/>' \
               '</div>' \
               '<div class="uk-margin-small">' \
               '<input class="button uk-button uk-button-primary uk-button-small" type="submit" name="downloadPaper" value="Download"/>' \
               '</div>' \
               '</form>'
        return format_html(form, value)


class ActionDiscussionColumn(tables.Column):
    def render(self, value):
        form = '<form action="/LM_DB/userInteraction/" method="post" class="action_form">' \
               ' <input type="hidden" class="user_interaction" name="paper_id" value="{}">' \
               '<div class="uk-margin-small">' \
               '<input class="button uk-button uk-button-primary uk-button-small" type="submit" name="verifyPaper" value="Verify"/>' \
               '</div>' \
               '<div class"uk-margin-small">' \
               '<input class="button uk-button uk-button-primary uk-button-small" type="submit" name="needForDiscussion" value="toggle need for discussion"/>' \
               '</div>' \
               '</form>'
        return format_html(form, value)


# displays info in table in viewData,
# commented out columns were previously displayed (also in excel file), but are not desired anymore
class PaperTable(tables.Table):
    actions = ActionColumn()
    # doi = tables.Column()
    # bibtex = tables.Column()
    cite_command = tables.Column()
    title = tables.Column()
    year = tables.Column()
    authors = tables.Column()
    abstract = tables.Column(attrs={"td": {"class": "abstract_col"}})
    is_fulltext_in_repo = tables.Column()
    experiment_design = tables.Column()
    concept_name = tables.Column()
    core_attributes = tables.Column(attrs={"td":{"class": "core_attribute_col"}})
    links = tables.Column()
    keywords = tables.Column()
    categories = tables.Column()
    purpose = tables.Column()
    creation = tables.Column()
    last_edit = tables.Column()
    verification = tables.Column()
    need_for_discussion = tables.Column()
    checking = ActionDiscussionColumn()

    class Meta:
        template_name = 'django_tables2/table.html'
        attrs = {'class': 'uk-table uk-table-striped'}


