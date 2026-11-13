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


PSS_SNAPSHOT_PATH = os.path.join(DATA_DIR, "monitrac_pss_snapshot.csv.gz")
PSS_EXCEL_FALLBACK = os.path.expanduser("~/Desktop/Patient Satisfactory Survey 2026.xlsx")

PSS_NET_SCORE_UID = "MjBgkWmZLDB"
PSS_RAW_SCORE_UID = "p7wxPf6zWvq"
PSS_OBTAINED_UID = "pI0zqzbU5gG"
PSS_MAX_UID = "Jb8RDzofj4V"


def _rolling_12_pe_codes():
    """Return exact YYYYMM codes for the past 12 completed months (excluding current incomplete month)."""
    today = date.today()
    y, m = today.year, today.month
    codes = []
    for _ in range(12):
        m -= 1
        if m == 0:
            m = 12
            y -= 1
        codes.append(f"{y}{m:02d}")
    return sorted(codes)


def sync_monitrac_pss(force_live=False):
    """Sync rolling Past 12 Months Patient Satisfaction Survey (PSS) from MoniTrac API strictly for LifeNet Kenya's 38 facilities."""
    pe_12m = _rolling_12_pe_codes()

    if not force_live and os.path.exists(PSS_SNAPSHOT_PATH):
        df_cached = pd.read_csv(PSS_SNAPSHOT_PATH, compression="gzip")
        if not df_cached.empty and "periodid" in df_cached.columns:
            df_cached["periodid"] = df_cached["periodid"].astype(str)
            return df_cached[df_cached["periodid"].isin(pe_12m)].copy()

    roster = _get_active_38_roster()
    norm_to_canonical = {_norm_key(f): f for f in roster}

    base_url, username, password = _get_monitrac_credentials()
    rows_out = []

    if base_url and username and password:
        try:
            resp = requests.get(
                f"{base_url}/api/analytics.json",
                params={
                    "dimension": [
                        f"dx:{PSS_NET_SCORE_UID};{PSS_RAW_SCORE_UID};{PSS_OBTAINED_UID};{PSS_MAX_UID}",
                        "pe:LAST_12_MONTHS",
                        f"ou:{KENYA_OU_UID};LEVEL-6",
                    ],
                    "displayProperty": "NAME",
                    "outputIdScheme": "UID",
                },
                auth=(username, password),
                verify=False,
                timeout=30,
            )
            resp.raise_for_status()
            payload = resp.json()
            meta_items = payload.get("metaData", {}).get("items", {})
            raw_rows = payload.get("rows", [])

            grouped = {}
            for dx_uid, pe_code, ou_uid, val in raw_rows:
                pe_str = str(pe_code)
                if pe_str not in pe_12m:
                    continue
                ou_name = meta_items.get(ou_uid, {}).get("name", "")
                if not ou_name or re.search(r"sambocho|mwihila", ou_name, re.I):
                    continue
                canonical = norm_to_canonical.get(_norm_key(ou_name))
                if not canonical:
                    continue  # Strictly LifeNet Kenya's 38 partner facilities only

                pe_name = meta_items.get(pe_code, {}).get("name", pe_str)
                key = (canonical, pe_str, pe_name)
                if key not in grouped:
                    grouped[key] = {
                        "organisationunitid": ou_uid,
                        "organisationunitname": canonical,
                        "periodid": pe_str,
                        "periodname": pe_name,
                        "Net_Satisfaction_Score": pd.NA,
                        "Survey_Score": pd.NA,
                        "Obtained_Points": pd.NA,
                        "Max_Points": pd.NA,
                    }
                num_val = pd.to_numeric(val, errors="coerce")
                if dx_uid == PSS_NET_SCORE_UID:
                    grouped[key]["Net_Satisfaction_Score"] = num_val
                elif dx_uid == PSS_RAW_SCORE_UID:
                    grouped[key]["Survey_Score"] = num_val
                elif dx_uid == PSS_OBTAINED_UID:
                    grouped[key]["Obtained_Points"] = num_val
                elif dx_uid == PSS_MAX_UID:
                    grouped[key]["Max_Points"] = num_val

            rows_out = list(grouped.values())
        except Exception as exc:
            print(f"Warning: Live MoniTrac PSS LAST_12_MONTHS pull failed ({exc}); checking fallback.")

    if not rows_out and os.path.exists(PSS_EXCEL_FALLBACK):
        df_xl = pd.read_excel(PSS_EXCEL_FALLBACK)
        for _, r in df_xl.iterrows():
            pe_str = str(r.get("periodid", "")).strip()
            if pe_str not in pe_12m:
                continue
            ou_name = str(r.get("organisationunitname", "")).strip()
            if not ou_name or re.search(r"sambocho|mwihila", ou_name, re.I):
                continue
            canonical = norm_to_canonical.get(_norm_key(ou_name))
            if not canonical:
                continue
            rows_out.append({
                "organisationunitid": str(r.get("organisationunitid", "")),
                "organisationunitname": canonical,
                "periodid": pe_str,
                "periodname": str(r.get("periodname", "")),
                "Net_Satisfaction_Score": pd.to_numeric(r.get("IPTT_PSS - % Net Patient Satisfaction Score"), errors="coerce"),
                "Survey_Score": pd.to_numeric(r.get("Patient Satisfaction Survey pss - Patient satisfaction survey score"), errors="coerce"),
                "Obtained_Points": pd.to_numeric(r.get("Patient Satisfaction Survey pss - Patient satisfaction survey obtained points"), errors="coerce"),
                "Max_Points": pd.to_numeric(r.get("Patient Satisfaction Survey pss - Patient satisfaction survey max points"), errors="coerce"),
            })

    if not rows_out:
        if os.path.exists(PSS_SNAPSHOT_PATH):
            df_cached = pd.read_csv(PSS_SNAPSHOT_PATH, compression="gzip")
            df_cached["periodid"] = df_cached["periodid"].astype(str)
            return df_cached[df_cached["periodid"].isin(pe_12m)].copy()
        return pd.DataFrame(columns=[
            "organisationunitid", "organisationunitname", "periodid", "periodname",
            "Net_Satisfaction_Score", "Survey_Score", "Obtained_Points", "Max_Points"
        ])

    df_pss = pd.DataFrame(rows_out)
    df_pss = df_pss[df_pss["Net_Satisfaction_Score"].notna()].copy()
    df_pss["periodid"] = df_pss["periodid"].astype(str)
    df_pss = df_pss[df_pss["periodid"].isin(pe_12m)].copy()
    df_pss["Year"] = df_pss["periodid"].str[:4].astype(int)
    df_pss["Month_Num"] = df_pss["periodid"].str[4:6].astype(int)
    df_pss["Quarter"] = "Q" + ((df_pss["Month_Num"] - 1) // 3 + 1).astype(str) + " " + df_pss["Year"].astype(str)
    df_pss = df_pss.sort_values(["organisationunitname", "periodid"]).drop_duplicates(
        subset=["organisationunitname", "periodid"], keep="last"
    )

    os.makedirs(DATA_DIR, exist_ok=True)
    df_pss.to_csv(PSS_SNAPSHOT_PATH, index=False, compression={"method": "gzip", "mtime": 0})
    return df_pss
