import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from preprocess_salary import load_salary_summary

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

@st.cache_data(show_spinner=False)
def salary_render():
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