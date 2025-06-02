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
        url = f'https://drive.google.com/uc?id={file_id}'
        if not os.path.exists(filename):
            gdown.download(url, filename, quiet=True)
        df = pd.read_csv(filename)
        dataframes[filename] = df
    return dataframes
