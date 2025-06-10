import sqlite3
import pandas as pd
import streamlit as st
import os

DB_PATH = 'jobs_skills.db'

@st.cache_data(show_spinner=False)
def create_top_skills_summary():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cek tabel
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_title_skill_count'")
    exists = cursor.fetchone()

    if not exists:
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

    conditions = []
    params = []

    if job_title_short is not None:
        conditions.append("job_title_short = ?")
        params.append(job_title_short)
    if type is not None:
        conditions.append("type = ?")
        params.append(type)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"SELECT * FROM job_title_skill_count {where_clause}"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

