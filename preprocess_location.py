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

    # Filter negara tidak valid
    invalid_countries = ("Remote", "Worldwide", "Europe", "Asia", "Africa", "", None)

    # Buat tabel dengan jumlah pekerjaan per negara
    cursor.execute("""
        CREATE TABLE job_country_summary AS
        SELECT 
            job_country AS country,
            COUNT(*) AS job_count
        FROM job_postings_fact
        WHERE job_country NOT IN (?, ?, ?, ?, ?, '')
           AND job_country IS NOT NULL
        GROUP BY job_country
    """, invalid_countries[:-1])  # Tanpa elemen terakhir (None)

    conn.commit()
    conn.close()

@st.cache_data(show_spinner=False)
def load_job_country_summary():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM job_country_summary", conn)
    conn.close()
    return df
