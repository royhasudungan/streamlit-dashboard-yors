import streamlit as st
import pandas as pd

st.title("Load CSV <100 mb from Google Drive 🚀")

file_id = '1yqlyO577VtMn-xfJ2g_efxwaM0H8Y1dc'
url = f'https://drive.google.com/uc?export=download&id={file_id}'

try:
    df = pd.read_csv(url)
    st.success("Data loaded successfully!")
    st.write(df.head())

    st.subheader("Summary Stats")
    st.write(df.describe())

except Exception as e:
    st.error(f"Failed to load data: {e}")
