import pandas as pd
import numpy as np

def clean_pv_and_kpi_data(df):
    if df.empty:
        return df
    
    df_clean = df.copy()
    
    for col in ['facility_name', 'period', 'data_element', 'value']:
        if col not in df_clean.columns:
            df_clean[col] = None
    
    for col in ['facility_name', 'period', 'data_element']:
        df_clean[col] = df_clean[col].astype(str).str.strip()
    
    df_clean['value'] = pd.to_numeric(df_clean['value'], errors='coerce')
    
    return df_clean
