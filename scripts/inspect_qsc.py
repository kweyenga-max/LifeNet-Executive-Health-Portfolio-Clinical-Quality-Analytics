import pandas as pd
import os

data_dir = "data"
qsc_files = [
    os.path.join(data_dir, f) for f in os.listdir(data_dir) 
    if any(k in f.lower() for k in ["qsc", "cohort", "module", "performance"])
]

print(f"🔍 Found {len(qsc_files)} potential QSC/Cohort data files in '{data_dir}':")
for f in qsc_files:
    print(f"  • {f}")

print("\n" + "="*60)

for file_path in qsc_files:
    if not file_path.endswith(('.xlsx', '.xls')):
        continue
    
    print(f"\n📂 File: {file_path}")
    try:
        xl = pd.ExcelFile(file_path)
        print("  📋 Sheets Found:", xl.sheet_names)
        
        for sheet in xl.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet)
            print(f"\n  --- Sheet: '{sheet}' (Rows: {df.shape[0]}, Cols: {df.shape[1]}) ---")
            
            print("  Headers:")
            for i, col in enumerate(df.columns[:15]):
                print(f"    Col {i}: {col}")
            
            print("\n  Sample Data (First 2 rows):")
            print(df.iloc[:2, :min(6, df.shape[1])])
            print("-" * 40)
            
    except Exception as e:
        print(f"  ❌ Failed to read {file_path}: {e}")

