import streamlit as st
import pandas as pd
import altair as alt
from preprocess_viz_top_skills import *
from load_data import *

st.title("Top Skills by Job Title")

# load summary data
dataframes = download_and_load_csv()
df_jobs, df_skills, df_skills_job = dataframes['job_postings_fact.csv'], dataframes['skills_dim.csv'], dataframes['skills_job_dim.csv']

df_jobs, df_skills, df_skills_job = preprocess_data(df_jobs, df_skills, df_skills_job)

# Cek apakah file summary sudah ada
if not os.path.exists('job_title_skill_count.csv'):
    with st.spinner("Creating summary file..."):
        create_view_model_top_skills(df_jobs, df_skills, df_skills_job)

df_summary = pd.read_csv('job_title_skill_count.csv')



#membuat option
job_titles = df_summary['job_title_short'].unique()
selected_job_title = st.selectbox("Pilih Job Title Short:", sorted(job_titles))

filtered = df_summary[df_summary['job_title_short'] == selected_job_title]

# Sort descending by count
filtered = filtered.sort_values(by='count', ascending=True)  # ascending=True biar bar dari bawah ke atas

# Buat chart horizontal dengan Altair
chart = alt.Chart(filtered).mark_bar().encode(
    x='count:Q',
    y=alt.Y('skills:N', sort='-x'),  # sort descending berdasarkan count
    tooltip=['skills', 'count']
).properties(
    width=700,
    height=400,
    title=f"Top Skills for {selected_job_title}"
)

st.altair_chart(chart)
