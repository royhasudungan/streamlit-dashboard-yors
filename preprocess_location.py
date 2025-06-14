import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = 'jobs_skills.db'

@st.cache_data(show_spinner=False)
def create_job_country_summary():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Hapus jika tabel sudah ada
    cursor.execute("DROP TABLE IF EXISTS job_country_summary")

    # Negara yang akan dikecualikan
    invalid_countries = ("Remote", "Worldwide", "Europe", "Asia", "Africa", "", None)
    valid_exclusions = [c for c in invalid_countries if c not in (None, '')]
    placeholders = ",".join("?" for _ in valid_exclusions)

    query = f"""
        CREATE TABLE job_country_summary AS
        SELECT 
            job_country AS country,
            COUNT(*) AS job_count
        FROM job_postings_fact
        WHERE job_country NOT IN ({placeholders})
          AND job_country IS NOT NULL
        GROUP BY job_country
    """

    cursor.execute(query, valid_exclusions)
    conn.commit()
    conn.close()


@st.cache_data(show_spinner=False)
def load_job_country_summary():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM job_country_summary", conn)
    conn.close()
    return df
