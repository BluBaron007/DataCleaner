import streamlit as st
import pandas as pd
import numpy as np
import os
from scipy import stats

# ---- Custom CSS Styling (Olive Theme) ----
st.set_page_config(page_title="Data Cleaning Bot", page_icon="🧹", layout="centered")
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f6f9f6;
    }

    .main {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 2rem;
    }

    .stButton > button {
        background-color: #556B2F;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #3e4e20;
        color: white;
    }

    .stFileUploader {
        border: 2px dashed #556B2F;
        background-color: #eef2e6;
        padding: 1rem;
        border-radius: 10px;
    }

    .stTextInput > div > input,
    .stNumberInput > div > input,
    .stSelectbox > div {
        background-color: #f9fcf6;
        border: 1px solid #556B2F;
        border-radius: 6px;
        padding: 0.4rem;
    }

    .stDataFrame {
        border: 1px solid #cdd8c3;
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #556B2F;
    }

    .stAlert {
        border-left: 5px solid #556B2F !important;
        background-color: #f6fbf3 !important;
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
- Remove duplicates, optionally fill missing values, fix data types
- Remove numeric outliers and view a detailed cleaning summary 🚀
""")

# ---- Sidebar Info ----
st.sidebar.header("About")
st.sidebar.info("""
This bot helps automate advanced data cleaning tasks using **Python**.

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
        summary_log = []

        # 1. Remove duplicates
        dup_count = df.duplicated().sum()
        df_cleaned = df.drop_duplicates()
        summary_log.append(f"✔ {dup_count} duplicate rows removed.")

        # 2. Prompt user for how to handle missing values
        st.subheader("🧩 Handle Missing Values")
        fill_strategies = {}
        for col in df_cleaned.columns:
            if df_cleaned[col].isna().sum() > 0:
                strategy = st.selectbox(
                    f"Column '{col}' has {df_cleaned[col].isna().sum()} missing values. Choose a fill method:",
                    ["Leave as is", "Median", "Mean", "Mode"],
                    key=col
                )
                fill_strategies[col] = strategy

        # Apply selected fill strategies
        missing_filled = {}
        for col, strategy in fill_strategies.items():
            missing_before = df_cleaned[col].isna().sum()
            if strategy == "Median":
                df_cleaned[col].fillna(df_cleaned[col].median(), inplace=True)
                missing_filled[col] = f"filled {missing_before} NaNs with median ({df_cleaned[col].median()})"
            elif strategy == "Mean":
                df_cleaned[col].fillna(df_cleaned[col].mean(), inplace=True)
                missing_filled[col] = f"filled {missing_before} NaNs with mean ({df_cleaned[col].mean()})"
            elif strategy == "Mode":
                mode_val = df_cleaned[col].mode()[0] if not df_cleaned[col].mode().empty else "N/A"
                df_cleaned[col].fillna(mode_val, inplace=True)
                missing_filled[col] = f"filled {missing_before} NaNs with mode ('{mode_val}')"
            else:
                missing_filled[col] = "left unchanged"

        if missing_filled:
            summary_log.append("✔ Missing values handled:")
            for col, msg in missing_filled.items():
                summary_log.append(f"    - '{col}': {msg}")

        # 3. Standardize column names
        df_cleaned.columns = [col.strip().lower().replace(' ', '_') for col in df_cleaned.columns]

        # 4. Enforce data types
        conversions = []
        for col in df_cleaned.columns:
            original_dtype = df_cleaned[col].dtype
            try:
                df_cleaned[col] = pd.to_numeric(df_cleaned[col])
                conversions.append(f"'{col}': converted to numeric")
            except:
                try:
                    df_cleaned[col] = pd.to_datetime(df_cleaned[col])
                    conversions.append(f"'{col}': converted to datetime")
                except:
                    conversions.append(f"'{col}': kept as {original_dtype}")
        summary_log.append("✔ Data type conversions:")
        summary_log.extend([f"    - {c}" for c in conversions])

        # 5. Remove numeric outliers (Z-score method)
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        before_rows = df_cleaned.shape[0]
        df_cleaned = df_cleaned[(np.abs(stats.zscore(df_cleaned[numeric_cols], nan_policy='omit')) < 3).all(axis=1)]
        after_rows = df_cleaned.shape[0]
        outliers_removed = before_rows - after_rows
        summary_log.append(f"✔ {outliers_removed} outlier rows removed from numeric columns.")

        st.subheader("✨ Cleaned Data Preview")
        st.dataframe(df_cleaned.head(), use_container_width=True)

        # Save cleaned file
        cleaned_filename = f"cleaned_{uploaded_file.name.replace(' ', '_')}"
        df_cleaned.to_csv(cleaned_filename, index=False)

        # Download button
        with open(cleaned_filename, "rb") as file:
            st.download_button(label="📥 Download Cleaned File", data=file, file_name=cleaned_filename, mime='text/csv')

        st.success("🎉 Cleaning complete! Download your file above.")

        # Show summary
        st.subheader("🧾 Cleaning Summary")
        for line in summary_log:
            st.write(line)

        # Cleanup temp file
        os.remove(cleaned_filename)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("⬆️ Please upload a CSV or Excel file to get started.")
