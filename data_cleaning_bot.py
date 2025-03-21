import streamlit as st
import pandas as pd
import os

# Streamlit UI
st.title("Data Cleaning & Processing Bot 🤖")
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    st.write(f"Received file: {uploaded_file.name}")
    
    # Read file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.write("### Raw Data Preview", df.head())
    
    # Cleaning steps
    df = df.drop_duplicates()
    df = df.fillna('N/A')
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
    
    st.write("### Cleaned Data Preview", df.head())
    
    # Save cleaned file
    cleaned_filename = f"cleaned_{uploaded_file.name.replace(' ', '_')}"
    df.to_csv(cleaned_filename, index=False)
    
    # Provide download button
    with open(cleaned_filename, "rb") as file:
        st.download_button(label="Download Cleaned File", data=file, file_name=cleaned_filename, mime='text/csv')
    
    st.success("Cleaning complete! Download your file above.")
