import streamlit as st
import pandas as pd
import requests
import json
import tempfile
from pathlib import Path
from convert import convert_excel_to_glossary

# ===== Config OpenMetadata =====
OPENMETADATA_URL = st.secrets["OPENMETADATA_URL"]
TOKEN = st.secrets["TOKEN"]
GLOSSARY_ID = st.secrets["GLOSSARY_ID"]

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# ===== Function import terms =====
def import_glossary_terms(csv_file, glossary_id):
    df = pd.read_csv(csv_file)
    results = []
    for _, row in df.iterrows():
        term = {
            "name": row["name*"],
            "displayName": row.get("displayName", ""),
            "description": row.get("description", ""),
            "glossary": {
                "id": glossary_id,
                "type": "glossary"
            }
        }
        # Nếu có parent → cần xử lý mapping sang ID thật
        if row.get("parent"):
            term["parent"] = {
                "id": row["parent"],
                "type": "glossaryTerm"
            }

        res = requests.post(
            f"{OPENMETADATA_URL}/glossaryTerms",
            headers=headers,
            data=json.dumps(term)
        )
        if res.status_code in (200, 201):
            results.append((row["name*"], "✅ Imported"))
        else:
            results.append((row["name*"], f"❌ {res.text}"))
    return results


# ===== Streamlit UI =====
st.set_page_config(page_title="Excel → OpenMetadata Glossary (Multi-files)", layout="centered")
st.title("📑 Excel Glossary → OpenMetadata Importer (Multi-files)")

uploaded_files = st.file_uploader("Chọn nhiều file Excel", type=["xlsx", "xls"], accept_multiple_files=True)

if uploaded_files:
    st.info(f"Đã tải lên {len(uploaded_files)} file")

    if st.button("Convert & Import tất cả"):
        for uploaded_file in uploaded_files:
            with tempfile.TemporaryDirectory() as tmpdir:
                src = Path(tmpdir) / uploaded_file.name
                out_csv = Path(tmpdir) / (src.stem + "_converted.csv")

                # Save Excel tạm
                with open(src, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Convert sang CSV
                convert_excel_to_glossary(src, out_csv)

                # Import vào OpenMetadata
                results = import_glossary_terms(out_csv, GLOSSARY_ID)

                # Hiển thị kết quả từng file
                st.subheader(f"📊 Kết quả cho file: {uploaded_file.name}")
                for name, status in results:
                    st.write(f"- {name}: {status}")
