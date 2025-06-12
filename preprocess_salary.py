import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = 'jobs_skills.db'

@st.cache_data(show_spinner=False)
def create_salary_summary():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS salary_summary")
    cursor.execute("""
        CREATE TABLE salary_summary AS
        SELECT
            job_title_short,
            CAST(strftime('%m', job_posted_date) AS INTEGER) AS month,
            COUNT(*) AS count,
            AVG(salary_year_avg) AS avg_salary,
            MAX(salary_year_avg) AS max_salary,
            MIN(salary_year_avg) AS min_salary
        FROM job_postings_fact
        WHERE salary_year_avg IS NOT NULL
        GROUP BY job_title_short, month
    """)
    conn.commit()
    conn.close()

@st.cache_data(show_spinner=False)
def load_demand_skills(job_title_short=None, job_type=None):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM demand_skill_trend"
    filters = []
    params = []

    if job_title_short:
        filters.append("job_title_short = ?")
        params.append(job_title_short)

    if job_type:
        filters.append("job_schedule_type= ?")
        params.append(job_type)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    df['job_posted_date'] = pd.to_datetime(df['job_posted_date'])
    return df
