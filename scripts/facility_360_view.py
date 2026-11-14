import re
import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scripts import pss_analytics as pssa
from scripts import finance_analytics as fa

NAVY = "#0F2C59"
NAVY_MID = "#1E40AF"
CRIMSON = "#C8102E"
TEAL = "#0D9488"
AMBER = "#D97706"
SLATE_MUTED = "#64748B"
TEXT_MAIN = "#0F172A"
CARD_BG = "#FFFFFF"

C3_FACILITIES = {
    "butula health centre",
    "misikhu health centre",
    "mukumu mission hospital",
    "kilingili health centre",
    "khunyangu sub county hospital",
    "navakholo sub county hospital",
}


def _kpi_card_html(title: str, value: str, badge_text: str, badge_tone: str = "navy", icon: str = "") -> str:
    tone_styles = {
        "navy": ("#EFF6FF", "#0F2C59", "#0F2C59"),
        "green": ("#ECFDF5", "#047857", "#0D9488"),
        "crimson": ("#FEF2F2", "#B91C1C", "#C8102E"),
        "amber": ("#FFFBEB", "#B45309", "#D97706"),
        "slate": ("#F1F5F9", "#334155", "#64748B"),
    }
    bg, fg, border = tone_styles.get(badge_tone, tone_styles["navy"])
    return f"""
    <div style="
        background:#FFFFFF;
        border:1px solid #E2E8F0;
        border-top:3.5px solid {border};
        border-radius:10px;
        padding:14px 16px;
        box-shadow:0 2px 6px rgba(15,44,89,0.05);
        height:100%;
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-size:0.74rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#475569;">{title}</span>
            <span style="font-size:1.0rem;">{icon}</span>
        </div>
        <div style="font-size:1.55rem; font-weight:800; color:#0F172A; line-height:1.15; margin-bottom:8px;">{value}</div>
        <span style="
            display:inline-block;
            background:{bg};
            color:{fg};
            font-size:0.74rem;
            font-weight:700;
            padding:3px 9px;
            border-radius:999px;
        ">{badge_text}</span>
    </div>
    """


def _section_header(title: str, subtitle: str = "") -> None:
    sub_html = f'<div style="color:#64748B; font-size:0.86rem; margin-top:2px;">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div style="
            border-left:4px solid #0F2C59;
            padding:2px 0 2px 12px;
            margin:1.1rem 0 0.75rem 0;
        ">
            <div style="color:#0F2C59; font-size:1.08rem; font-weight:800; letter-spacing:-0.01em;">{title}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )



def normalize_facility_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    s = name.strip().lower()
    s = re.sub(r"^(ke[\s\-]+|kakamega[\s\-]+|busia[\s\-]+|vihiga[\s\-]+|bungoma[\s\-]+|narok[\s\-]+|kisumu[\s\-]+)", "", s)
    s = re.sub(r"^(agc|ack|aic|sda|pcea|st\.?|saint|catholic|mission)[\s\-]+", "", s)
    s = re.sub(r"\b(sub[\s\-]?county|mission|community|lions|memorial)\b", " ", s)
    s = re.sub(r"\b(hospital|health\s*cent(re|er)|dispensary|medical\s*cent(re|er)|clinic|nursing\s*home|hc|sch)\b", " ", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return " ".join(s.split())


def get_facility_match(df: pd.DataFrame, target_fac: str) -> pd.DataFrame:
    if df is None or df.empty or not target_fac:
        return pd.DataFrame()
    preferred_cols = [
        c for c in df.columns
        if any(k in str(c).lower() for k in ["organisationunitname", "facility_name", "facility", "orgunitname"])
        and not any(bad in str(c).lower() for bad in ["id", "code", "uid"])
    ]
    if not preferred_cols:
        preferred_cols = [
            c for c in df.columns
            if any(k in str(c).lower() for k in ["organisation", "facility", "unit", "org", "name"])
            and not any(bad in str(c).lower() for bad in ["id", "code", "uid"])
        ]
    col = preferred_cols[0] if preferred_cols else df.columns[0]
    raw_target = target_fac.strip().lower()
    exact_raw = df[df[col].astype(str).str.strip().str.lower() == raw_target]
    if not exact_raw.empty:
        return exact_raw

    norm_target = normalize_facility_name(target_fac)
    if not norm_target:
        return pd.DataFrame()

    norm_series = df[col].astype(str).apply(normalize_facility_name)
    exact_norm = df[norm_series == norm_target]
    if not exact_norm.empty:
        return exact_norm

    target_tokens = set(norm_target.split())
    if target_tokens:
        partial = df[
            norm_series.apply(
                lambda x: bool(x) and (
                    norm_target in x
                    or x in norm_target
                    or (len(target_tokens & set(x.split())) >= 1 and len(target_tokens) == 1)
                    or (len(target_tokens & set(x.split())) >= 2)
                )
            )
        ]
        if not partial.empty:
            return partial
    return pd.DataFrame()


def render_facility_360_tab(
    facility_pv_df: pd.DataFrame,
    kpi_2025: pd.DataFrame,
    kpi_2026: pd.DataFrame,
    df_qsc_med: pd.DataFrame,
    df_qsc_mgmt: pd.DataFrame,
    comparison_year: str,
    focus_year: str,
    selected_months: list,
    selected_period: str,
) -> None:
    st.markdown(
        """
        <style>
        div[data-testid="stRadio"] > label {
            color: #0F2C59 !important;
            font-weight: 700 !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label {
            background: #F8FAFC !important;
            border: 1.5px solid #CBD5E1 !important;
            border-radius: 8px !important;
            padding: 6px 14px !important;
            margin-right: 8px !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label p {
            color: #0F172A !important;
            font-weight: 700 !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] {
            background: #0F2C59 !important;
            border-color: #0F2C59 !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] p {
            color: #FFFFFF !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if facility_pv_df is None or facility_pv_df.empty:
        st.warning("No facility patient volume records available for the selected reporting window.")
        return

    fac_col = facility_pv_df.columns[0]
    available_facs = sorted(facility_pv_df[fac_col].dropna().unique().tolist())

    sel_col, exp_col = st.columns([3.2, 1.0])
    with sel_col:
        selected_fac = st.selectbox(
            "Select Partner Health Facility for 360° Audit:",
            available_facs,
            key="fac_360_selector",
        )

    if not selected_fac:
        return

    norm_fac = normalize_facility_name(selected_fac).lower()
    is_cohort3 = norm_fac in C3_FACILITIES
    cohort_label = "Cohort 3 (2026 Onboarded)" if is_cohort3 else "Cohort 1 & 2 Partner"

    # 1. Patient Volume from standardized process_pv_timeline output
    fac_pv_row = facility_pv_df[facility_pv_df[fac_col] == selected_fac]
    num_cols = [c for c in facility_pv_df.columns if c != fac_col and pd.api.types.is_numeric_dtype(facility_pv_df[c])]
    pv_25 = float(fac_pv_row[num_cols[0]].values[0]) if (not fac_pv_row.empty and len(num_cols) >= 1) else 0.0
    pv_26 = float(fac_pv_row[num_cols[1]].values[0]) if (not fac_pv_row.empty and len(num_cols) >= 2) else 0.0
    pv_var = pv_26 - pv_25
    pv_growth = ((pv_var / pv_25) * 100.0) if pv_25 > 0 else 0.0

    # 2. Maternal & Newborn KPIs
    fac_deliv_25 = fac_deliv_26 = fac_live_26 = fac_cs_26 = fac_pph_26 = fac_apgar_26 = 0.0
    df_b_target = kpi_2025 if str(comparison_year) == "2025" else kpi_2026
    df_f_target = kpi_2026 if str(focus_year) == "2026" else kpi_2025

    if df_b_target is not None and df_f_target is not None:
        cols_norm_25 = [
            f"MOH 711 Normal Deliveries {m} {comparison_year}"
            for m in selected_months
            if f"MOH 711 Normal Deliveries {m} {comparison_year}" in df_b_target.columns
        ]
        cols_cs_25 = [
            f"MOH 711 Caesarian Sections {m} {comparison_year}"
            for m in selected_months
            if f"MOH 711 Caesarian Sections {m} {comparison_year}" in df_b_target.columns
        ]
        cols_norm_26 = [
            f"MOH 711 Normal Deliveries {m} {focus_year}"
            for m in selected_months
            if f"MOH 711 Normal Deliveries {m} {focus_year}" in df_f_target.columns
        ]
        cols_cs_26 = [
            f"MOH 711 Caesarian Sections {m} {focus_year}"
            for m in selected_months
            if f"MOH 711 Caesarian Sections {m} {focus_year}" in df_f_target.columns
        ]
        cols_live_26 = [
            f"MOH 711 Live birth {m} {focus_year}"
            for m in selected_months
            if f"MOH 711 Live birth {m} {focus_year}" in df_f_target.columns
        ]
        cols_pph_26 = [
            f"MOH 711 PPH (Post Partum Haemorrage) A {m} {focus_year}"
            for m in selected_months
            if f"MOH 711 PPH (Post Partum Haemorrage) A {m} {focus_year}" in df_f_target.columns
        ]
        cols_apgar_26 = [
            f"MOH 711 Births with low APGAR score {m} {focus_year}"
            for m in selected_months
            if f"MOH 711 Births with low APGAR score {m} {focus_year}" in df_f_target.columns
        ]

        row_25 = get_facility_match(df_b_target, selected_fac)
        row_26 = get_facility_match(df_f_target, selected_fac)

        if not row_25.empty:
            fac_deliv_25 = float(row_25[cols_norm_25 + cols_cs_25].sum(axis=1).values[0]) if cols_norm_25 else 0.0
        if not row_26.empty:
            fac_deliv_26 = float(row_26[cols_norm_26 + cols_cs_26].sum(axis=1).values[0]) if cols_norm_26 else 0.0
            fac_live_26 = float(row_26[cols_live_26].sum(axis=1).values[0]) if cols_live_26 else 0.0
            fac_cs_26 = float(row_26[cols_cs_26].sum(axis=1).values[0]) if cols_cs_26 else 0.0
            fac_pph_26 = float(row_26[cols_pph_26].sum(axis=1).values[0]) if cols_pph_26 else 0.0
            fac_apgar_26 = float(row_26[cols_apgar_26].sum(axis=1).values[0]) if cols_apgar_26 else 0.0

    live_pct = (fac_live_26 / fac_deliv_26 * 100.0) if fac_deliv_26 > 0 else 100.0

    # 3. Pre-fetch QSC, Finance, and PSS summaries
    med_match = get_facility_match(df_qsc_med, selected_fac) if df_qsc_med is not None else pd.DataFrame()
    mgmt_match = get_facility_match(df_qsc_mgmt, selected_fac) if df_qsc_mgmt is not None else pd.DataFrame()

    def _extract_overall_qsc(df_m):
        if df_m is None or df_m.empty:
            return None
        ov_cols = [c for c in df_m.columns if "overall" in str(c).lower()]
        if not ov_cols:
            return None
        v = pd.to_numeric(df_m[ov_cols[-1]].values[0], errors="coerce")
        if pd.isna(v):
            return None
        return float(v) * 100.0 if v <= 1.0 else float(v)

    med_ov = _extract_overall_qsc(med_match)
    mgmt_ov = _extract_overall_qsc(mgmt_match)

    df_fin_fac = fa.get_facility_finance_breakdown()
    fac_fin_match = get_facility_match(df_fin_fac, selected_fac) if (df_fin_fac is not None and not df_fin_fac.empty) else pd.DataFrame()
    fin_status_str = "Not Reported"
    if not fac_fin_match.empty:
        fin_r = fac_fin_match.iloc[0]
        cov_col = "Cost_Coverage_Pct" if "Cost_Coverage_Pct" in fac_fin_match.columns else ("Cost_Coverage_Ratio" if "Cost_Coverage_Ratio" in fac_fin_match.columns else None)
        st_col = "Status" if "Status" in fac_fin_match.columns else ("Financial_Status" if "Financial_Status" in fac_fin_match.columns else None)
        if cov_col and st_col:
            fin_status_str = f"{float(fin_r[cov_col]):.2f}x ({fin_r[st_col]})"
        elif "Total_Revenue" in fac_fin_match.columns and "Total_Expense" in fac_fin_match.columns:
            r_v = float(fin_r["Revenue"])
            e_v = float(fin_r["Expense"])
            ratio = (r_v / e_v) if e_v > 0 else 0.0
            fin_status_str = f"{ratio:.2f}x ({'Surplus' if r_v >= e_v else 'Deficit'})"

    pss_bundle_360 = pssa.get_pss_me_analytics(force_live=False)
    win_lbl_360 = pss_bundle_360.get("window_label", "Past 12 Months")
    fac_pss = pd.DataFrame()
    net_mean_360 = 0.0
    if not pss_bundle_360.get("empty", True):
        df_pss_360 = pss_bundle_360["df"]
        fac_pss = get_facility_match(df_pss_360, selected_fac).copy()
        sort_col = next((c for c in ["periodid", "Period_ID", "Period", "periodname", "Month_Label"] if c in fac_pss.columns), None)
        if sort_col and not fac_pss.empty:
            fac_pss = fac_pss.sort_values(sort_col)
        if not fac_pss.empty:
            if "Month_Label" not in fac_pss.columns:
                fac_pss["Month_Label"] = fac_pss["periodname"].astype(str) if "periodname" in fac_pss.columns else fac_pss[sort_col].astype(str)
            if "Tier" not in fac_pss.columns:
                fac_pss["Tier"] = fac_pss["Net_Satisfaction_Score"].apply(
                    lambda v: "Target Met (≥80%)" if float(v) >= 80.0 else ("Near Target (70–79%)" if float(v) >= 70.0 else "Needs Improvement (<70%)")
                )
        net_mean_360 = float(df_pss_360["Net_Satisfaction_Score"].mean())

    pss_pill = (
        f"{fac_pss['Net_Satisfaction_Score'].mean():.1f}% ({len(fac_pss)} rounds)"
        if not fac_pss.empty
        else "Pending 12M Round"
    )
    qsc_pill = (
        f"Med {med_ov:.1f}% | Mgmt {mgmt_ov:.1f}%"
        if (med_ov is not None and mgmt_ov is not None)
        else (f"Med {med_ov:.1f}%" if med_ov is not None else ("Cohort 3 Baseline" if is_cohort3 else "Pending"))
    )

    dossier_df = pd.DataFrame(
        [
            {
                "Facility": selected_fac,
                "Cohort": cohort_label,
                "Reporting_Window": f"{selected_period} ({comparison_year} vs {focus_year})",
                f"Visits_{comparison_year}": int(pv_25),
                f"Visits_{focus_year}": int(pv_26),
                "YoY_Visit_Growth_Pct": round(pv_growth, 2),
                f"Deliveries_{focus_year}": int(fac_deliv_26),
                f"Live_Births_{focus_year}": int(fac_live_26),
                "Live_Birth_Rate_Pct": round(live_pct, 2),
                "Medical_QSC_Overall_Pct": round(med_ov, 1) if med_ov is not None else None,
                "Management_QSC_Overall_Pct": round(mgmt_ov, 1) if mgmt_ov is not None else None,
                "Finance_Cost_Coverage": fin_status_str,
                "PSS_12M_Summary": pss_pill,
            }
        ]
    )
    with exp_col:
        st.markdown("<div style='height:26px;'></div>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Export Facility Brief (CSV)",
            data=dossier_df.to_csv(index=False).encode("utf-8"),
            file_name=f"LifeNet_360_{selected_fac.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Deep Navy Executive Hero Banner
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #0F2C59 0%, #173F7A 100%);
            border-radius: 12px;
            padding: 20px 24px;
            color: #FFFFFF;
            margin: 0.4rem 0 1.1rem 0;
            box-shadow: 0 6px 18px rgba(15, 44, 89, 0.16);
            border-left: 6px solid #C8102E;
        ">
            <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#93C5FD;">
                Facility 360° Executive Dossier &nbsp;•&nbsp; {cohort_label}
            </div>
            <h2 style="color:#FFFFFF; font-size:1.55rem; font-weight:800; margin:4px 0 4px 0;">
                {selected_fac}
            </h2>
            <div style="color:#E2E8F0; font-size:0.88rem;">
                Window: <b>{selected_period}</b> ({comparison_year} vs. {focus_year}) &nbsp;|&nbsp;
                QSC: <b>{qsc_pill}</b> &nbsp;|&nbsp;
                Solvency: <b>{fin_status_str}</b> &nbsp;|&nbsp;
                PSS: <b>{pss_pill}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 5 Executive KPI Cards
    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        st.markdown(
            _kpi_card_html(
                f"{comparison_year} Baseline PV",
                f"{int(pv_25):,}",
                f"Baseline ({selected_period})",
                "slate",
                "📅",
            ),
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            _kpi_card_html(
                f"{focus_year} Focus PV",
                f"{int(pv_26):,}",
                f"Current ({selected_period})",
                "navy",
                "🏥",
            ),
            unsafe_allow_html=True,
        )
    with f3:
        tone_pv = "green" if pv_var >= 0 else "crimson"
        st.markdown(
            _kpi_card_html(
                "YoY Attendance Growth",
                f"{pv_growth:+.1f}%",
                f"{int(pv_var):+,} Visits vs {comparison_year}",
                tone_pv,
                "📈",
            ),
            unsafe_allow_html=True,
        )
    with f4:
        deliv_var = fac_deliv_26 - fac_deliv_25
        st.markdown(
            _kpi_card_html(
                "Total Deliveries",
                f"{int(fac_deliv_26):,}",
                f"{int(deliv_var):+,} vs {comparison_year}",
                "navy",
                "👶",
            ),
            unsafe_allow_html=True,
        )
    with f5:
        tone_lb = "green" if live_pct >= 98.0 else ("amber" if live_pct >= 95.0 else "crimson")
        st.markdown(
            _kpi_card_html(
                "Live Birth Rate",
                f"{live_pct:.1f}%",
                f"{int(fac_live_26):,} Live Births",
                tone_lb,
                "🌱",
            ),
            unsafe_allow_html=True,
        )

    # Section 1: Attendance & Maternal Clinical Outcomes
    _section_header(
        "1. Patient Attendance & MOH 711 Maternal Outcomes",
        f"Comparing {comparison_year} baseline against {focus_year} clinical service delivery for {selected_fac}.",
    )
    c_fac1, c_fac2 = st.columns([1.15, 1.0])

    with c_fac1:
        y_max_pv = max(pv_25, pv_26) * 1.32 if max(pv_25, pv_26) > 0 else 100
        fig_fac_pv = go.Figure(
            data=[
                go.Bar(
                    name=f"{comparison_year} Baseline",
                    x=["Patient Attendance"],
                    y=[pv_25],
                    text=[f"{int(pv_25):,}"],
                    textposition="outside",
                    cliponaxis=False,
                    textfont=dict(color=TEXT_MAIN, size=13, family="Inter"),
                    marker_color="#94A3B8",
                    width=0.28,
                ),
                go.Bar(
                    name=f"{focus_year} Focus",
                    x=["Patient Attendance"],
                    y=[pv_26],
                    text=[f"{int(pv_26):,} ({pv_growth:+.1f}%)"],
                    textposition="outside",
                    cliponaxis=False,
                    textfont=dict(color=NAVY, size=13, family="Inter"),
                    marker_color=NAVY,
                    width=0.28,
                ),
            ]
        )
        fig_fac_pv.update_layout(
            barmode="group",
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            title=dict(
                text=f"<b>Patient Attendance — {comparison_year} vs. {focus_year}</b>",
                font=dict(size=15, color=TEXT_MAIN),
            ),
            font=dict(family="Inter"),
            height=360,
            xaxis=dict(showgrid=False, tickfont=dict(color=TEXT_MAIN, size=13)),
            yaxis=dict(
                range=[0, y_max_pv],
                showgrid=True,
                gridcolor="#E2E8F0",
                tickfont=dict(color=SLATE_MUTED, size=12),
            ),
            legend=dict(
                orientation="h",
                y=1.14,
                x=0,
                xanchor="left",
                font=dict(color=TEXT_MAIN, size=12.5),
            ),
            margin=dict(l=40, r=30, t=75, b=30),
        )
        st.plotly_chart(fig_fac_pv, use_container_width=True)

    with c_fac2:
        outcomes_labels = ["Deliveries", "Live Births", "C-Sections", "PPH Cases", "Low APGAR"]
        outcomes_vals = [fac_deliv_26, fac_live_26, fac_cs_26, fac_pph_26, fac_apgar_26]
        y_max_out = max(outcomes_vals) * 1.32 if max(outcomes_vals) > 0 else 10

        fig_fac_kpi = go.Figure(
            go.Bar(
                x=outcomes_labels,
                y=outcomes_vals,
                text=[f"{int(v):,}" for v in outcomes_vals],
                textposition="outside",
                cliponaxis=False,
                textfont=dict(color=TEXT_MAIN, size=12.5, family="Inter"),
                marker_color=[NAVY, TEAL, NAVY_MID, CRIMSON, AMBER],
            )
        )
        fig_fac_kpi.update_layout(
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            title=dict(
                text=f"<b>MOH 711 Clinical Outcomes ({focus_year})</b>",
                font=dict(size=15, color=TEXT_MAIN),
            ),
            font=dict(family="Inter"),
            height=360,
            xaxis=dict(showgrid=False, tickfont=dict(color=TEXT_MAIN, size=12)),
            yaxis=dict(
                range=[0, y_max_out],
                showgrid=True,
                gridcolor="#E2E8F0",
                tickfont=dict(color=SLATE_MUTED, size=12),
            ),
            margin=dict(l=40, r=30, t=75, b=30),
        )
        st.plotly_chart(fig_fac_kpi, use_container_width=True)

    # Section 2: Quality Scorecard (QSC) Facility Progress Audit
    _section_header(
        f"2. Quality Scorecard (QSC) Module Audit — {selected_fac}",
        "Module-by-module clinical and operational quality compliance against LifeNet's 85% excellence benchmark.",
    )
    fac_qsc_pillar = st.radio(
        "Select QSC Audit Pillar:",
        ["Medical QSC (Clinical)", "Management QSC (Operations)"],
        horizontal=True,
        key="fac_inspector_qsc_pillar",
    )
    is_fac_med = "Medical" in fac_qsc_pillar
    target_qsc_df = df_qsc_med if is_fac_med else df_qsc_mgmt
    df_fac_qsc = pd.DataFrame()

    qsc_path = os.path.join("data", "Cohort 1&2 QSC Analytics final.xlsx")
    if not os.path.exists(qsc_path) and os.path.exists("Cohort 1&2 QSC Analytics final.xlsx"):
        qsc_path = "Cohort 1&2 QSC Analytics final.xlsx"

    if is_cohort3:
        st.info(
            f"**Cohort 3 Baseline Facility:** **{selected_fac}** was onboarded in 2026. Initial QSC assessment rounds are shown below."
        )
        c3_sheet_name = "Cohort 3 Medical QSC" if is_fac_med else "Cohort 3 Management QSC"
        if os.path.exists(qsc_path):
            xl_qsc = pd.ExcelFile(qsc_path, engine="openpyxl")
            if c3_sheet_name in xl_qsc.sheet_names:
                df_c3_qsc = pd.read_excel(qsc_path, sheet_name=c3_sheet_name, engine="openpyxl")
                df_fac_qsc = get_facility_match(df_c3_qsc, selected_fac)
                if not df_fac_qsc.empty:
                    q_cols = [
                        c
                        for c in df_fac_qsc.columns
                        if any(k in str(c).lower() for k in ["q1", "q2", "q3", "q4", "baseline", "overall", "score"])
                    ]
                    if q_cols:
                        df_c3_melt = df_fac_qsc[q_cols].melt(var_name="Assessment Round", value_name="Score").dropna()
                        df_c3_melt["Score (%)"] = df_c3_melt["Score"].apply(
                            lambda x: round(float(x) * 100, 1)
                            if isinstance(x, (int, float)) and x <= 1.0
                            else (round(float(x), 1) if isinstance(x, (int, float)) else 0.0)
                        )
                        st.dataframe(
                            df_c3_melt[["Assessment Round", "Score (%)"]],
                            use_container_width=True,
                            hide_index=True,
                        )
    else:
        df_fac_qsc = get_facility_match(target_qsc_df, selected_fac)

    if not df_fac_qsc.empty and not is_cohort3:
        med_module_titles = {
            1: ("M1: Back to Basics", "M1: Back to<br>Basics"),
            2: ("M2: Safe Baby", "M2: Safe<br>Baby"),
            3: ("M3: Safe Mother", "M3: Safe<br>Mother"),
            4: ("M4: Healthy Children", "M4: Healthy<br>Children"),
            5: ("M5: Top Burdens of Disease", "M5: Top Burdens<br>of Disease"),
            6: ("M6: Infection Prevention", "M6: Infection<br>Prevention"),
        }
        mgmt_module_titles = {
            1: ("M1: Financial Mgmt 1 & Admin", "M1: Financial Mgmt 1<br>& Administration"),
            2: ("M2: Financial Mgmt 2 with HRM", "M2: Financial Mgmt 2<br>with HRM"),
            3: ("M3: Pharmaceutical Management", "M3: Pharmaceutical<br>Management"),
            4: ("M4: Marketing & Sustainability", "M4: Marketing & Fin.<br>Sustainability"),
        }
        title_map = med_module_titles if is_fac_med else mgmt_module_titles

        paired_rows = []
        for mod_num in range(1, 7):
            base_cols = [
                c for c in df_fac_qsc.columns
                if f"module {mod_num}" in str(c).lower() and "baseline" in str(c).lower()
            ]
            end_cols = [
                c for c in df_fac_qsc.columns
                if f"module {mod_num}" in str(c).lower() and "endline" in str(c).lower()
            ]
            if base_cols or end_cols:
                b_raw = pd.to_numeric(df_fac_qsc[base_cols[0]].values[0], errors="coerce") if base_cols else None
                e_raw = pd.to_numeric(df_fac_qsc[end_cols[0]].values[0], errors="coerce") if end_cols else None
                b_val = (float(b_raw) * 100.0 if float(b_raw) <= 1.0 else float(b_raw)) if pd.notna(b_raw) else None
                e_val = (float(e_raw) * 100.0 if float(e_raw) <= 1.0 else float(e_raw)) if pd.notna(e_raw) else None
                if b_val is not None or e_val is not None:
                    full_lbl, wrap_lbl = title_map.get(mod_num, (f"Module {mod_num}", f"Module {mod_num}"))
                    paired_rows.append(
                        {
                            "Module": full_lbl,
                            "Module_Wrap": wrap_lbl,
                            "Baseline": round(b_val, 1) if b_val is not None else 0.0,
                            "Endline": round(e_val, 1) if e_val is not None else 0.0,
                            "Gain_pp": round((e_val or 0.0) - (b_val or 0.0), 1),
                        }
                    )

        if paired_rows:
            df_qsc_paired = pd.DataFrame(paired_rows)
            chart_h = 370 if len(df_qsc_paired) <= 4 else 415
            q_col_chart, q_col_tbl = st.columns([1.22, 1.0])

            with q_col_chart:
                fig_fac_qsc = go.Figure(
                    data=[
                        go.Bar(
                            name="Baseline Audit",
                            x=df_qsc_paired["Module_Wrap"],
                            y=df_qsc_paired["Baseline"],
                            text=[f"{v:.1f}%" for v in df_qsc_paired["Baseline"]],
                            textposition="outside",
                            cliponaxis=False,
                            textfont=dict(color=SLATE_MUTED, size=11, family="Inter"),
                            marker_color="#94A3B8",
                        ),
                        go.Bar(
                            name="Endline Audit",
                            x=df_qsc_paired["Module_Wrap"],
                            y=df_qsc_paired["Endline"],
                            text=[f"{v:.1f}%" for v in df_qsc_paired["Endline"]],
                            textposition="outside",
                            cliponaxis=False,
                            textfont=dict(color=NAVY, size=11, family="Inter"),
                            marker_color=NAVY,
                        ),
                    ]
                )
                fig_fac_qsc.add_hline(
                    y=85.0,
                    line_dash="dash",
                    line_color=TEAL,
                    annotation_text="<b>85% Target</b>",
                    annotation_position="top left",
                    annotation_font=dict(color=TEAL, size=11),
                )
                fig_fac_qsc.update_layout(
                    barmode="group",
                    bargap=0.28,
                    bargroupgap=0.08,
                    paper_bgcolor=CARD_BG,
                    plot_bgcolor=CARD_BG,
                    title=dict(
                        text=f"<b>{'Medical' if is_fac_med else 'Management'} QSC: Baseline vs. Endline</b>",
                        font=dict(size=15, color=TEXT_MAIN),
                    ),
                    font=dict(family="Inter"),
                    height=chart_h,
                    xaxis=dict(
                        showgrid=False,
                        tickangle=0,
                        tickfont=dict(color=TEXT_MAIN, size=11),
                    ),
                    yaxis=dict(
                        range=[0, 118],
                        showgrid=True,
                        gridcolor="#E2E8F0",
                        title="Compliance (%)",
                        tickfont=dict(color="#1E293B", size=11),
                    ),
                    legend=dict(
                        orientation="h",
                        y=1.13,
                        x=0,
                        xanchor="left",
                        font=dict(color=TEXT_MAIN, size=12),
                    ),
                    margin=dict(l=42, r=20, t=68, b=46),
                )
                st.plotly_chart(fig_fac_qsc, use_container_width=True)

            with q_col_tbl:
                rows_html = []
                for _, r in df_qsc_paired.iterrows():
                    end_v = float(r["Endline"])
                    if end_v >= 85.0:
                        badge = '<span style="background:#DCFCE7;color:#166534;padding:3px 8px;border-radius:12px;font-weight:600;font-size:0.74rem;">✓ Target Met</span>'
                    elif end_v >= 75.0:
                        badge = '<span style="background:#FEF3C7;color:#92400E;padding:3px 8px;border-radius:12px;font-weight:600;font-size:0.74rem;">▲ Near Target</span>'
                    else:
                        badge = '<span style="background:#FEE2E2;color:#991B1B;padding:3px 8px;border-radius:12px;font-weight:600;font-size:0.74rem;">! Priority Gap</span>'
                    rows_html.append(
                        f"<tr style='border-bottom:1px solid #E2E8F0;'>"
                        f"<td style='padding:10px 10px;font-weight:600;color:#0F172A;'>{r['Module']}</td>"
                        f"<td style='padding:10px 8px;text-align:right;color:#475569;'>{r['Baseline']:.1f}%</td>"
                        f"<td style='padding:10px 8px;text-align:right;font-weight:700;color:#0F2C59;'>{end_v:.1f}%</td>"
                        f"<td style='padding:10px 8px;text-align:right;font-weight:600;color:#0D9488;'>{r['Gain_pp']:+.1f} pp</td>"
                        f"<td style='padding:10px 10px;text-align:center;'>{badge}</td>"
                        f"</tr>"
                    )

                best_row = df_qsc_paired.loc[df_qsc_paired["Gain_pp"].idxmax()]
                below_target = df_qsc_paired[df_qsc_paired["Endline"] < 85.0]["Module"].tolist()
                gap_text = (
                    f"Focus mentorship on <b>{', '.join(below_target)}</b> to clear the 85% threshold."
                    if below_target
                    else "All audited modules have cleared LifeNet's <b>85.0%</b> excellence benchmark."
                )

                right_panel_html = f"""
                <div style="
                    height:{chart_h}px;
                    display:flex;
                    flex-direction:column;
                    justify-content:space-between;
                    box-sizing:border-box;
                ">
                    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(15,23,42,0.04);">
                        <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;font-size:0.82rem;">
                            <thead>
                                <tr style="background:#0F2C59;color:#FFFFFF;text-transform:uppercase;font-size:0.71rem;letter-spacing:0.04em;">
                                    <th style="padding:11px 10px;text-align:left;">Module</th>
                                    <th style="padding:11px 8px;text-align:right;">Base</th>
                                    <th style="padding:11px 8px;text-align:right;">End</th>
                                    <th style="padding:11px 8px;text-align:right;">Gain</th>
                                    <th style="padding:11px 10px;text-align:center;">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(rows_html)}
                            </tbody>
                        </table>
                    </div>
                    <div style="
                        background:#F8FAFC;
                        border:1px solid #E2E8F0;
                        border-left:4px solid #0F2C59;
                        border-radius:8px;
                        padding:11px 14px;
                        color:#1E293B;
                        font-size:0.84rem;
                        line-height:1.45;
                    ">
                        <b>M&E Quality Note:</b> Largest gain achieved in <b>{best_row['Module']}</b>
                        (<b>{best_row['Gain_pp']:+.1f} pp</b>, reaching <b>{best_row['Endline']:.1f}%</b>). {gap_text}
                    </div>
                </div>
                """
                st.markdown(right_panel_html, unsafe_allow_html=True)
    elif df_fac_qsc.empty:
        st.info(
            f"No individual {'Medical' if is_fac_med else 'Management'} QSC module records found for **{selected_fac}** in the current master file."
        )

    # Section 3: Financial Performance & Operational Solvency
    _section_header(
        f"3. Financial Performance & Operational Solvency — {selected_fac}",
        "MoniTrac income vs. operating expenditure and cost-coverage sustainability.",
    )
    if not fac_fin_match.empty:
        fin_r = fac_fin_match.iloc[0]
        rev_val = float(pd.to_numeric(fin_r.get("Total_Revenue", 0.0), errors="coerce") or 0.0)
        exp_val = float(pd.to_numeric(fin_r.get("Total_Expense", 0.0), errors="coerce") or 0.0)
        net_val = float(pd.to_numeric(fin_r.get("Net_Margin", rev_val - exp_val), errors="coerce") or (rev_val - exp_val))
        cov_pct = float(pd.to_numeric(fin_r.get("Cost_Coverage_Pct", (rev_val / exp_val * 100.0) if exp_val > 0 else 0.0), errors="coerce") or 0.0)
        cov_ratio = (cov_pct / 100.0) if exp_val > 0 else 0.0
        months_rep = int(pd.to_numeric(fin_r.get("Months_Reported", 0), errors="coerce") or 0)
        deficit_months = int(pd.to_numeric(fin_r.get("Deficit_Months", 0), errors="coerce") or 0)
        fin_status = str(fin_r.get("Status", "Surplus" if net_val >= 0 else "Operating Deficit"))

        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            st.markdown(
                _kpi_card_html(
                    "FY2026 Total Revenue",
                    f"KES {rev_val:,.0f}",
                    f"{months_rep} Months Reported",
                    "navy",
                    "💰",
                ),
                unsafe_allow_html=True,
            )
        with fc2:
            exp_badge = f"{deficit_months} Deficit Month{'s' if deficit_months != 1 else ''}" if deficit_months > 0 else "Total Reported Outflow"
            st.markdown(
                _kpi_card_html(
                    "FY2026 Operating Expenses",
                    f"KES {exp_val:,.0f}",
                    exp_badge,
                    "amber" if deficit_months > 0 else "slate",
                    "🧾",
                ),
                unsafe_allow_html=True,
            )
        with fc3:
            margin_pct = (net_val / rev_val * 100.0) if rev_val > 0 else 0.0
            tone_net = "green" if net_val >= 0 else "crimson"
            st.markdown(
                _kpi_card_html(
                    "Net Surplus / Deficit",
                    f"KES {net_val:,.0f}",
                    f"{margin_pct:+.1f}% Operating Margin",
                    tone_net,
                    "📊",
                ),
                unsafe_allow_html=True,
            )
        with fc4:
            if exp_val <= 0:
                cov_disp = "N/A"
                cov_badge = "Expenses Not Logged"
                tone_cov = "slate"
            else:
                cov_disp = f"{cov_ratio:.2f}x"
                cov_badge = f"{cov_pct:.0f}% ({fin_status})"
                tone_cov = "green" if cov_ratio >= 1.0 else ("amber" if cov_ratio >= 0.85 else "crimson")
            st.markdown(
                _kpi_card_html(
                    "Cost Coverage Ratio",
                    cov_disp,
                    cov_badge,
                    tone_cov,
                    "🏦",
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        fin_c1, fin_c2 = st.columns([1.0, 1.45])

        with fin_c1:
            if rev_val > 0 or exp_val > 0:
                if net_val >= 0:
                    d_labels = ["Operating Expenses", "Retained Net Surplus"]
                    d_vals = [max(exp_val, 0.0), max(net_val, 0.0)]
                    d_colors = ["#0F2C59", "#0D9488"]
                else:
                    d_labels = ["Revenue Collected", "Uncovered Deficit"]
                    d_vals = [max(rev_val, 0.0), abs(net_val)]
                    d_colors = ["#0F2C59", "#C8102E"]

                center_txt = (
                    f"<b>{cov_ratio:.2f}x</b><br><span style='font-size:11px;color:#64748B;'>Coverage</span>"
                    if exp_val > 0
                    else "<b>100%</b><br><span style='font-size:11px;color:#64748B;'>Margin</span>"
                )
                fig_fin_donut = go.Figure(
                    data=[
                        go.Pie(
                            labels=d_labels,
                            values=d_vals,
                            hole=0.60,
                            marker=dict(colors=d_colors, line=dict(color="#FFFFFF", width=2)),
                            textinfo="percent",
                            textposition="inside",
                            textfont=dict(color="#FFFFFF", size=12, family="Inter"),
                            hovertemplate="<b>%{label}</b><br>KES %{value:,.0f} (%{percent})<extra></extra>",
                        )
                    ]
                )
                fig_fin_donut.add_annotation(
                    text=center_txt,
                    x=0.5,
                    y=0.5,
                    font=dict(size=18, color=TEXT_MAIN, family="Inter"),
                    showarrow=False,
                )
                fig_fin_donut.update_layout(
                    paper_bgcolor=CARD_BG,
                    plot_bgcolor=CARD_BG,
                    title=dict(
                        text="<b>Revenue Utilization & Surplus Split</b>",
                        font=dict(size=14.5, color=TEXT_MAIN),
                    ),
                    font=dict(family="Inter"),
                    height=335,
                    legend=dict(
                        orientation="h",
                        y=-0.08,
                        x=0.5,
                        xanchor="center",
                        font=dict(color=TEXT_MAIN, size=11.5),
                    ),
                    margin=dict(l=20, r=20, t=55, b=45),
                )
                st.plotly_chart(fig_fin_donut, use_container_width=True)

        with fin_c2:
            monthly_rows = []
            try:
                df_fin_raw = fa.load_finance_data()
                fac_raw_match = get_facility_match(df_fin_raw, selected_fac)
                if not fac_raw_match.empty:
                    r_raw = fac_raw_match.iloc[0]
                    month_pairs = [
                        ("Jan", "January"), ("Feb", "February"), ("Mar", "March"),
                        ("Apr", "April"), ("May", "May"), ("Jun", "June"),
                        ("Jul", "July"), ("Aug", "August"), ("Sep", "September"),
                        ("Oct", "October"), ("Nov", "November"), ("Dec", "December"),
                    ]
                    for m_short, m_full in month_pairs:
                        rev_c = [c for c in df_fin_raw.columns if "reven" in str(c).lower() and m_full.lower() in str(c).lower()]
                        exp_c = [c for c in df_fin_raw.columns if "expense" in str(c).lower() and m_full.lower() in str(c).lower()]
                        r_m = pd.to_numeric(r_raw[rev_c[0]], errors="coerce") if rev_c else None
                        e_m = pd.to_numeric(r_raw[exp_c[0]], errors="coerce") if exp_c else None
                        if pd.notna(r_m) or pd.notna(e_m):
                            rv = float(r_m) if pd.notna(r_m) else 0.0
                            ev = float(e_m) if pd.notna(e_m) else 0.0
                            if rv > 0 or ev > 0:
                                monthly_rows.append({"Month": m_short, "Revenue": rv, "Expenses": ev})
            except Exception:
                monthly_rows = []

            if monthly_rows:
                df_m_fin = pd.DataFrame(monthly_rows)
                exp_bar_colors = [
                    "#C8102E" if row["Expenses"] > row["Revenue"] else "#94A3B8"
                    for _, row in df_m_fin.iterrows()
                ]
                def _fmt_kes_short(v):
                    if v >= 1_000_000:
                        return f"{v / 1_000_000:.2f}M"
                    if v >= 1_000:
                        return f"{v / 1_000:.0f}K"
                    return f"{v:,.0f}"

                max_fin_y = max(
                    float(df_m_fin["Revenue"].max()) if not df_m_fin.empty else 0.0,
                    float(df_m_fin["Expenses"].max()) if not df_m_fin.empty else 0.0,
                )
                fig_fin_trend = go.Figure(
                    data=[
                        go.Bar(
                            name="Monthly Revenue",
                            x=df_m_fin["Month"],
                            y=df_m_fin["Revenue"],
                            text=[_fmt_kes_short(v) for v in df_m_fin["Revenue"]],
                            textposition="outside",
                            cliponaxis=False,
                            textfont=dict(color="#0F2C59", size=10.5, family="Inter"),
                            marker_color=NAVY,
                            hovertemplate="<b>%{x} Revenue</b><br>KES %{y:,.0f}<extra></extra>",
                        ),
                        go.Bar(
                            name="Operating Expenses (Red = Deficit)",
                            x=df_m_fin["Month"],
                            y=df_m_fin["Expenses"],
                            text=[_fmt_kes_short(v) for v in df_m_fin["Expenses"]],
                            textposition="outside",
                            cliponaxis=False,
                            textfont=dict(color="#334155", size=10.5, family="Inter"),
                            marker_color=exp_bar_colors,
                            hovertemplate="<b>%{x} Expenses</b><br>KES %{y:,.0f}<extra></extra>",
                        ),
                    ]
                )
                fig_fin_trend.update_layout(
                    barmode="group",
                    bargap=0.24,
                    bargroupgap=0.08,
                    paper_bgcolor=CARD_BG,
                    plot_bgcolor=CARD_BG,
                    title=dict(
                        text="<b>Monthly Revenue vs. Operating Expenses (FY2026)</b>",
                        font=dict(size=14.5, color=TEXT_MAIN),
                    ),
                    font=dict(family="Inter", color=TEXT_MAIN),
                    height=345,
                    xaxis=dict(showgrid=False, tickfont=dict(color="#0F172A", size=11.5)),
                    yaxis=dict(
                        range=[0, max_fin_y * 1.18 if max_fin_y > 0 else 1],
                        showgrid=True,
                        gridcolor="#E2E8F0",
                        title=dict(text="Amount (KES)", font=dict(color="#1E293B", size=11.5)),
                        tickfont=dict(color="#1E293B", size=11),
                    ),
                    legend=dict(
                        orientation="h",
                        y=1.14,
                        x=0,
                        xanchor="left",
                        font=dict(color="#0F172A", size=11.5),
                    ),
                    margin=dict(l=58, r=20, t=68, b=40),
                )
                st.plotly_chart(fig_fin_trend, use_container_width=True)
    else:
        st.info(
            f"No financial records found for **{selected_fac}** in the FY2026 MoniTrac finance dataset."
        )

    # Section 4: Patient Satisfaction Survey (PSS) Profile — Rolling Past 12 Months
    _section_header(
        f"4. Patient Satisfaction Survey (PSS) Profile — {selected_fac} ({win_lbl_360})",
        "Rolling 12-month MoniTrac exit-interview trajectory against LifeNet's 80.0% patient satisfaction target.",
    )
    if not pss_bundle_360.get("empty", True):
        if fac_pss.empty:
            st.info(
                f"**Unassessed in Past 12 Months ({win_lbl_360}):** **{selected_fac}** has no recorded Patient Satisfaction Survey in MoniTrac during this window. "
                f"Prioritize an exit-interview round during the next field mentorship visit."
            )
        else:
            ov_fac = float(fac_pss["Net_Satisfaction_Score"].mean())
            latest_row = fac_pss.iloc[-1]
            latest_sc = float(latest_row["Net_Satisfaction_Score"])
            diff_vs_net = ov_fac - net_mean_360

            kp1, kp2, kp3, kp4 = st.columns(4)
            with kp1:
                st.markdown(
                    _kpi_card_html(
                        "Net Satisfaction (12M Mean)",
                        f"{ov_fac:.1f}%",
                        f"{diff_vs_net:+.1f} pp vs Network ({net_mean_360:.1f}%)",
                        "green" if ov_fac >= 80.0 else "amber",
                        "😊",
                    ),
                    unsafe_allow_html=True,
                )
            with kp2:
                st.markdown(
                    _kpi_card_html(
                        f"Latest Round ({latest_row['Month_Label']})",
                        f"{latest_sc:.1f}%",
                        f"{latest_sc - 80.0:+.1f} pp vs 80% Target",
                        "green" if latest_sc >= 80.0 else "crimson",
                        "🎯",
                    ),
                    unsafe_allow_html=True,
                )
            with kp3:
                st.markdown(
                    _kpi_card_html(
                        "Network 12M Benchmark",
                        "80.0%",
                        f"Network Mean: {net_mean_360:.1f}%",
                        "navy",
                        "📏",
                    ),
                    unsafe_allow_html=True,
                )
            with kp4:
                st.markdown(
                    _kpi_card_html(
                        "Completed 12M Rounds",
                        f"{len(fac_pss)} Surveys",
                        "MoniTrac PSS Element",
                        "slate",
                        "📋",
                    ),
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            pss_chart_h = 335
            c_pss_360_1, c_pss_360_2 = st.columns([1.22, 1.0])
            with c_pss_360_1:
                fig_pss_tr = go.Figure()
                fig_pss_tr.add_trace(
                    go.Scatter(
                        x=fac_pss["Month_Label"],
                        y=fac_pss["Net_Satisfaction_Score"],
                        mode="lines+markers+text",
                        name=selected_fac,
                        text=[f"{v:.1f}%" for v in fac_pss["Net_Satisfaction_Score"]],
                        textposition="top center",
                        textfont=dict(color=NAVY, size=12, family="Inter"),
                        line=dict(color=NAVY, width=3),
                        marker=dict(size=10, color=NAVY),
                    )
                )
                fig_pss_tr.add_hline(
                    y=80.0,
                    line_dash="dash",
                    line_color=TEAL,
                    annotation_text="<b>80% Target</b>",
                    annotation_position="top right",
                    annotation_font=dict(color=TEAL, size=11),
                )
                fig_pss_tr.add_hline(
                    y=net_mean_360,
                    line_dash="dot",
                    line_color=CRIMSON,
                    annotation_text=f"<b>Network Mean ({net_mean_360:.1f}%)</b>",
                    annotation_position="bottom right",
                    annotation_font=dict(color=CRIMSON, size=11),
                )
                fig_pss_tr.update_layout(
                    title=dict(
                        text=f"<b>Net Satisfaction Trajectory — {win_lbl_360}</b>",
                        font=dict(size=14.5, color=TEXT_MAIN),
                    ),
                    paper_bgcolor=CARD_BG,
                    plot_bgcolor=CARD_BG,
                    font=dict(family="Inter", color=TEXT_MAIN),
                    height=pss_chart_h,
                    yaxis=dict(
                        range=[0, 118],
                        showgrid=True,
                        gridcolor="#E2E8F0",
                        title=dict(text="Net Satisfaction (%)", font=dict(color="#1E293B", size=11.5)),
                        tickfont=dict(color="#1E293B", size=11),
                    ),
                    xaxis=dict(
                        showgrid=False,
                        title=dict(text="Survey Period", font=dict(color="#1E293B", size=11.5)),
                        tickfont=dict(color="#0F172A", size=11.5),
                    ),
                    margin=dict(l=48, r=28, t=55, b=46),
                )
                st.plotly_chart(fig_pss_tr, use_container_width=True)

            with c_pss_360_2:
                pss_rows_html = []
                for _, pr in fac_pss.iterrows():
                    sc_v = float(pr["Net_Satisfaction_Score"])
                    diff_v = sc_v - net_mean_360
                    if sc_v >= 80.0:
                        p_badge = '<span style="background:#DCFCE7;color:#166534;padding:3px 8px;border-radius:12px;font-weight:600;font-size:0.74rem;">✓ Target Met</span>'
                    elif sc_v >= 70.0:
                        p_badge = '<span style="background:#FEF3C7;color:#92400E;padding:3px 8px;border-radius:12px;font-weight:600;font-size:0.74rem;">▲ Near Target</span>'
                    else:
                        p_badge = '<span style="background:#FEE2E2;color:#991B1B;padding:3px 8px;border-radius:12px;font-weight:600;font-size:0.74rem;">! Below Target</span>'
                    pss_rows_html.append(
                        f"<tr style='border-bottom:1px solid #E2E8F0;'>"
                        f"<td style='padding:10px 10px;font-weight:600;color:#0F172A;'>{pr['Month_Label']}</td>"
                        f"<td style='padding:10px 8px;text-align:right;font-weight:700;color:#0F2C59;'>{sc_v:.1f}%</td>"
                        f"<td style='padding:10px 8px;text-align:right;font-weight:600;color:{'#0D9488' if diff_v >= 0 else '#C8102E'};'>{diff_v:+.1f} pp</td>"
                        f"<td style='padding:10px 10px;text-align:center;'>{p_badge}</td>"
                        f"</tr>"
                    )

                if len(fac_pss) == 1:
                    pss_note_txt = (
                        f"<b>M&E Huddle Note:</b> <b>{selected_fac}</b> recorded <b>{ov_fac:.1f}%</b> net patient satisfaction in "
                        f"<b>{latest_row['Month_Label']}</b> (<b>{diff_vs_net:+.1f} pp</b> vs. the {net_mean_360:.1f}% network mean). "
                        f"Schedule a follow-up exit-interview round next quarter to track longitudinal trajectory."
                    )
                else:
                    net_chg = float(
                        fac_pss["Net_Satisfaction_Score"].iloc[-1] - fac_pss["Net_Satisfaction_Score"].iloc[0]
                    )
                    direction = "improved" if net_chg >= 2 else ("declined" if net_chg <= -2 else "remained stable")
                    pss_note_txt = (
                        f"<b>M&E Huddle Note:</b> <b>{selected_fac}</b> averages <b>{ov_fac:.1f}%</b> "
                        f"(<b>{diff_vs_net:+.1f} pp</b> vs. the {net_mean_360:.1f}% network mean) and has {direction} "
                        f"by <b>{net_chg:+.1f} pp</b> across {len(fac_pss)} completed 12M rounds."
                    )

                pss_right_html = f"""
                <div style="
                    height:{pss_chart_h}px;
                    display:flex;
                    flex-direction:column;
                    justify-content:space-between;
                    box-sizing:border-box;
                ">
                    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(15,23,42,0.04);">
                        <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;font-size:0.82rem;">
                            <thead>
                                <tr style="background:#0F2C59;color:#FFFFFF;text-transform:uppercase;font-size:0.71rem;letter-spacing:0.04em;">
                                    <th style="padding:11px 10px;text-align:left;">Period</th>
                                    <th style="padding:11px 8px;text-align:right;">Score</th>
                                    <th style="padding:11px 8px;text-align:right;">Vs Net</th>
                                    <th style="padding:11px 10px;text-align:center;">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(pss_rows_html)}
                            </tbody>
                        </table>
                    </div>
                    <div style="
                        background:#F8FAFC;
                        border:1px solid #E2E8F0;
                        border-left:4px solid #0F2C59;
                        border-radius:8px;
                        padding:11px 14px;
                        color:#1E293B;
                        font-size:0.84rem;
                        line-height:1.45;
                    ">
                        {pss_note_txt}
                    </div>
                </div>
                """
                st.markdown(pss_right_html, unsafe_allow_html=True)
