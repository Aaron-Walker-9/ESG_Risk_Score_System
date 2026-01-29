"""
ESG Risk:

A Real-Time ESG Risk Scoring Framework for Company Filings 

Authored in 2025 by Aaron Walker


Change log:
- 04/09/2025: added def text_to_scored_ESG_() & def ESG_risk_score()
- 11/09/25: converted code into modules & created sql database to store company risk scores

"""

print("ESG Risk: initializing...")

import os
import re
import psycopg2
import urllib.request
from pathlib import Path
from processors.text_cleaner import pdf_to_clean_sentences
from processors.risk_model import clean_text_to_scored_ESG_df
from processors.risk_score import calculate_risk_score


DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "esgdb")
DB_USER = os.getenv("DB_USER", "esguser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "esgpassword")

def init_db():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()
    # Ensure tables exist, this def is used by api_main on app startup
    cur.execute("""
    CREATE TABLE IF NOT EXISTS company_esg_scores (
        id SERIAL PRIMARY KEY,
        company_name TEXT,
        company_url TEXT,
        report_year INT,
        esg_risk_score FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS company_pdfs (
        id SERIAL PRIMARY KEY,
        company TEXT UNIQUE,
        url TEXT,
        status TEXT DEFAULT 'pending',
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    return conn, cur
# ---------------- ESG Pipeline ----------------
def run_pipeline(company_url_list, conn=None, cur=None):
    """
    Runs ESG pipeline for a list of company PDF URLs.
    If conn/cur are provided, results are written to DB.
    Returns a dict of {company: risk_score}.
    """
    data_folder = Path("data")
    data_folder.mkdir(exist_ok=True)

    results = {}
    print("ESG Risk: pipeline running...")
    for file_url in company_url_list:
        match = re.search(r'/([^/]+)\.pdf$', file_url)
        if not match:
            print(f"No PDF match found in URL: {file_url}")
            continue

        file_name = match.group(1) + ".pdf"
        filepath = data_folder / file_name

        # download company pdf if not already present
        if not filepath.exists():
            print(f"Downloading {file_name} ...")
            urllib.request.urlretrieve(file_url, filepath)
        else:
            print(f"File found: {file_name}")

        # extract company + year from filename
        match_name_year = re.match(r'.*_(\w+)_(\d{4})\.pdf', file_name)
        if match_name_year:
            company_name = match_name_year.group(1)
            report_year = int(match_name_year.group(2))
        else:
            company_name = "Unknown"
            report_year = 0

        # run the ESG risk pipeline
        print(f"Processing {file_name} ...")
        clean_text = pdf_to_clean_sentences(filepath)
        df = clean_text_to_scored_ESG_df(clean_text)
        df["ESG_risk_score"] = df.apply(calculate_risk_score, axis=1)
        total_esg_risk = df["ESG_risk_score"].sum()
        print(f"{file_name} ESG risk score: {total_esg_risk}")

        results[company_name] = total_esg_risk

        # Save to DB if connection provided
        if conn and cur:
            cur.execute(
                "INSERT INTO company_esg_scores (company_name, report_year, esg_risk_score, company_url) VALUES (%s, %s, %s, %s)",
                (company_name, report_year, float(total_esg_risk), file_url)
            )

    if conn:
        conn.commit()
    print("Pipeline running complete.")
    return results



#run in terminal to view PostgreSQL database as .csv:

#docker exec -i esg_db psql -U esguser -d esgdb -c "\COPY company_esg_scores TO '/tmp/company_esg_scores.csv' CSV HEADER;"

#docker cp esg_db:/tmp/company_esg_scores.csv ./company_esg_scores.csv

#Extract from:
#https://www.responsibilityreports.com/ and

#https://www.sec.gov/edgar/search/
#https://www.sec.gov/Archives/edgar/data/2488/000000248825000012/ex19_1amdstocktradingpolic.htm

#List of company urls to process/inference
# company_url_list = [
# "https://www.responsibilityreports.com/HostedData/ResponsibilityReports/PDF/NASDAQ_AMD_2024.pdf",
# "https://www.responsibilityreports.com/HostedData/ResponsibilityReports/PDF/NYSE_MCD_2023.pdf",
# "https://www.responsibilityreports.com/HostedData/ResponsibilityReports/PDF/LSE_BT_2023.pdf",
# "https://www.responsibilityreports.com/HostedData/ResponsibilityReports/PDF/LSE_VTC_2023.pdf", # Additional companies
# "https://www.responsibilityreports.com/HostedData/ResponsibilityReports/PDF/LSE_BARC_2024.pdf",
# "https://www.responsibilityreports.com/HostedData/ResponsibilityReports/PDF/NYSE_BSAC_2024.pdf",
# "https://www.responsibilityreports.com/HostedData/ResponsibilityReports/PDF/NASDAQ_AAPL_2024.pdf",
# "https://www.responsibilityreports.com/HostedData/ResponsibilityReports/PDF/NYSE_HSBC_2024.pdf",
# "https://www.responsibilityreports.com/HostedData/ResponsibilityReports/PDF/OTC_SSDIY_2024.pdf",
# "https://www.responsibilityreports.com/HostedData/ResponsibilityReports/PDF/OTC_BAMGF_2024.pdf",
# "https://www.responsibilityreports.com/HostedData/ResponsibilityReports/PDF/OTC_MBGAF_2024.pdf"
