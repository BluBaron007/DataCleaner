import streamlit as st
import pandas as pd
import numpy as np
import os
from scipy import stats

# ---- Custom CSS Styling ----
st.set_page_config(page_title="Data Cleaning Bot", page_icon="🧹", layout="centered")
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
    }
    .stButton > button {
        color: white;
        background-color: #4CAF50;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: none;
    }
    .stFileUploader {
        background-color: white;
        padding: 1rem;
        border: 2px dashed #4CAF50;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- App Title & Description ----
st.title("🧹 Clean & Process Your Data Easily")
st.write("""
Welcome to the **Data Cleaning Bot!**

- Upload your CSV or Excel files 📄
- Remove duplicates, fill missing values, fix data types
- Remove numeric outliers 
""")

# ---- Sidebar Info ----
st.sidebar.header("About")
st.sidebar.info("""
This bot helps automate advanced data cleaning tasks using **Python & Streamlit**.

Author: Jalen Claytor
""")

# ---- File Uploader ----
uploaded_file = st.file_uploader("📂 Upload your file", type=["csv", "xlsx"])

if uploaded_file is not None:
    st.success(f"✅ Uploaded file: {uploaded_file.name}")

    try:
        # Read file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("🔍 Raw Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        # ---- Cleaning Steps ----

        # 1. Remove duplicates
        df_cleaned = df.drop_duplicates()

        # 2. Fill missing values
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype in [np.float64, np.int64]:
                df_cleaned[col].fillna(df_cleaned[col].median(), inplace=True)
            elif df_cleaned[col].dtype == object:
                df_cleaned[col].fillna(df_cleaned[col].mode()[0] if not df_cleaned[col].mode().empty else "N/A", inplace=True)
            else:
                df_cleaned[col].fillna("N/A", inplace=True)

        # 3. Standardize column names
        df_cleaned.columns = [col.strip().lower().replace(' ', '_') for col in df_cleaned.columns]

        # 4. Enforce data types
        for col in df_cleaned.columns:
            try:
                df_cleaned[col] = pd.to_numeric(df_cleaned[col])
            except:
                try:
                    df_cleaned[col] = pd.to_datetime(df_cleaned[col])
                except:
                    pass

        # 5. Remove numeric outliers (Z-score method)
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        df_cleaned = df_cleaned[(np.abs(stats.zscore(df_cleaned[numeric_cols], nan_policy='omit')) < 3).all(axis=1)]

        st.subheader("✨ Cleaned Data Preview")
        st.dataframe(df_cleaned.head(), use_container_width=True)

        # Save cleaned file
        cleaned_filename = f"cleaned_{uploaded_file.name.replace(' ', '_')}"
        df_cleaned.to_csv(cleaned_filename, index=False)

        # Download button
        with open(cleaned_filename, "rb") as file:
            st.download_button(label="📥 Download Cleaned File", data=file, file_name=cleaned_filename, mime='text/csv')

        st.success("🎉 Cleaning complete! Download your file above.")

        # Cleanup temp file
        os.remove(cleaned_filename)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("⬆️ Please upload a CSV or Excel file to get started.")
