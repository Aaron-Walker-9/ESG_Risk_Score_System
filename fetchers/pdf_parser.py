#ETL code for EGR Risk Model
import urllib.request
import re

def url_to_pdf(company_url_list):
    """Extracts company reports from .PDF and saves to data folder
    Args:
        company_url_list (list): list of urls to company reports
    """
    for company_url in company_url_list:
        match = re.search(r'/([^/]+)\.pdf$', company_url)
        if match:
            file_name = match.group(1)
        urllib.request.urlretrieve(company_url, f"data\{file_name}.pdf")