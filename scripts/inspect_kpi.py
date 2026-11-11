import os
import pandas as pd

file_path = os.path.join("data", "Key Performing Indicators for Program Monitoring.xls")

try:
    xl = pd.ExcelFile(file_path, engine="xlrd")
    df_2025 = pd.read_excel(file_path, sheet_name="2025 Data", header=1, engine="xlrd")
    
    # Standardize whitespace
    cols = [" ".join(str(c).split()) for c in df_2025.columns if c != "organisationunitname"]
    
    print("============================================================")
    print("📋 KPI INDICATOR HEADERS MAPPING (2025 Data)")
    print("============================================================")
    for idx, col in enumerate(cols, 1):
        print(f"{idx:03d}. {col}")

except Exception as e:
    print(f"❌ Error inspecting columns: {e}")