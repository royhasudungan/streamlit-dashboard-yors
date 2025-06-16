import time
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from preprocess_top_skills import load_top_skills_summary
from preprocess_demand_skills import load_demand_skills

@st.cache_data(show_spinner=False)
def top_skills_render():
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