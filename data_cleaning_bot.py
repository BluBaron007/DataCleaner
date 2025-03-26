import streamlit as st
import pandas as pd
import numpy as np
import os
from scipy import stats

# Streamlit UI Setup
st.set_page_config(page_title="Advanced Data Cleaning Bot", page_icon="🧹", layout="centered")
st.title("🧹 Data Cleaning Bot with Custom Fill Options")

# Sidebar Info
st.sidebar.header("About")
st.sidebar.info("Clean your data interactively. Choose how to fill missing values for each column.")

uploaded_file = st.file_uploader("📂 Upload a CSV or Excel file", type=["csv", "xlsx"])

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

        cleaning_log = []

        # Remove duplicates
        num_duplicates = df.duplicated().sum()
        df = df.drop_duplicates()
        cleaning_log.append(f"✔ Removed {num_duplicates} duplicate rows.")

        # Handle missing values with user input
        st.subheader("🧩 Handle Missing Values")
        fill_choices = {}
        for col in df.columns[df.isnull().any()]:
            dtype = df[col].dtype
            st.markdown(f"**Column:** `{col}` — Missing: {df[col].isnull().sum()}")

            options = ["Median", "Mean", "Mode", "Custom Value", "Leave as N/A"]
            choice = st.selectbox(f"Fill strategy for `{col}`", options, key=col)

            custom_value = None
            if choice == "Custom Value":
                if np.issubdtype(dtype, np.number):
                    custom_value = st.number_input(f"Enter custom numeric value for `{col}`", key=col + "_custom")
                else:
                    custom_value = st.text_input(f"Enter custom value for `{col}`", key=col + "_custom")

            fill_choices[col] = (choice, custom_value)

        if st.button("🧼 Clean Data"):
            for col, (choice, custom_value) in fill_choices.items():
                if choice == "Median":
                    val = df[col].median()
                elif choice == "Mean":
                    val = df[col].mean()
                elif choice == "Mode":
                    val = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"
                elif choice == "Custom Value":
                    val = custom_value
                elif choice == "Leave as N/A":
                    val = None

                if val is not None:
                    df[col].fillna(val, inplace=True)
                    cleaning_log.append(f"✔ Filled missing values in `{col}` with {choice} ({val})")
                else:
                    cleaning_log.append(f"✔ Left missing values in `{col}` as N/A")

            # Data type conversions
            conversions = []
            for col in df.columns:
                if df[col].dtype == object:
                    try:
                        df[col] = pd.to_datetime(df[col])
                        conversions.append(f"`{col}` → datetime")
                    except:
                        try:
                            df[col] = pd.to_numeric(df[col])
                            conversions.append(f"`{col}` → numeric")
                        except:
                            continue
            cleaning_log.append("✔ Data type conversions: " + ", ".join(conversions) if conversions else "✔ No data type conversions applied.")

            # Outlier removal using Z-score
            numeric_df = df.select_dtypes(include=[np.number])
            z_scores = np.abs(stats.zscore(numeric_df, nan_policy='omit'))
            outliers = (z_scores > 3).any(axis=1)
            num_outliers = outliers.sum()
            df = df[~outliers]
            cleaning_log.append(f"✔ Removed {num_outliers} outlier rows using Z-score.")

            # Clean column names
            df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

            st.subheader("✨ Cleaned Data Preview")
            st.dataframe(df.head(), use_container_width=True)

            # Save cleaned file
            cleaned_filename = f"cleaned_{uploaded_file.name.replace(' ', '_')}"
            df.to_csv(cleaned_filename, index=False)

            with open(cleaned_filename, "rb") as file:
                st.download_button(label="📥 Download Cleaned File", data=file, file_name=cleaned_filename, mime='text/csv')

            st.success("🎉 Cleaning complete!")

            # Display cleaning summary
            st.subheader("📋 Cleaning Summary")
            for log in cleaning_log:
                st.write(log)

            # Cleanup
            os.remove(cleaned_filename)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("⬆️ Upload a file to begin.")
