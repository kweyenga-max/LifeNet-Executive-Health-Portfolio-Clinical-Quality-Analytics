import os
import pandas as pd

# 1. Locate the dataset file (.xlsx or .xls)
folder_path = "."
excel_files = [f for f in os.listdir(folder_path) if f.endswith(('.xlsx', '.xls'))]

if not excel_files:
    print("❌ Error: No Excel file found in the Python_Projects folder.")
    exit()

target_file = excel_files[0]
print(f"📁 Processing File: '{target_file}'")

# 2. Read dataset using appropriate engine
if target_file.endswith('.xls'):
    df = pd.read_excel(target_file, engine='xlrd')
else:
    df = pd.read_excel(target_file, engine='openpyxl')

# 3. Clean Missing Values & Column Names
# Fill NaNs with 0 for numeric aggregations
df = df.fillna(0)

# Filter out metadata columns if present in other monthly files (keep organisationunitname and indicators)
keep_cols = [c for c in df.columns if not any(x in c.lower() for x in ['code', 'id', 'uid', 'period'])]
df = df[keep_cols]

# 4. Computed Aggregate Indicators
# OPD Total Attendance
opd_cols = [c for c in df.columns if 'OPD' in c]
df['Total OPD Attendance'] = df[opd_cols].apply(pd.to_numeric, errors='coerce').sum(axis=1)

# Total Deliveries (MOH 711)
delivery_cols = [c for c in df.columns if 'Delivery' in c or 'Deliveries' in c or 'Caesarian' in c]
df['Total Deliveries'] = df[delivery_cols].apply(pd.to_numeric, errors='coerce').sum(axis=1)

# Total Immunization Doses (MOH 710)
immunization_cols = [c for c in df.columns if 'MOH710' in c or 'doses' in c.lower()]
df['Total Immunizations'] = df[immunization_cols].apply(pd.to_numeric, errors='coerce').sum(axis=1)

# Total Active ART Clients (MOH 731)
art_cols = [c for c in df.columns if 'OnART' in c]
df['Total Active ART Clients'] = df[art_cols].apply(pd.to_numeric, errors='coerce').sum(axis=1)

# 5. Facility-Level Executive Summary
summary_cols = [
    'organisationunitname',
    'Total OPD Attendance',
    'Total Deliveries',
    'Total Immunizations',
    'Total Active ART Clients'
]
summary_df = df[[c for c in summary_cols if c in df.columns]]

# 6. Display Summary Output
print("\n" + "=" * 60)
print("             HEALTH FACILITY PERFORMANCE SUMMARY             ")
print("=" * 60)
print(summary_df.to_string(index=False))

# 7. Save Processed Metrics to Excel
output_file = "Cleaned_Impact_Report.xlsx"
summary_df.to_excel(output_file, index=False)
print("\n" + "=" * 60)
print(f"✅ Processed metrics exported successfully to '{output_file}'!")
print("=" * 60)