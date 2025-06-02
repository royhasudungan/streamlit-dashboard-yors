import streamlit as st
from load_data import download_and_load_csv
from visualize_top_skills import show_top_skills

st.title("Top Skills Dashboard 🚀")

with st.spinner("Loading data..."):
    dataframes = download_and_load_csv()

df_jobs = dataframes['job_postings_fact.csv']
df_skills = dataframes['skills_dim.csv']
df_skills_job = dataframes['skills_job_dim.csv']

st.success("✅ All data loaded!")

show_top_skills(df_jobs, df_skills, df_skills_job)
