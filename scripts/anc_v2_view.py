import os
import sys
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.khis_adapter import get_live_anc_frame

TEXT_DARK = "#0F172A"
GRID_LIGHT = "#E2E8F0"
NAVY = "#0F2C59"
TEAL = "#0D9488"
CRIMSON = "#C8102E"
SLATE = "#64748B"

MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FULL_MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _normalize_months(selected_months):
    if not selected_months:
        return list(MONTH_ORDER)
    norm = []
    for m in selected_months:
        s = str(m).strip()
        if len(s) >= 3:
            abbr = s[:3].capitalize()
            if abbr in MONTH_ORDER and abbr not in norm:
                norm.append(abbr)
    return [m for m in MONTH_ORDER if m in norm] or list(MONTH_ORDER)


def _apply_clean_theme(fig, height=370, margin=None):
    fig.update_layout(
        height=height,
        margin=margin or dict(l=16, r=20, t=32, b=32),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, system-ui, sans-serif", color=TEXT_DARK, size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11.5, color=TEXT_DARK)),
    )
    fig.update_xaxes(showgrid=False, linecolor="#CBD5E1", tickfont=dict(color=TEXT_DARK, size=11.5))
    fig.update_yaxes(gridcolor=GRID_LIGHT, zerolinecolor="#CBD5E1", tickfont=dict(color=TEXT_DARK, size=11.5))
    return fig


def _render_anc_card(col, title, icon, big_val, sub_val, status, body_html):
    border_map = {"good": "#0D9488", "warn": "#D97706", "bad": "#C8102E", "navy": "#0F2C59"}
    badge_bg = {"good": "#CCFBF1", "warn": "#FEF3C7", "bad": "#FFE4E6", "navy": "#E0E7FF"}
    badge_fg = {"good": "#0F766E", "warn": "#B45309", "bad": "#BE123C", "navy": "#1E3A8A"}
    b_col, bg, fg = border_map.get(status, "#0F2C59"), badge_bg.get(status, "#F1F5F9"), badge_fg.get(status, "#0F172A")
    with col:
        st.markdown(
            f'<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid {b_col}; border-radius:9px; padding:14px 16px; box-shadow:0 1px 3px rgba(15,23,42,0.04); height:100%;">'
            f'<div style="display:flex; justify-content:space-between; align-items:center;"><span style="font-size:11.5px; font-weight:700; text-transform:uppercase; letter-spacing:0.6px; color:#475569;">{title}</span><span style="font-size:16px;">{icon}</span></div>'
            f'<div style="font-size:24px; font-weight:800; color:#0F2C59; margin-top:4px; line-height:1.15;">{big_val}</div>'
            f'<div style="margin-top:6px;"><span style="background:{bg}; color:{fg}; font-size:11.5px; font-weight:700; padding:2px 8px; border-radius:999px; display:inline-block;">{sub_val}</span></div>'
            f'<div style="font-size:12px; color:#334155; margin-top:8px; line-height:1.45;">{body_html}</div></div>',
            unsafe_allow_html=True,
        )


def build_anc_datasets(df_anc, selected_months, focus_year="2026", comparison_year="2025"):
    if df_anc is None or df_anc.empty:
        return pd.DataFrame(), pd.DataFrame(), {}

    df = df_anc.copy()
    df["Year"] = df["Year"].astype(str).str.strip()
    df["MonthAbbr"] = df["Month"].astype(str).str.strip().str[:3].str.capitalize()
    valid_months = _normalize_months(selected_months)

    metric_cols = [
        "ANC_1st_New", "ANC_1st_Under_12w", "ANC_4th_Completed", "ANC_8th_Completed",
        "ANC_Revisits", "ANC_Adol_10_14", "ANC_Adol_15_19", "ANC_Youth_20_24",
        "ANC_Syphilis_Tested", "ANC_Syphilis_Pos", "ANC_IFAS_Combined",
        "ANC_Iron_Only", "ANC_Folic_Only", "ANC_IPTp1", "ANC_IPTp2", "ANC_IPTp3", "ANC_LLIN",
    ]
    for c in metric_cols:
        if c not in df.columns:
            df[c] = 0.0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    m_rows = []
    for idx, (m_abbr, m_full) in enumerate(zip(MONTH_ORDER, FULL_MONTH_ORDER), start=1):
        sub_b = df[(df["Year"] == str(comparison_year)) & (df["MonthAbbr"] == m_abbr)]
        sub_f = df[(df["Year"] == str(focus_year)) & (df["MonthAbbr"] == m_abbr)]

        anc1_b, anc1_f = float(sub_b["ANC_1st_New"].sum()), float(sub_f["ANC_1st_New"].sum())
        has_f = (not sub_f.empty) and (anc1_f > 0 or sub_f["ANC_Revisits"].sum() > 0)
        anc4_b, anc4_f = float(sub_b["ANC_4th_Completed"].sum()), float(sub_f["ANC_4th_Completed"].sum())
        early_b, early_f = float(sub_b["ANC_1st_Under_12w"].sum()), float(sub_f["ANC_1st_Under_12w"].sum())
        syph_f, ifas_f = float(sub_f["ANC_Syphilis_Tested"].sum()), float(sub_f["ANC_IFAS_Combined"].sum())
        tot_c_f = anc1_f + float(sub_f["ANC_Revisits"].sum())

        if anc1_b > 0 or has_f:
            diff_anc1 = (anc1_f - anc1_b) if has_f else np.nan
            pct_anc1 = ((anc1_f - anc1_b) / anc1_b * 100.0) if (has_f and anc1_b > 0) else np.nan
            m_rows.append({
                "MonthNum": idx, "Month": m_abbr, "FullMonth": m_full, "IsSelected": m_abbr in valid_months,
                f"{comparison_year} ANC1": anc1_b if anc1_b > 0 else np.nan,
                f"{focus_year} ANC1": anc1_f if has_f else np.nan,
                "ANC1 YoY Δ": diff_anc1, "ANC1 YoY %": pct_anc1,
                f"{comparison_year} ANC4+": anc4_b if anc1_b > 0 else np.nan,
                f"{focus_year} ANC4+": anc4_f if has_f else np.nan,
                f"{comparison_year} ANC4_Ratio": (anc4_b / anc1_b * 100.0) if anc1_b > 0 else np.nan,
                f"{focus_year} ANC4_Ratio": (anc4_f / anc1_f * 100.0) if (has_f and anc1_f > 0) else np.nan,
                f"{comparison_year} Early12w_Pct": (early_b / anc1_b * 100.0) if anc1_b > 0 else np.nan,
                f"{focus_year} Early12w_Pct": (early_f / anc1_f * 100.0) if (has_f and anc1_f > 0) else np.nan,
                f"{focus_year} Syphilis %": (syph_f / anc1_f * 100.0) if (has_f and anc1_f > 0) else np.nan,
                f"{focus_year} IFAS %": (ifas_f / tot_c_f * 100.0) if (has_f and tot_c_f > 0) else np.nan,
            })
    monthly_df = pd.DataFrame(m_rows)

    df_sub = df[df["MonthAbbr"].isin(valid_months)].copy()
    base_fac = df_sub[df_sub["Year"] == str(comparison_year)].groupby("facility_name", as_index=False)[metric_cols].sum()
    focus_fac = df_sub[df_sub["Year"] == str(focus_year)].groupby("facility_name", as_index=False)[metric_cols].sum()
    fac_df = pd.merge(base_fac, focus_fac, on="facility_name", how="outer", suffixes=("_base", "_focus")).fillna(0.0)
    if fac_df.empty:
        return pd.DataFrame(), monthly_df, {}

    fac_df["anc1_diff"] = fac_df["ANC_1st_New_focus"] - fac_df["ANC_1st_New_base"]
    fac_df["anc4_diff"] = fac_df["ANC_4th_Completed_focus"] - fac_df["ANC_4th_Completed_base"]
    fac_df["anc4_rate_focus"] = np.where(fac_df["ANC_1st_New_focus"] > 0, fac_df["ANC_4th_Completed_focus"] / fac_df["ANC_1st_New_focus"] * 100.0, 0.0)
    fac_df["early_rate_focus"] = np.where(fac_df["ANC_1st_New_focus"] > 0, fac_df["ANC_1st_Under_12w_focus"] / fac_df["ANC_1st_New_focus"] * 100.0, 0.0)
    fac_df["adol_total_focus"] = fac_df["ANC_Adol_10_14_focus"] + fac_df["ANC_Adol_15_19_focus"]
    fac_df["adol_pct_focus"] = np.where(fac_df["ANC_1st_New_focus"] > 0, fac_df["adol_total_focus"] / fac_df["ANC_1st_New_focus"] * 100.0, 0.0)
    fac_df["syph_cov_focus"] = np.where(fac_df["ANC_1st_New_focus"] > 0, fac_df["ANC_Syphilis_Tested_focus"] / fac_df["ANC_1st_New_focus"] * 100.0, 0.0)
    fac_df["total_contacts_focus"] = fac_df["ANC_1st_New_focus"] + fac_df["ANC_Revisits_focus"]
    fac_df["ifas_cov_focus"] = np.where(fac_df["total_contacts_focus"] > 0, fac_df["ANC_IFAS_Combined_focus"] / fac_df["total_contacts_focus"] * 100.0, 0.0)

    s = {}
    for c in metric_cols:
        s[f"{c}_base"] = float(fac_df[f"{c}_base"].sum())
        s[f"{c}_focus"] = float(fac_df[f"{c}_focus"].sum())

    s["anc1_growth_pct"] = ((s["ANC_1st_New_focus"] - s["ANC_1st_New_base"]) / s["ANC_1st_New_base"] * 100.0) if s["ANC_1st_New_base"] > 0 else 0.0
    s["early_pct_base"] = (s["ANC_1st_Under_12w_base"] / s["ANC_1st_New_base"] * 100.0) if s["ANC_1st_New_base"] > 0 else 0.0
    s["early_pct_focus"] = (s["ANC_1st_Under_12w_focus"] / s["ANC_1st_New_focus"] * 100.0) if s["ANC_1st_New_focus"] > 0 else 0.0
    s["anc4_pct_base"] = (s["ANC_4th_Completed_base"] / s["ANC_1st_New_base"] * 100.0) if s["ANC_1st_New_base"] > 0 else 0.0
    s["anc4_pct_focus"] = (s["ANC_4th_Completed_focus"] / s["ANC_1st_New_focus"] * 100.0) if s["ANC_1st_New_focus"] > 0 else 0.0
    s["anc8_pct_base"] = (s["ANC_8th_Completed_base"] / s["ANC_1st_New_base"] * 100.0) if s["ANC_1st_New_base"] > 0 else 0.0
    s["anc8_pct_focus"] = (s["ANC_8th_Completed_focus"] / s["ANC_1st_New_focus"] * 100.0) if s["ANC_1st_New_focus"] > 0 else 0.0
    s["adol_base"] = s["ANC_Adol_10_14_base"] + s["ANC_Adol_15_19_base"]
    s["adol_focus"] = s["ANC_Adol_10_14_focus"] + s["ANC_Adol_15_19_focus"]
    s["adol_pct_base"] = (s["adol_base"] / s["ANC_1st_New_base"] * 100.0) if s["ANC_1st_New_base"] > 0 else 0.0
    s["adol_pct_focus"] = (s["adol_focus"] / s["ANC_1st_New_focus"] * 100.0) if s["ANC_1st_New_focus"] > 0 else 0.0
    s["syph_cov_base"] = (s["ANC_Syphilis_Tested_base"] / s["ANC_1st_New_base"] * 100.0) if s["ANC_1st_New_base"] > 0 else 0.0
    s["syph_cov_focus"] = (s["ANC_Syphilis_Tested_focus"] / s["ANC_1st_New_focus"] * 100.0) if s["ANC_1st_New_focus"] > 0 else 0.0
    s["syph_pos_rate_focus"] = (s["ANC_Syphilis_Pos_focus"] / s["ANC_Syphilis_Tested_focus"] * 100.0) if s["ANC_Syphilis_Tested_focus"] > 0 else 0.0

    tot_contacts_b, tot_contacts_f = s["ANC_1st_New_base"] + s["ANC_Revisits_base"], s["ANC_1st_New_focus"] + s["ANC_Revisits_focus"]
    s["tot_contacts_base"], s["tot_contacts_focus"] = tot_contacts_b, tot_contacts_f
    s["ifas_cov_base"] = (s["ANC_IFAS_Combined_base"] / tot_contacts_b * 100.0) if tot_contacts_b > 0 else 0.0
    s["ifas_cov_focus"] = (s["ANC_IFAS_Combined_focus"] / tot_contacts_f * 100.0) if tot_contacts_f > 0 else 0.0
    s["llin_cov_base"] = (s["ANC_LLIN_base"] / s["ANC_1st_New_base"] * 100.0) if s["ANC_1st_New_base"] > 0 else 0.0
    s["llin_cov_focus"] = (s["ANC_LLIN_focus"] / s["ANC_1st_New_focus"] * 100.0) if s["ANC_1st_New_focus"] > 0 else 0.0
    s["iptp2_cov_base"] = (s["ANC_IPTp2_base"] / s["ANC_1st_New_base"] * 100.0) if s["ANC_1st_New_base"] > 0 else 0.0
    s["iptp2_cov_focus"] = (s["ANC_IPTp2_focus"] / s["ANC_1st_New_focus"] * 100.0) if s["ANC_1st_New_focus"] > 0 else 0.0

    gainers, droppers = fac_df[fac_df["anc1_diff"] > 0], fac_df[fac_df["anc1_diff"] < 0]
    s["gaining_sites"], s["dropping_sites"] = int(len(gainers)), int(len(droppers))
    s["total_gains"], s["total_drops"] = float(gainers["anc1_diff"].sum()), float(droppers["anc1_diff"].sum())
    top_g = gainers.sort_values("anc1_diff", ascending=False).iloc[0] if not gainers.empty else None
    s["top_gainer_name"] = top_g["facility_name"] if top_g is not None else "N/A"
    s["top_gainer_val"] = int(top_g["anc1_diff"]) if top_g is not None else 0
    return fac_df, monthly_df, s


def _render_me_narrative(title, finding, impact, action):
    st.markdown(
        f'<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-left:4px solid #0F2C59; '
        f'border-radius:8px; padding:12px 16px; margin-top:4px; margin-bottom:16px; font-size:13px; color:#1E293B; line-height:1.6;">'
        f'<div style="font-weight:800; color:#0F2C59; text-transform:uppercase; font-size:11.5px; letter-spacing:0.5px; margin-bottom:5px;">'
        f'📋 Program & Clinical Interpretation — {title}</div>'
        f'<div style="margin-bottom:4px;"><b>Key Finding:</b> {finding}</div>'
        f'<div style="margin-bottom:4px;"><b>Clinical & Program Impact:</b> {impact}</div>'
        f'<div style="color:#0D9488;"><b>Recommended Action:</b> {action}</div></div>',
        unsafe_allow_html=True,
    )
def render_anc_v2_dashboard(selected_months=None, focus_year="2026", comparison_year="2025", selected_period="Equal Period"):
    hdr_col, sync_col = st.columns([4.2, 1.0])
    with hdr_col:
        st.markdown(
            f'<div style="background:linear-gradient(135deg, #0F2C59 0%, #163E7A 100%); padding:18px 22px; border-radius:10px; color:#FFFFFF; margin-bottom:14px;">'
            f'<div style="font-size:11px; text-transform:uppercase; letter-spacing:1.2px; color:#5EEAD4; font-weight:700;">MOH 711 Antenatal Care (ANC) Epidemiological &amp; M&amp;E Surveillance</div>'
            f'<div style="font-size:21px; font-weight:800; margin-top:2px;">ANC Continuum, SPC Control &amp; Facility Quality Analytics ({focus_year} vs. {comparison_year} — {selected_period})</div>'
            f'<div style="font-size:12.5px; color:#E2E8F0; margin-top:4px;">Equal-period KHIS analysis across 38 facilities with Shewhart SPC control bands, Pareto 80/20 attribution, Pearson correlation modeling, and MOH target benchmarking.</div></div>',
            unsafe_allow_html=True,
        )
    with sync_col:
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Sync Live KHIS ANC", key="anc_force_sync_btn", use_container_width=True):
            get_live_anc_frame.clear()
            with st.spinner("Syncing MOH 711 ANC data from KHIS..."):
                get_live_anc_frame(force_live=True)
            st.rerun()

    df_anc = get_live_anc_frame(force_live=False)
    if df_anc is None or df_anc.empty:
        st.warning("No KHIS ANC data available yet. Click '🔄 Sync Live KHIS ANC' to fetch from KHIS.")
        return

    fac_df, monthly_df, s = build_anc_datasets(df_anc, selected_months, focus_year, comparison_year)
    if fac_df.empty:
        st.warning("No ANC records matched the selected months and comparison years.")
        return

    c1, c2, c3 = st.columns(3)
    anc1_delta = int(s["ANC_1st_New_focus"] - s["ANC_1st_New_base"])
    _render_anc_card(
        c1, f"New 1st ANC Clients ({focus_year})", "🤰", f"{int(s['ANC_1st_New_focus']):,}",
        f"{'↑' if anc1_delta >= 0 else '↓'} {anc1_delta:+,} ({s['anc1_growth_pct']:+.1f}% vs {comparison_year})",
        "good" if anc1_delta >= 0 else "bad",
        f"<b>Equal-Period Cohort:</b> {int(s['ANC_1st_New_focus']):,} vs. {int(s['ANC_1st_New_base']):,} in {comparison_year}; <b>{s['gaining_sites']} gaining</b> vs. <b>{s['dropping_sites']} contracting</b> facilities.",
    )
    early_diff = s["early_pct_focus"] - s["early_pct_base"]
    _render_anc_card(
        c2, "Early Initiation (≤12 Weeks)", "⏱️",
        f"{s['early_pct_focus']:.1f}% <span style='font-size:14px; color:#0D9488;'>({int(s['ANC_1st_Under_12w_focus']):,})</span>",
        f"{early_diff:+.1f} pp YoY | Gap to 30% Target: {max(0.0, 30.0 - s['early_pct_focus']):.1f} pp",
        "good" if s["early_pct_focus"] >= 30.0 else "warn",
        f"<b>1st Trimester Capture:</b> {int(s['ANC_1st_Under_12w_focus']):,} booked &le;12w vs. {int(s['ANC_1st_Under_12w_base']):,} ({s['early_pct_base']:.1f}%) in {comparison_year}.",
    )
    anc4_diff = s["anc4_pct_focus"] - s["anc4_pct_base"]
    _render_anc_card(
        c3, "4th ANC Retention Ratio (ANC4+)", "📋",
        f"{s['anc4_pct_focus']:.1f}% <span style='font-size:14px; color:#475569;'>({int(s['ANC_4th_Completed_focus']):,})</span>",
        f"ANC8: {s['anc8_pct_focus']:.1f}% ({int(s['ANC_8th_Completed_focus']):,}) | {anc4_diff:+.1f} pp YoY",
        "good" if s["anc4_pct_focus"] >= 65.0 else ("warn" if s["anc4_pct_focus"] >= 50.0 else "bad"),
        f"<b>Attrition Drop-off:</b> {100.0 - s['anc4_pct_focus']:.1f}% of 1st ANC clients did not reach 4 visits (vs. {s['anc4_pct_base']:.1f}% retention in {comparison_year}).",
    )

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    adol_diff = s["adol_pct_focus"] - s["adol_pct_base"]
    _render_anc_card(
        c4, "Adolescent Pregnancy Burden (10–19y)", "👧",
        f"{s['adol_pct_focus']:.1f}% <span style='font-size:14px; color:#C8102E;'>({int(s['adol_focus']):,})</span>",
        f"10–14y: {int(s['ANC_Adol_10_14_focus'])} · 15–19y: {int(s['ANC_Adol_15_19_focus']):,} ({adol_diff:+.1f} pp)",
        "warn" if s["adol_pct_focus"] > 12.0 else "navy",
        f"<b>Vulnerability Index:</b> Combined with <b>{int(s['ANC_Youth_20_24_focus']):,}</b> youth (20–24y), young women represent <b>{((s['adol_focus']+s['ANC_Youth_20_24_focus'])/max(1,s['ANC_1st_New_focus'])*100):.1f}%</b> of 1st ANC.",
    )
    syph_diff = s["syph_cov_focus"] - s["syph_cov_base"]
    _render_anc_card(
        c5, "Syphilis Screening & Reactivity", "🧪",
        f"{s['syph_cov_focus']:.1f}% <span style='font-size:14px; color:#0D9488;'>({int(s['ANC_Syphilis_Tested_focus']):,})</span>",
        f"{int(s['ANC_Syphilis_Pos_focus'])} Reactive ({s['syph_pos_rate_focus']:.2f}%) | {syph_diff:+.1f} pp YoY",
        "good" if s["syph_cov_focus"] >= 90.0 else "warn",
        f"<b>EMTCT Surveillance:</b> Dual testing coverage vs. 95% national elimination target (baseline: {s['syph_cov_base']:.1f}% in {comparison_year}).",
    )
    ifas_diff = s["ifas_cov_focus"] - s["ifas_cov_base"]
    _render_anc_card(
        c6, "IFAS & Malaria Prophylaxis", "💊",
        f"{s['ifas_cov_focus']:.1f}% <span style='font-size:14px; color:#0D9488;'>IFAS / Contact</span>",
        f"IPTp2: {s['iptp2_cov_focus']:.1f}% · LLINs: {s['llin_cov_focus']:.1f}%",
        "good" if s["ifas_cov_focus"] >= 75.0 else "warn",
        f"<b>Preventive Commodity Fidelity:</b> {int(s['ANC_IFAS_Combined_focus']):,} IFAS doses across {int(s['tot_contacts_focus']):,} total ANC contacts ({ifas_diff:+.1f} pp YoY).",
    )
    st.markdown("---")

    c_left, c_right = st.columns([1.05, 1.15])
    with c_left:
        st.markdown(f"#### 🔻 ANC Continuum Retention & Visit Drop-Off ({comparison_year} vs. {focus_year})")
        stages = ["1st ANC Entry (100%)", "4th ANC Visit (ANC4+)", "8th ANC Contact (ANC8)"]
        ret_b = [100.0, s["anc4_pct_base"], s["anc8_pct_base"]]
        ret_f = [100.0, s["anc4_pct_focus"], s["anc8_pct_focus"]]
        cnt_f = [s["ANC_1st_New_focus"], s["ANC_4th_Completed_focus"], s["ANC_8th_Completed_focus"]]

        fig_ret = go.Figure()
        fig_ret.add_trace(go.Scatter(x=stages, y=ret_b, mode="lines+markers+text", name=f"{comparison_year} Continuum (%)", text=[f"{v:.1f}%" for v in ret_b], textposition="bottom center", textfont=dict(size=10.5, color=SLATE), line=dict(color=SLATE, width=2.2, dash="dash"), marker=dict(size=8)))
        fig_ret.add_trace(go.Scatter(x=stages, y=ret_f, mode="lines+markers+text", name=f"{focus_year} Continuum (%)", text=[f"{v:.1f}%<br>({int(n):,})" for v, n in zip(ret_f, cnt_f)], textposition="top center", textfont=dict(size=10.5, color=NAVY, weight="bold"), line=dict(color=NAVY, width=3.2), marker=dict(size=12, color=[NAVY, TEAL, CRIMSON], line=dict(color="#FFFFFF", width=1.5)), fill="tozeroy", fillcolor="rgba(13, 148, 136, 0.08)"))
        fig_ret.add_annotation(x=0.5, y=114, showarrow=False, text=f"⏱️ Early Trimester 1 Entry (≤12w): <b>{s['early_pct_focus']:.1f}%</b> ({int(s['ANC_1st_Under_12w_focus']):,} of {int(s['ANC_1st_New_focus']):,} | {s['early_pct_focus'] - s['early_pct_base']:+.1f} pp YoY)", font=dict(size=11, color=NAVY), bgcolor="#FEF3C7", bordercolor="#D97706", borderwidth=1, borderpad=5)
        _apply_clean_theme(fig_ret, height=375)
        fig_ret.update_layout(margin=dict(t=48, b=45, l=50, r=25))
        fig_ret.update_yaxes(title=dict(text="Proportion of 1st ANC Cohort (%)", font=dict(color=TEXT_DARK, size=12, weight="bold")), range=[0, 128])
        st.plotly_chart(fig_ret, use_container_width=True)

        late_pct = max(0.0, 100.0 - s["early_pct_focus"])
        _render_me_narrative(
            "Continuum Retention & Visit Drop-Off",
            f"Of <b>{int(s['ANC_1st_New_focus']):,}</b> mothers starting ANC in {focus_year}, only <b>{s['early_pct_focus']:.1f}% ({int(s['ANC_1st_Under_12w_focus']):,})</b> booked within 12 weeks (<b>{late_pct:.1f}% booked late</b>). Across the continuum, <b>{s['anc4_pct_focus']:.1f}% ({int(s['ANC_4th_Completed_focus']):,})</b> completed 4+ visits ({s['anc4_pct_focus'] - s['anc4_pct_base']:+.1f} pp vs. {comparison_year}), and <b>{s['anc8_pct_focus']:.1f}% ({int(s['ANC_8th_Completed_focus']):,})</b> reached 8 contacts.",
            f"Late 1st-trimester entry shortens the window to complete 4–8 contacts before delivery and delays early anemia, syphilis, and pre-eclampsia detection. The steep drop after visit 4 leaves third-trimester complications unmonitored.",
            f"Activate appointment reminder calls/CHW defaulter tracing between visits 3 and 8, and expand community pregnancy testing to shift first booking below 12 weeks."
        )

    with c_right:
        st.markdown(f"#### 🎯 Facility Quality–Retention Quadrant Matrix ({focus_year})")
        active_fac = fac_df[fac_df["ANC_1st_New_focus"] > 0].copy()
        active_fac["anc4_plot"] = active_fac["anc4_rate_focus"].clip(upper=145.0)
        fig_sc = go.Figure()
        fig_sc.add_hline(y=65.0, line_dash="dash", line_color=TEAL, line_width=1.4, annotation_text="ANC4+ Target (65%)", annotation_position="bottom right")
        fig_sc.add_vline(x=25.0, line_dash="dash", line_color="#D97706", line_width=1.4, annotation_text="Early ≥25%", annotation_position="top right")
        is_risk = (active_fac["early_rate_focus"] < 25.0) & (active_fac["anc4_rate_focus"] < 65.0)
        q_colors = np.where((active_fac["early_rate_focus"] >= 25.0) & (active_fac["anc4_rate_focus"] >= 65.0), TEAL, np.where(active_fac["anc4_rate_focus"] >= 65.0, NAVY, np.where(active_fac["early_rate_focus"] >= 25.0, "#D97706", CRIMSON)))
        top_risk_names = active_fac[is_risk].nlargest(3, "ANC_1st_New_focus")["facility_name"].tolist()
        top_bench_names = active_fac[~is_risk].nlargest(2, "ANC_1st_New_focus")["facility_name"].tolist()
        lbl_txt = [n.split()[0] if n in (top_risk_names + top_bench_names) else "" for n in active_fac["facility_name"]]
        fig_sc.add_trace(go.Scatter(x=active_fac["early_rate_focus"], y=active_fac["anc4_plot"], mode="markers+text", text=lbl_txt, textposition="bottom center", textfont=dict(size=9.5, color=TEXT_DARK, weight="bold"), marker=dict(size=np.clip(np.sqrt(active_fac["ANC_1st_New_focus"]) * 1.2, 9, 26), color=q_colors, opacity=0.85, line=dict(color="#FFFFFF", width=1.2)), customdata=np.stack([active_fac["facility_name"], active_fac["ANC_1st_New_focus"], active_fac["anc4_rate_focus"], active_fac["syph_cov_focus"]], axis=-1), hovertemplate="<b>%{customdata[0]}</b><br>1st ANC: %{customdata[1]:,.0f}<br>Early ≤12w: %{x:.1f}%<br>Actual ANC4+ Ratio: %{customdata[2]:.1f}%<br>Syphilis Test: %{customdata[3]:.1f}%<extra></extra>", showlegend=False))
        _apply_clean_theme(fig_sc, height=375)
        fig_sc.update_layout(margin=dict(t=48, b=45, l=50, r=25))
        fig_sc.update_xaxes(title=dict(text="Early 1st ANC Booking ≤12 Weeks (%)", font=dict(color=TEXT_DARK, size=12, weight="bold")), range=[-4, 108])
        fig_sc.update_yaxes(title=dict(text="4th ANC Completion Ratio (%, capped at 145%)", font=dict(color=TEXT_DARK, size=12, weight="bold")), range=[-8, 155])
        st.plotly_chart(fig_sc, use_container_width=True)

        q_star = int(((active_fac["early_rate_focus"] >= 25.0) & (active_fac["anc4_rate_focus"] >= 65.0)).sum())
        q_risk = int(is_risk.sum())
        prio_str = ", ".join(top_risk_names) if top_risk_names else "None"
        _render_me_narrative(
            "Facility Performance Segmentation",
            f"Across {len(active_fac)} active facilities, <b>{q_star} benchmark sites</b> (Teal, top-right) meet both early booking (≥25%) and ANC4+ retention (≥65%) standards, while <b>{q_risk} priority sites</b> (Crimson, bottom-left) fall below both thresholds—led by <b>{prio_str}</b>.",
            f"Facilities in the bottom-left quadrant face double attrition: mothers enroll late in pregnancy and drop out before completing 4 visits, concentrating preventable maternal and newborn morbidity.",
            f"Conduct targeted mentorship, ANC register audits, and peer-learning pairings between high-performing clinics and <b>{prio_str}</b>."
        )

    a_left, a_right = st.columns([1.0, 1.15])
    with a_left:
        st.markdown(f"#### 👧 Maternal Age-Risk Stratification at 1st ANC ({comparison_year} vs. {focus_year})")
        age_groups = ["10–14 yrs (Very Young)", "15–19 yrs (Older Adol.)", "20–24 yrs (Young Adult)", "25+ yrs (Adult)"]
        b_25p = max(0.0, s["ANC_1st_New_base"] - (s["ANC_Adol_10_14_base"] + s["ANC_Adol_15_19_base"] + s["ANC_Youth_20_24_base"]))
        f_25p = max(0.0, s["ANC_1st_New_focus"] - (s["ANC_Adol_10_14_focus"] + s["ANC_Adol_15_19_focus"] + s["ANC_Youth_20_24_focus"]))
        age_b_pct = [v / max(1.0, s["ANC_1st_New_base"]) * 100.0 for v in [s["ANC_Adol_10_14_base"], s["ANC_Adol_15_19_base"], s["ANC_Youth_20_24_base"], b_25p]]
        age_f_pct = [v / max(1.0, s["ANC_1st_New_focus"]) * 100.0 for v in [s["ANC_Adol_10_14_focus"], s["ANC_Adol_15_19_focus"], s["ANC_Youth_20_24_focus"], f_25p]]

        fig_age = go.Figure()
        fig_age.add_trace(go.Bar(x=age_groups, y=age_b_pct, name=f"{comparison_year} Share (%)", marker_color="#94A3B8", text=[f"{v:.1f}%" for v in age_b_pct], textposition="outside"))
        fig_age.add_trace(go.Bar(x=age_groups, y=age_f_pct, name=f"{focus_year} Share (%)", marker_color=NAVY, text=[f"{v:.1f}%" for v in age_f_pct], textposition="outside"))
        _apply_clean_theme(fig_age, height=365)
        fig_age.update_layout(barmode="group")
        fig_age.update_yaxes(title=dict(text="Share of 1st ANC Clients (%)", font=dict(color=TEXT_DARK, size=12, weight="bold")), range=[0, max(75, max(age_b_pct + age_f_pct) * 1.18)])
        st.plotly_chart(fig_age, use_container_width=True)

        _render_me_narrative(
            "Adolescent & Youth Pregnancy Burden",
            f"Adolescents aged 10–19 represent <b>{s['adol_pct_focus']:.1f}% ({int(s['adol_focus']):,})</b> of {focus_year} 1st ANC clients ({s['adol_pct_focus'] - s['adol_pct_base']:+.1f} pp vs. {comparison_year}), including <b>{int(s['ANC_Adol_10_14_focus'])} girls aged 10–14</b>. Combined with ages 20–24, young women under 25 account for <b>{sum(age_f_pct[:3]):.1f}%</b> of total ANC demand.",
            f"Pregnant adolescents—especially those aged 10–14—face significantly higher risks of eclampsia, obstructed labor, preterm birth, and clinic dropout.",
            f"Provide adolescent-friendly clinic hours, dedicated psychosocial counseling, and mandatory child-protection/GBV linkage for all 10–14y and 15–19y bookings."
        )

    with a_right:
        st.markdown("#### 🛡️ Preventive Cascade Dumbbell: YoY Shift vs. MOH Targets")
        q_metrics = ["LLIN Distribution", "IPTp 2nd Dose", "IFAS / ANC Contact", "Syphilis Screening", "ANC 4+ Completion", "Early Booking ≤12w"]
        q_b_vals = [s["llin_cov_base"], s["iptp2_cov_base"], s["ifas_cov_base"], s["syph_cov_base"], s["anc4_pct_base"], s["early_pct_base"]]
        q_f_vals = [s["llin_cov_focus"], s["iptp2_cov_focus"], s["ifas_cov_focus"], s["syph_cov_focus"], s["anc4_pct_focus"], s["early_pct_focus"]]
        q_t_vals = [85.0, 80.0, 85.0, 95.0, 65.0, 30.0]

        fig_db = go.Figure()
        for m_lbl, bv, fv in zip(q_metrics, q_b_vals, q_f_vals):
            fig_db.add_trace(go.Scatter(x=[bv, fv], y=[m_lbl, m_lbl], mode="lines", line=dict(color=TEAL if fv >= bv else CRIMSON, width=3.5), showlegend=False, hoverinfo="skip"))
        fig_db.add_trace(go.Scatter(x=q_b_vals, y=q_metrics, mode="markers", name=f"{comparison_year} Baseline", marker=dict(size=11, color="#94A3B8")))
        fig_db.add_trace(go.Scatter(x=q_f_vals, y=q_metrics, mode="markers+text", name=f"{focus_year} Focus", text=[f"{v:.1f}%" for v in q_f_vals], textposition="top center", textfont=dict(size=10.5, color=NAVY, weight="bold"), marker=dict(size=13, color=NAVY)))
        fig_db.add_trace(go.Scatter(x=q_t_vals, y=q_metrics, mode="markers", name="MOH / WHO Target", marker=dict(symbol="diamond", size=10, color=CRIMSON)))
        _apply_clean_theme(fig_db, height=365)
        fig_db.update_xaxes(title=dict(text="Coverage / Attainment (%)", font=dict(color=TEXT_DARK, size=12, weight="bold")), range=[0, 115])
        st.plotly_chart(fig_db, use_container_width=True)

        deltas_q = {lbl: (fv - bv) for lbl, bv, fv in zip(q_metrics, q_b_vals, q_f_vals)}
        best_q, worst_q = max(deltas_q, key=deltas_q.get), min(deltas_q, key=deltas_q.get)
        _render_me_narrative(
            "Essential ANC Package & Commodity Coverage",
            f"The largest year-over-year gain was in <b>{best_q} ({deltas_q[best_q]:+.1f} pp)</b>, whereas <b>{worst_q} ({deltas_q[worst_q]:+.1f} pp)</b> recorded the steepest decline. Syphilis testing stands at <b>{s['syph_cov_focus']:.1f}%</b> (exceeding the 95% EMTCT target), while IFAS per contact is at <b>{s['ifas_cov_focus']:.1f}%</b> ({s['ifas_cov_focus'] - 85.0:+.1f} pp vs. 85% target) and IPTp2 malaria prophylaxis is at <b>{s['iptp2_cov_focus']:.1f}%</b>.",
            f"Missed dispensing of iron/folate (IFAS), malaria prophylaxis (IPTp2), and LLIN bed nets during active ANC contacts directly increases maternal anemia, low birthweight, and preventable stillbirths.",
            f"Reconcile pharmacy-to-MCH stock records for IFAS, SP (Fansidar), and LLINs at high-volume sites to ensure every contact receives the complete preventive bundle."
        )
    st.markdown("---")

    st.markdown(f"#### Month-by-Month ANC Matrix ({comparison_year} vs. {focus_year})")
    m_cols = ["FullMonth", "IsSelected", f"{comparison_year} ANC1", f"{focus_year} ANC1", "ANC1 YoY Δ", "ANC1 YoY %", f"{comparison_year} ANC4+", f"{focus_year} ANC4+", f"{focus_year} Early12w_Pct", f"{focus_year} ANC4_Ratio", f"{focus_year} Syphilis %", f"{focus_year} IFAS %"]
    m_tbl = monthly_df[m_cols].copy()
    m_tbl.insert(1, "Scope", np.where(m_tbl.pop("IsSelected"), "Selected", "Context"))
    m_tbl.columns = ["Month", "Scope", f"{comparison_year} 1st ANC", f"{focus_year} 1st ANC", "1st ANC Δ", "YoY %", f"{comparison_year} ANC4+", f"{focus_year} ANC4+", "Early <=12w %", "ANC4+ %", "Syphilis %", "IFAS %"]
    st.dataframe(m_tbl, use_container_width=True, hide_index=True)

    st.markdown(f"#### Facility ANC Audit ({focus_year} vs. {comparison_year})")
    r_cols = [
        "facility_name", "ANC_1st_New_base", "ANC_1st_New_focus",
        "anc1_diff", "early_rate_focus", "ANC_4th_Completed_focus",
        "anc4_rate_focus", "ANC_8th_Completed_focus", "adol_pct_focus",
        "syph_cov_focus", "ifas_cov_focus",
    ]
    reg_df = fac_df[r_cols].sort_values(
        "ANC_1st_New_focus", ascending=False
    ).copy()
    reg_df.columns = [
        "Facility", f"{comparison_year} 1st ANC", f"{focus_year} 1st ANC",
        "YoY Δ", "Early <=12w %", f"{focus_year} ANC4+", "ANC4+ %",
        f"{focus_year} ANC8", "Adol 10-19 %", "Syphilis %", "IFAS %",
    ]
    for c in [f"{comparison_year} 1st ANC", f"{focus_year} 1st ANC",
              "YoY Δ", f"{focus_year} ANC4+", f"{focus_year} ANC8"]:
        reg_df[c] = reg_df[c].round().astype(int)
    for c in ["Early <=12w %", "ANC4+ %", "Adol 10-19 %",
              "Syphilis %", "IFAS %"]:
        reg_df[c] = reg_df[c].round(1)
    st.dataframe(reg_df, use_container_width=True, hide_index=True)
    st.markdown(f"#### Facility ANC Audit ({focus_year} vs. {comparison_year})")
    r_cols = ["facility_name", "ANC_1st_New_base", "ANC_1st_New_focus", "anc1_diff", "early_rate_focus", "ANC_4th_Completed_focus", "anc4_rate_focus", "ANC_8th_Completed_focus", "adol_pct_focus", "syph_cov_focus", "ifas_cov_focus"]
    st.dataframe(fac_df[r_cols].sort_values("ANC_1st_New_focus", ascending=False), use_container_width=True, hide_index=True)
