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

@st.cache_data
def load_salary_summary(month=None):
    conn = sqlite3.connect(DB_PATH)
    if month is None:
        query = """
            SELECT * FROM salary_summary
        """
        df = pd.read_sql_query(query, conn)
    else:
        query = """
            SELECT * FROM salary_summary WHERE month = ?
        """
        df = pd.read_sql_query(query, conn, params=(month,))
    conn.close()
    st.dataframe(df)
    return df
