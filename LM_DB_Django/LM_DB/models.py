# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
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


class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50, blank=True, null=True)
    shortcut = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ref_category_to_super_category = models.ForeignKey('SuperCategories', models.DO_NOTHING, db_column='ref_category_to_super_category', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categories'


class CategoriesUnused(models.Model):
    uniqueid = models.SmallIntegerField(primary_key=True)
    short = models.CharField(max_length=-1, blank=True, null=True)
    lng = models.CharField(max_length=-1, blank=True, null=True)
    descr = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categories_unused'


class ConceptNames(models.Model):
    concept_name_id = models.AutoField(primary_key=True)
    concept_name = models.TextField(blank=True, null=True)
    ref_concept_name_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_concept_name_to_paper', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'concept_names'


class CoreAttributes(models.Model):
    core_attribute_id = models.AutoField(primary_key=True)
    core_attribute = models.TextField(blank=True, null=True)
    is_literal_quotation = models.NullBooleanField()
    page_num = models.IntegerField(blank=True, null=True)
    ref_core_attribute_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_core_attribute_to_paper', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_attributes'


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


class Keywords(models.Model):
    keyword_id = models.AutoField(primary_key=True)
    keyword = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'keywords'


class Links(models.Model):
    link_id = models.AutoField(primary_key=True)
    link_text = models.TextField(blank=True, null=True)
    is_local_link = models.NullBooleanField()
    ref_link_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_link_to_paper', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'links'


class PaperCategory(models.Model):
    paper_category_id = models.AutoField(primary_key=True)
    ref_paper_category_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_paper_category_to_paper', blank=True, null=True)
    ref_paper_category_to_category = models.ForeignKey(Categories, models.DO_NOTHING, db_column='ref_paper_category_to_category', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'paper_category'


class PaperKeyword(models.Model):
    paper_keyword_id = models.AutoField(primary_key=True)
    ref_paper_keyword_to_paper = models.ForeignKey('Papers', models.DO_NOTHING, db_column='ref_paper_keyword_to_paper', blank=True, null=True)
    ref_paper_keyword_to_keyword = models.ForeignKey(Keywords, models.DO_NOTHING, db_column='ref_paper_keyword_to_keyword', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'paper_keyword'


class Papers(models.Model):
    paper_id = models.AutoField(primary_key=True)
    doi = models.CharField(max_length=50, blank=True, null=True)
    bibtex = models.TextField(blank=True, null=True)
    cite_command = models.CharField(max_length=50, blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    is_fulltext_in_repo = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'papers'


class SuperCategories(models.Model):
    super_category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'super_categories'
