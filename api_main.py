"""
ESG Risk:

A Real-Time ESG Risk Scoring Framework for Company Filings 

Authored in 2025 by Aaron Walker


Change log:
- 04/09/2025: added def text_to_scored_ESG_() & def ESG_risk_score()
- 11/09/25: converted code into modules & created sql database to store company risk scores

"""
from fastapi import FastAPI, HTTPException
from main import run_pipeline, init_db

app = FastAPI(title="ESG Risk API")

# ---------------- Database Setup ----------------
DB_HOST = "db"
DB_PORT = 5432
DB_NAME = "esgdb"
DB_USER = "esguser"
DB_PASSWORD = "esgpassword"

# Global connection and cursor
conn, cur = None, None

@app.on_event("startup")
def startup_event():
    global conn, cur
    conn, cur = init_db()
    print("Database initialized and tables ensured.")


@app.on_event("shutdown")
def shutdown_event():
    global conn, cur
    if cur:
        cur.close()
    if conn:
        conn.close()
    print("Database connection closed.")


@app.get("/check_company")
def check_company(company_name: str):
    global conn, cur
    cur.execute(
        "SELECT company_name, esg_risk_score FROM company_esg_scores WHERE company_name=%s",
        (company_name,)
    )
    result = cur.fetchone()
    if result:
        return {"company": result[0], "risk_score": result[1]}
    raise HTTPException(status_code=404, detail="Company not found. Please submit URL.")


@app.post("/submit_pdf")
def submit_pdf(company_name: str, url_to_pdf: str):
    global conn, cur
    cur.execute(
        """
        INSERT INTO company_pdfs (company, url, status)
        VALUES (%s, %s, %s)
        ON CONFLICT (company) DO NOTHING
        """,
        (company_name, url_to_pdf, "pending")
    )
    conn.commit()
    return {"message": f"Stored {company_name} with PDF URL, will be analysed later."}


@app.post("/update_scores")
def update_scores():
    global conn, cur
    cur.execute("SELECT company, url FROM company_pdfs WHERE status='pending'")
    rows = cur.fetchall()

    if not rows:
        return {"message": "No pending companies to process."}

    company_url_list = [row[1] for row in rows]
    results = run_pipeline(company_url_list, conn, cur)

    # Mark as processed
    for row in rows:
        cur.execute("UPDATE company_pdfs SET status='processed' WHERE company=%s", (row[0],))
    conn.commit()

    return {"message": "Pipeline executed", "results": results}