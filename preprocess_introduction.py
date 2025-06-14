import sqlite3
import streamlit as st
import pandas as pd

DB_PATH = 'jobs_skills.db'

@st.cache_data(show_spinner=False)
def create_all_intro_summaries():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Top 5 Most In-Demand Job Titles
    cursor.execute("DROP TABLE IF EXISTS top_job_title_summary")
    cursor.execute("""
        CREATE TABLE top_job_title_summary AS
        SELECT job_title_short, COUNT(DISTINCT job_id) AS count
        FROM job_postings_fact
        GROUP BY job_title_short
        ORDER BY count DESC
        LIMIT 5
    """)

    # 2. Skill Type Distribution
    cursor.execute("DROP TABLE IF EXISTS skill_type_distribution_summary")
    cursor.execute("""
        CREATE TABLE skill_type_distribution_summary AS
        SELECT s.type AS skill_type, COUNT(DISTINCT j.job_title) AS job_title_count
        FROM skills_job_dim sj
        JOIN skills_dim s ON sj.skill_id = s.skill_id
        JOIN job_postings_fact j ON sj.job_id = j.job_id
        WHERE s.type IS NOT NULL
        GROUP BY s.type
    """)

    # 3. Job Country Distribution
    cursor.execute("DROP TABLE IF EXISTS job_country_summary")
    cursor.execute("""
        CREATE TABLE job_country_summary AS
        SELECT job_country, COUNT(*) AS count
        FROM job_postings_fact
        GROUP BY job_country
        ORDER BY count DESC
    """)

    # 4. Total Jobs & Average Salary
    cursor.execute("DROP TABLE IF EXISTS job_summary_stats")
    cursor.execute("""
        CREATE TABLE job_summary_stats AS
        SELECT 
            COUNT(*) AS total_jobs,
            ROUND(AVG(salary_year_avg), 2) AS avg_salary
        FROM job_postings_fact
        WHERE salary_year_avg IS NOT NULL
    """)

    conn.commit()
    conn.close()



@st.cache_data(show_spinner=False)
def load_top_job_title_summary():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM top_job_title_summary", conn)
    conn.close()
    return df

@st.cache_data(show_spinner=False)
def load_skill_type_distribution():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM skill_type_distribution_summary", conn)
    conn.close()
    return df

@st.cache_data(show_spinner=False)
def load_job_country():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM job_country_summary", conn)
    conn.close()
    return df

@st.cache_data(show_spinner=False)
def load_job_summary_stats():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM job_summary_stats", conn)
    conn.close()
    return df
