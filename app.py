import streamlit as st
import pandas as pd

st.title("My First Streamlit Cloud App 🎉")

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Preview Data:", df.head())

    st.subheader("Basic Stats")
    st.write(df.describe())
