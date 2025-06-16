import time
import sqlite3
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from load_data import download_and_load_parquet
from preprocess_top_skills import load_top_skills_summary,create_top_skills_summary
from streamlit_option_menu import option_menu
from preprocess_salary import load_salary_summary, create_salary_summary
from preprocess_demand_skills import load_demand_skills, create_demand_skill_summary
from preprocess_location import create_job_country_summary, load_job_country_summary
from preprocess_introduction import create_all_intro_summaries, load_job_country, load_job_summary_stats,load_skill_type_distribution,load_top_job_title_summary
import pydeck as pdk
import os


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
        default_index=1,
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
    create_all_intro_summaries()

    top_jobs_df = load_top_job_title_summary()
    summary_stats = load_job_summary_stats()


    total_jobs = summary_stats["total_jobs"].iloc[0]
    avg_salary = summary_stats["avg_salary"].iloc[0]

    # Layout dua kolom
    col1, col3, col2 = st.columns([5, 0.1, 2])

    with col1:

        # Gradasi warna manual
        gradient_colors = [
            'rgba(173, 216, 230, 0.9)',  # light blue
            'rgba(135, 206, 250, 0.9)',
            'rgba(100, 149, 237, 0.9)',
            'rgba(70, 130, 180, 0.9)',
            'rgba(65, 105, 225, 0.9)'   # royal blue
        ]

        # Buat figure
        fig = go.Figure()

        for i, row in top_jobs_df.iterrows():
            fig.add_trace(go.Bar(
                x=[row['job_title_short']],
                y=[row['count']],
                marker=dict(color=gradient_colors[i]),
                hovertemplate=f"{row['job_title_short']}<br>Count: {row['count']} Jobs<extra></extra>",
                showlegend=False
            ))

        fig.update_layout(
            hoverlabel=dict(
                bgcolor='#16213e',
                bordercolor='white',
                font=dict(color='white', size=20),
            ),
            title= dict(
                text='Top 5 Most In-Demand Data IT Job Roles',
                x=0.5,
                xanchor='center',
                font=dict(size=25, color='white')
            ),
            xaxis=dict(
                title='', 
                showline=False, 
                showticklabels=True, 
                showgrid=False,
                tickfont=dict(size=20)
            ),
            yaxis=dict(
                visible=False  # Ini matiin semua tampilan sumbu Y
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=80, b=40)
        )

        # Hapus toolbar dan disable zoom
        config = {
            "displayModeBar": False,
            "scrollZoom": False
        }

        st.plotly_chart(fig, use_container_width=True, config=config)

    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
            margin-bottom: 1.5rem;
        ">
            <h3 style="margin-bottom: 0.5rem;">🏢 Total Jobs</h3>
            <div style="font-size: 2rem; font-weight: 600;">{total_jobs:,} post</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #4facfe, #00f2fe);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 25px rgba(79, 172, 254, 0.15);
            margin-bottom: 1.5rem;
        ">
            <h3 style="margin-bottom: 0.5rem;">💰 Average Salary (USD)</h3>
            <div style="font-size: 2rem; font-weight: 600;">${avg_salary:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="height: 100%; border-left: 2px solid #ccc;"></div>
    """, unsafe_allow_html=True)
        

    col11, col12  = st.columns([1,1])
    skill_dist_df = load_skill_type_distribution()
    country_df = load_job_country()

    with col11:
        # Mapping label format
        def format_label(option):
            return {
                "databases": "Databases",
                "analyst_tools": "Tools",
                "programming": "Languages",
                "webframeworks": "Frameworks",
                "cloud": "Cloud",
                "os": "OS",
                "sync": "Sync",
                "async": "Async",
                "other": "Other"
            }.get(option, option)

        # Hitung distribusi skill type (tanpa filter)
        type_distribution = (
            skill_dist_df.groupby("skill_type")["job_title_count"]
            .sum()
            .sort_values(ascending=False)
        )


        # Format labels
        formatted_labels = [format_label(t) for t in type_distribution.index]

        # Hitung persentase
        type_percent = (type_distribution / type_distribution.sum() * 100).round(2)

        # Pie Chart
        fig = go.Figure(data=[go.Pie(
            labels=formatted_labels,
            values=type_percent.values,
            hole=0.45,
            textinfo='label',
            showlegend=False,
            hovertemplate="<b>%{label}</b><br>📊 Required in %{value:.2f}% of postings<extra></extra>",
            marker=dict(colors=px.colors.qualitative.Set3)
        )])

        fig.update_layout(
            title= dict(
                text='Skill Type Distribution by Percentage',
                x=0.5,
                xanchor='center',
                font=dict(size=25, color='white')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=15),
            margin=dict(t=40, b=40, l=20, r=20),
            hoverlabel=dict(
                bgcolor='#16213e',
                bordercolor='white',
                font=dict(color='white', size=20),
            ),
            
            
        )

        # Show it
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': False,
            'displaylogo': False
        })
    
    with col12 :

        # Hitung jumlah lokasi unik
        n_locations = country_df['job_country'].nunique()

        # Hitung jumlah job per country, urut dari terbesar
        job_counts = country_df.set_index('job_country')['count'].sort_values(ascending=False)


        # Buat bar chart
        fig = go.Figure(go.Bar(
            x=job_counts.index,
            y=job_counts.values,
            marker_color='royalblue',
            hovertemplate='%{x}<br>Jobs: %{y}<extra></extra>'
        ))

        fig.update_layout(
            title= dict(
                text='🌍 Job Locations<br><span style="font-size:16px;">Total: <b>' + str(n_locations) + ' locations</b></span>',
                x=0.5,
                xanchor='center',
                font=dict(size=25, color='white')
            ),
            xaxis_title="",
            yaxis_title="Number of Jobs",
            font=dict(color='white', size=18),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=40, l=40, r=40),
            hoverlabel=dict(
                bgcolor='#16213e',
                bordercolor='white',
                font=dict(color='white', size=20),
            ),
            hoverdistance=100
        )

        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': False,
            'displaylogo': False
        })



# 💰 Salary
elif selected == "💰 Salary":
    st.header("💰 Salary Analysis")
    
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

    # Load filtered data
    filtered = load_top_skills_summary(job_chosen, type_chosen)
    st.write(f"⏱️ Loaded data filtered **{(time.time() - start):.2f} seconds**")

    if filtered.empty:
        st.info("No data found for the selected filters.")
    else:
        skill_order = filtered['skills']
        percent_per_skill = filtered.set_index('skills')['percent']

        # Plotting
        colorscale = px.colors.sequential.Tealgrn[::-1]
        xaxis_max = min(percent_per_skill.max() + 5, 100)
        font_size = 25
        bar_count = len(skill_order)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=skill_order,
            x=percent_per_skill.loc[skill_order],
            orientation='h',
            marker=dict(color=percent_per_skill.loc[skill_order], colorscale=colorscale),
            hovertemplate="<b>%{y}</b><br>📊 jobfair requires %{x:.1f}% <extra></extra>"
        ))

        annotations = []
        for skill in skill_order:
            val = percent_per_skill[skill]
            annotations.extend([
                dict(x=0, y=skill, xanchor='right', yanchor='middle',
                     text=skill, font=dict(color='white', size=font_size), showarrow=False, xshift=-10),
                dict(x=val, y=skill, xanchor='left', yanchor='middle',
                     text=f"{val:.1f}%", font=dict(color='white', size=font_size), showarrow=False, xshift=10)
            ])

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


        # --- Demand Skills Section ---

    st.markdown("---")
    st.markdown("### 📈 In-Demand Skills Over Time")


    start2 = time.time()

    create_demand_skill_summary()

    job_titles2 = [
        "Select All", "Business Analyst", "Cloud Engineer", "Data Analyst", "Data Engineer",
        "Data Scientist", "Machine Learning Engineer", "Senior Data Analyst",
        "Senior Data Engineer", "Senior Data Scientist", "Software Engineer"
    ]

    job_schedule_types = [
        "Select All", "Full-time", "Internship",
        "Contractor", "Part-Time", "Temp work"
    ]

    selected_title = st.selectbox("Pilih Job Title", options=job_titles2, index=0)
    selected_schedule = st.selectbox("Pilih Job Schedule Type", options=job_schedule_types, index=0)

    job_chosen2 = None if selected_title == "Select All" else selected_title
    schedule_chosen2 = None if selected_schedule == "Select All" else selected_schedule

    df = load_demand_skills(job_chosen2, schedule_chosen2)
    top5_skills = df['skills'].unique()

    # Buat line chart per skill
    fig = go.Figure()
    for skill in top5_skills:
        df_skill = df[df['skills'] == skill]
        fig.add_trace(go.Scatter(
            x=df_skill['job_posted_date'],
            y=df_skill['count'],
            mode='lines',
            name=skill
            
    ))


    min_date = df['job_posted_date'].min()
    max_date = df['job_posted_date'].max()

    fig.update_layout(
        title=dict(
            text="Top 5 Trend Skills in Demand by Time Series",
            x=0.5,
            xanchor='center',
            font=dict(size=15, color='white')
        ),
        xaxis_title='',
        yaxis_title='',
        hoverdistance=100,
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='black',
            bordercolor='white',
            font_size=14,
            font_color='white'
        ),
        dragmode='pan',
        xaxis=dict(
            range=[min_date, max_date],
            minallowed=min_date,
            maxallowed=max_date,
            type='date',
            fixedrange=False,
            constrain='range',
            rangeslider=dict(visible=True, thickness=0.0),
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikecolor='rgba(255, 255, 255, 0.4)',
            spikethickness=0.05,
            showline=True,
            showgrid=True,
            linecolor='white',
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False
        ),


        yaxis=dict(
            showspikes=False,
            spikemode='across',
            spikesnap='cursor',
            showline=True,
            showgrid=True,
            linecolor='white',
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # Tampilkan di Streamlit
    st.plotly_chart(fig, use_container_width=True, config={
        'scrollZoom': True,  # zoom dengan scroll mouse aktif
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtons': [
            ['pan2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d']
        ],
    })

    st.write(f"⏱️ Test **{(time.time() - start2):.2f} seconds**")



# 📍 Location
elif selected == "📍 Location":
    st.header("🌍 Job Openings by Country")
    st.markdown("This map shows the distribution of job vacancies across countries from the dataset.")

    create_job_country_summary()
    country_counts = load_job_country_summary()

    # Koordinat negara (sementara hardcoded)
    country_coords = pd.DataFrame({
        'Country': ['United States', 'India', 'Germany', 'United Kingdom', 'Indonesia',
                    'Canada', 'Australia', 'France', 'Brazil', 'Japan'],
        'lat': [37.0902, 20.5937, 51.1657, 55.3781, -0.7893,
                56.1304, -25.2744, 46.2276, -14.2350, 36.2048],
        'lon': [-95.7129, 78.9629, 10.4515, -3.4360, 113.9213,
                -106.3468, 133.7751, 2.2137, -51.9253, 138.2529]
    })

    # Gabungkan koordinat
    map_data = pd.merge(country_counts, country_coords, left_on='country', right_on='Country', how='left')
    map_data.dropna(subset=['lat', 'lon'], inplace=True)

    # Radius bubble
    map_data['radius'] = map_data['job_count'] / map_data['job_count'].max() * 500000

    # Tampilkan map
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v10',
        initial_view_state=pdk.ViewState(
            latitude=20,
            longitude=0,
            zoom=1.5,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=map_data,
                get_position='[lon, lat]',
                get_fill_color='[255, 100, 100, 160]',
                get_radius='radius',
                pickable=True,
            ),
        ],
        tooltip={"text": "{country}\nJobs: {job_count}"}
    ))
