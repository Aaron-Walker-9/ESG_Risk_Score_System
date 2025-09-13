import re
import os
from pathlib import Path
from fetchers.pdf_parser import url_to_pdf

def check_or_parse(company_url_list):
    for file_url in company_url_list:
        match = re.search(r'/([^/]+)\.pdf$', file_url)
        if match:
            file_name = match.group(1)+ ".pdf"
            filepath = Path("data")/file_name
            
            if filepath.exists():
                print(f"File found: {file_name}")
            else:
                print(f"No file found for: {file_name}")
                print("Parsing new file to database..")
                url_to_pdf([file_url])
                
        else:
            print(f"No url match for: {file_url}")
    