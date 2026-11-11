import os
import pandas as pd
import numpy as np

data_dir = "data"
qsc_input_file = os.path.join(data_dir, "Cohort 3 End of Module 1 Performance March 2026.xlsx")
qsc_output_file = os.path.join(data_dir, "Cleaned_Cohort_3_QSC.xlsx")

print("⏳ Executing clean_cohort3_qsc.py: Processing Medical & Management QSC Data...")

if not os.path.exists(qsc_input_file):
    print(f"❌ Input file not found: {qsc_input_file}")
    exit(1)

xl = pd.ExcelFile(qsc_input_file)

# --- Standard Facility Mapping Dictionary ---
FACILITY_ALIAS_MAP = {
    # Buyangu variations
    "Buyangu": "Buyangu Health Centre",
    "Buyangu HF": "Buyangu Health Centre",
    "Buyangu Dispensary": "Buyangu Health Centre",
    "Buyangu Health Center": "Buyangu Health Centre",
    
    # St Monica variations
    "St Monica Eregi HC": "St. Monica Eregi Mission Health Centre",
    "St. Monica Eregi HC": "St. Monica Eregi Mission Health Centre",
    "St Monica Eregi Health Centre": "St. Monica Eregi Mission Health Centre",
    
    # Ingotse variations
    "Ingotse": "Ingotse Health Centre",
    "Ingotse HF": "Ingotse Health Centre",
    "Ingotse Dispensary": "Ingotse Health Centre"
}

# --- Standard Facility Cleaning Helper ---
def clean_facility_name(name):
    if pd.isna(name):
        return ""
    name_str = str(name).strip()
    name_str = " ".join(name_str.split())  # Clean extra spaces
    
    # Normalize common suffix variations
    name_str = name_str.replace(" HF", " Health Centre").replace(" Dispensary", " Health Centre")
    
    # Return mapped alias if exists, else return cleaned name
    return FACILITY_ALIAS_MAP.get(name_str, name_str)

# 1. Process Medical QSC Performance
df_med_perf = pd.read_excel(qsc_input_file, sheet_name="Medical QSC Performance")
df_med_perf = df_med_perf.rename(columns={
    df_med_perf.columns[0]: "organisationunitname",
    df_med_perf.columns[1]: "Medical_Baseline_Module1_Pct",
    df_med_perf.columns[2]: "Medical_Endline_Module1_Pct"
})

# 2. Process Management QSC Performance
df_mgt_perf = pd.read_excel(qsc_input_file, sheet_name="Management QSC Performance")
df_mgt_perf = df_mgt_perf.rename(columns={
    df_mgt_perf.columns[0]: "organisationunitname",
    df_mgt_perf.columns[1]: "Management_Baseline_Module1_Pct",
    df_mgt_perf.columns[2]: "Management_Endline_Module1_Pct"
})

# Clean facility names for merging
df_med_perf["organisationunitname"] = df_med_perf["organisationunitname"].apply(clean_facility_name)
df_mgt_perf["organisationunitname"] = df_mgt_perf["organisationunitname"].apply(clean_facility_name)

# 3. Merge Medical & Management Performance
df_qsc_merged = pd.merge(
    df_med_perf,
    df_mgt_perf,
    on="organisationunitname",
    how="outer"
)

# Convert score columns to numeric percentages
score_cols = [
    "Medical_Baseline_Module1_Pct", "Medical_Endline_Module1_Pct",
    "Management_Baseline_Module1_Pct", "Management_Endline_Module1_Pct"
]

for col in score_cols:
    if col in df_qsc_merged.columns:
        df_qsc_merged[col] = pd.to_numeric(df_qsc_merged[col], errors="coerce").round(2)

# Calculate Overall Combined Module 1 Scores
df_qsc_merged["Combined_Baseline_Module1_Pct"] = df_qsc_merged[["Medical_Baseline_Module1_Pct", "Management_Baseline_Module1_Pct"]].mean(axis=1).round(2)
df_qsc_merged["Combined_Endline_Module1_Pct"] = df_qsc_merged[["Medical_Endline_Module1_Pct", "Management_Endline_Module1_Pct"]].mean(axis=1).round(2)

# 4. Generate Missing Baseline Audit
missing_baselines = df_qsc_merged[
    (df_qsc_merged["Medical_Baseline_Module1_Pct"].isna()) | 
    (df_qsc_merged["Management_Baseline_Module1_Pct"].isna())
]

audit_records = []
for _, row in missing_baselines.iterrows():
    fac = row["organisationunitname"]
    missing_track = []
    if pd.isna(row["Medical_Baseline_Module1_Pct"]):
        missing_track.append("Medical")
    if pd.isna(row["Management_Baseline_Module1_Pct"]):
        missing_track.append("Management")
    
    audit_records.append({
        "Year": "2026",
        "Facility": fac,
        "Issue Category": "Missing QSC Baseline Track",
        "Description": f"Facility '{fac}' is missing baseline data for: {', '.join(missing_track)} track(s)."
    })

df_audit = pd.DataFrame(audit_records)

# 5. Export Clean Master
with pd.ExcelWriter(qsc_output_file, engine="openpyxl") as writer:
    df_qsc_merged.to_excel(writer, sheet_name="Cleaned_Cohort3_QSC", index=False)
    df_audit.to_excel(writer, sheet_name="QSC_Baseline_Audit", index=False)

print(f"✅ Success! Cleaned QSC master exported to: {qsc_output_file}")
print(f"🚨 Missing baseline issues flagged: {len(df_audit)}")