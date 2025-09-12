"""
ESG Risk:

A Real-Time ESG Risk Scoring Framework for Company Filings 

Authored in 2025 by Aaron Walker


Change log:
- 04/09/2025: added def text_to_scored_ESG_() & def ESG_risk_score()
- 11/09/25: converted code into modules & created sql database to store company risk scores

"""
print("ESG Risk: initalising...")
#Import modules
import pandas as pd
from fetchers.pdf_parser import url_to_pdf
from processors.text_cleaner import pdf_to_clean_sentences
from processors.risk_model import clean_text_to_scored_ESG_df
from processors.risk_score import calculate_risk_score

print("ESG Risk: running")
#Main: runs pdf to esg score pipeline
pdf_path = r'data/LSE_BT_2023.pdf'

 # turns pdf into clean text (sentences)
clean_text = pdf_to_clean_sentences(pdf_path) 

# scores each sentence and returns as a pd dataframe
df = clean_text_to_scored_ESG_df(clean_text) 

# calculates risk score for each sentence
df["ESG_risk_score"] = df.apply(calculate_risk_score, axis=1) 

# total risk score for report
total_esg_risk = df["ESG_risk_score"].sum() 
print("ESG risk score:", total_esg_risk)