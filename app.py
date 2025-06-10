import os
import time
import sqlite3
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from load_data import download_and_load_parquet
from preprocess_viz_top_skills import load_csv_summary
from streamlit_option_menu import option_menu
from preprocess_salary import load_salary_summary, create_salary_summary


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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = set(row[0] for row in cursor.fetchall())
    conn.close()
    required = {'job_postings_fact', 'skills_dim', 'skills_job_dim'}
    return required.issubset(tables)

def ensure_db_and_summary():
    if not db_has_required_tables():
        st.warning("Database incomplete. Reloading from Parquet...")
        dataframes = download_data_cached()
        setup_sqlite_db_from_csv(dataframes)

    # Create/load summary
    return load_csv_summary()

# Cache loading
@st.cache_data
def download_data_cached():
    return download_and_load_parquet()

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

    # Pastikan tabel summary ada, buat jika belum
    create_salary_summary()

    month_num = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May",
        6: "June", 7: "July", 8: "August", 9: "September",
        10: "October", 11: "November", 12: "December"
    }
    month_name_to_num = {v: k for k, v in month_num.items()}

    # Selectbox bulan
    month_options = ["All Months"] + list(month_num.values())
    month_list = st.selectbox('Select a month', month_options, index=0)

    month_chosen = None if month_list == "All Months" else month_name_to_num[month_list]

    # Load data dari DB
    salary_df = load_salary_summary(month_chosen)

    # Filter jika ingin menampilkan hanya data dengan count > 0
    salary_df = salary_df[salary_df['count'] > 0]

    # Jika "All Months" tampilkan rata-rata across all months
    if month_chosen is None:
        summary_df = salary_df.groupby('job_title_short').agg(
            avg_salary=('avg_salary', 'mean'),
            max_salary=('max_salary', 'max'),
            min_salary=('min_salary', 'min'),
            count=('count', 'sum')
        ).reset_index()
        display_month = "All Months"
    else:
        summary_df = salary_df.copy()
        display_month = month_list

    # Sort dan ambil top 10 highest avg salary
    display_df = summary_df.sort_values(by="avg_salary", ascending=False).head(10)
    chart_title = f"Top 10 Highest Paying Jobs - {display_month} 2023"

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="🏢 Total Jobs", value=f"{summary_df['count'].sum():,}")

    with col2:
        avg_salary = summary_df['avg_salary'].mean()
        st.metric(label="💰 Avg Salary", value=f"${avg_salary:,.0f}")

    with col3:
        max_salary = summary_df['max_salary'].max()
        st.metric(label="🚀 Highest Salary", value=f"${max_salary:,.0f}")

    with col4:
        unique_titles = summary_df['job_title_short'].nunique()
        st.metric(label="🎯 Job Types", value=unique_titles)

    st.markdown("---")

    # Chart utama
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=display_df.sort_values(by="avg_salary")["avg_salary"],
        y=display_df.sort_values(by="avg_salary")["job_title_short"],
        orientation='h',
        marker=dict(
            color=display_df.sort_values(by="avg_salary", ascending=False)["avg_salary"],
            colorscale='Plasma',
            line=dict(color='rgba(0,0,0,0)')
        ),
        text=[f'${x:,.0f}' for x in display_df.sort_values(by="avg_salary")["avg_salary"]],
        textposition='outside',
        textfont=dict(color='white', size=11),
        customdata=display_df.sort_values(by="avg_salary")[["max_salary", "min_salary", "count"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "💰 Avg Salary: $%{x:,.0f}<br>"
            "📈 Max Salary: $%{customdata[0]:,.0f}<br>"
            "📉 Min Salary: $%{customdata[1]:,.0f}<br>"
            "👥 Total Workers: %{customdata[2]}<br>"
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        title={
            'text': chart_title,
            'font': {'size': 20, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center',
        },
        font=dict(color='white'),
        xaxis=dict(
            title="Average Yearly Salary (USD)",
            title_font=dict(size=18),
            title_standoff=25,
            zeroline=False,
            tickformat='$,.0f',
            tickfont=dict(size=14),
            gridcolor='gray'
        ),
        yaxis=dict(
            title="Job Title",
            title_font=dict(size=18),
            zeroline=False,
            tickfont=dict(size=14),
            gridcolor='gray',
            autorange="reversed"
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(
            bgcolor='#16213e',
            bordercolor='#0F3460',
            font_color='white'
        )
    )

    st.plotly_chart(fig, use_container_width=True)
# 🛠️ Top Skills
elif selected == "🛠️ Top Skills":
    start = time.time()

    st.header("🛠️ Top Skills")

    with st.spinner("Checking DB and summary..."):
        df_top10_skills = ensure_db_and_summary()

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
