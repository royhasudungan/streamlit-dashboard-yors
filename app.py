import streamlit as st
import pandas as pd

st.title("Load CSV from Google Drive 🚀")

# Google Drive file ID
file_id = '1drExsbrK32VjG5Xh_CAmtZ7jtPs'
url = f'https://drive.google.com/uc?id={file_id}'
# Load data
try:
    df = pd.read_csv(url)
    st.success("Data loaded successfully!")
    st.write(df.head())

    # Basic stats
    st.subheader("Summary Stats")
    st.write(df.describe())

    # Add more visualizations here...
except Exception as e:
    st.error(f"Failed to load data: {e}")
