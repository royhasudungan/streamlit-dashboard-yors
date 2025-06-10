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
    """
    Load skills summary with optimized database access.
    Uses prepared statements and existing indexes.
    """
    with sqlite3.connect(DB_PATH) as conn:
        # Use parameterized query with proper type handling
        query = """
        SELECT * FROM job_title_skill_count
        WHERE (:job_title_short IS NULL OR job_title_short = :job_title_short)
        AND (:type IS NULL OR type = :type)
        """
        
        params = {
            'job_title_short': job_title_short,
            'type': type
        }
        
        # Use pandas with named parameters
        df = pd.read_sql_query(query, conn, params=params)
        
        # Ensure proper data types (optional)
        if 'count' in df.columns:
            df['count'] = pd.to_numeric(df['count'], errors='coerce')
        
    return df

# Ensure indexes exist (run this once during initialization)
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

