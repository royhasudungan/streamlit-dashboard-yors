import streamlit as st
import pydeck as pdk
import pandas as pd
from preprocess_location import load_job_country_summary


@st.cache_data(show_spinner=False)
def location_render():
    st.header("🌍 Job Openings by Country")
    st.markdown("This map shows the distribution of job vacancies across countries from the dataset.")

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