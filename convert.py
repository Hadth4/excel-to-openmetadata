#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chuyển đổi Excel glossary sang CSV chuẩn cho OpenMetadata
"""

import argparse
import pandas as pd
from pathlib import Path


def convert_excel_to_glossary(src: Path, out_csv: Path):
    # Đọc sheet đầu tiên
    df = pd.read_excel(src, sheet_name=0)

    # Loại bỏ khoảng trắng thừa trong tên cột
    df.columns = [str(x).strip() for x in df.columns]

    # Tạo DataFrame kết quả với header chuẩn
    out_df = pd.DataFrame({
        "parent": df["parent"],
        "name*": df["name*"],
        "displayName": df["displayName"],
        "description": df["description"],
        "synonyms": df["synonyms"],
        "relatedTerms": df["relatedTerms"],
        "references": df["references"],
        "tags": df["tags"],
        "reviewers": df["reviewers"],
        "owner": df["owner"],
        "glossaryStatus": df["glossaryStatus"],
    })

    # Điền giá trị rỗng cho các ô NaN
    out_df = out_df.fillna('')

    # Hàm build extension dựa trên cấu trúc của KS_Demo.csv
    def make_extension(row):
        props = {
            "codeDocuments": row['codeDocuments'],
            "confidentialData": row['confidentialData'],
            "corePersonalData": row['corePersonalData'],
            "dataReadiness": row['dataReadiness'],
            "dataSource": row['dataSource'],
            "frequency": row['frequency'],
            "functionsAndDuties": row['functionsAndDuties'],
            "id": row['ID'],
            "importantData": row['importantData'],
            "masterData": row['masterData'],
            "nameSurveyUnit": row['nameSurveyUnit'],
            "nationalConfidentialData": row['nationalConfidentialData'],
            "openData": row['openData'],
            "referenceData": row['referenceData'],
            "sensitivePersonalData": row['sensitivePersonalData'],
            "unit": row['unit'],
        }
        fields = []
        for key, value in props.items():
            if pd.isna(value):
                continue
            str_value = str(value).strip()
            # Xử lý đặc biệt cho codeDocuments: thay thế newline bằng space
            if key == "codeDocuments":
                str_value = str_value.replace('\n', ' ')
            # Chuẩn hóa dataReadiness
            if key == "dataReadiness" and str_value:
                str_value = str_value.lower().strip()  # Chuẩn hóa chữ thường và loại bỏ khoảng trắng thừa
                if not str_value:  # Nếu trống hoặc null
                    str_value = "0. Chưa có dữ liệu"
                elif "chưa hệ thống" in str_value or "1. có dữ liệu" in str_value:
                    str_value = "1. Có dữ liệu, chưa hệ thống"
            # Quote giá trị nếu chứa ký tự đặc biệt, nhưng bỏ qua quote cho dataReadiness nếu là enum hợp lệ
            if any(c in str_value for c in ' ,;:"') and key != "dataReadiness":
                str_value = f'"{str_value.replace('"', '""')}"'
            fields.append(f"{key}:{str_value}")
        return ";".join(fields) if fields else ""

    out_df["extension"] = df.apply(make_extension, axis=1)

    # Ghi file CSV với định dạng chính xác như KS_Demo.csv
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_csv, index=False, encoding="utf-8-sig")  # Sử dụng quoting mặc định (QUOTE_MINIMAL)
    print("✅ Wrote:", out_csv)


def main():
    ap = argparse.ArgumentParser(description="Convert Excel → CSV Glossary chuẩn cho OpenMetadata")
    ap.add_argument("--in", dest="inp", required=True, help="File Excel nguồn (vd: XuLy.xlsx)")
    ap.add_argument("--out", dest="out_csv", required=True, help="File CSV đích (vd: XuLy_converted.csv)")
    args = ap.parse_args()

    src = Path(args.inp)
    out_csv = Path(args.out_csv)

    if src.is_file() and src.suffix.lower() in (".xlsx", ".xls"):
        convert_excel_to_glossary(src, out_csv)
    else:
        print("⚠️ Input không phải Excel file:", src)


if __name__ == "__main__":
    main()