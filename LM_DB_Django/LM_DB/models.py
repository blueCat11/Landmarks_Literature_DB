# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import os

from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'

    def __str__(self):
        return self.username


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Authors(models.Model):
    author_id = models.AutoField(primary_key=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'authors'

    def __str__(self):
        author_string = ""
        if self.last_name is not None:
            author_string += self.last_name + ", "
        if self.first_name is not None:
            author_string += self.first_name
        if len(author_string) > 0:
            return author_string
        else:
            return "no author name given"


class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50, blank=True, null=True)
    shortcut = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ref_category_to_super_category = models.ForeignKey('SuperCategories', models.DO_NOTHING, db_column='ref_category_to_super_category', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categories'
        unique_together = (('category_name', 'shortcut'),)

    def __str__(self):
        return self.category_name


class CategoriesUnused(models.Model):
    uniqueid = models.SmallIntegerField(primary_key=True)
    short = models.CharField(max_length=10, blank=True, null=True)
    lng = models.CharField(max_length=50, blank=True, null=True)
    descr = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categories_unused'


class ConceptNames(models.Model):
    concept_name_id = models.AutoField(primary_key=True)
    concept_name = models.TextField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'concept_names'

    def __str__(self):
        return self.concept_name


class CoreAttributes(models.Model):
    core_attribute_id = models.AutoField(primary_key=True)
    core_attribute = models.TextField(blank=True, null=True)
    is_literal_quotation = models.NullBooleanField()
    ref_core_attribute_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_core_attribute_to_paper', blank=True, null=True)
    page_num = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_attributes'

    def __str__(self):
        string = ""
        if self.is_literal_quotation:
            string += '"' + str(self.core_attribute) + '"'
        else:
            string += str(self.core_attribute)
        if self.page_num is not None:
            string += ' (p. ' + str(self.page_num) + ')'
            print(self.page_num)
        return string


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


# the data in this model comes from the categories in the excel file with "e([something])"
class ExperimentDesigns(models.Model):
    experiment_design_id = models.AutoField(primary_key=True)
    ref_experiment_design_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_experiment_design_to_paper', blank=True, null=True)
    total_num_participants = models.IntegerField(blank=True, null=True)
    experiment_design = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'experiment_designs'


class Files(models.Model):

    # method from docs (strg f for files: https://docs.djangoproject.com/en/2.1/ref/models/fields/)
    def year_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        # in case user did not enter data for file_name, use default of previous name of file
        print(filename)
        if instance.file_name != "" and instance.file_name is not None:
            file_name_for_path = instance.file_name
        else:
            file_name_for_path = filename
        year = instance.year
        print(year)
        if instance.year is None or instance.year == "":
            year = "unknown_year"

        path = os.path.join(year, file_name_for_path)
        return path

    file_id = models.AutoField(primary_key=True)
    ref_file_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_file_to_paper', blank=True, null=True)
    file_name = models.CharField(max_length=50, blank=True, null=True)
    complete_file_path = models.FileField(upload_to=year_directory_path, blank=True, null=True)  # only path saved here, not filename
    year = models.CharField(max_length=12, blank=True, null=True)#DONE change widget to hidden and prepopulate from bibtex

    def filename(self):
        return os.path.basename(self.file.name)

    class Meta:
        managed = False
        db_table = 'files'

    def __str__(self):
        if self.complete_file_path is not None:
            return str(self.complete_file_path)
        else:
            return "None"


class Keywords(models.Model):
    keyword_id = models.AutoField(primary_key=True)
    keyword = models.TextField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'keywords'

    def __str__(self):
        return self.keyword


class Links(models.Model):
    link_id = models.AutoField(primary_key=True)
    link_text = models.TextField(blank=True, null=True)
    is_local_link = models.NullBooleanField()
    ref_link_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_link_to_paper', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'links'

    def __str__(self):
        string = ""
        if self.is_local_link:
            string += "local: "
        else:
            string += "web: "
        string += str(self.link_text)
        return string


class PaperAuthor(models.Model):
    paper_author_id = models.AutoField(primary_key=True)
    ref_paper_author_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_paper_author_to_paper', blank=True, null=True)
    ref_paper_author_to_author = models.ForeignKey(Authors, models.DO_NOTHING, db_column='ref_paper_author_to_author', blank=True, null=True)
    author_order_on_paper = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'paper_author'
        ordering = ('author_order_on_paper',)#TODO check if this is really solution to ordering authors according to it


class PaperCategory(models.Model):
    paper_category_id = models.AutoField(primary_key=True)
    ref_paper_category_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_paper_category_to_paper', blank=True, null=True)
    ref_paper_category_to_category = models.ForeignKey(Categories, models.DO_NOTHING, db_column='ref_paper_category_to_category', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'paper_category'


class PaperConceptName(models.Model):
    paper_concept_name_id = models.AutoField(primary_key=True)
    ref_paper_concept_name_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_paper_concept_name_to_paper', blank=True, null=True)
    ref_paper_concept_name_to_concept_name = models.ForeignKey(ConceptNames, models.DO_NOTHING, db_column='ref_paper_concept_name_to_concept_name', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'paper_concept_name'


class PaperKeyword(models.Model):
    paper_keyword_id = models.AutoField(primary_key=True)
    ref_paper_keyword_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_paper_keyword_to_paper', blank=True, null=True)
    ref_paper_keyword_to_keyword = models.ForeignKey(Keywords, models.DO_NOTHING, db_column='ref_paper_keyword_to_keyword', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'paper_keyword'


class Papers(models.Model):
    paper_id = models.AutoField(primary_key=True)
    doi = models.CharField(max_length=150, blank=True, null=True)
    bibtex = models.TextField(blank=True, null=True)
    cite_command = models.CharField(max_length=50, blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    creation_timestamp = models.DateTimeField(blank=True, null=True)
    creation_user = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='creation_user', blank=True, null=True,
                                      related_name="creation_user")
    last_edit_timestamp = models.DateTimeField(blank=True, null=True)
    last_edit_user = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='last_edit_user', blank=True, null=True,
                                       related_name="last_edit_user")
    authors = models.TextField(blank=True, null=True)
    year = models.SmallIntegerField(blank=True, null=True)
    verified_timestamp = models.DateTimeField(blank=True, null=True)
    verified_user = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='verified_user', blank=True, null=True)
    is_need_for_discussion = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'papers'


class Purposes(models.Model):
    purpose_id = models.AutoField(primary_key=True)
    purpose = models.TextField(blank=True, null=True)
    ref_purpose_to_paper = models.ForeignKey(Papers, models.DO_NOTHING, db_column='ref_purpose_to_paper', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'purposes'

    def __str__(self):
        return self.purpose


class SuperCategories(models.Model):
    super_category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'super_categories'

    def __str__(self):
        return self.name