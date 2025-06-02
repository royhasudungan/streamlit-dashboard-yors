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
else:
    if selected_job_titles:
        filtered = df_summary[df_summary['job_title_short'].isin(selected_job_titles)]
        total_jobs = df_jobs[df_jobs['job_title_short'].isin(selected_job_titles)]['job_id'].nunique()

        # Gabungkan skill dengan total count dari semua job title terpilih
        filtered_grouped = (
            filtered.groupby('skills')['count'].sum().reset_index()
            .sort_values(by='count', ascending=False)
        )

        # Buat kolom tooltip custom
        filtered_grouped['tooltip_text'] = filtered_grouped.apply(
            lambda row: f"{row['count']} total from {total_jobs} jobs",
            axis=1
        )

        chart = alt.Chart(filtered_grouped).mark_bar().encode(
            x='count:Q',
            y=alt.Y('skills:N', sort='-x'),
            tooltip=[alt.Tooltip('skills:N', title='Skill'),
                     alt.Tooltip('tooltip_text:N', title='Detail')]
        ).properties(
            width=700,
            height=400,
            title=f"Top Skills for {', '.join(selected_job_titles)}"
        )

        st.altair_chart(chart)
    else:
        st.info("Pilih minimal satu job title untuk melihat grafik.")
