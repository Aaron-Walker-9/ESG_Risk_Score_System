
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from main import run_pipeline, init_db
from psycopg2 import pool

desc = "API for ESG risk scoring, including company lookup, PDF submission, and model updates."

@asynccontextmanager
async def lifespan(app: FastAPI):
    #startup sequence: runs below before api begins serving requests
    # initalise a connection pool with 1-10 max connecitons
    global db_pool
    db_pool = pool.SimpleConnectionPool(
        1,10, # min and max pool connections
        host = "db",
        port = 5432,
        name = "esgdb",
        user = "esguser",
        password = "esgpassword" 
    )
    # initalise the tables using a single connection
    conn = db_pool.getconn()
    cur = conn.cursor()
    init_db(cur)
    conn.commit()
    db_pool.putconn(conn)
    print("Database initialized and tables ensured.")
    
    yield # running the app in here
    
    #shutdown sequence: close all connections in the pool
    db_pool.closeall()
    print("Database connection closed.")
    
app = FastAPI(title="ESG Risk API", description=desc, version = "2.0", lifespan=lifespan)


@app.get("/check_company") # checks company in esgdb, if exists return risk score. Else prompt adding compand
def check_company(company_name: str):
    conn = db_pool.getconn()
    cur = conn.cursor() #open connection
    try: #check comapny in esgdb
        cur.execute(
            "SELECT company_name, esg_risk_score FROM company_esg_scores WHERE company_name=%s",
            (company_name,)
        )
        result = cur.fetchone()
        
    finally:#close connection
        cur.close()
        db_pool.putconn()
    
    if result: # if result found, return scores, else return error 
        return {"company": result[0], "risk_score": result[1]}
    raise HTTPException(status_code=404, detail="Company not found. Please submit URL to company file pdf.")


@app.post("/submit_pdf") # Stores company report url in database as pending for next pipeline inference run
def submit_pdf(company_name: str, url_to_pdf: str):
    conn = db_pool.getconn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO company_pdfs (company, url, status)
            VALUES (%s, %s, %s)
            ON CONFLICT (company) DO NOTHING
            """,
            (company_name, url_to_pdf, "pending")
        )
        conn.commit()
        
    finally:
        cur.close()
        db_pool.putconn()
    return {"message": f"Stored {company_name} with URL to file. {company_name} will be analysed during the next inference cycle."}


@app.post("/update_scores") # runs risk score model using urls from companies with pending status and updates esg risk score in esgdb
def update_scores(): 
    # open connection to postgres db (esgdb)
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT company, url FROM company_pdfs WHERE status='pending'") # identify companies why have been submitted to db but not processed
        rows = cur.fetchall() #return all rows where this is true

        if not rows:
            return {"message": "No pending companies to process."}

        urls = [row[1] for row in rows] # extracts urls, row[1] = url, from esgdb where status = pending
        results = run_pipeline(urls, conn, cur) #run inference model using url link to pdf
    
        # Update the processed company rows in esgdb to status=processed
        for row in rows:
            cur.execute("UPDATE company_pdfs SET status='processed' WHERE company=%s", (row[0],))
        conn.commit()
    finally:
        cur.close()
        db_pool.putconn(conn)

    return {"message": "Pipeline executed", "results": results}