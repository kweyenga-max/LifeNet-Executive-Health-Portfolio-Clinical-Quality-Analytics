import pandas as pd
import requests
import streamlit as st
import urllib3
import scripts.apply_dq_patch as dq_audit

# Suppress SSL certificate verification warnings in logs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Map KHIS column names to match your exact static CSV structure
COLUMN_RENAME_MAP = {
    "ou": "facility_name",
    "pe": "period",
    "dx": "data_element"
}

def fetch_and_adapt_khis_visualization(visualization_uid):
    """
    Fetches raw data from KHIS by Visualizer UID, bypasses SSL check,
    cleans layout headers, and removes pre-calculated total rows.
    """
    base_url = st.secrets["khis"]["url"]
    username = st.secrets["khis"]["username"]
    password = st.secrets["khis"]["password"]
    
    endpoint = f"{base_url}/api/visualizations/{visualization_uid}/data.json"
    
    # verify=False bypasses the NET::ERR_CERT_AUTHORITY_INVALID security prompt
    response = requests.get(
        endpoint, 
        auth=(username, password), 
        verify=False
    )
    
    if response.status_code != 200:
        st.error(f"Failed to fetch KHIS visualization {visualization_uid}. Status: {response.status_code}")
        return pd.DataFrame()
        
    data = response.json()
    headers = [h["column"] for h in data["headers"]]
    df_raw = pd.DataFrame(data["rows"], columns=headers)
    
    # 1. Rename columns to match internal standard
    df_raw = df_raw.rename(columns=COLUMN_RENAME_MAP)
    
    # 2. Filter out KHIS pre-calculated 'Total' or 'Subtotal' rows to avoid double-counting
    if "facility_name" in df_raw.columns:
        df_raw = df_raw[~df_raw["facility_name"].str.lower().str.contains("total|subtotal", na=False)]
        
    return df_raw


@st.cache_data(ttl=3600)  # Caches live data for 1 hour to keep dashboard fast
def get_live_cleaned_dataset(pv_uid, kpi_uid):
    """
    Fetches both PV and KPI data directly from KHIS and passes them through
    your existing apply_dq_patch cleaning functions.
    """
    # Fetch raw streams directly from KHIS API
    df_pv_raw = fetch_and_adapt_khis_visualization(pv_uid)
    df_kpi_raw = fetch_and_adapt_khis_visualization(kpi_uid)
    
    # Combine raw extracts
    df_combined_raw = pd.concat([df_pv_raw, df_kpi_raw], ignore_index=True)
    
    # Pass directly into your EXISTING cleaning logic (apply_dq_patch.py)
    df_clean = dq_audit.clean_pv_and_kpi_data(df_combined_raw)
    
    return df_clean