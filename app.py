import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
from convert import convert_excel_to_glossary

st.set_page_config(page_title="Excel → CSV Converter", layout="centered")

st.title("📑 Excel Glossary → CSV Converter")
st.write("Upload file Excel glossary và tải về file CSV chuẩn cho OpenMetadata.")

# Upload Excel file
uploaded_file = st.file_uploader("Chọn file Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    st.success(f"Đã tải lên: {uploaded_file.name}")

    # Nút chạy convert
    if st.button("Convert to CSV"):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / uploaded_file.name
            out_csv = Path(tmpdir) / (src.stem + "_converted.csv")

            # Lưu file Excel tạm
            with open(src, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Gọi hàm convert trong convert.py
            convert_excel_to_glossary(src, out_csv)

            # Hiển thị preview
            df_preview = pd.read_csv(out_csv)
            st.subheader("📊 Preview kết quả (5 dòng đầu)")
            st.dataframe(df_preview.head())

            # Cho tải về file CSV
            with open(out_csv, "rb") as f:
                st.download_button(
                    label="⬇️ Tải CSV",
                    data=f,
                    file_name=out_csv.name,
                    mime="text/csv"
                )
