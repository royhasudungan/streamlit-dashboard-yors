import streamlit as st
from preprocess_introduction import load_job_country, load_job_summary_stats,load_skill_type_distribution,load_top_job_title_summary
import plotly.graph_objects as go
import plotly.express as px

@st.cache_data(show_spinner=False)
def introduction_render():
    st.title("💼 IT Job Market Explorer 2023")
    st.markdown("---")

    top_jobs_df = load_top_job_title_summary()
    summary_stats = load_job_summary_stats()
    


    total_jobs = summary_stats["total_jobs"].iloc[0]
    avg_salary = summary_stats["avg_salary"].iloc[0]

    # Layout dua kolom
    col1,col2 = st.columns([1,1])

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
                text='Top 5 Most In-Demand <br> Data IT Job Roles',
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
                text='Skill Type Distribution <br> by Percentage',
                x=0.5,
                xanchor='center',
                font=dict(size=25, color='white')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=15),
            margin=dict(t=40, b=40, l=20, r=70),
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
        n_locations = country_df['country'].nunique()

        # Hitung jumlah job per country, urut dari terbesar
        job_counts = country_df.set_index('country')['job_count'].sort_values(ascending=False).head(10)


        # Buat bar chart
        fig = go.Figure(go.Bar(
            x=job_counts.index,
            y=job_counts.values,
            marker_color='royalblue',
            hovertemplate='%{x}<br>Jobs: %{y}<extra></extra>'
        ))

        fig.update_layout(
            title= dict(
                text='🌍 Job Locations',
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
    
    st.markdown("---")
    # Journey Steps
    st.markdown("## 🗺️ Your Exploration Journey")
    
    # Create better spacing for journey steps
    step1, step2, step3 = st.columns(3)
    
    with step1:
        st.markdown("""
        <div style="background: #f8fafc; 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    text-align: center;
                    border: 2px solid #e2e8f0;
                    height: 180px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📍</div>
            <h4 style="color: #667eea; margin-bottom: 0.5rem;">Explore</h4>
            <p style="color: #4a5568; margin: 0; font-size: 0.9rem;">
                Navigate through different sections using the sidebar
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with step2:
        st.markdown("""
        <div style="background: #f8fafc; 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    text-align: center;
                    border: 2px solid #e2e8f0;
                    height: 180px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🔍</div>
            <h4 style="color: #667eea; margin-bottom: 0.5rem;">Analyze</h4>
            <p style="color: #4a5568; margin: 0; font-size: 0.9rem;">
                Dive deep into salary trends and market insights
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with step3:
        st.markdown("""
        <div style="background: #f8fafc; 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    text-align: center;
                    border: 2px solid #e2e8f0;
                    height: 180px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🎯</div>
            <h4 style="color: #667eea; margin-bottom: 0.5rem;">Decide</h4>
            <p style="color: #4a5568; margin: 0; font-size: 0.9rem;">
                Make informed career decisions with data
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to Action
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2.5rem; 
                border-radius: 12px; 
                text-align: center; 
                color: white; 
                margin: 2rem 0;">
        <h3 style="margin-bottom: 1rem; font-weight: 300;">Ready to Shape Your Future? 🚀</h3>
        <p style="font-size: 1.1rem; margin-bottom: 1.5rem; opacity: 0.95;">
            Use the sidebar to navigate through detailed analytics and uncover the opportunities that await you in the IT industry
        </p>
        <div style="background: rgba(255,255,255,0.2); 
                    padding: 0.8rem 2rem; 
                    border-radius: 25px; 
                    display: inline-block; 
                    backdrop-filter: blur(10px);">
            ✨ Start exploring now and discover your next career move!
        </div>
    </div>
    """, unsafe_allow_html=True)