import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def preprocess_data(df_jobs, df_skills, df_skills_job):
    df_jobs = df_jobs.drop_duplicates(subset=['job_id'])
    df_skills = df_skills.drop_duplicates(subset=['skill_id'])
    df_skills_job = df_skills_job.drop_duplicates(subset=['job_id', 'skill_id'])

    df_jobs = df_jobs.dropna(subset=['job_id', 'job_title_short'])
    df_skills = df_skills.dropna(subset=['skill_id', 'skills'])
    df_skills_job = df_skills_job.dropna(subset=['job_id', 'skill_id'])

    df_jobs['job_id'] = df_jobs['job_id'].astype(str)
    df_skills['skill_id'] = df_skills['skill_id'].astype(str)
    df_skills_job['job_id'] = df_skills_job['job_id'].astype(str)
    df_skills_job['skill_id'] = df_skills_job['skill_id'].astype(str)

    df_jobs['job_title_short'] = df_jobs['job_title_short'].str.strip()
    df_skills['skills'] = df_skills['skills'].str.strip()

    return df_jobs, df_skills, df_skills_job

@st.cache_data(show_spinner=False)
def create_view_model_top_skills(df_jobs, df_skills, df_skills_job):
    df_skills_job = df_skills_job.merge(df_skills, on='skill_id', how='left')
    df_merged = df_skills_job.merge(df_jobs[['job_id', 'job_title_short']], on='job_id', how='left')

    df_summary = df_merged.groupby(['job_title_short', 'skills']).size().reset_index(name='count')
    df_top10 = df_summary.sort_values(['job_title_short', 'count'], ascending=[True, False]) \
                        .groupby('job_title_short').head(10)

    df_top10.to_csv('job_title_skill_count.csv', index=False)
    return df_top10

@st.cache_data(show_spinner=False)
def create_skill_trend_data(df_jobs, df_skills, df_skills_job):
    """
    Membuat data tren skill dari waktu ke waktu.
    Output: CSV dengan kolom [date, job_title_short, skills, count]
    """

    # Merge skills-job dengan skill dan job untuk dapatkan skill + job title + tanggal
    df_skills_job = df_skills_job.merge(df_skills, on='skill_id', how='left')
    df_merged = df_skills_job.merge(
        df_jobs[['job_id', 'job_title_short', 'job_posted_date']],
        on='job_id',
        how='left'
    )

    # Pastikan kolom tanggal sudah datetime
    df_merged['job_posted_date'] = pd.to_datetime(df_merged['job_posted_date'], errors='coerce')

    # Buang data tanpa tanggal valid
    df_merged = df_merged.dropna(subset=['job_posted_date'])

    # Kita group berdasarkan tanggal, job title dan skill
    # Bisa juga gunakan bulan/tahun untuk granularitas yang lebih rendah, contoh ambil bulan saja:
    df_merged['date'] = df_merged['job_posted_date'].dt.to_period('M').dt.to_timestamp()

    df_trend = df_merged.groupby(['date', 'job_title_short', 'skills']).size().reset_index(name='count')

    # Simpan ke CSV
    df_trend.to_csv('skill_trend.csv', index=False)

    return df_trend
