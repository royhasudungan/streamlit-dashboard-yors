import streamlit as st
import pandas as pd

def show_top_skills(df_jobs, df_skills, df_skills_job):
    job_title_options = df_jobs['job_title_short'].dropna().unique()
    selected_job_title = st.selectbox("Pilih Job Title Short:", options=sorted(job_title_options))

    job_ids = df_jobs.loc[df_jobs['job_title_short'] == selected_job_title, 'job_id'].unique()
    skills_for_jobs = df_skills_job[df_skills_job['job_id'].isin(job_ids)]
    skills_merged = pd.merge(skills_for_jobs, df_skills, on='skill_id', how='left')

    top_skills = skills_merged['skills'].value_counts().head(20)

    st.subheader(f"Top 20 Skills for '{selected_job_title}'")
    if not top_skills.empty:
        st.bar_chart(top_skills)
    else:
        st.write("No skills found for this selection.")
