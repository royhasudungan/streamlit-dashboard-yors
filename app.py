import time
import sqlite3
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from load_data import download_and_load_parquet
from preprocess_top_skills import load_top_skills_summary,create_top_skills_summary, initialize_database
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

 # Warna tema dark yang konsisten
DARK_THEME = {
    'background_color': '#0E1117',
    'paper_color': '#262730',
    'text_color': '#FAFAFA',
    'grid_color': '#464853',
    'primary_color': '#FF6B6B',
    'secondary_color': '#4ECDC4',
    'success_color': '#45B7D1',
    'accent_colors': ['#FF6B6B', '#4ECDC4', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF'],
    'gradient_colors' : ['#014A7A', '#01579B', '#0277BD', '#0288D1', '#039BE5', '#03A9F4', '#29B6F6', '#4FC3F7', '#81D4FA', '#B3E5FC']
}


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

# Cache loading
@st.cache_data
def download_data_cached():
    return download_and_load_parquet()

ensure_db_and_summary()
initialize_database()

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

    # Add bars dengan gradient effect
    fig.add_trace(go.Bar(
        x=display_df.sort_values(by="avg_salary")["avg_salary"],
        y=display_df.sort_values(by="avg_salary")["job_title_short"],
        orientation='h',
        marker=dict(
            color=display_df.sort_values(by="avg_salary", ascending=False)["avg_salary"],
            # colorscale='Plasma',
            line=dict(color=DARK_THEME["gradient_colors"])
        ),
        text=[f'${x:,.0f}' for x in display_df.sort_values(by="avg_salary")["avg_salary"]],
        textposition='outside',
        textfont=dict(color=DARK_THEME['text_color'], size=11),
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

    # Layout dengan tema dark
    fig.update_layout(
        title={
            'text': chart_title,
            'font': {'size': 20, 'color': DARK_THEME['text_color']},
            'x': 0.5,
            'xanchor' : 'center',
        },
        # plot_bgcolor=DARK_THEME['background_color'],
        # paper_bgcolor=DARK_THEME['paper_color'],
        font=dict(color=DARK_THEME['text_color']),
        xaxis=dict(
            title="Average Yearly Salary (USD)",
            title_font=dict(size=18),  # Set x-axis title font size to 18
            title_standoff=25,         # Add space between title and tick labels
            gridcolor=DARK_THEME['grid_color'],
            zeroline=False,
            tickformat='$,.0f',
            tickfont=dict(size=14) # Optionally set tick label font size
        ),
        yaxis=dict(
            title="Job Title",
            title_font=dict(size=18),  # Set y-axis title font size to 18
            gridcolor=DARK_THEME['grid_color'],
            zeroline=False,
            # autorange="reversed", # To show highest paying job at the top
            tickfont=dict(size=14) # Optionally set tick label font size
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=500,
        hoverlabel=dict(
            bgcolor=DARK_THEME['paper_color'],
            bordercolor=DARK_THEME['primary_color'],
            font_color=DARK_THEME['text_color']
        )
    )

    st.plotly_chart(fig, use_container_width=True)


    # Chart tambahan
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Salary Distribution")

        # Pastikan menggunakan salary_df untuk distribusi gaji
        fig_hist = px.histogram(
            salary_df,  # Menggunakan salary_df untuk distribusi gaji
            x="avg_salary",  # Menggunakan 'avg_salary' untuk distribusi gaji
            nbins=20,
            title="Salary Distribution"
        )

        fig_hist.update_layout(
            font=dict(color=DARK_THEME['text_color']),
            title={
                'text': "Salary Distribution",
                'x': 0.5,  # Posisi tengah (0=kiri, 0.5=tengah, 1=kanan)
                'xanchor': 'center',  # Anchor point di tengah
                'y': 0.95,  # Posisi vertikal title (sama dengan pie chart)
                'yanchor': 'top',
                'font': {'size': 20, 'color': DARK_THEME['text_color']}
            },
            xaxis=dict(
                gridcolor=DARK_THEME['grid_color'], 
                title_text="Average Salary (USD)",
                title_font=dict(size=18),  # Ukuran font title x-axis
                tickfont=dict(size=14),    # Ukuran font tick labels
                title_standoff=25          # Jarak title dari axis (default ~20)
            ),
            yaxis=dict(
                gridcolor=DARK_THEME['grid_color'],
                title_text="Number of Workers",
                title_font=dict(size=18),  # Ukuran font title y-axis
                tickfont=dict(size=14)     # Ukuran font tick labels
            ),
            bargap=0.1,
            height=600,  # Sama dengan pie chart
            margin=dict(l=80, r=20, t=80, b=80)  # Margin yang konsisten
        )

        fig_hist.update_traces(
            textfont=dict(color=DARK_THEME['text_color'], size=12),  # Font size untuk text di pie chart
            marker_color=DARK_THEME['primary_color'],
            hovertemplate='<b>Average Salary:</b> %{x}<br>' +
                        '<b>Workers:</b> %{y}<br>' +
                        '<extra></extra>'  # Menghilangkan box tambahan
        )

        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.markdown("###  Job Title Distribution")

        # Gunakan job_df_filtered untuk distribusi job title
        job_counts = salary_df['job_title_short'].value_counts().head(8)  # Gunakan data dari salary_df

        fig_pie = px.pie(
            values=job_counts.values,
            names=job_counts.index,
            title="Job Title Distribution"
        )

        fig_pie.update_layout(
            title={
                'text': "Job Title Distribution",
                'x': 0.5,  # Posisi tengah (0=kiri, 0.5=tengah, 1=kanan)
                'xanchor': 'center',  # Anchor point di tengah
                'y': 0.95,  # Posisi vertikal title yang sama dengan histogram
                'yanchor': 'top',
                'font': {'size': 20, 'color': DARK_THEME['text_color']}
            },
            font=dict(color=DARK_THEME['text_color'], size=14),  # Font size untuk legend
            legend=dict(
                orientation="h",  # horizontal
                yanchor="top",
                y=-0.05,  # Jarak legenda diperkecil (dari -0.1 ke -0.05)
                xanchor="center",
                x=0.5,    # centered horizontally
                font=dict(size=14)  # Font size legend
            ),
            margin=dict(l=20, r=20, t=80, b=80),  # Margin top sama dengan histogram, bottom dikurangi
            height=600,
            showlegend=True
        )

        fig_pie.update_traces(
            domain=dict(x=[0.1, 0.9], y=[0.15, 0.85]),  # Posisi pie chart disesuaikan untuk jarak legend lebih kecil
            marker=dict(colors=DARK_THEME['accent_colors']),
            textfont=dict(color=DARK_THEME['text_color'], size=12),  # Font size untuk text di pie chart
            hovertemplate='<b>Job Title:</b> %{label}<br>' +
                        '<b>Workers:</b> %{value}<br>' +
                        '<extra></extra>'  # Menghilangkan box tambahan
        )

        st.plotly_chart(fig_pie, use_container_width=True)


# 🛠️ Top Skills
elif selected == "🛠️ Top Skills":
    start = time.time()

    st.header("🛠️ Top Skills")

    create_top_skills_summary()


    # UI filters
    job_titles = [
        "Select All", "Business Analyst", "Cloud Engineer", "Data Analyst", "Data Engineer",
        "Data Scientist", "Machine Learning Engineer", "Senior Data Analyst", 
        "Senior Data Engineer", "Senior Data Scientist", "Software Engineer"
    ]
    selected_job_title = st.selectbox("Job Title :", options=job_titles, index=0)

    job_chosen = None if selected_job_title == "Select All" else selected_job_title

    def format_label(option):
        labels = {
            "databases": "Databases", "analyst_tools": "Tools", "programming": "Languages",
            "webframeworks": "Frameworks", "cloud": "Cloud", "os": "OS", "other": "Other"
        }
        return labels.get(option, option)

    skill_types = ["All", "programming", "databases", "webframeworks", "analyst_tools", "cloud", "os", "sync", "async", "other"]
    selected_type_skill = st.radio("Skills :", options=skill_types, index=0, format_func=format_label, horizontal=True)

    type_chosen = None if selected_type_skill == "All" else selected_type_skill

    st.write(f"⏱️ Loaded & setup in **{(time.time() - start):.2f} seconds**")
    # Filter logic
    filtered = load_top_skills_summary(job_chosen, type_chosen)
    st.write(f"⏱️ Loaded data filtered **{(time.time() - start):.2f} seconds**")
    percent_per_skill = filtered['percent']
    skill_order = filtered['skills']

    st.write(f"⏱️ filtered2 **{(time.time() - start):.2f} seconds**")

    # Bar chart
    colorscale = px.colors.sequential.Tealgrn[::-1]
    xaxis_max = min(percent_per_skill.max() + 5, 100)
    bar_count = len(skill_order)
    font_size = 25

    st.write(f"⏱️ define **{(time.time() - start):.2f} seconds**")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=skill_order,
        x=percent_per_skill[skill_order],
        orientation='h',
        marker=dict(color=percent_per_skill[skill_order], colorscale=colorscale),
        hovertemplate=f"<b>%{{y}}</b><br>📊 jobfair requires %{{x:.1f}}% <extra></extra>"
    ))

    st.write(f"⏱️ go **{(time.time() - start):.2f} seconds**")

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
