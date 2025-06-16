import os
import sqlite3
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from load_data import download_and_load_parquet
from preprocess_top_skills import create_top_skills_summary
from preprocess_salary import create_salary_summary
from preprocess_demand_skills import create_demand_skill_summary
from preprocess_location import create_job_country_summary
from preprocess_introduction import create_all_intro_summaries
from pages import introduction, salary, top_skills,location



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



DB_PATH = 'jobs_skills.db'

def setup_sqlite_db_from_csv(dataframes):
    conn = sqlite3.connect(DB_PATH)
    dataframes['job_postings_fact.parquet'].to_sql('job_postings_fact', conn, if_exists='replace', index=False)
    dataframes['skills_dim.parquet'].to_sql('skills_dim', conn, if_exists='replace', index=False)
    dataframes['skills_job_dim.parquet'].to_sql('skills_job_dim', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()

def db_has_required_tables():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        required_tables = {
            "top_10_skills_summary",
            "skill_type_distribution_summary",
            "job_country_summary",
            "top_job_titles_summary"
        }

        return required_tables.issubset(tables)
    except Exception as e:
        print(f"Error checking DB tables: {e}")
        return False

def ensure_db_and_summary():
    if not db_has_required_tables():
        dataframes = download_data_cached()
        setup_sqlite_db_from_csv(dataframes)
        create_salary_summary()
        create_top_skills_summary()
        create_demand_skill_summary()
        create_all_intro_summaries()
        create_job_country_summary()

# Cache loading
@st.cache_data
def download_data_cached():
    return download_and_load_parquet()

ensure_db_and_summary()

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
    introduction.introduction_render()
# 💰 Salary
elif selected == "💰 Salary":
    salary.salary_render()
# 🛠️ Top Skills
elif selected == "🛠️ Top Skills":
    top_skills.top_skills_render()
# 📍 Location
elif selected == "📍 Location":
    location.location_render()
    
