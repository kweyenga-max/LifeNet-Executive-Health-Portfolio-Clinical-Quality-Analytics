import os
import re
import warnings
import pandas as pd

# Suppress engine deprecation warnings
warnings.filterwarnings('ignore', category=Warning)

# 1. Locate dataset workbook
folder_path = "."
excel_files = [
    f for f in os.listdir(folder_path) 
    if f.endswith(('.xlsx', '.xls')) 
    and not f.startswith('~$') 
    and not f.startswith('Cleaned_') 
    and not f.startswith('PV_Q3_')
    and not f.startswith('Standardized_')
]

if not excel_files:
    print("❌ Error: No Excel dataset found in Python_Projects.")
    exit()

target_file = excel_files[0]
print("=" * 85)
print(f"📁 Processing Combined Dataset Workbook: '{target_file}'")
print("=" * 85)

# Load workbook
if target_file.endswith('.xls'):
    xls_workbook = pd.ExcelFile(target_file, engine='xlrd')
else:
    xls_workbook = pd.ExcelFile(target_file, engine='openpyxl')

sheet_names = xls_workbook.sheet_names

# Header cleaning helper
def strip_month_year(col_name):
    col_str = str(col_name).strip()
    cleaned = re.sub(r'\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', '', col_str, flags=re.I)
    cleaned = re.sub(r'\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', '', cleaned, flags=re.I)
    return cleaned.strip()

# 2. STEP 1: Establish January 2025 Master Template Schema
jan_sheet_df = None
for sheet in sheet_names:
    if sheet.strip().lower() == 'january 2025':
        jan_sheet_df = xls_workbook.parse(sheet).fillna(0)
        break

if jan_sheet_df is None:
    jan_sheet_df = xls_workbook.parse(sheet_names[0]).fillna(0)

# Build strict Master Column list (drop unitid, unitcode, unitdescription)
master_columns = [
    strip_month_year(c) for c in jan_sheet_df.columns 
    if not any(meta in str(c).lower() for meta in ['unitid', 'unitcode', 'unitdescription'])
]

print(f"📋 Master Template established with EXACTLY {len(master_columns)} columns.")
print(f"   First metric column: '{master_columns[1]}'")
print(f"   Last metric column:  '{master_columns[-1]}'\n")

# 3. STEP 2: Process All Sheets Using Strict Full Column-Range Summing
processed_records = []

for sheet in sheet_names:
    raw_df = xls_workbook.parse(sheet).fillna(0)
    if raw_df.empty:
        continue

    # Strip month/year suffixes from column headers
    raw_df.columns = [strip_month_year(c) for c in raw_df.columns]

    # Drop extra metadata columns (unitid, unitcode, unitdescription)
    cols_to_keep = [c for c in raw_df.columns if not any(meta in str(c).lower() for meta in ['unitid', 'unitcode', 'unitdescription'])]
    clean_df = raw_df[cols_to_keep].copy()

    # Re-align column order to match January 2025 master schema exactly
    matching_cols = [c for c in master_columns if c in clean_df.columns]
    clean_df = clean_df[matching_cols]

    # Extract exact Period label from sheet name
    sheet_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', sheet, re.I)
    period_label = f"{sheet_match.group(1).capitalize()} {sheet_match.group(2)}" if sheet_match else sheet.strip()

    if 'organisationunitname' not in clean_df.columns:
        continue

    # Range Summing: Select ALL indicator columns from index 1 (OPD Over 5) to the last column (HIV Total)
    indicator_cols = clean_df.columns[1:]
    
    # Calculate complete PV per row
    clean_df['Full_PV'] = clean_df[indicator_cols].apply(pd.to_numeric, errors='coerce').sum(axis=1)

    out_df = pd.DataFrame({
        'organisationunitname': clean_df['organisationunitname'],
        'Period': period_label,
        'PV': clean_df['Full_PV']
    })

    processed_records.append(out_df)

master_df = pd.concat(processed_records, ignore_index=True)

# 4. STEP 3: Map Q3 Periods & Compute Quarterly Totals
q3_2025_months = ['July 2025', 'August 2025', 'September 2025']
q3_2026_months = ['July 2026', 'August 2026', 'September 2026']

def label_quarter(period_str):
    p = str(period_str).strip()
    if p in q3_2025_months:
        return 'Q3_2025'
    elif p in q3_2026_months:
        return 'Q3_2026'
    return 'Other'

master_df['Quarter'] = master_df['Period'].apply(label_quarter)
q3_filtered = master_df[master_df['Quarter'] != 'Other']

# Pivot facility performance
comparison_tbl = q3_filtered.groupby(['organisationunitname', 'Quarter'])['PV'].sum().unstack(fill_value=0)

if 'Q3_2025' not in comparison_tbl.columns:
    comparison_tbl['Q3_2025'] = 0.0
if 'Q3_2026' not in comparison_tbl.columns:
    comparison_tbl['Q3_2026'] = 0.0

comparison_tbl['Absolute_Variance'] = comparison_tbl['Q3_2026'] - comparison_tbl['Q3_2025']
comparison_tbl['Growth_%'] = comparison_tbl.apply(
    lambda r: ((r['Q3_2026'] - r['Q3_2025']) / r['Q3_2025'] * 100) if r['Q3_2025'] > 0 else 0.0, axis=1
).round(2)

comparison_tbl = comparison_tbl.reset_index().sort_values(by='Q3_2026', ascending=False)

# 5. STEP 4: Add Overall Summary Row
total_q3_2025 = comparison_tbl['Q3_2025'].sum()
total_q3_2026 = comparison_tbl['Q3_2026'].sum()
total_abs_var = total_q3_2026 - total_q3_2025
total_growth_pct = round((total_abs_var / total_q3_2025) * 100, 2) if total_q3_2025 > 0 else 0.0

total_row = pd.DataFrame([{
    'organisationunitname': 'TOTAL / OVERALL PV',
    'Q3_2025': total_q3_2025,
    'Q3_2026': total_q3_2026,
    'Absolute_Variance': total_abs_var,
    'Growth_%': total_growth_pct
}])

final_report = pd.concat([comparison_tbl, total_row], ignore_index=True)

# 6. Output to Console & Export
print("\n" + "=" * 85)
print("             PATIENT VOLUME (PV) COMPARISON: Q3 2025 vs Q3 2026             ")
print("=" * 85)
print(final_report.to_string(index=False))

# Save standardized full datasets and Q3 comparison output
master_df.to_excel("Standardized_Master_Dataset.xlsx", index=False)
final_report.to_excel("PV_Q3_2025_vs_2026_Comparison.xlsx", index=False)

print("\n" + "=" * 85)
print("✅ Full range-summed Q3 report saved to 'PV_Q3_2025_vs_2026_Comparison.xlsx'")
print("=" * 85)