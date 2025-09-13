#ETL code for EGR Risk Model
import urllib.request
from pathlib import Path
import re

def url_to_pdf(company_url_list):
    """Extracts company reports from .PDF and saves to data folder
    Args:
        company_url_list (list): list of URLs to company reports
    """
    data_folder = Path("data")
    data_folder.mkdir(exist_ok=True)  # ensure folder exists

    for company_url in company_url_list:
        match = re.search(r'/([^/]+)\.pdf$', company_url)
        if match:
            file_name = match.group(1) + ".pdf"
            filepath = data_folder / file_name

            if filepath.exists():
                print(f"File already exists: {file_name}")
            else:
                print(f"Downloading: {file_name} ...")
                urllib.request.urlretrieve(company_url, filepath)
        else:
            print(f"No PDF match found in URL: {company_url}")