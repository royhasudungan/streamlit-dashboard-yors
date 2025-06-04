import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from load_data import download_and_load_csv
from preprocess_viz_top_skills import create_view_model_top_skills_sql
from streamlit_option_menu import option_menu
import sqlite3

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #152a4f 0%, #161B22 50%, #0c172d 100%);
        color: #E6EDF3;
        font-family: sans-serif !important
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<style>
div[data-testid="stSelectbox"] > div {
    width: 300px;
}
</style>
""", unsafe_allow_html=True)

DB_PATH = 'jobs_skills.db'

# Setup SQLite DB dari CSV kalau DB belum ada
def setup_sqlite_db_from_csv(dataframes):
    conn = sqlite3.connect(DB_PATH)
    # Replace tabel SQLite
    dataframes['job_postings_fact.csv'].to_sql('job_postings_fact', conn, if_exists='replace', index=False)
    dataframes['skills_dim.csv'].to_sql('skills_dim', conn, if_exists='replace', index=False)
    dataframes['skills_job_dim.csv'].to_sql('skills_job_dim', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()


with st.spinner("Loading data..."):
    dataframes = download_and_load_csv()

if not os.path.exists(DB_PATH):
    with st.spinner("Setting up SQLite DB..."):
        setup_sqlite_db_from_csv(dataframes)

if not os.path.exists('job_title_skill_count.csv'):
    with st.spinner("Creating summary file with SQL..."):
        try:
            create_view_model_top_skills_sql()
        except Exception as e:
            st.error(f"Failed to generate view model: {e}")

df_top10_skills = pd.read_csv('job_title_skill_count.csv')

# Sidebar menu
with st.sidebar:
    st.markdown("<h2 style='color:white; font-weight:bold;'> 💼  Data IT</h2>", unsafe_allow_html=True)
    selected = option_menu(
        menu_title = "",
        options=["🏠 Introduction", "💰 Salary", "🛠️ Top Skills", "📍 Location"],
        default_index=0,
        styles={
            "container": {
                "background-color": "transparent",
            },
            "icon": {
                "color": "transparent",
                "font-size": "20px"
            },
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

if selected == "🏠 Introduction":
    st.title("💼 IT Job Market Explorer 2023")

elif selected == "💰 Salary":
    st.header("💰 Salary Analysis")

elif selected == "🛠️ Top Skills":
    st.header("🛠️ Top Skills")

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

    # Select job title short
    job_titles = ["Select All"] + sorted(df_top10_skills['job_title_short'].unique())
    selected_job_title = st.selectbox("Job Title :", options=job_titles, index=0)

    # Select skill type
    skill_types = ["All", "programming","databases", "webframeworks", "analyst_tools", "cloud", "os","sync","async", "other"]
    selected_type_skill = st.radio("Skills :", options=skill_types, index=0, format_func=format_label, horizontal=True)

    filtered = df_top10_skills.copy()

    if selected_job_title != "Select All":
        filtered = filtered[filtered['job_title_short'] == selected_job_title]

    if selected_type_skill != "All":
        filtered = filtered[filtered['type'] == selected_type_skill]

    total_jobs = filtered['job_title'].nunique()
    skill_job_counts = filtered.groupby('skills')['job_title'].nunique()
    top_skills = skill_job_counts.nlargest(20).index.dropna().tolist()
    percent_per_skill = (skill_job_counts[top_skills] / total_jobs * 100).round(2)
    threshold = 0.05
    percent_per_skill = percent_per_skill[percent_per_skill >= threshold]

    skill_order = percent_per_skill.sort_values().index.tolist()

    colorscale = px.colors.sequential.Tealgrn[::-1]
    max_val = max(percent_per_skill[skill_order]) if not percent_per_skill.empty else 0
    xaxis_max = max_val + 5 if max_val + 5 <= 100 else 100

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
    for i, skill in enumerate(skill_order):
        val = percent_per_skill[skill]
        annotations.append(dict(
            x=0,
            y=skill,
            xanchor='right',
            yanchor='middle',
            text=skill,
            font=dict(color='white', size=font_size),
            showarrow=False,
            xshift=-10
        ))
        annotations.append(dict(
            x=val,
            y=skill,
            xanchor='left',
            yanchor='middle',
            text=f"{val:.1f}%",
            font=dict(color='white', size=font_size),
            showarrow=False,
            xshift=10
        ))

    bar_height = 37
    fig_height = max(300, bar_height * bar_count)
    fig.update_layout(
        annotations=annotations,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            visible=False,
            range=[0, xaxis_max]
        ),
        yaxis=dict(
            visible=False,
            categoryorder='total ascending'
        ),
        margin=dict(l=150, r=40, t=60, b=40),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor='#16213e',
            bordercolor='white',
            font=dict(color='white', size=0.75*font_size),
        ),
        bargap=0.3,
        height=fig_height,
    )

    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': True,
        'modeBarButtonsToRemove': [
            'zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
            'autoScale2d', 'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian',
            'toggleSpikelines', 'toImage'
        ],
        'displaylogo': False
    })

elif selected == "📍 Location":
    st.header("🌍 Job Openings by Country")
