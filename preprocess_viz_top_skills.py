import sqlite3
import streamlit as st

DB_PATH = 'jobs_skills.db'

@st.cache_data(show_spinner=False)
def create_view_model_top_skills_sql():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Buat tabel summary di SQLite (replace jika sudah ada)
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

    # Load hasil ke DataFrame untuk dipakai Streamlit
    import pandas as pd
    df_summary = pd.read_sql_query("SELECT * FROM job_title_skill_count", conn)
    conn.close()

    # Simpan csv sebagai cache (optional, agar konsisten dengan kode lama)
    df_summary.to_parquet("job_title_skill_count.parquet")


    return df_summary
