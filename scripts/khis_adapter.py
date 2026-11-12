from datetime import date
import pandas as pd
import requests
import streamlit as st
import urllib3
import apply_dq_patch as dq_audit

# Suppress SSL certificate verification warnings in logs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

COLUMN_RENAME_MAP = {
    "ou": "facility_name",
    "pe": "period",
    "dx": "data_element"
}


def _apply_dq_cleaning(df):
    if hasattr(dq_audit, "clean_pv_and_kpi_data"):
        return _apply_dq_cleaning(df)
    if df is None or df.empty:
        return df
    df = df.copy()
    for col in ("facility_name", "period", "data_element"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce").fillna(0)
    return df


def _get_rolling_focus_and_baseline_periods():
    """
    Returns full Q4 of last year (Oct, Nov, Dec) plus the dynamic rolling
    completed month(s) of the current cycle.
    In Nov 2026 -> ['202510', '202511', '202512', '202610']
    """
    today = date.today()
    if today.month == 1:
        focus_year, focus_month = today.year - 1, 12
    else:
        focus_year, focus_month = today.year, today.month - 1

    last_year = focus_year - 1
    periods = [f"{last_year}10", f"{last_year}11", f"{last_year}12"]

    prior_same_month = f"{last_year}{focus_month:02d}"
    if prior_same_month not in periods:
        periods.append(prior_same_month)

    if focus_month >= 10:
        for m in range(10, focus_month + 1):
            p = f"{focus_year}{m:02d}"
            if p not in periods:
                periods.append(p)
    else:
        p = f"{focus_year}{focus_month:02d}"
        if p not in periods:
            periods.append(p)

    return periods


def _extract_dimensions(viz_meta):
    """Extracts dx (including dataElementOperands), ou, and pe lists from DHIS2 visualization metadata."""
    dx_items = []
    for item in viz_meta.get("dataDimensionItems", []):
        if "dataElementOperand" in item:
            operand = item["dataElementOperand"]
            dim_id = operand.get("dimensionItem") or operand.get("id")
            if dim_id:
                dx_items.append(dim_id)
        else:
            for key in ("dataElement", "indicator", "dataSet", "programIndicator"):
                if key in item and "id" in item[key]:
                    dx_items.append(item[key]["id"])

    ou_items = [ou["id"] for ou in viz_meta.get("organisationUnits", []) if "id" in ou]
    if viz_meta.get("userOrganisationUnit"):
        ou_items.append("USER_ORGUNIT")
    if viz_meta.get("userOrganisationUnitChildren"):
        ou_items.append("USER_ORGUNIT_CHILDREN")
    if viz_meta.get("userOrganisationUnitGrandChildren"):
        ou_items.append("USER_ORGUNIT_GRANDCHILDREN")

    pe_items = [pe["id"] for pe in viz_meta.get("periods", []) if "id" in pe]
    rel_map = {
        "thisMonth": "THIS_MONTH",
        "lastMonth": "LAST_MONTH",
        "last3Months": "LAST_3_MONTHS",
        "last6Months": "LAST_6_MONTHS",
        "last12Months": "LAST_12_MONTHS",
        "thisQuarter": "THIS_QUARTER",
        "lastQuarter": "LAST_QUARTER",
        "last4Quarters": "LAST_4_QUARTERS",
        "thisYear": "THIS_YEAR",
        "lastYear": "LAST_YEAR",
        "last5Years": "LAST_5_YEARS",
    }
    for rel_key, enabled in viz_meta.get("relativePeriods", {}).items():
        if enabled and rel_key in rel_map:
            pe_items.append(rel_map[rel_key])

    return dx_items, ou_items, pe_items


def _period_to_quarter(period_str):
    """Converts 'October 2025' -> 'Q4 2025' to match Cleaned_PV_Master.xlsx."""
    dt = pd.to_datetime(period_str, format="%B %Y", errors="coerce")
    if pd.isna(dt):
        return ""
    q = (dt.month - 1) // 3 + 1
    return f"Q{q} {dt.year}"


def fetch_and_adapt_khis_visualization(visualization_uid, target_period=None):
    base_url = st.secrets["khis"]["url"]
    username = st.secrets["khis"]["username"]
    password = st.secrets["khis"]["password"]

    meta_url = f"{base_url}/api/visualizations/{visualization_uid}.json"
    meta_params = {
        "fields": "id,name,dataDimensionItems[dataDimensionItemType,dataElement[id],indicator[id],dataSet[id],programIndicator[id],dataElementOperand[id,dimensionItem]],organisationUnits[id],periods[id],relativePeriods,userOrganisationUnit,userOrganisationUnitChildren,userOrganisationUnitGrandChildren"
    }

    meta_resp = requests.get(meta_url, params=meta_params, auth=(username, password), verify=False)
    if meta_resp.status_code != 200:
        st.error(f"Failed to fetch metadata for KHIS visualization {visualization_uid}. Status: {meta_resp.status_code}")
        return pd.DataFrame()

    dx_items, ou_items, pe_items = _extract_dimensions(meta_resp.json())

    if target_period is None:
        pe_items = _get_rolling_focus_and_baseline_periods()
    else:
        pe_items = [target_period] if isinstance(target_period, str) else list(target_period)

    dimensions = []
    if dx_items:
        dimensions.append(f"dx:{';'.join(dx_items)}")
    if ou_items:
        dimensions.append(f"ou:{';'.join(ou_items)}")
    if pe_items:
        dimensions.append(f"pe:{';'.join(pe_items)}")

    analytics_url = f"{base_url}/api/analytics.json"
    analytics_params = [
        ("displayProperty", "NAME"),
        ("skipMeta", "false"),
        ("hierarchyMeta", "false"),
    ] + [("dimension", d) for d in dimensions]

    response = requests.get(analytics_url, params=analytics_params, auth=(username, password), verify=False)
    if response.status_code != 200:
        st.error(f"Failed to fetch analytics for KHIS visualization {visualization_uid}. Status: {response.status_code}")
        return pd.DataFrame()

    data = response.json()
    headers = [h["name"] for h in data.get("headers", [])]
    df_raw = pd.DataFrame(data.get("rows", []), columns=headers)

    meta_items = data.get("metaData", {}).get("items", {})
    for col in ("dx", "ou", "pe"):
        if col in df_raw.columns:
            df_raw[col] = df_raw[col].map(lambda uid: meta_items.get(uid, {}).get("name", uid))

    df_raw = df_raw.rename(columns=COLUMN_RENAME_MAP)

    if "facility_name" in df_raw.columns:
        df_raw = df_raw[~df_raw["facility_name"].str.lower().str.contains("total|subtotal", na=False)]

    if "value" in df_raw.columns:
        df_raw["value"] = pd.to_numeric(df_raw["value"], errors="coerce").fillna(0)

    return df_raw


@st.cache_data(ttl=3600)
def get_live_cleaned_dataset(pv_uid, kpi_uid, target_period=None):
    df_pv_raw = fetch_and_adapt_khis_visualization(pv_uid, target_period=target_period)
    df_kpi_raw = fetch_and_adapt_khis_visualization(kpi_uid, target_period=target_period)

    df_combined_raw = pd.concat([df_pv_raw, df_kpi_raw], ignore_index=True)
    df_clean = _apply_dq_cleaning(df_combined_raw)

    return df_clean


@st.cache_data(ttl=3600)
def get_live_pv_and_kpi_frames(pv_uid="IwUxQNFazpx", kpi_uid="IPjuLUsTQHG", target_period=None):
    df_pv_raw = fetch_and_adapt_khis_visualization(pv_uid, target_period=target_period)
    df_pv_raw = _apply_dq_cleaning(df_pv_raw)

    if not df_pv_raw.empty:
        df_pv_live = (
            df_pv_raw.groupby(["facility_name", "period"], as_index=False)["value"]
            .sum()
            .rename(columns={"facility_name": "organisationunitname", "period": "Period", "value": "PV"})
        )
        df_pv_live["PV"] = df_pv_live["PV"].round().astype(int)
        df_pv_live["Quarter"] = df_pv_live["Period"].map(_period_to_quarter)
    else:
        df_pv_live = pd.DataFrame(columns=["organisationunitname", "Period", "PV", "Quarter"])

    df_kpi_raw = fetch_and_adapt_khis_visualization(kpi_uid, target_period=target_period)
    df_kpi_raw = _apply_dq_cleaning(df_kpi_raw)

    if not df_kpi_raw.empty:
        df_kpi_raw["metric_col"] = df_kpi_raw["data_element"].str.strip() + " " + df_kpi_raw["period"].str.strip()
        df_kpi_live_wide = (
            df_kpi_raw.pivot_table(
                index="facility_name",
                columns="metric_col",
                values="value",
                aggfunc="sum",
            )
            .reset_index()
            .rename(columns={"facility_name": "organisationunitname"})
        )
        df_kpi_live_wide.columns.name = None
    else:
        df_kpi_live_wide = pd.DataFrame(columns=["organisationunitname"])

    return df_pv_live, df_kpi_live_wide
