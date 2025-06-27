import streamlit as st
import pandas as pd
import os
from io import BytesIO
import zipfile

st.set_page_config(page_title="File Renamer & Zipper", layout="centered")
st.title("📁 File Renaming Tool (Upload → Rename → Download ZIP)")

# Step 1: Upload multiple files
st.header("📌 Step 1: Upload Your Files")
uploaded_files = st.file_uploader(
    "Select multiple files to rename",
    accept_multiple_files=True,
    type=None
)

# Step 2: Download sample CSV template
st.header("📄 Step 2: Download Rename Template")

# Create a sample CSV in memory
sample_df = pd.DataFrame({
    "Old File Name": ["example1.pdf", "example2.png"],
    "New File Name": ["invoice_2024.pdf", "logo_final.png"]
})

csv_buffer = BytesIO()
sample_df.to_csv(csv_buffer, index=False)
csv_buffer.seek(0)

# Display download button
st.download_button(
    label="📥 Download Sample CSV Template",
    data=csv_buffer,
    file_name="file_rename_template.csv",
    mime="text/csv"
)

# Step 3: Upload rename mapping CSV
st.header("📂 Step 3: Upload CSV with Rename Mapping")
csv_file = st.file_uploader("Upload CSV file", type=["csv"])

# Step 4: Process and rename
if st.button("▶️ Rename Files & Download ZIP"):
    if not uploaded_files or not csv_file:
        st.error("❌ Please upload both files and the CSV file.")
    else:
        try:
            df = pd.read_csv(csv_file)
            if "Old File Name" not in df.columns or "New File Name" not in df.columns:
                st.error("❌ CSV must contain 'Old File Name' and 'New File Name' columns.")
            else:
                rename_map = dict(zip(df["Old File Name"].str.strip(), df["New File Name"].str.strip()))
                memory_zip = BytesIO()

                renamed, skipped = 0, 0

                with zipfile.ZipFile(memory_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file in uploaded_files:
                        original_name = file.name.strip()

                        if original_name in rename_map:
                            new_name = rename_map[original_name]
                            file_bytes = file.read()
                            zipf.writestr(new_name, file_bytes)
                            st.success(f"✅ Renamed: {original_name} → {new_name}")
                            renamed += 1
                        else:
                            st.warning(f"⚠️ No match in CSV for: {original_name}")
                            skipped += 1

                memory_zip.seek(0)

                # Show ZIP download button
                st.download_button(
                    label="📦 Download Renamed Files as ZIP",
                    data=memory_zip,
                    file_name="Renamed_Files.zip",
                    mime="application/zip"
                )

                st.info(f"✅ Files Renamed: {renamed}, ⚠️ Skipped (no match): {skipped}")
        except Exception as e:
            st.error(f"❌ Error processing CSV: {e}")

# Footer
st.markdown("---")
st.caption("🔒 Files are processed in your browser session and not saved on any server.")
