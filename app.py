import os
import streamlit as st
import pandas as pd
import altair as alt
from preprocess_viz_top_skills import preprocess_data, create_view_model_top_skills, create_skill_trend_data
from load_data import download_and_load_csv

st.title("Top Skills by Job Title & Skill Trend")

with st.spinner("Loading data..."):
    dataframes = download_and_load_csv()

df_jobs = dataframes['job_postings_fact.csv']
df_skills = dataframes['skills_dim.csv']
df_skills_job = dataframes['skills_job_dim.csv']

df_jobs, df_skills, df_skills_job = preprocess_data(df_jobs, df_skills, df_skills_job)

# Buat file summary utama jika belum ada
if not os.path.exists('job_title_skill_count.csv'):
    with st.spinner("Creating summary file..."):
        create_view_model_top_skills(df_jobs, df_skills, df_skills_job)

df_summary = pd.read_csv('job_title_skill_count.csv')

# Buat file tren skill per waktu jika belum ada
if not os.path.exists('skill_trend.csv'):
    with st.spinner("Creating skill trend data..."):
        create_skill_trend_data(df_jobs, df_skills, df_skills_job)

df_trend = pd.read_csv('skill_trend.csv')
df_trend['date'] = pd.to_datetime(df_trend['date'])  # pastikan kolom date datetime

# Pilih Job Title (max 3)
job_titles = sorted(df_summary['job_title_short'].unique())
selected_job_titles = st.multiselect("Pilih maksimal 3 Job Title:", job_titles)

if len(selected_job_titles) > 3:
    st.warning("⚠️ Maksimal 3 job title boleh dipilih. Tolong kurangi pilihanmu.")

if selected_job_titles and len(selected_job_titles) <= 3:
    # === Bar Chart: Top Skills per Job Title ===
    filtered = df_summary[df_summary['job_title_short'].isin(selected_job_titles)]

    total_per_skill = filtered.groupby('skills')['count'].sum().reset_index()
    top_skills = total_per_skill.nlargest(10, 'count')['skills'].tolist()

    filtered_top = filtered[filtered['skills'].isin(top_skills)]

    # Hitung total job per job_title untuk persen tooltip
    job_title_totals = {jt: df_jobs[df_jobs['job_title_short'] == jt]['job_id'].nunique() for jt in selected_job_titles}

    def make_tooltip(row):
        total_jobs = job_title_totals.get(row['job_title_short'], 1)
        percent = row['count'] / total_jobs * 100 if total_jobs > 0 else 0
        return f"{row['count']} ({percent:.1f}%) dari {total_jobs} data"

    filtered_top = filtered_top.copy()
    filtered_top['tooltip_text'] = filtered_top.apply(make_tooltip, axis=1)

    bar_chart = alt.Chart(filtered_top).mark_bar().encode(
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

    st.altair_chart(bar_chart)

    # === Line Chart: Tren Skill dari Waktu ke Waktu ===
    trend_filtered = df_trend[
        (df_trend['job_title_short'].isin(selected_job_titles)) &
        (df_trend['skills'].isin(top_skills))
    ]

    line_chart = alt.Chart(trend_filtered).mark_line(point=True).encode(
        x='date:T',
        y='count:Q',
        color='skills:N',
        strokeDash='job_title_short:N',
        tooltip=['date:T', 'job_title_short:N', 'skills:N', 'count:Q']
    ).properties(
        width=800,
        height=400,
        title="Tren Skill per Waktu"
    ).interactive()

    st.altair_chart(line_chart)

else:
    if selected_job_titles:
        st.warning("⚠️ Maksimal 3 job title boleh dipilih. Tolong kurangi pilihanmu.")
    else:
        st.info("Pilih minimal satu job title untuk melihat grafik.")
