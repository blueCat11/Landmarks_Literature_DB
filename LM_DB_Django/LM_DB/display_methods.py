from LM_DB.models import *


# This file contains methods used to get data in a form suited for handling in the templates


# This method returns all information on one paper in form of a dictionary, to be used for display in EnterData-View
# information for different forms is stored in different dictionaries
# some contain more than one object e.g. core attributes
def get_dict_for_enter_data(current_paper_pk):
    paper = Papers.objects.filter(pk=current_paper_pk)
    all_table_data = {}
    paper_data = paper.values()[0]
    paper_data["don_t_overwrite"] = True
    all_table_data["paper"] = paper_data

    current_file = Files.objects.filter(ref_file_to_paper=current_paper_pk)
    if len(current_file) > 0:
        file_data = current_file.values()[0]
    else:
        file_data = {}
    all_table_data["file"] = file_data  # Done (file field inherent): possibly add possibility to delete files

    current_concept_name = ConceptNames.objects.filter(
        paperconceptname__ref_paper_concept_name_to_paper=current_paper_pk)
    concept_name_data = current_concept_name.values_list('concept_name_id', flat=True)
    print(concept_name_data)
    # priorly empty forms are automatically set to be deleted
    all_table_data["paper_concept_name"] = concept_name_data

    current_core_attributes = CoreAttributes.objects.filter(ref_core_attribute_to_paper=current_paper_pk)
    core_attributes_data = current_core_attributes.values()
    for core_attribute in core_attributes_data:
        core_attribute['delete_this_core_attribute'] = False
    all_table_data["core_attribute"] = core_attributes_data

    current_links = Links.objects.filter(ref_link_to_paper=current_paper_pk)
    links_data = current_links.values()
    for link in links_data:
        link['delete_this_link'] = False  # makes default for already there data not deleted automatically
    all_table_data["link"] = links_data
    print(links_data)

    current_paper_keywords = Keywords.objects.filter(paperkeyword__ref_paper_keyword_to_paper=current_paper_pk)
    paper_keywords_data = current_paper_keywords.values_list('keyword_id', flat=True)
    all_table_data["paper_keyword"] = paper_keywords_data

    current_paper_categories = Categories.objects.filter(papercategory__ref_paper_category_to_paper=current_paper_pk)
    paper_categories_data = current_paper_categories.values_list('category_id', flat=True)
    all_table_data["paper_category"] = paper_categories_data

    current_paper_authors_order = PaperAuthor.objects.filter(ref_paper_author_to_paper=current_paper_pk).order_by("author_order_on_paper")
    paper_authors_order_data = current_paper_authors_order.values()
    for i, paper_author in enumerate(paper_authors_order_data):
        data_object = current_paper_authors_order[i]
        author = Authors.objects.get(author_id=data_object.ref_paper_author_to_author_id)
        paper_authors_order_data[i]['first_name'] = author.first_name
        print(author.first_name)
        paper_authors_order_data[i]['last_name'] = author.last_name
        paper_authors_order_data[i]['author_id'] = author.author_id
        paper_authors_order_data[i]["delete_this_author"] = False

    all_table_data["author"] = paper_authors_order_data


    current_purposes = Purposes.objects.filter(ref_purpose_to_paper=current_paper_pk)
    purposes_data = current_purposes.values()
    for purpose in purposes_data:
        purpose['delete_this_purpose'] = False
    all_table_data["purpose"] = purposes_data

    return all_table_data


# This method returns all information on one paper in form of a dictionary, to be used in ViewData-View
# for each column per paper, the data is in String-form
def get_dict_of_all_data_on_one_paper(current_paper_pk):
    paper = Papers.objects.filter(pk=current_paper_pk)
    paper_data = get_paper_data_for_display(paper)
    current_paper = paper[0]
    paper_data["actions"] = current_paper.pk  # value is passed to Column in tables.py for form in table
    paper_data["checking"] = current_paper.pk  # value is passed to Column in tables.py for form in table
    current_files = Files.objects.filter(ref_file_to_paper=current_paper_pk)
    file_data = ''
    year = ''
    if len(current_files) < 1:
        file_data += "False"
    else:
        for file in current_files:
            file_data += str(file)
            year = file.year
    paper_data["is_fulltext_in_repo"] = file_data
    # paper_data["year"] = year

    current_concept_name = ConceptNames.objects.filter(
        paperconceptname__ref_paper_concept_name_to_paper=current_paper_pk)
    concept_name_data = ''
    for concept_name in current_concept_name:
        concept_name_data += str(concept_name) + ", "
    paper_data["concept_name"] = concept_name_data

    current_core_attributes = CoreAttributes.objects.filter(ref_core_attribute_to_paper=current_paper_pk)
    core_attributes_data = ''
    for core_attribute in current_core_attributes:
        core_attributes_data += str(core_attribute) + "; "
    paper_data['core_attributes'] = core_attributes_data

    current_links = Links.objects.filter(ref_link_to_paper=current_paper_pk)
    links_data = ''
    for link in current_links:
        links_data += str(link) + " ; "
    paper_data['links'] = links_data

    # the keywords that are linked to a paper
    current_keywords = Keywords.objects.filter(paperkeyword__ref_paper_keyword_to_paper=current_paper_pk)
    keywords_data = ''
    for keyword in current_keywords:
        keywords_data += str(keyword) + ", "
    paper_data['keywords'] = keywords_data

    # the categories that are linked to a paper
    current_categories = Categories.objects.filter(papercategory__ref_paper_category_to_paper=current_paper_pk)
    categories_data = ""
    for category in current_categories:
        categories_data += str(category) + ", "
    paper_data['categories'] = categories_data

    current_purposes = Purposes.objects.filter(ref_purpose_to_paper=current_paper_pk)
    purposes_data = ''
    for purpose in current_purposes:
        purposes_data += str(purpose) + "; "
    paper_data['purpose'] = purposes_data

    current_authors = Authors.objects.filter(paperauthor__ref_paper_author_to_paper=current_paper_pk).order_by(
        "paperauthor__author_order_on_paper")
    paper_data["authors"] = reformat_authors(current_authors)

    # get creation and edit dates per paper
    paper_data['creation'] = get_user_name_time_string(get_user_name(current_paper.creation_user),
                                                 current_paper.creation_timestamp)
    paper_data['last_edit'] = get_user_name_time_string(get_user_name(current_paper.last_edit_user),
                                              current_paper.last_edit_timestamp)
    paper_data['verification'] = get_user_name_time_string(get_user_name(current_paper.verified_user),
                                                         current_paper.verified_timestamp)
    paper_data['need_for_discussion'] = current_paper.is_need_for_discussion

    # old version:
    # paper_data = {"paper_id":paper.pk, "doi":paper.doi, "bibtex":paper.bibtex, "cite_command":paper.cite_command,
    # "title":paper.title, "abstract":paper.abstract}
    return paper_data


# This method gets a list of the columns which should be displayed in ViewData-View,
# currently they are generated hard-coded :(
# not in use anymore, see instead tables.py
def get_list_of_included_columns():
    # first column empty because in table, the edit button should not have a heading
    included_columns = ["", "pk", "doi", "bibtex", "cite_command", "title", "abstract", "is_fulltext_in_repo",
                        "concept_name", "core_attributes", "links", "keywords", "categories", "purpose",
                        "creation", "last_edit"]
    return included_columns


# Gets the paper which is being currently edited
def get_current_paper(pk):
    return Papers.objects.get(pk=pk)


# Gets username for a given user_id
def get_user_name(user):
    if user is not None:
        return AuthUser.objects.get(id=user.id).username
    else:
        return " "

# formats username and time appropriately
def get_user_name_time_string(user_name, time):
    time_str = str(time)[:-7]  # shave off milliseconds...
    if len(user_name)<2: # empty string, that is to say no user
        return None
    else:
        return "at " + time_str + ", by " + user_name


# gets only those data from a paper that should also be displayed in viewData-View
def get_paper_data_for_display(paper):
    paper_data = paper.values()[0]
    try:
        paper_data.pop("creation_timestamp")
        paper_data.pop("creation_user_id")
        paper_data.pop("last_edit_timestamp")
        paper_data.pop("last_edit_user_id")
    except KeyError:
        print("Key not found")
    return paper_data


# returns string representation of a list of authors (for more than three, first author et al)
def reformat_authors(authors):
    index = 0
    many_authors_string = ""
    authors_string = ""
    for author in authors:
        if index == 0:
            many_authors_string += str(author) + " et al."
        authors_string += str(author) + " & "
        index += 1
    authors_string = authors_string[:-2]
    if index > 2:
        return many_authors_string
    else:
        return authors_string


# TODO need to test this method
def get_authors_from_bibtex(authors):
    author_list = authors.split(" and ")
    i = 1
    author_dict_list = []
    for author in author_list:
        author_num = i
        comma_separated = author.split(",")
        print("one author: ")
        print(comma_separated)
        if len(comma_separated) == 2:
            last_name = comma_separated[0].strip()
            first_name = comma_separated[1].strip()
        else:
            first_last = author.split(" ")
            last_name = first_last[-1]
            index = 1
            first_name = ""
            for name_part in first_last:
                if index < len(first_last):
                    first_name += name_part + " "
                index += 1
        author_dict = {"first_name": first_name.strip(), "last_name":last_name, "order_on_paper":author_num}
        author_dict_list.append(author_dict)
        i += 1
    return author_dict_list
