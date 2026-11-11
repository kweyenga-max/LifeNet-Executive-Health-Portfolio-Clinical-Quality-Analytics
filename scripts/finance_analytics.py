import os
import pandas as pd
import numpy as np

def load_finance_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "Finance Data 2026.xlsx")
    if not os.path.exists(file_path):
        file_path = os.path.join("data", "Finance Data 2026.xlsx")
    
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        # Exclude Sambocho and Mwihila (38 HFs total)
        df = df[~df['organisationunitname'].str.lower().str.contains('sambocho|mwihila', regex=True)].copy()
        return df
    return pd.DataFrame()

def get_monthly_finance_summary(df=None):
    if df is None or df.empty:
        df = load_finance_data()
    if df.empty:
        return pd.DataFrame()
        
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
    month_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct']
    
    rev_cols = [f"kny - fr - Total revenu {m} 2026" for m in months]
    exp_cols = [f"kny - fr - Total expenses {m} 2026" for m in months]
    
    for col in rev_cols + exp_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    summary = []
    for m, m_s, r_col, e_col in zip(months, month_short, rev_cols, exp_cols):
        if r_col in df.columns and e_col in df.columns:
            tot_rev = df[r_col].sum(min_count=1)
            tot_exp = df[e_col].sum(min_count=1)
            rep_hfs = df[r_col].notna().sum()
            
            if pd.notna(tot_rev) and pd.notna(tot_exp):
                summary.append({
                    'Month': m_s,
                    'Revenue': float(tot_rev),
                    'Expense': float(tot_exp),
                    'Net_Margin': float(tot_rev - tot_exp),
                    'Reporting_HFs': int(rep_hfs),
                    'Missing_HFs': int(len(df) - rep_hfs)
                })
    return pd.DataFrame(summary)
import streamlit as st

@st.cache_data(ttl=3600)  # <-- ADD THIS LINE ABOVE THE FUNCTION
def get_facility_finance_breakdown():
    # (Leave your existing financial calculations code intact here)
    return df_fin_fac

def get_facility_finance_breakdown(df=None):
    if df is None or df.empty:
        df = load_finance_data()
    if df.empty:
        return pd.DataFrame()
        
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
    rev_cols = [f"kny - fr - Total revenu {m} 2026" for m in months]
    exp_cols = [f"kny - fr - Total expenses {m} 2026" for m in months]
    
    for col in rev_cols + exp_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    fac_summary = []
    for _, row in df.iterrows():
        fac = row['organisationunitname']
        rev_vals = pd.to_numeric(row[rev_cols], errors='coerce')
        exp_vals = pd.to_numeric(row[exp_cols], errors='coerce')
        
        missing_months = []
        present_months = []
        for m, r, e in zip(months, rev_vals, exp_vals):
            if pd.isna(r) or pd.isna(e):
                missing_months.append(m)
            else:
                present_months.append(m)
                
        tot_r = float(rev_vals.sum(skipna=True))
        tot_e = float(exp_vals.sum(skipna=True))
        months_rep = len(present_months)
        missing_cnt = len(missing_months)
        
        deficit_months = 0
        for r, e in zip(rev_vals, exp_vals):
            if pd.notna(r) and pd.notna(e) and r < e:
                deficit_months += 1
                
        net_margin = tot_r - tot_e
        cost_coverage_pct = (tot_r / tot_e * 100) if tot_e > 0 else 0
        
        fac_summary.append({
            'Facility': fac,
            'Total_Revenue': tot_r,
            'Total_Expense': tot_e,
            'Net_Margin': net_margin,
            'Cost_Coverage_Pct': cost_coverage_pct,
            'Months_Reported': months_rep,
            'Missing_Months_Count': missing_cnt,
            'Missing_Months_List': ", ".join(missing_months) if missing_months else "None",
            'Deficit_Months': deficit_months,
            'Status': 'Missing Data' if months_rep == 0 else ('Operating Deficit' if net_margin < 0 else 'Surplus / Breakeven')
        })
    return pd.DataFrame(fac_summary)