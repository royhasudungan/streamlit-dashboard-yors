import os
import streamlit as st
import pandas as pd
import altair as alt
from preprocess_viz_top_skills import preprocess_data, create_view_model_top_skills, create_skill_trend_data
from load_data import download_and_load_csv
from streamlit_option_menu import option_menu

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




# Custom CSS
st.markdown("""
<style>
div[data-testid="stSelectbox"] > div {
    width: 300px;
}
</style>
""", unsafe_allow_html=True)


with st.spinner("Loading data..."):
    dataframes = download_and_load_csv()

job_df = dataframes['job_postings_fact.csv']
df_skills = dataframes['skills_dim.csv']
df_skills_job = dataframes['skills_job_dim.csv']

df_jobs_clean, df_skills_clean, df_skills_job_clean = preprocess_data(job_df, df_skills, df_skills_job)

if not os.path.exists('job_title_skill_count.csv'):
    with st.spinner("Creating summary file..."):
        create_view_model_top_skills(df_jobs_clean, df_skills_clean, df_skills_job_clean)


df_top10_skills = pd.read_csv('job_title_skill_count.csv')

# =========================================== SIDEBAR =======================================================
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
# =========================================== SIDEBAR =======================================================

if selected == "🏠 Introduction":
    st.title("💼 IT Job Market Explorer 2023")
elif selected == "💰 Salary":
    st.header("💰 Salary Analysis")
elif selected == "🛠️ Top Skills":
    st.header("🛠️ Top Skills")



    # Tambahkan visualisasi skills di sini
    def format_k(n):
        return f"{n / 1_000:.3f}K" if n >= 1_000 else str(n)
    
    st.markdown("""
        <style>
        div[data-baseweb="select"] > div {
            font-size: 20px;  /* ukuran teks dropdown */
        }
        label {
            font-size: 22px;  /* ukuran label 'Job Title :' */
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    #job title short
    filtered = df_top10_skills.copy()
    job_titles = ["Select All"] + sorted(filtered['job_title_short'].unique())

    selected_job_title = st.selectbox(
        "Job Title :",
        options=job_titles,
        key='job_title1',
        index=0
    )

    # type skills
    skill_type = ["All", "programming","databases", "webframeworks", "analyst_tools", "cloud", "os","sync","async", "other"]
    def format_label(option):
        if option == "databases":
            return "Databases"
        elif option == "analyst_tools":
            return "Tools"
        elif option == "programming":
            return "Languages"
        elif option == "webframeworks":
            return "Frameworks"
        elif option == "cloud":
            return "Cloud"
        elif option == "os":
            return "OS"
        elif option == "other":
            return "Other"
        else:
            return option
        

    selected_type_skill = st.radio(
        "Skills :",
        options=skill_type,
        index=0,
        format_func=format_label,
        horizontal=True
    )


    # Filter data
    if selected_job_title != "Select All":
        filtered = filtered[filtered['job_title_short'] == selected_job_title]

    if selected_type_skill != "All":
        filtered = filtered[filtered['type'] == selected_type_skill]


    # Total job postings (unik job_id)
    total_jobs = filtered['job_title'].nunique()

    # Hitung berapa job unik per skill
    skill_job_counts = filtered.groupby('skills')['job_title'].nunique()

    # Ambil top 20 skills berdasarkan jumlah job_id (bukan count rows)
    top10_skills = skill_job_counts.nlargest(20).index.dropna().tolist()

    # Hitung persentase per skill per total job_id
    percent_per_skill = (skill_job_counts[top10_skills] / total_jobs * 100).round(2)
    threshold = 0.05
    percent_per_skill = percent_per_skill[percent_per_skill >= threshold]

    # Urutkan skill berdasarkan persentase (atau tetap pakai original order, sesuai preferensi)
    skill_order = percent_per_skill.sort_values().index.tolist()
        
    colorscale = px.colors.sequential.Tealgrn[::-1]
    max_val = max(percent_per_skill[skill_order])
    xaxis_max = max_val + 5 if max_val + 5 <= 100 else 100

    bar_count = len(skill_order)
    fig_height = 700
    bar_slot = fig_height / bar_count
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
        # Text skill di kiri
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
        # Persentase di kanan
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
        newselection_line=dict(
            color='white',
            dash='solid'
        ),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor='#16213e',
            bordercolor='white',
            font=dict(color='white', size=0.75*font_size),
        ),
        hoverdistance=40,
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
