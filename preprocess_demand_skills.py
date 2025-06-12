import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "jobs_skills.db"

@st.cache_data(show_spinner=False)
def create_demand_skill_summary():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS demand_skill_trend")
    cursor.execute("""
        CREATE TABLE demand_skill_trend AS
        SELECT
            j.job_id,
            j.job_title,
            j.job_title_short,
            j.job_posted_date,
            s.skills
        FROM skills_job_dim sj
        JOIN job_postings_fact j ON sj.job_id = j.job_id
        JOIN skills_dim s ON sj.skill_id = s.skill_id
        WHERE s.skills IS NOT NULL
    """)
    conn.commit()
    conn.close()


@st.cache_data(show_spinner=False)
def load_demand_skills(job_title_short=None, job_type=None):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT * FROM TABLE demand_skill_trend
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

