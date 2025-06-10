import os
import time
import sqlite3
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from load_data import download_and_load_parquet
from preprocess_viz_top_skills import create_view_model_top_skills_sql
from streamlit_option_menu import option_menu

DB_PATH = 'jobs_skills.db'
CSV_SUMMARY_PATH = 'job_title_skill_count.parquet'

# Styling
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #152a4f 0%, #161B22 50%, #0c172d 100%);
    color: #E6EDF3;
}
div[data-testid="stSelectbox"] > div {
    width: 300px;
}
</style>
""", unsafe_allow_html=True)

# Cache loading
@st.cache_data
def load_csv_summary():
    return pd.read_parquet(CSV_SUMMARY_PATH)

@st.cache_data
def download_data_cached():
    return download_and_load_parquet()

def setup_sqlite_db_from_csv(dataframes):
    conn = sqlite3.connect(DB_PATH)
    dataframes['job_postings_fact.parquet'].to_sql('job_postings_fact', conn, if_exists='replace', index=False)
    dataframes['skills_dim.parquet'].to_sql('skills_dim', conn, if_exists='replace', index=False)
    dataframes['skills_job_dim.parquet'].to_sql('skills_job_dim', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()

# Check if DB has required tables
def db_has_required_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = set(row[0] for row in cursor.fetchall())
    conn.close()
    required = {'job_postings_fact', 'skills_dim', 'skills_job_dim'}
    return required.issubset(tables)

# Make sure summary file exists, else create it
def ensure_summary_exists():
    if not db_has_required_tables():
        st.warning("Database incomplete. Reloading from Parquet...")
        dataframes = download_data_cached()
        setup_sqlite_db_from_csv(dataframes)

    if not os.path.exists(CSV_SUMMARY_PATH):
        st.info("Creating summary file...")
        df_summary = create_view_model_top_skills_sql()
        return df_summary
    else:
        return load_csv_summary()

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='color:white; font-weight:bold;'> 💼  Data IT</h2>", unsafe_allow_html=True)
    selected = option_menu(
        menu_title="",
        options=["🏠 Introduction", "💰 Salary", "🛠️ Top Skills", "📍 Location"],
        default_index=0,
        styles={
            "container": {"background-color": "transparent"},
            "icon": {"color": "transparent", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px", "text-align": "left", "margin": "0.3rem 0",
                "color": "white", "border-radius": "8px"
            },
            "nav-link-hover": {
                "background-color": "rgba(255, 255, 255, 0.2)", "color": "white", "font-weight": "bold"
            },
            "nav-link-selected": {
                "background-color": "rgba(255, 255, 255, 0.2)", "color": "white", "font-weight": "bold"
            }
        }
    )

# 🏠 Introduction
if selected == "🏠 Introduction":
    st.title("💼 IT Job Market Explorer 2023")

# 💰 Salary
elif selected == "💰 Salary":
    st.header("💰 Salary Analysis")

# 🛠️ Top Skills
elif selected == "🛠️ Top Skills":
    start = time.time()

    st.header("🛠️ Top Skills")

    if not db_has_required_tables():
        with st.spinner("Setting up SQLite DB..."):
            dataframes = download_data_cached()
            setup_sqlite_db_from_csv(dataframes)

    with st.spinner("Loading summary..."):
        df_top10_skills = ensure_summary_exists()

    st.write(f"⏱️ Loaded & setup in **{(time.time() - start):.2f} seconds**")

    # UI filters
    job_titles = ["Select All"] + sorted(df_top10_skills['job_title_short'].dropna().unique())
    selected_job_title = st.selectbox("Job Title :", options=job_titles, index=0)

    def format_label(option):
        labels = {
            "databases": "Databases", "analyst_tools": "Tools", "programming": "Languages",
            "webframeworks": "Frameworks", "cloud": "Cloud", "os": "OS", "other": "Other"
        }
        return labels.get(option, option)

    skill_types = ["All", "programming", "databases", "webframeworks", "analyst_tools", "cloud", "os", "sync", "async", "other"]
    selected_type_skill = st.radio("Skills :", options=skill_types, index=0, format_func=format_label, horizontal=True)

    # Filter logic
    filtered = df_top10_skills.copy()
    if selected_job_title != "Select All":
        filtered = filtered[filtered['job_title_short'] == selected_job_title]
    if selected_type_skill != "All":
        filtered = filtered[filtered['type'] == selected_type_skill]

    total_jobs = filtered['job_title'].nunique()
    skill_job_counts = filtered.groupby('skills')['job_title'].nunique()
    top_skills = skill_job_counts.nlargest(20).index.dropna().tolist()
    percent_per_skill = (skill_job_counts[top_skills] / total_jobs * 100).round(2)
    percent_per_skill = percent_per_skill[percent_per_skill >= 0.05]
    skill_order = percent_per_skill.sort_values().index.tolist()

    # Bar chart
    colorscale = px.colors.sequential.Tealgrn[::-1]
    xaxis_max = min(percent_per_skill.max() + 5, 100)
    bar_count = len(skill_order)
    font_size = 25

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=skill_order,
        x=percent_per_skill[skill_order],
        orientation='h',
        marker=dict(color=percent_per_skill[skill_order], colorscale=colorscale),
        hovertemplate=f"<b>%{{y}}</b><br>📊 jobfair requires %{{x:.1f}}% <extra></extra>"
    ))

    # Annotations
    annotations = []
    for skill in skill_order:
        val = percent_per_skill[skill]
        annotations.append(dict(x=0, y=skill, xanchor='right', yanchor='middle',
                                text=skill, font=dict(color='white', size=font_size), showarrow=False, xshift=-10))
        annotations.append(dict(x=val, y=skill, xanchor='left', yanchor='middle',
                                text=f"{val:.1f}%", font=dict(color='white', size=font_size), showarrow=False, xshift=10))

    fig.update_layout(
        annotations=annotations,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(visible=False, range=[0, xaxis_max]),
        yaxis=dict(visible=False),
        margin=dict(l=150, r=40, t=60, b=40),
        hoverlabel=dict(bgcolor='#16213e', font=dict(size=0.75 * font_size)),
        height=max(300, 37 * bar_count)
    )

    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d',
                                   'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
                                   'hoverClosestCartesian', 'hoverCompareCartesian',
                                   'toggleSpikelines', 'toImage'],
        'displaylogo': False
    })

    st.write(f"⏱️ Render complete in **{(time.time() - start):.2f} seconds**")

# 📍 Location
elif selected == "📍 Location":
    st.header("🌍 Job Openings by Country")
