import pandas as pd
import gdown
import os
import streamlit as st

files = {
    'job_postings_fact.parquet': '19I6zhi6y-ETs2A25RfAZbxNjcWz6RhOO',
    'skills_dim.parquet': '1DCAqlJuA2TbCvpuB0Kvp8dvY9hoH09L7',
    'skills_job_dim.parquet': '1ZVSyFBSLQJzv8n6oqERhpOHY2j2gVlWs'
}

@st.cache_data(show_spinner=False)
def download_and_load_parquet():
    dataframes = {}
    for filename, file_id in files.items():
        url = f'https://drive.google.com/uc?id={file_id}'
        if not os.path.exists(filename):
            gdown.download(url, filename, quiet=True)
        df = pd.read_parquet(filename)
        dataframes[filename] = df
    return dataframes


