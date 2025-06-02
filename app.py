import streamlit as st
import pandas as pd
import gdown
import os

st.title("Load Large CSV (>100mb) from Google Drive with gdown 🚀")

file_id = '1drExsbrK32VjG5Xh_CAmtZ7jtPs-S0fU'
url = f'https://drive.google.com/uc?id={file_id}'

output = 'job_postings_fact.csv'

# Download file cuma sekali, kalau belum ada
if not os.path.exists(output):
    with st.spinner("Downloading file..."):
        gdown.download(url, output, quiet=False)
else:
    st.info("File already downloaded.")

try:
    df = pd.read_csv(output)
    st.success("Data loaded successfully!")
    st.write(df.head())

    st.subheader("Summary Stats")
    st.write(df.describe())

except Exception as e:
    st.error(f"Failed to load data: {e}")
