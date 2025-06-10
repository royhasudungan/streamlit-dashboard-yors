import pandas as pd
import gdown
import os
import streamlit as st

files = {
    'job_postings_fact.csv': '1drExsbrK32VjG5Xh_CAmtZ7jtPs-S0fU',
    'skills_dim.csv': '1YxJej2L9yNMJXLshuUcV06Zll2zaaFH9',
    'skills_job_dim.csv': '1eq7osBABUfja8W3nO5S1JrQK50pYN4nK'
}

@st.cache_data(show_spinner=False)
def download_and_load_csv():
    dataframes = {}
    for filename, file_id in files.items():
        parquet_file = filename.replace('.csv', '.parquet')

        # Download CSV kalau belum ada
        if not os.path.exists(filename):
            url = f'https://drive.google.com/uc?id={file_id}'
            gdown.download(url, filename, quiet=True)

        # Load dari parquet kalau ada, kalau nggak load csv dan simpan parquet
        if os.path.exists(parquet_file):
            df = pd.read_parquet(parquet_file)
        else:
            df = pd.read_csv(filename, low_memory=False)
            df.to_parquet(parquet_file)

        dataframes[filename] = df
    return dataframes


