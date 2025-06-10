import os
import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from load_data import download_and_load_parquet
from preprocess_viz_top_skills import create_view_model_top_skills_sql
from streamlit_option_menu import option_menu
import sqlite3
import plotly.express as px

# Style
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

DB_PATH = 'jobs_skills.db'
CSV_SUMMARY_PATH = 'job_title_skill_count.parquet'

@st.cache_data
def load_csv_summary():
    return pd.read_parquet(CSV_SUMMARY_PATH)

# Fungsi ini untuk memastikan file summary ada, kalau belum, buat dulu
def ensure_summary_exists():
    if not os.path.exists(CSV_SUMMARY_PATH):
        st.info("Summary file tidak ditemukan, membuat baru...")
        df_summary = create_view_model_top_skills_sql()
        return df_summary
    else:
        return load_csv_summary()


@st.cache_data
def download_data_cached():
    return download_and_load_parquet()

def setup_sqlite_db_from_csv(dataframes):
    conn = sqlite3.connect(DB_PATH)

    # Ubah ke nama file Parquet
    dataframes['job_postings_fact.parquet'].to_sql('job_postings_fact', conn, if_exists='replace', index=False)
    dataframes['skills_dim.parquet'].to_sql('skills_dim', conn, if_exists='replace', index=False)
    dataframes['skills_job_dim.parquet'].to_sql('skills_job_dim', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

# Sidebar menu
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
                "font-size": "16px",
                "text-align": "left",
                "margin": "0.3rem 0",
                "color": "white",
                "border-radius": "8px",
            },
            "nav-link-hover": {
                "background-color": "rgba(255, 255, 255, 0.2)",
                "color": "white",
                "font-weight": "bold",
            },
            "nav-link-selected": {
                "background-color": "rgba(255, 255, 255, 0.2)",
                "color": "white",
                "font-weight": "bold",
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

    with st.spinner("Loading data..."):
        dataframes = download_data_cached()
    
    st.write(f"⏱️ Loaded  **{(time.time() - start):.2f} seconds**")

    if not os.path.exists(DB_PATH):
        with st.spinner("Setting up SQLite DB..."):
            setup_sqlite_db_from_csv(dataframes)

    st.write(f"⏱️ Setup db  **{(time.time() - start):.2f} seconds**")


    df_top10_skills = ensure_summary_exists()
    st.write(f"⏱️ load csv  **{(time.time() - start):.2f} seconds**")

    job_titles = ["Select All"] + sorted(df_top10_skills['job_title_short'].unique())
    selected_job_title = st.selectbox("Job Title :", options=job_titles, index=0)

    def format_label(option):
        labels = {
            "databases": "Databases",
            "analyst_tools": "Tools",
            "programming": "Languages",
            "webframeworks": "Frameworks",
            "cloud": "Cloud",
            "os": "OS",
            "other": "Other"
        }
        return labels.get(option, option)

    skill_types = ["All", "programming", "databases", "webframeworks", "analyst_tools", "cloud", "os", "sync", "async", "other"]
    selected_type_skill = st.radio("Skills :", options=skill_types, index=0, format_func=format_label, horizontal=True)

    # Filter
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

    colorscale = px.colors.sequential.Tealgrn[::-1]
    max_val = max(percent_per_skill[skill_order]) if not percent_per_skill.empty else 0
    xaxis_max = min(max_val + 5, 100)
    bar_count = len(skill_order)
    font_size = 25

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=skill_order,
        x=percent_per_skill[skill_order],
        orientation='h',
        marker=dict(
            color=percent_per_skill[skill_order],
            colorscale=colorscale,
            line=dict(color='rgba(0,0,0,0)', width=2),
        ),
        hovertemplate=f"<b>%{{y}}</b><br>📊jobfair requires %{{x:.1f}}% <extra></extra>"
    ))

    annotations = []
    for skill in skill_order:
        val = percent_per_skill[skill]
        annotations.append(dict(
            x=0, y=skill, xanchor='right', yanchor='middle',
            text=skill, font=dict(color='white', size=font_size),
            showarrow=False, xshift=-10
        ))
        annotations.append(dict(
            x=val, y=skill, xanchor='left', yanchor='middle',
            text=f"{val:.1f}%", font=dict(color='white', size=font_size),
            showarrow=False, xshift=10
        ))

    fig.update_layout(
        annotations=annotations,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(visible=False, range=[0, xaxis_max]),
        yaxis=dict(visible=False, categoryorder='total ascending'),
        margin=dict(l=150, r=40, t=60, b=40),
        hovermode='closest',
        hoverlabel=dict(bgcolor='#16213e', bordercolor='white', font=dict(color='white', size=0.75 * font_size)),
        bargap=0.3,
        height=max(300, 37 * bar_count),
    )

    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d',
                                   'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
                                   'hoverClosestCartesian', 'hoverCompareCartesian',
                                   'toggleSpikelines', 'toImage'],
        'displaylogo': False
    })

    # Show debug time
    st.write(f"⏱️ Loaded & rendered in **{(time.time() - start):.2f} seconds**")

# 📍 Location
elif selected == "📍 Location":
    st.header("🌍 Job Openings by Country")
