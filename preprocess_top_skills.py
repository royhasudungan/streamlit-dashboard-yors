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
def load_top_skills_summary(job_title_short=None, skill_type=None, top_n=20):
    conditions = []
    params = []

    if job_title_short:
        conditions.append("job_title_short = ?")
        params.append(job_title_short)
    if skill_type:
        conditions.append("type = ?")
        params.append(skill_type)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query_total_jobs = f"""
        SELECT COUNT(DISTINCT job_title) as total_jobs
        FROM job_title_skill_count
        {where_clause}
    """

    query_top_skills = f"""
        SELECT skills, COUNT(DISTINCT job_title) as job_count
        FROM job_title_skill_count
        {where_clause}
        GROUP BY skills
        HAVING skills IS NOT NULL
        ORDER BY job_count DESC
        LIMIT {top_n}
    """

    with sqlite3.connect(DB_PATH) as conn:
        total_jobs = pd.read_sql_query(query_total_jobs, conn, params=params).iloc[0]['total_jobs']
        top_skills_df = pd.read_sql_query(query_top_skills, conn, params=params)

    # Hitung persentase dan filter nilai kecil
    top_skills_df['percent'] = (top_skills_df['job_count'] / total_jobs * 100).round(2)
    top_skills_df = top_skills_df[top_skills_df['percent'] >= 0.05]

    # Urutkan skill berdasarkan percent ascending (kalau mau descending tinggal ganti)
    top_skills_df = top_skills_df.sort_values('percent', ascending=True).reset_index(drop=True)

    # Pilih dan rename kolom sesuai kebutuhan
    result_df = top_skills_df[['skills', 'percent']]

    return result_df



# Ensure indexes exist (run this once during initialization)
@st.cache_data
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_job_title_short 
        ON job_title_skill_count(job_title_short)
        """)
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_type 
        ON job_title_skill_count(type)
        """)
        conn.commit()
    finally:
        conn.close()

