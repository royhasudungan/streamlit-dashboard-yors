import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = 'jobs_skills.db'


@st.cache_data(show_spinner=False)
def create_demand_skill_summary():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS demand_skill_trend")

    cursor.execute("""
        CREATE TABLE demand_skill_trend AS
        SELECT 
            DATE(j.job_posted_date) AS job_posted_date,
            j.job_title_short,
            j.job_schedule_type,
            s.skills,
            j.job_title
        FROM job_postings_fact j
        JOIN skills_job_dim sj ON sj.job_id = j.job_id
        JOIN skills_dim s ON sj.skill_id = s.skill_id
        WHERE s.skills IS NOT NULL
    """)
    conn.commit()
    conn.close()


@st.cache_data(show_spinner=False)
def load_demand_skills(job_title_short=None, job_schedule_type=None):
    conn = sqlite3.connect(DB_PATH)

    # Filter SQL dinamis
    conditions = []
    params = []

    if job_title_short:
        conditions.append("job_title_short = ?")
        params.append(job_title_short)

    if job_schedule_type:
        conditions.append("job_schedule_type LIKE ?")
        params.append(job_schedule_type)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
        SELECT *
        FROM demand_skill_trend
        {where_clause}
    """
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        return df

    # Ambil top 5 skill berdasarkan jumlah job_title unik
    top_skills = (
        df.groupby("skills")["job_title"]
        .nunique()
        .sort_values(ascending=False)
        .head(5)
        .index.tolist()
    )

    # Filter skill yang termasuk top 5
    df = df[df["skills"].isin(top_skills)]

    # Hitung jumlah job_title unik per tanggal per skill
    df_trend = (
        df.groupby(["job_posted_date", "skills"])["job_title"]
        .nunique()
        .reset_index(name="count")
        .sort_values(["job_posted_date", "skills"])
    )

    return df_trend