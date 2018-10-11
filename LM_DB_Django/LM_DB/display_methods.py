from LM_DB.models import *

# This file contains methods used to get data in a form suited for handling in the templates


# This method returns all information on one paper in form of a dictionary, to be used for display in EnterData-View
# information for different forms is stored in different dictionaries
# some contain more than one object e.g. core attributes
def get_dict_for_enter_data(current_paper_pk):
    paper = Papers.objects.filter(pk=current_paper_pk)
    all_table_data = {}
    paper_data = paper.values()[0]
    all_table_data["paper"] = paper_data

    current_file = Files.objects.filter(ref_file_to_paper=current_paper_pk)
    print(len(current_file))
    if len(current_file) > 0:
        file_data = current_file.values()[0]
    else:
        file_data = {}
    print("file data in method: ")
    print(file_data)
    all_table_data["file"] = file_data  # TODO: possibly add possibility to delete files

    current_concept_name = ConceptNames.objects.filter(paperconceptname__ref_paper_concept_name_to_paper=current_paper_pk)
    concept_name_data = current_concept_name.values_list('concept_name_id', flat=True)
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

    current_paper_keywords = Keywords.objects.filter(paperkeyword__ref_paper_keyword_to_paper=current_paper_pk)
    paper_keywords_data = current_paper_keywords.values_list('keyword_id', flat=True)
    all_table_data["paper_keyword"] = paper_keywords_data

    current_paper_categories = Categories.objects.filter(papercategory__ref_paper_category_to_paper=current_paper_pk)
    paper_categories_data = current_paper_categories.values_list('category_id', flat=True)
    all_table_data["paper_category"] = paper_categories_data

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
    paper_data = paper.values()[0]

    current_files = Files.objects.filter(ref_file_to_paper=current_paper_pk)
    file_data = ''
    if len(current_files) < 1:
        file_data += "False"
    else:
        for file in current_files:
            file_data += str(file)
    paper_data["is_fulltext_in_repo"] = file_data

    current_concept_name = ConceptNames.objects.filter(paperconceptname__ref_paper_concept_name_to_paper=current_paper_pk)
    concept_name_data = ''
    for concept_name in current_concept_name:
        concept_name_data += str(concept_name)+", "
    paper_data["concept_name"] = concept_name_data

    current_core_attributes = CoreAttributes.objects.filter(ref_core_attribute_to_paper=current_paper_pk)
    core_attributes_data = ''
    for core_attribute in current_core_attributes:
        core_attributes_data += str(core_attribute) + "; "
    paper_data['core_attributes'] = core_attributes_data

    current_links = Links.objects.filter(ref_link_to_paper=current_paper_pk)
    links_data = ''
    for link in current_links:
        links_data += str(link) + "; "
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
        categories_data += str(category) + ";"
    paper_data['categories'] = categories_data

    current_purposes = Purposes.objects.filter(ref_purpose_to_paper=current_paper_pk)
    purposes_data = ''
    for purpose in current_purposes:
        purposes_data += str(purpose) + "; "
    paper_data['purpose'] = purposes_data

    # old version:
    # paper_data = {"paper_id":paper.pk, "doi":paper.doi, "bibtex":paper.bibtex, "cite_command":paper.cite_command,
    # "title":paper.title, "abstract":paper.abstract}
    return paper_data


# This method gets a list of the columns which should be displayed in ViewData-View,
# currently they are generated hard-coded :(
def get_list_of_included_columns():
    # first column empty because in table, the edit button should not have a heading
    included_columns = ["", "pk", "doi", "bibtex", "cite_command", "title", "abstract", "is_fulltext_in_repo",
                        "concept_name", "core_attributes", "links", "keywords", "categories", "purpose"]
    return included_columns


# Gets the paper which is being currently edited
def get_current_paper(pk):
    return Papers.objects.get(pk=pk)
