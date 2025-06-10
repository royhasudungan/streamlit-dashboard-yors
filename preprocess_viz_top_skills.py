import sqlite3
import pandas as pd
import streamlit as st
import os

DB_PATH = 'jobs_skills.db'
CSV_SUMMARY_PATH = 'job_title_skill_count.parquet'

@st.cache_data(show_spinner=False)
def create_view_model_top_skills_sql():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("Database not found, please setup DB first.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop view/table jika sudah ada, lalu buat baru
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

    # Save summary locally untuk cache load lebih cepat
    df_summary.to_parquet(CSV_SUMMARY_PATH)
    return df_summary

@st.cache_data
def load_csv_summary():
    if not os.path.exists(CSV_SUMMARY_PATH):
        return create_view_model_top_skills_sql()
    return pd.read_parquet(CSV_SUMMARY_PATH)
