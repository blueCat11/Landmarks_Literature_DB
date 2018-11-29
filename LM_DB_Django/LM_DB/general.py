from LM_DB.models import Papers


# calculates which is the highest no_doi-value at the moment
def get_non_doi_number():
    newest_no_doi_paper = Papers.objects.filter(doi__startswith='no_doi_').order_by('-paper_id')[0]
    doi_without_prefix = newest_no_doi_paper.doi[7:]
    return doi_without_prefix