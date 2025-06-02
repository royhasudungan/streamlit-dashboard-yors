import os
import streamlit as st
import pandas as pd
import altair as alt
from preprocess_viz_top_skills import preprocess_data, create_view_model_top_skills, create_skill_trend_data
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

if not os.path.exists('skill_trend.csv'):
    with st.spinner("Creating skill trend file..."):
        create_skill_trend_data(df_jobs, df_skills, df_skills_job)

df_summary = pd.read_csv('job_title_skill_count.csv')
df_trend = pd.read_csv('skill_trend.csv')

# --- BAR CHART: Top Skills by Job Title ---
job_titles = sorted(df_summary['job_title_short'].unique())
selected_job_titles = st.multiselect("Pilih maksimal 3 Job Title (Bar Chart):", job_titles)

if len(selected_job_titles) > 3:
    st.warning("⚠️ Maksimal 3 job title boleh dipilih. Tolong kurangi pilihanmu.")
elif selected_job_titles:
    filtered = df_summary[df_summary['job_title_short'].isin(selected_job_titles)]
    total_per_skill = filtered.groupby('skills')['count'].sum().reset_index()
    top_skills = total_per_skill.nlargest(10, 'count')['skills'].tolist()
    filtered_top = filtered[filtered['skills'].isin(top_skills)]

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
    ).properties(width=700, height=400, title="Top 10 Skills untuk Job Titles Terpilih")

    st.altair_chart(bar_chart)
else:
    st.info("Pilih minimal satu job title untuk melihat bar chart.")



# --- LINE CHART: Skill Trend by Job Title ---
st.markdown("---")
st.header("Skill Demand Trend per Job Title")

# Input job titles for line chart (no max limit)
selected_job_titles_line = st.multiselect(
    "Pilih Job Title (Line Chart):",
    job_titles,
    key="line_chart_job_titles"
)

if selected_job_titles_line:
    # Pastikan kolom 'date' bertipe datetime
    df_trend['date'] = pd.to_datetime(df_trend['date'])

    # Filter df_trend untuk job title yang dipilih
    filtered_trend = df_trend[df_trend['job_title_short'].isin(selected_job_titles_line)]

    # Totalin jumlah per skill dan tanggal dari gabungan job title terpilih
    total_skill_per_date = filtered_trend.groupby(['date', 'skills'])['count'].sum().reset_index()

    # Ambil top 5 skill berdasarkan total keseluruhan periode
    total_skill_sum = total_skill_per_date.groupby('skills')['count'].sum().reset_index()
    top_skills_line = total_skill_sum.nlargest(5, 'count')['skills'].tolist()

    # Filter hanya top 5 skill yang sudah ditentukan
    final_trend = total_skill_per_date[total_skill_per_date['skills'].isin(top_skills_line)]

    if final_trend.empty:
        st.info("Data tren skill tidak ditemukan untuk pilihan ini.")
    else:
        line_chart = alt.Chart(final_trend).mark_line(point=False).encode(
            x=alt.X('date:T', title='Tanggal'),
            y=alt.Y('count:Q', title='Jumlah Lowongan'),
            color=alt.Color('skills:N', title='Skill'),
            tooltip=[
                alt.Tooltip('date:T', title='Tanggal'),
                alt.Tooltip('skills:N', title='Skill'),
                alt.Tooltip('count:Q', title='Jumlah Lowongan')
            ]
        ).properties(
            width=700,
            height=400,
            title="Tren Permintaan Top 5 Skill Gabungan Job Titles Terpilih"
        ).interactive()

        st.altair_chart(line_chart)
