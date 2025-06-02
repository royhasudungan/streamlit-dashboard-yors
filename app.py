import streamlit as st
import pandas as pd
import altair as alt

st.title("Top Skills by Job Title (Horizontal Bar Chart)")

# Contoh load summary data
df_summary = pd.read_csv('job_title_skill_count.csv')

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
