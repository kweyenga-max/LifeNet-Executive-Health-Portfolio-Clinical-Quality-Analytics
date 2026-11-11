import pandas as pd
import requests
import streamlit as st
import urllib3
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import apply_dq_patch as dq_audit

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

COLUMN_RENAME_MAP = {
    "ou": "facility_name",
    "pe": "period",
    "dx": "data_element"
}

def fetch_and_adapt_khis_visualization(visualization_uid):
    base_url = st.secrets["khis"]["url"]
    username = st.secrets["khis"]["username"]
    password = st.secrets["khis"]["password"]
    
    endpoint = f"{base_url}/api/visualizations/{visualization_uid}/data.json"
    
    response = requests.get(
        endpoint, 
        auth=(username, password), 
        verify=False
    )
    
    if response.status_code != 200:
        st.error(f"Failed to feetch KHIS visualization {visualization_uid}. Status: {response.status_code}")
        return pd.DataFrame()
        
    data = response.json()
    headers = [h["column"] for h in data["headers"]]
    df_raw = pd.DataFrame(data["rows"], columns=headers)
    
    df_raw = df_raw.rename(columns=COLUMN_RENAME_MAP)
    
    if "facility_name" in df_raw.columns:
        df_raw = df_raw[~df_raw["facility_name"].str.lower().str.contains("total|subtotal", na=False)]
        
    return df_raw

@st.cache_data(ttl=3600)
def get_live_cleaned_dataset(pv_uid, kpi_uid):
    df_pv_raw = fetch_and_adapt_khis_visualization(pv_uid)
    df_kpi_raw = fetch_and_adapt_khis_visualization(kpi_uid)
    
    df_combined_raw = pd.concat([df_pv_raw, df_kpi_raw], ignore_index=True)
    df_clean = dq_audit.clean_pv_and_kpi_data(df_combined_raw)
    
    return df_clean
