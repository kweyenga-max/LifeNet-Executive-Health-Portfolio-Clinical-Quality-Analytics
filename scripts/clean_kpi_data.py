import os
import pandas as pd
import numpy as np

data_dir = "data"
raw_kpi_file = os.path.join(data_dir, "Key Performing Indicators for Program Monitoring.xls")
output_kpi_file = os.path.join(data_dir, "Cleaned_KPI_Master.xlsx")

print("🔄 Executing Complete Longitudinal KPI Data Pipeline...")

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

QUARTERS = {
    "Q1": ["January", "February", "March"],
    "Q2": ["April", "May", "June"],
    "Q3": ["July", "August", "September"],
    "Q4": ["October", "November", "December"]
}

BIANNUAL = {
    "H1": ["January", "February", "March", "April", "May", "June"],
    "H2": ["July", "August", "September", "October", "November", "December"]
}

try:
    xl = pd.ExcelFile(raw_kpi_file, engine="xlrd")
    cleaned_master_sheets = {}
    quality_audit_records = []

    for sheet in xl.sheet_names:
        # Determine target year from sheet name
        year_str = "2025" if "2025" in sheet else "2026"
        df_raw = pd.read_excel(raw_kpi_file, sheet_name=sheet, header=1, engine="xlrd")
        
        # Clean column whitespace
        df_raw.columns = [" ".join(str(c).split()) for c in df_raw.columns]
        facility_col = df_raw.columns[0]
        df_raw.rename(columns={facility_col: "organisationunitname"}, inplace=True)
        df_raw = df_raw.dropna(subset=["organisationunitname"]).copy()

        # Zero-fill numeric entries (KHIS reporting standard)
        indicator_cols = [c for c in df_raw.columns if c != "organisationunitname"]
        for c in indicator_cols:
            df_raw[c] = pd.to_numeric(df_raw[c], errors='coerce').fillna(0)

        # 1. Monthly Composite Computations with Flexible Column Matcher
        for month in MONTHS:
            def find_col(keyword):
                for col in df_raw.columns:
                    col_str = str(col).lower()
                    if keyword.lower() in col_str and month.lower() in col_str:
                        return col
                return None

            normal_col = find_col("Normal Deliveries")
            assisted_col = find_col("Assisted vaginal delivery")
            breech_col = find_col("Breach Delivery")
            cs_col = find_col("Caesarian Sections")
            
            live_col = find_col("Live birth")
            fsb_col = find_col("Fresh Still Birth")
            msb_col = find_col("Macerated still Birth")
            
            pph_a_col = find_col("PPH (Post Partum Haemorrage) A")
            pph_d_col = find_col("PPH (Post Partum Haemorrage) D")

            # Calculate Monthly Totals if indicators exist
            if normal_col or live_col:
                tot_del_series = (
                    (df_raw[normal_col] if normal_col else 0) + 
                    (df_raw[assisted_col] if assisted_col else 0) + 
                    (df_raw[breech_col] if breech_col else 0) + 
                    (df_raw[cs_col] if cs_col else 0)
                )
                tot_outcomes_series = (
                    (df_raw[live_col] if live_col else 0) + 
                    (df_raw[fsb_col] if fsb_col else 0) + 
                    (df_raw[msb_col] if msb_col else 0)
                )
                tot_pph_series = (
                    (df_raw[pph_a_col] if pph_a_col else 0) + 
                    (df_raw[pph_d_col] if pph_d_col else 0)
                )

                del_col_name = f"Calculated_Total_Deliveries_{month}_{year_str}"
                out_col_name = f"Calculated_Total_Birth_Outcomes_{month}_{year_str}"
                pph_col_name = f"Calculated_Total_PPH_{month}_{year_str}"

                df_raw[del_col_name] = tot_del_series
                df_raw[out_col_name] = tot_outcomes_series
                df_raw[pph_col_name] = tot_pph_series

                # ---------------------------------------------------------
                # Comprehensive Anomaly Audit Engine
                # ---------------------------------------------------------
                for _, row in df_raw.iterrows():
                    fac = row["organisationunitname"]
                    tot_del = row[del_col_name]
                    tot_outcomes = row[out_col_name]
                    tot_pph = row[pph_col_name]

                    normal_del = row.get(normal_col, 0) if normal_col else 0
                    cs_del = row.get(cs_col, 0) if cs_col else 0
                    live_births = row.get(live_col, 0) if live_col else 0

                    # 1. Birth Outcomes Discrepancy (Flags Outcomes != Deliveries, e.g. September)
                    if tot_del > 0 and tot_outcomes != tot_del:
                        if tot_outcomes < tot_del:
                            diff = tot_del - tot_outcomes
                            desc = f"Outcomes ({tot_outcomes}) < Deliveries ({tot_del}). Unrecorded birth outcomes: -{diff}."
                        else:
                            diff = tot_outcomes - tot_del
                            desc = f"Outcomes ({tot_outcomes}) EXCEED Deliveries ({tot_del}). Unlinked birth outcomes: +{diff}."
                            
                        quality_audit_records.append({
                            "Year": year_str, "Month": month, "Facility": fac,
                            "Issue Category": "Birth Outcomes Discrepancy",
                            "Description": desc
                        })

                    # 2. Ghost Outcomes (Birth Outcomes recorded with ZERO Deliveries)
                    elif tot_del == 0 and tot_outcomes > 0:
                        quality_audit_records.append({
                            "Year": year_str, "Month": month, "Facility": fac,
                            "Issue Category": "Unlinked Birth Outcomes",
                            "Description": f"Zero deliveries recorded, but {tot_outcomes} birth outcomes reported."
                        })

                    # 3. High PPH Ratio Anomaly
                    if tot_del > 0 and tot_pph > tot_del:
                        quality_audit_records.append({
                            "Year": year_str, "Month": month, "Facility": fac,
                            "Issue Category": "PPH Reporting Anomaly",
                            "Description": f"PPH cases ({tot_pph}) exceed total recorded deliveries ({tot_del})."
                        })

                    # 4. Negative Value Check
                    if any(val < 0 for val in [tot_del, tot_outcomes, normal_del, cs_del, live_births]):
                        quality_audit_records.append({
                            "Year": year_str, "Month": month, "Facility": fac,
                            "Issue Category": "Invalid Negative Value",
                            "Description": "Negative numbers detected in monthly delivery indicator fields."
                        })

        # 2. Quarterly Aggregations
        for q_name, q_months in QUARTERS.items():
            q_cols = [f"Calculated_Total_Deliveries_{m}_{year_str}" for m in q_months if f"Calculated_Total_Deliveries_{m}_{year_str}" in df_raw.columns]
            if q_cols:
                df_raw[f"Deliveries_{q_name}_{year_str}"] = df_raw[q_cols].sum(axis=1)

        # 3. Biannual Aggregations
        for h_name, h_months in BIANNUAL.items():
            h_cols = [f"Calculated_Total_Deliveries_{m}_{year_str}" for m in h_months if f"Calculated_Total_Deliveries_{m}_{year_str}" in df_raw.columns]
            if h_cols:
                df_raw[f"Deliveries_{h_name}_{year_str}"] = df_raw[h_cols].sum(axis=1)

        cleaned_master_sheets[sheet] = df_raw
        print(f"✅ Processed sheet '{sheet}' ({year_str}): {df_raw.shape[0]} Facilities.")

    df_auditing = pd.DataFrame(quality_audit_records)
    with pd.ExcelWriter(output_kpi_file, engine="openpyxl") as writer:
        for sheet_name, df_clean in cleaned_master_sheets.items():
            df_clean.to_excel(writer, sheet_name=sheet_name, index=False)
        df_auditing.to_excel(writer, sheet_name="Data Quality Issues", index=False)

    print(f"\n🎉 Cleaned KPI dataset successfully saved to: {output_kpi_file}")

except Exception as e:
    print(f"❌ Error during ETL: {e}")