import sqlite3
import pandas as pd
import streamlit as st
import os

DB_PATH = 'jobs_skills.db'

@st.cache_data(show_spinner=False)
def create_top_skills_summary():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("Database not found, please setup DB first.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS job_title_skill_count")
    cursor.execute("""
        CREATE TABLE job_title_skill_count AS
        SELECT 
            j.job_title_short,
            s.skills,
            j.job_title,
            s.type,
            COUNT(*) AS count
        FROM skills_job_dim sj
        JOIN skills_dim s ON sj.skill_id = s.skill_id
        JOIN job_postings_fact j ON sj.job_id = j.job_id
        GROUP BY j.job_title_short, s.skills, j.job_title, s.type
    """)

    conn.commit()
    conn.close()

@st.cache_data
def load_top_skills_summary(job_title_short=None, type=None):
    conn = sqlite3.connect(DB_PATH)
    
    if job_title_short is None and type is None:
        query = "SELECT * FROM job_title_skill_count"
        df = pd.read_sql_query(query, conn)

    elif job_title_short is not None and type is None:
        query = "SELECT * FROM job_title_skill_count WHERE job_title_short = ?"
        df = pd.read_sql_query(query, conn, params=(job_title_short,))

    elif job_title_short is None and type is not None:
        query = "SELECT * FROM job_title_skill_count WHERE type = ?"
        df = pd.read_sql_query(query, conn, params=(type,))

    else:  # both job_title_short and type are provided
        query = "SELECT * FROM job_title_skill_count WHERE job_title_short = ? AND type = ?"
        df = pd.read_sql_query(query, conn, params=(job_title_short, type))
    
    conn.close()
    return df

