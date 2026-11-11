import pandas as pd
import numpy as np
import math
import re
import os
import streamlit as st

FILE_PATH = os.path.join("data", "Cleaned_Cohort_3_QSC.xlsx")
if not os.path.exists(FILE_PATH):
    FILE_PATH = "Cleaned_Cohort_3_QSC.xlsx"


def paired_ttest(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    diff = b - a
    n = len(diff)
    if n < 2:
        return 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0
    mean_a, std_a = np.mean(a), np.std(a, ddof=1)
    mean_b, std_b = np.mean(b), np.std(b, ddof=1)
    mean_d = np.mean(diff)
    std_d = np.std(diff, ddof=1)
    if std_d == 0:
        return 0.0, 1.0, mean_a, std_a, mean_b, std_b, 0.0
    t_stat = mean_d / (std_d / math.sqrt(n))
    z = abs(t_stat)
    p_val = math.erfc(z / math.sqrt(2))
    cohens_dz = mean_d / std_d if std_d > 0 else 0.0
    return (
        float(t_stat),
        float(p_val),
        float(mean_a),
        float(std_a),
        float(mean_b),
        float(std_b),
        float(cohens_dz),
    )


def clean_facility_filter(df):
    if df is None or df.empty:
        return df

    # Find the column containing facility names
    fac_col = None
    for col in df.columns:
        if any(k in str(col).lower() for k in ["facility", "site", "name", "health"]):
            fac_col = col
            break
    if fac_col is None:
        fac_col = df.columns[0]

    # Valid Cohort 3 target facilities
    valid_keywords = [
        "buyangu",
        "ingotse",
        "kaptama",
        "khasoko",
        "kolanya",
        "mercy",
        "mundoli",
        "namasoli",
        "namboboto",
        "charles",
        "martha",
        "pius",
        "monica",
    ]

    # Exclude facilities explicitly noted as non-QSC or invalid
    exclude_facilities = ["butula", "misikhu"]

    pattern = "|".join(valid_keywords)

    # Apply string filtering
    mask_valid = df[fac_col].astype(str).str.contains(pattern, case=False, na=False)
    mask_exclude = df[fac_col].astype(str).str.lower().isin(exclude_facilities)

    filtered = df[mask_valid & ~mask_exclude].copy()
    filtered = filtered.drop_duplicates(subset=[fac_col])

    return filtered


def get_cohort3_paired_ttest(is_medical=True):
    sheet_name = (
        "Medical QSC Performance" if is_medical else "Management QSC Performance"
    )
    if not os.path.exists(FILE_PATH):
        return None

    # Change sheet_name to 'Cleaned_Cohort3_QSC'
    # Read cleaned QSC file

    # Dynamically select sheet based on curriculum track
    # Select target sheet based on curriculum track for paired t-test
    sheet_name = (
        "Medical_QSC_Performance" if is_medical else "Management_QSC_Performance"
    )
    xl = pd.ExcelFile(FILE_PATH, engine="openpyxl")
    if sheet_name not in xl.sheet_names:
        sheet_name = xl.sheet_names[0]  # Safe fallback to first available sheet

    df = pd.read_excel(FILE_PATH, sheet_name=sheet_name, engine="openpyxl")
    df = clean_facility_filter(df)

    # Select target columns based on curriculum track
    # Auto-detect baseline and endline columns in the sheet
    b_col_name = None
    e_col_name = None

    for col in df.columns:
        col_str = str(col).lower()
        if "baseline" in col_str or "base" in col_str or "pre" in col_str:
            b_col_name = col
        elif "endline" in col_str or "end" in col_str or "post" in col_str:
            e_col_name = col

    # Fallback to column indices 1 and 2 if specific names aren't matched
    if not b_col_name and len(df.columns) > 1:
        b_col_name = df.columns[1]
    if not e_col_name and len(df.columns) > 2:
        e_col_name = df.columns[2]

    if not b_col_name or not e_col_name:
        st.warning(f"Columns in sheet are: {list(df.columns)}")
        return Noneß

    b_series = pd.to_numeric(df[b_col_name], errors="coerce").dropna()
    e_series = pd.to_numeric(df[e_col_name], errors="coerce").dropna()

    common_idx = b_series.index.intersection(e_series.index)

    b_arr = b_series.loc[common_idx].values
    e_arr = e_series.loc[common_idx].values

    t_stat, p_val, m_a, s_a, m_b, s_b, dz = paired_ttest(b_arr, e_arr)

    return {
        "Module": (
            "Module 1: Back to Basics" if is_medical else "Module 1: Governance & Ops"
        ),
        "Baseline_Mean": round(m_a, 2),
        "Baseline_SD": round(s_a, 2),
        "Endline_Mean": round(m_b, 2),
        "Endline_SD": round(s_b, 2),
        "Mean_Gain": round(m_b - m_a, 2),
        "Cohen_dz": round(dz, 2),
        "p_value": p_val,
        "N": len(b_arr),
        "b_arr": b_arr,
        "e_arr": e_arr,
    }


def get_cohort3_item_scorecard(is_medical=True):
    sheet_base = (
        "Medical All Items Baseline" if is_medical else "Management Baseline All Items"
    )
    sheet_end = (
        "Medical All Items Endline" if is_medical else "Management All Items Endline"
    )
    prefix = "V2med - qsc - M1-" if is_medical else "man - qsc -"

    if not os.path.exists(FILE_PATH):
        return pd.DataFrame(), pd.DataFrame()

    try:
        df_base = pd.read_excel(FILE_PATH, sheet_name=sheet_base)
        df_end = pd.read_excel(FILE_PATH, sheet_name=sheet_end)

        df_base = clean_facility_filter(df_base)
        df_end = clean_facility_filter(df_end)

        items_summary = []
        end_cols = [c for c in df_end.columns if c.startswith(prefix)]

        for e_col in end_cols:
            col_clean = e_col.split(". ")[-1].strip() if ". " in e_col else e_col
            code_match = re.search(r"(M1-\d+|AM1-\d+|F1-\d+|E1-\d+)", e_col)
            code = code_match.group(0) if code_match else "M1"

            best_b_col = None
            for b_col in df_base.columns:
                if code in b_col or col_clean.lower()[:15] in str(b_col).lower():
                    best_b_col = b_col
                    break

            if best_b_col:
                b_vals = pd.to_numeric(df_base[best_b_col], errors="coerce").fillna(0)
                e_vals = pd.to_numeric(df_end[e_col], errors="coerce").fillna(0)

                b_pct = (
                    (b_vals.mean() / (5.0 if b_vals.max() <= 5 else b_vals.max()) * 100)
                    if b_vals.max() > 0
                    else 0
                )
                e_pct = (
                    (e_vals.mean() / (5.0 if e_vals.max() <= 5 else e_vals.max()) * 100)
                    if e_vals.max() > 0
                    else 0
                )

                items_summary.append(
                    {
                        "Code": code,
                        "Indicator": col_clean,
                        "Baseline": round(b_pct, 1),
                        "Endline": round(e_pct, 1),
                        "Gain": round(e_pct - b_pct, 1),
                    }
                )

        df_all = pd.DataFrame(items_summary)
        if df_all.empty:
            return pd.DataFrame(), pd.DataFrame()

        df_top10 = df_all.sort_values(by="Gain", ascending=False).head(10)
        df_bot10 = df_all.sort_values(by="Endline", ascending=True).head(10)

        return df_top10, df_bot10

    except Exception as e:
        print(f"Error reading Cohort 3 items: {e}")
        return pd.DataFrame(), pd.DataFrame()
