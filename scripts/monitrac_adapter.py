from datetime import date
import os
import re
import pandas as pd
import requests
import streamlit as st
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
)
FINANCE_SNAPSHOT_PATH = os.path.join(DATA_DIR, "monitrac_finance_snapshot.csv.gz")
FINANCE_EXCEL_PATH = os.path.join(DATA_DIR, "Finance Data 2026.xlsx")

KENYA_OU_UID = "HfVjCurKxh2"
REV_DE_UID = "VECbmDpP2Gi"
EXP_DE_UID = "e5yxlPybvMH"

ALL_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _get_monitrac_credentials():
    try:
        sec = st.secrets.get("monitrac", {})
        url = sec.get("url") or os.getenv("MONITRAC_BASE_URL", "")
        user = sec.get("username") or os.getenv("MONITRAC_USERNAME", "")
        pwd = sec.get("password") or os.getenv("MONITRAC_PASSWORD", "")
        return str(url).rstrip("/"), str(user), str(pwd)
    except Exception:
        return (
            os.getenv("MONITRAC_BASE_URL", "").rstrip("/"),
            os.getenv("MONITRAC_USERNAME", ""),
            os.getenv("MONITRAC_PASSWORD", ""),
        )


def _norm_key(name):
    s = str(name or "").lower().strip()
    s = re.sub(r"\(.*?\)", "", s)
    for tok in ["mission", "health centre", "health center", "dispensary", "hospital", "medical centre", "clinic"]:
        s = s.replace(tok, "")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def _get_active_38_roster():
    if os.path.exists(FINANCE_EXCEL_PATH):
        df_xl = pd.read_excel(FINANCE_EXCEL_PATH)
        facs = df_xl["organisationunitname"].dropna().astype(str).str.strip().tolist()
        facs = [f for f in facs if not re.search(r"sambocho|mwihila", f, re.I)]
        return list(dict.fromkeys(facs))
    return []


def sync_monitrac_finance(year=2026, force_live=False):
    if not force_live and os.path.exists(FINANCE_SNAPSHOT_PATH):
        return pd.read_csv(FINANCE_SNAPSHOT_PATH, compression="gzip")

    base_url, username, password = _get_monitrac_credentials()
    if not (base_url and username and password):
        if os.path.exists(FINANCE_SNAPSHOT_PATH):
            return pd.read_csv(FINANCE_SNAPSHOT_PATH, compression="gzip")
        return pd.DataFrame()

    today = date.today()
    max_m = 12 if year < today.year else min(today.month, 12)
    pe_codes = [f"{year}{m:02d}" for m in range(1, max_m + 1)]
    months_target = ALL_MONTHS[:max_m]

    resp = requests.get(
        f"{base_url}/api/analytics.json",
        params={
            "dimension": [
                f"dx:{REV_DE_UID};{EXP_DE_UID}",
                f"pe:{" ; ".join(pe_codes).replace(" ", "")}",
                f"ou:{KENYA_OU_UID};LEVEL-6",
            ],
            "displayProperty": "NAME",
            "outputIdScheme": "NAME",
        },
        auth=(username, password),
        verify=False,
        timeout=30,
    )
    resp.raise_for_status()
    rows = resp.json().get("rows", [])

    roster = _get_active_38_roster()
    norm_to_canonical = {_norm_key(f): f for f in roster}

    records = {}
    for f in roster:
        records[f] = {"organisationunitname": f}

    for dx_name, pe_label, ou_name, val in rows:
        if re.search(r"sambocho|mwihila", ou_name, re.I):
            continue
        canonical = norm_to_canonical.get(_norm_key(ou_name), ou_name.strip())
        if canonical not in records:
            if roster:
                # Only include facilities in the active 38 network
                continue
            records[canonical] = {"organisationunitname": canonical}

        # pe_label is e.g. "October 2026"
        parts = pe_label.strip().split()
        if len(parts) != 2:
            continue
        m_name, y_str = parts[0], parts[1]
        if "revenu" in dx_name.lower():
            col = f"kny - fr - Total revenu {m_name} {y_str}"
        elif "expense" in dx_name.lower():
            col = f"kny - fr - Total expenses {m_name} {y_str}"
        else:
            continue
        records[canonical][col] = pd.to_numeric(val, errors="coerce")

    ordered_cols = ["organisationunitname"]
    for m in months_target:
        ordered_cols.append(f"kny - fr - Total revenu {m} {year}")
        ordered_cols.append(f"kny - fr - Total expenses {m} {year}")

    df_out = pd.DataFrame(list(records.values()))
    for col in ordered_cols:
        if col not in df_out.columns:
            df_out[col] = pd.NA
    df_out = df_out[ordered_cols]

    os.makedirs(DATA_DIR, exist_ok=True)
    df_out.to_csv(FINANCE_SNAPSHOT_PATH, index=False, compression={"method": "gzip", "mtime": 0})
    return df_out
