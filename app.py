import pandas as pd
import streamlit as st
import os
from io import BytesIO
import zipfile

st.set_page_config(page_title="File Renamer & Zipper", layout="centered")
st.title("📁 Local File Renamer & ZIP Downloader")

# Step 1: Upload multiple files
st.header("Step 1: Upload Your Files")
uploaded_files = st.file_uploader("Select multiple files", type=None, accept_multiple_files=True)

# Step 2: Upload CSV mapping
st.header("Step 2: Upload Rename Mapping (CSV)")
csv_file = st.file_uploader("Upload CSV with 'Old File Name' and 'New File Name'", type=["csv"])

# Step 3: Rename and generate zip
if st.button("Rename and Download ZIP"):
    if not uploaded_files or not csv_file:
        st.error("Please upload both files and the CSV.")
    else:
        try:
            df = pd.read_csv(csv_file)
            if "Old File Name" not in df.columns or "New File Name" not in df.columns:
                st.error("CSV must contain 'Old File Name' and 'New File Name' columns.")
            else:
                rename_map = dict(zip(df["Old File Name"].str.strip(), df["New File Name"].str.strip()))
                memory_zip = BytesIO()

                with zipfile.ZipFile(memory_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                    renamed, skipped = 0, 0
                    for file in uploaded_files:
                        original_name = file.name.strip()
                        if original_name in rename_map:
                            new_name = rename_map[original_name]
                            zipf.writestr(new_name, file.read())
                            st.success(f"Renamed: {original_name} → {new_name}")
                            renamed += 1
                        else:
                            st.warning(f"No match found in CSV for: {original_name}")
                            skipped += 1

                memory_zip.seek(0)
                st.download_button(
                    label="📦 Download Renamed Files as ZIP",
                    data=memory_zip,
                    file_name="Renamed_Files.zip",
                    mime="application/zip"
                )
                st.info(f"✅ Renamed: {renamed}, ⚠️ Skipped: {skipped}")
        except Exception as e:
            st.error(f"Error during processing: {e}")
