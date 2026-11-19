import io
import os
import re
from typing import Optional
import numpy as np
import openpyxl
import pandas as pd
import streamlit as st

TEMPLATE_PATH = "data/KPI Dashboard HF Level_EN 120625.xlsx"

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FULL_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# Exact 25 indicators matching rows 4..28 of KPI Dashboard HF Level_EN 120625.xlsx
HF_KPI_SPECS = [
    # (row_idx, domain, indicator_label, target_label, agg_type)
    (4,  "Service Utilization & ANC", "Total Workload", "Facility Target", "sum"),
    (5,  "Service Utilization & ANC", "Total ANC visits", "Facility Target", "sum"),
    (6,  "Service Utilization & ANC", "New ANC Visits", "Facility Target", "sum"),
    (7,  "Service Utilization & ANC", "Number attending 1st ANC visit in 1st Trimester(<12Wks)", "≥ 50% of New ANC", "sum"),
    (8,  "Service Utilization & ANC", "Number Attending at least 4 ANC visits", "≥ 80% of New ANC", "sum"),
    (9,  "Service Utilization & ANC", "Number Attending 8 ANC visits", "WHO 8-Contact Goal", "sum"),
    (10, "Deliveries & Maternal/Newborn Outcomes", "Number of Deliveries", "Facility Target", "sum"),
    (11, "Deliveries & Maternal/Newborn Outcomes", "Number of Live Births", "100% Live Outcomes", "sum"),
    (12, "Deliveries & Maternal/Newborn Outcomes", "Number of Macerated Still Birth", "0", "sum"),
    (13, "Deliveries & Maternal/Newborn Outcomes", "Number of Fresh Still Birth", "0", "sum"),
    (14, "Deliveries & Maternal/Newborn Outcomes", "Number of Newborn death 0 - 28 days", "0", "sum"),
    (15, "Deliveries & Maternal/Newborn Outcomes", "Number of Perinatal Deaths Audited", "100% of Deaths", "sum"),
    (16, "Deliveries & Maternal/Newborn Outcomes", "Number of Under Five(<5) cases treated", "Facility Target", "sum"),
    (17, "Deliveries & Maternal/Newborn Outcomes", "Number of Maternal deaths", "0", "sum"),
    (18, "Deliveries & Maternal/Newborn Outcomes", "Number of Maternal Deaths Audited", "100% of Deaths", "sum"),
    (19, "Emergency Obstetric & Newborn Care", "Number of PPH cases Identified", "Monitor Incidence", "sum"),
    (20, "Emergency Obstetric & Newborn Care", "Number of PPH cases successfully managed", "100% Managed", "sum"),
    (21, "Emergency Obstetric & Newborn Care", "Number of PPH cases referred", "Timely Referral", "sum"),
    (22, "Emergency Obstetric & Newborn Care", "Number of Birth asphyxia cases", "Monitor Incidence", "sum"),
    (23, "Emergency Obstetric & Newborn Care", "Number of Birth Asphyxia cases Successfully Managed", "100% Resuscitated", "sum"),
    (24, "Health Systems & eLearning", "Routine Full Stock Take Conducted (Yes/No)", "Yes (Monthly)", "yesno"),
    (25, "Health Systems & eLearning", "Percentage of essential medicines available in stock", "≥ 95%", "pct"),
    (26, "Health Systems & eLearning", "Management Review Meeting Conducted (Yes/No)", "Yes (Monthly)", "yesno"),
    (27, "Health Systems & eLearning", "Number of Staff enrolled on LifeNet eLearning platform", "100% Clinical Staff", "max"),
    (28, "Health Systems & eLearning", "Number of Staff completed eLearning lessons", "≥ 80% Enrolled", "max"),
]


def _norm_fac(name: str) -> str:
    s = str(name or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


@st.cache_data(ttl=3600, show_spinner=False)
def _load_anc_snapshot() -> pd.DataFrame:
    path = "data/khis_anc_snapshot.csv.gz"
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "facility_name" in df.columns:
        df["_fac_norm"] = df["facility_name"].map(_norm_fac)
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def _load_mentees_snapshot() -> pd.DataFrame:
    path = "data/monitrac_mentees_snapshot.csv.gz"
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    fac_col = next((c for c in ["facility_name", "Organisation unit name", "org_unit"] if c in df.columns), None)
    if fac_col:
        df["_fac_norm"] = df[fac_col].map(_norm_fac)
    dt_col = next((c for c in ["event_date", "Event date"] if c in df.columns), None)
    if dt_col:
        dt = pd.to_datetime(df[dt_col], errors="coerce")
        df["_Year"] = dt.dt.year
        df["_MonthNum"] = dt.dt.month
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def _load_template_defs_and_insights() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not os.path.exists(TEMPLATE_PATH):
        return pd.DataFrame(), pd.DataFrame()
    try:
        df_def = pd.read_excel(TEMPLATE_PATH, sheet_name="Indicator Definition").dropna(how="all")
        df_ins = pd.read_excel(TEMPLATE_PATH, sheet_name="Insights").dropna(how="all")
        return df_def, df_ins
    except Exception:
        return pd.DataFrame(), pd.DataFrame()


def _extract_kpi_wide_month(df_kpi: pd.DataFrame, fac_norm: str, year_str: str, full_month: str, patterns: list[str]) -> Optional[float]:
    if df_kpi is None or df_kpi.empty:
        return None
    fac_col = df_kpi.columns[0]
    sub = df_kpi[df_kpi[fac_col].map(_norm_fac) == fac_norm]
    if sub.empty:
        return None

    m_low = full_month.lower()
    y_low = str(year_str).lower()
    matched_cols = []
    for c in df_kpi.columns[1:]:
        c_compact = re.sub(r"\s+", "", str(c)).lower()
        if m_low in c_compact and y_low in c_compact:
            if any(re.sub(r"\s+", "", p).lower() in c_compact for p in patterns):
                matched_cols.append(c)
    if not matched_cols:
        return None
    vals = pd.to_numeric(sub[matched_cols].iloc[0], errors="coerce")
    if vals.isna().all():
        return None
    return float(vals.sum(skipna=True))


def build_hf_kpi_matrix(
    selected_fac: str,
    year_str: str,
    facility_pv_df: pd.DataFrame,
    kpi_df_year: pd.DataFrame,
) -> pd.DataFrame:
    """
    Auto-populates all 25 HF-level KPIs (Jan..Dec) for a single facility and reporting year.
    """
    fac_norm = _norm_fac(selected_fac)
    year_int = int(year_str)

    # 1. Patient Volume (Total Workload) by Month
    pv_by_month: dict[int, float] = {}
    if facility_pv_df is not None and not facility_pv_df.empty:
        pv_fac_col = facility_pv_df.columns[0]
        sub_pv = facility_pv_df[facility_pv_df[pv_fac_col].map(_norm_fac) == fac_norm].copy()
        if not sub_pv.empty and "Period" in sub_pv.columns and "PV" in sub_pv.columns:
            p_str = sub_pv["Period"].astype(str)
            # Match YYYYMM or Month Year
            for m_idx, (m_short, m_full) in enumerate(zip(MONTH_NAMES, FULL_MONTHS), start=1):
                ym_code = f"{year_int}{m_idx:02d}"
                mask = (
                    (p_str == ym_code)
                    | (p_str.str.contains(m_full, case=False, na=False) & p_str.str.contains(str(year_int), na=False))
                    | (p_str.str.contains(m_short, case=False, na=False) & p_str.str.contains(str(year_int), na=False))
                )
                if mask.any():
                    pv_vals = pd.to_numeric(sub_pv.loc[mask, "PV"], errors="coerce").dropna()
                    if not pv_vals.empty:
                        pv_by_month[m_idx] = float(pv_vals.sum())

    # 2. ANC Snapshot by Month
    df_anc = _load_anc_snapshot()
    anc_by_month: dict[int, pd.Series] = {}
    if not df_anc.empty and "_fac_norm" in df_anc.columns:
        sub_anc = df_anc[(df_anc["_fac_norm"] == fac_norm) & (pd.to_numeric(df_anc["Year"], errors="coerce") == year_int)]
        for _, r in sub_anc.iterrows():
            m_num = int(r["MonthNum"])
            anc_by_month[m_num] = r

    # 3. Mentorship & eLearning Engagement from MoniTrac Mentees
    df_mt = _load_mentees_snapshot()
    mt_by_month: dict[int, pd.DataFrame] = {}
    cum_enrolled: dict[int, int] = {}
    cum_completed: dict[int, int] = {}
    if not df_mt.empty and "_fac_norm" in df_mt.columns:
        sub_mt = df_mt[(df_mt["_fac_norm"] == fac_norm) & (df_mt["_Year"] == year_int)].copy()
        if not sub_mt.empty:
            for m_idx in range(1, 13):
                mt_by_month[m_idx] = sub_mt[sub_mt["_MonthNum"] == m_idx]
            # Cumulative unique learners reached / completed through month m
            uid_col = next((c for c in ["beneficiary_uid", "First name"] if c in sub_mt.columns), None)
            mod_col = next((c for c in ["ProgTrac_Lessons", "ProgTrac_Module", "Modality"] if c in sub_mt.columns), None)
            if uid_col:
                for m_idx in range(1, 13):
                    upto = sub_mt[sub_mt["_MonthNum"] <= m_idx]
                    if not upto.empty:
                        cum_enrolled[m_idx] = int(upto[uid_col].dropna().nunique())
                        if mod_col:
                            done = upto[upto[mod_col].notna() & (upto[mod_col].astype(str).str.strip() != "")]
                            cum_completed[m_idx] = int(done[uid_col].dropna().nunique())

    # Determine latest active reporting month for this facility/year (e.g., Oct = 10)
    active_months = set(pv_by_month.keys()) | set(anc_by_month.keys()) | set(mt_by_month.keys())
    if kpi_df_year is not None and not kpi_df_year.empty:
        fac_col_k = kpi_df_year.columns[0]
        sub_k = kpi_df_year[kpi_df_year[fac_col_k].map(_norm_fac) == fac_norm]
        if not sub_k.empty:
            for m_idx, m_full in enumerate(FULL_MONTHS, start=1):
                m_cols = [
                    c for c in kpi_df_year.columns[1:]
                    if m_full.lower() in re.sub(r"\s+", "", str(c)).lower()
                    and str(year_str) in str(c)
                ]
                if m_cols and pd.to_numeric(sub_k[m_cols].iloc[0], errors="coerce").notna().any():
                    active_months.add(m_idx)

    max_active_month = max(active_months) if active_months else 0

    rows = []
    for row_idx, domain, indicator, target, agg_type in HF_KPI_SPECS:
        rec = {
            "Row": row_idx,
            "Domain": domain,
            "Indicator": indicator,
            "Target": target,
            "_agg": agg_type,
        }
        numeric_vals = []
        yes_count = 0
        reported_months = 0

        for m_idx, (m_short, m_full) in enumerate(zip(MONTH_NAMES, FULL_MONTHS), start=1):
            val = None
            anc_r = anc_by_month.get(m_idx)

            if row_idx == 4:  # Total Workload
                val = pv_by_month.get(m_idx)
            elif row_idx == 5 and anc_r is not None:  # Total ANC visits = New + Revisits
                v_new = pd.to_numeric(anc_r.get("ANC_1st_New"), errors="coerce")
                v_rev = pd.to_numeric(anc_r.get("ANC_Revisits"), errors="coerce")
                if pd.notna(v_new) or pd.notna(v_rev):
                    val = float((0 if pd.isna(v_new) else v_new) + (0 if pd.isna(v_rev) else v_rev))
            elif row_idx == 6 and anc_r is not None:  # New ANC Visits
                v = pd.to_numeric(anc_r.get("ANC_1st_New"), errors="coerce")
                val = float(v) if pd.notna(v) else None
            elif row_idx == 7 and anc_r is not None:  # 1st ANC in 1st Trimester (<12Wks)
                v = pd.to_numeric(anc_r.get("ANC_1st_Under_12w"), errors="coerce")
                val = float(v) if pd.notna(v) else None
            elif row_idx == 8 and anc_r is not None:  # At least 4 ANC visits
                v = pd.to_numeric(anc_r.get("ANC_4th_Completed"), errors="coerce")
                val = float(v) if pd.notna(v) else None
            elif row_idx == 9 and anc_r is not None:  # 8 ANC visits
                v = pd.to_numeric(anc_r.get("ANC_8th_Completed"), errors="coerce")
                val = float(v) if pd.notna(v) else None
            elif row_idx == 10:  # Number of Deliveries = Normal + CS + Breach + Assisted
                val = _extract_kpi_wide_month(
                    kpi_df_year, fac_norm, year_str, m_full,
                    ["NormalDeliveries", "CaesarianSections", "BreachDelivery", "Assistedvaginaldelivery"]
                )
            elif row_idx == 11:  # Live Births
                val = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["Livebirth"])
            elif row_idx == 12:  # Macerated Still Birth
                val = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["MaceratedstillBirth"])
            elif row_idx == 13:  # Fresh Still Birth
                val = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["FreshStillBirth"])
            elif row_idx == 14:  # Newborn death 0 - 28 days
                val = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["Neonataldeaths0-28Days"])
            elif row_idx == 15:  # Perinatal Deaths Audited
                val = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["PerinatalDeathsAudited"])
            elif row_idx == 16:  # Under Five (<5) cases treated
                val = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["UnderFive", "<5"])
            elif row_idx == 17:  # Maternal deaths (all age bands)
                val = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["Maternaldeaths"])
            elif row_idx == 18:  # Maternal Deaths Audited
                val = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["MaternalDeathsAudited"])
            elif row_idx == 19:  # PPH cases Identified (A)
                val = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["PPH(PostPartumHaemorrage)A", "PPHcasesIdentified"])
            elif row_idx == 20:  # PPH cases successfully managed (A - Referred)
                pph_a = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["PPH(PostPartumHaemorrage)A"])
                pph_ref = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["PPH(PostPartumHaemorrage)D", "PPHcasesreferred"])
                if pph_a is not None:
                    val = max(0.0, pph_a - (pph_ref or 0.0))
            elif row_idx == 21:  # PPH cases referred (D)
                val = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["PPH(PostPartumHaemorrage)D", "PPHcasesreferred"])
            elif row_idx == 22:  # Birth asphyxia cases (low APGAR / asphyxia)
                val = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["BirthswithlowAPGARscore", "Birthasphyxiacases"])
            elif row_idx == 23:  # Birth Asphyxia cases Successfully Managed (Low APGAR - Asphyxia neonatal deaths)
                asph = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["BirthswithlowAPGARscore"])
                asph_d = _extract_kpi_wide_month(kpi_df_year, fac_norm, year_str, m_full, ["NeonataldeathsduetoAsphyxia"])
                if asph is not None:
                    val = max(0.0, asph - (asph_d or 0.0))
            elif row_idx == 24:  # Routine Full Stock Take Conducted (Yes/No)
                sub_m = mt_by_month.get(m_idx)
                if sub_m is not None and not sub_m.empty:
                    # Check if Management mentorship/review occurred in month
                    has_mgt = sub_m.astype(str).apply(lambda col: col.str.contains("Management|Stock", case=False, na=False)).any().any()
                    val = "Yes" if has_mgt else None
            elif row_idx == 26:  # Management Review Meeting Conducted (Yes/No)
                sub_m = mt_by_month.get(m_idx)
                if sub_m is not None and not sub_m.empty:
                    val = "Yes"
            elif row_idx == 27:  # Staff enrolled on LifeNet eLearning platform
                val = float(cum_enrolled[m_idx]) if m_idx in cum_enrolled else None
            elif row_idx == 28:  # Staff completed eLearning lessons
                val = float(cum_completed[m_idx]) if m_idx in cum_completed else None

            # Key in 0 for reported months up through latest active month (e.g., Jan–Oct)
            if val is None and agg_type in ("sum", "max") and m_idx <= max_active_month:
                val = 0.0

            if val is None:
                rec[m_short] = "—"
            elif isinstance(val, str):
                rec[m_short] = val
                reported_months += 1
                if val.lower() == "yes":
                    yes_count += 1
            else:
                rec[m_short] = int(round(val)) if abs(val - round(val)) < 1e-6 else round(val, 1)
                numeric_vals.append(float(val))
                reported_months += 1

        # Compute YTD Summary column
        if agg_type == "sum":
            rec["YTD Summary"] = int(round(sum(numeric_vals))) if numeric_vals else "—"
        elif agg_type == "max":
            rec["YTD Summary"] = int(round(max(numeric_vals))) if numeric_vals else "—"
        elif agg_type == "pct":
            rec["YTD Summary"] = f"{np.mean(numeric_vals):.1f}%" if numeric_vals else "—"
        elif agg_type == "yesno":
            rec["YTD Summary"] = f"{yes_count} Mos Yes" if reported_months > 0 else "—"
        else:
            rec["YTD Summary"] = "—"

        rows.append(rec)

    return pd.DataFrame(rows)


def export_hf_kpi_excel(selected_fac: str, year_str: str, df_matrix: pd.DataFrame) -> bytes:
    """
    Clones data/KPI Dashboard HF Level_EN 120625.xlsx, stamps Facility Name and Year,
    populates Jan..Dec cells (D4:O28), and returns formatted .xlsx bytes.
    """
    if os.path.exists(TEMPLATE_PATH):
        wb = openpyxl.load_workbook(TEMPLATE_PATH)
    else:
        wb = openpyxl.Workbook()
        wb.active.title = "HF KPIs"

    ws = wb["HF KPIs"]
    # Stamp Facility Name in top title banner & Year in D2
    ws["B1"] = f"KEY PERFORMANCE INDICATOR DASHBOARD — {selected_fac.upper()}"
    ws["D2"] = f"Health Facility: {selected_fac}    |    Reporting Year: {year_str}"

    for _, r in df_matrix.iterrows():
        excel_row = int(r["Row"])
        for m_offset, m_short in enumerate(MONTH_NAMES):
            cell_val = r[m_short]
            col_idx = 4 + m_offset  # Col D = 4 .. Col O = 15
            ws.cell(row=excel_row, column=col_idx, value=None if (cell_val == "—" or cell_val is None) else cell_val)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


def render_hf_kpi_dashboard_section(
    selected_fac: str,
    facility_pv_df: pd.DataFrame,
    kpi_2025: pd.DataFrame,
    kpi_2026: pd.DataFrame,
    focus_year: str,
) -> None:
    """
    Renders the auto-populated Health Facility (HF) Level KPI Dashboard inside Facility 360.
    """
    st.markdown("---")
    hdr_col, yr_col, dl_col = st.columns([2.8, 1.0, 1.3])
    with hdr_col:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(90deg, #C8102E 0%, #991B1B 100%);
                color: #FFFFFF;
                padding: 12px 18px;
                border-radius: 10px;
                border-left: 6px solid #0F2C59;
            ">
                <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; opacity:0.9;">
                    Health Facility Level Key Performance Indicator Dashboard
                </div>
                <div style="font-size:1.22rem; font-weight:800; margin-top:2px;">
                    🏥 {selected_fac}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    year_options = ["2026", "2025"]
    default_idx = year_options.index(str(focus_year)) if str(focus_year) in year_options else 0
    with yr_col:
        hf_year = st.selectbox(
            "Dashboard Year",
            options=year_options,
            index=default_idx,
            key=f"hf_kpi_year_{_norm_fac(selected_fac)}",
        )

    kpi_df_active = kpi_2026 if hf_year == "2026" else kpi_2025
    df_hf = build_hf_kpi_matrix(selected_fac, hf_year, facility_pv_df, kpi_df_active)

    with dl_col:
        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
        excel_bytes = export_hf_kpi_excel(selected_fac, hf_year, df_hf)
        safe_fac = re.sub(r"[^A-Za-z0-9_-]+", "_", selected_fac).strip("_")
        st.download_button(
            label=f"📥 Export {hf_year} Excel Wall-Chart",
            data=excel_bytes,
            file_name=f"HF_KPI_Dashboard_{safe_fac}_{hf_year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=f"dl_hf_kpi_{safe_fac}_{hf_year}",
        )

    st.caption(
        f"**Facility:** {selected_fac} &nbsp;|&nbsp; **Reporting Year:** {hf_year} &nbsp;|&nbsp; "
        f"Auto-populated from KHIS (MOH 711 & ANC), Patient Volume, and MoniTrac facility logs."
    )

    tab_board, tab_defs, tab_ins = st.tabs([
        f"📋 {selected_fac} — {hf_year} KPI Scorecard (Jan–Dec)",
        "📖 Indicator Definitions",
        "💡 Clinical & Management Insights",
    ])

    with tab_board:
        domain_filter = st.selectbox(
            "Filter Indicator Group",
            options=["All 25 HF KPIs"] + list(dict.fromkeys(df_hf["Domain"].tolist())),
            key=f"hf_kpi_dom_{_norm_fac(selected_fac)}_{hf_year}",
        )
        disp_df = df_hf if domain_filter == "All 25 HF KPIs" else df_hf[df_hf["Domain"] == domain_filter]
        cols_show = ["Domain", "Indicator", "Target"] + MONTH_NAMES + ["YTD Summary"]
        st.dataframe(
            disp_df[cols_show],
            use_container_width=True,
            hide_index=True,
            height=680 if domain_filter == "All 25 HF KPIs" else 280,
        )

    with tab_defs:
        df_def, _ = _load_template_defs_and_insights()
        if not df_def.empty:
            st.dataframe(df_def, use_container_width=True, hide_index=True)
        else:
            st.info("Indicator definitions are bundled in data/KPI Dashboard HF Level_EN 120625.xlsx.")

    with tab_ins:
        _, df_ins = _load_template_defs_and_insights()
        if not df_ins.empty:
            st.dataframe(df_ins, use_container_width=True, hide_index=True)
        else:
            st.info("Clinical & management insights are bundled in data/KPI Dashboard HF Level_EN 120625.xlsx.")
