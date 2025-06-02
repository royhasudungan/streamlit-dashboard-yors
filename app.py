import os
import streamlit as st
import pandas as pd
import altair as alt
from preprocess_viz_top_skills import preprocess_data, create_view_model_top_skills
from load_data import download_and_load_csv

st.title("Top Skills by Job Title")

with st.spinner("Loading data..."):
    dataframes = download_and_load_csv()

df_jobs = dataframes['job_postings_fact.csv']
df_skills = dataframes['skills_dim.csv']
df_skills_job = dataframes['skills_job_dim.csv']

df_jobs, df_skills, df_skills_job = preprocess_data(df_jobs, df_skills, df_skills_job)

if not os.path.exists('job_title_skill_count.csv'):
    with st.spinner("Creating summary file..."):
        create_view_model_top_skills(df_jobs, df_skills, df_skills_job)

df_summary = pd.read_csv('job_title_skill_count.csv')

job_titles = sorted(df_summary['job_title_short'].unique())
selected_job_titles = st.multiselect("Pilih maksimal 3 Job Title:", job_titles)

if len(selected_job_titles) > 3:
    st.warning("⚠️ Maksimal 3 job title boleh dipilih. Tolong kurangi pilihanmu.")
elif selected_job_titles:
    # Filter data untuk job title yang dipilih
    filtered = df_summary[df_summary['job_title_short'].isin(selected_job_titles)]

    # Hitung total count per skill untuk semua job title yg dipilih, untuk ambil top 10 skill
    total_per_skill = filtered.groupby('skills')['count'].sum().reset_index()
    top_skills = total_per_skill.nlargest(10, 'count')['skills'].tolist()

    # Filter lagi agar hanya top 10 skill yang diambil
    filtered_top = filtered[filtered['skills'].isin(top_skills)]

    # Untuk tooltip: kita bisa juga hitung total job per job_title untuk persen, optional
    job_title_totals = {}
    for jt in selected_job_titles:
        job_title_totals[jt] = df_jobs[df_jobs['job_title_short'] == jt]['job_id'].nunique()

    # Buat kolom tooltip custom
    def make_tooltip(row):
        total_jobs = job_title_totals.get(row['job_title_short'], 1)
        percent = row['count'] / total_jobs * 100 if total_jobs > 0 else 0
        return f"{row['count']} ({percent:.1f}%) dari {total_jobs} data"

    filtered_top = filtered_top.copy()
    filtered_top['tooltip_text'] = filtered_top.apply(make_tooltip, axis=1)

    # Buat chart dengan grouped bar chart: X=count, Y=skill, color=job title
    chart = alt.Chart(filtered_top).mark_bar().encode(
        x='count:Q',
        y=alt.Y('skills:N', sort='-x'),
        color=alt.Color('job_title_short:N', legend=alt.Legend(title="Job Title")),
        tooltip=[
            alt.Tooltip('skills:N', title='Skill'),
            alt.Tooltip('job_title_short:N', title='Job Title'),
            alt.Tooltip('tooltip_text:N', title='Detail')
        ]
    ).properties(
        width=700,
        height=400,
        title=f"Top 10 Skills untuk Job Titles Terpilih"
    ).interactive()

    st.altair_chart(chart)
else:
    st.info("Pilih minimal satu job title untuk melihat grafik.")
