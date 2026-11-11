import os
import pandas as pd

data_dir = "data"
raw_pv_file = os.path.join(data_dir, "Standardized_Master_Dataset.xlsx")
output_pv_file = os.path.join(data_dir, "Cleaned_PV_Master.xlsx")

if not os.path.exists(raw_pv_file) and os.path.exists("Standardized_Master_Dataset.xlsx"):
    raw_pv_file = "Standardized_Master_Dataset.xlsx"

print(f"🔄 Ingesting {raw_pv_file}...")

xl = pd.ExcelFile(raw_pv_file, engine="openpyxl")
sheet_name = xl.sheet_names[0]
df = pd.read_excel(raw_pv_file, sheet_name=sheet_name, engine="openpyxl")

# Clean column headers
df.columns = [str(c).strip() for c in df.columns]

# Ensure correct column renaming
fac_col = [c for c in df.columns if any(k in c.lower() for k in ["organisation", "facility", "unit", "org"])][0]
period_col = [c for c in df.columns if "period" in c.lower()][0]
pv_col = [c for c in df.columns if c.lower() in ["pv", "value", "attendance", "volume"] or "patient" in c.lower()][0]

df = df.rename(columns={
    fac_col: "organisationunitname",
    period_col: "Period",
    pv_col: "PV"
})

# Drop blank rows
df = df.dropna(subset=["organisationunitname", "Period"]).copy()

# Preserve Period as text and ensure PV is numeric
df["Period"] = df["Period"].astype(str).str.strip()
df["PV"] = pd.to_numeric(df["PV"], errors="coerce").fillna(0)

# Map Quarter correctly based on month name and year
def assign_quarter(period_str):
    p_lower = str(period_str).lower()
    
    # Extract year
    year = "2025" if "2025" in p_lower or "25" in p_lower else ("2026" if "2026" in p_lower or "26" in p_lower else "")
    
    if any(m in p_lower for m in ["january", "jan", "february", "feb", "march", "mar"]):
        q = "Q1"
    elif any(m in p_lower for m in ["april", "apr", "may", "june", "jun"]):
        q = "Q2"
    elif any(m in p_lower for m in ["july", "jul", "august", "aug", "september", "sep"]):
        q = "Q3"
    elif any(m in p_lower for m in ["october", "oct", "november", "nov", "december", "dec"]):
        q = "Q4"
    else:
        q = "Q3" # Default fallback
        
    return f"{q} {year}".strip()

df["Quarter"] = df["Period"].apply(assign_quarter)

# Save to Cleaned_PV_Master.xlsx
with pd.ExcelWriter(output_pv_file, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Cleaned PV Data", index=False)

print(f"🎉 Success! Cleaned_PV_Master.xlsx created with {len(df)} rows and correct text periods.")