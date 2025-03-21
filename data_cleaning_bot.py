import streamlit as st
import pandas as pd
import os

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
- Instantly remove duplicates & clean missing values
- Download your cleaned file 🚀
""")

# ---- Sidebar Info ----
st.sidebar.header("About")
st.sidebar.info("""
This bot helps automate basic data cleaning tasks using **Python & Streamlit**.

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
        
        # Cleaning steps
        df_cleaned = df.drop_duplicates()
        df_cleaned = df_cleaned.fillna('N/A')
        df_cleaned.columns = [col.strip().lower().replace(' ', '_') for col in df_cleaned.columns]
        
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
