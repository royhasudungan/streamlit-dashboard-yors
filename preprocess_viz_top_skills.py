import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = 'jobs_skills.db'
CSV_SUMMARY_PATH = 'job_title_skill_count.parquet'

@st.cache_data(show_spinner=False)
def create_view_model_top_skills_sql():
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

    df_summary = pd.read_sql_query("SELECT * FROM job_title_skill_count", conn)
    conn.close()

    # Simpan file hasil query untuk cache
    df_summary.to_parquet(CSV_SUMMARY_PATH)

    return df_summary