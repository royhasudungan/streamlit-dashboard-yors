import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "jobs_skills.db"

@st.cache_data(show_spinner=False)
def create_demand_skill_summary():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Cek apakah tabel sudah ada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='demand_skill_trend'")
        exists = cursor.fetchone()

        if not exists:
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

@st.cache_data(show_spinner=False)
def load_demand_skills(job_title_short=None, job_type=None):
    with sqlite3.connect(DB_PATH) as conn:
        query = "SELECT * FROM demand_skill_trend"
        filters = []
        params = []

        if job_title_short:
            filters.append("job_title_short = ?")
            params.append(job_title_short)

        if job_type:
            filters.append("job_type = ?")
            params.append(job_type)

        if filters:
            query += " WHERE " + " AND ".join(filters)

        df = pd.read_sql_query(query, conn, params=params)

    df['job_posted_date'] = pd.to_datetime(df['job_posted_date'])
    return df

