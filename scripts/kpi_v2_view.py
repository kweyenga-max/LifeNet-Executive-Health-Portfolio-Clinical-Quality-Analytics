import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#334155"
GRID_COLOR = "#E2E8F0"


def _apply_clean_theme(fig, height=370, margin=None):
    if margin is None:
        margin = dict(l=20, r=30, t=35, b=25)
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=margin,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        font=dict(family=FONT_FAMILY, color=TEXT_DARK, size=12),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor="#CBD5E1",
            tickfont=dict(color=TEXT_DARK, size=11.5),
            title_font=dict(color=TEXT_DARK, size=12, weight="bold"),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor="#CBD5E1",
            tickfont=dict(color=TEXT_DARK, size=11.5),
            title_font=dict(color=TEXT_DARK, size=12, weight="bold"),
        ),
        legend=dict(
            title=dict(font=dict(color=TEXT_DARK, size=12, weight="bold")),
            font=dict(color=TEXT_DARK, size=11.5),
            bgcolor="rgba(255,255,255,0.9)",
        ),
    )
    return fig


def _sum_cols(df, prefix, months, yr):
    if df is None or df.empty:
        return pd.Series(dtype=float)
    cols = [f"{prefix}{m} {yr}" for m in months if f"{prefix}{m} {yr}" in df.columns]
    if not cols:
        return pd.Series(0.0, index=df.index)
    return df[cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)


def build_v2_kpi_datasets(df_base, df_focus, months, focus_yr, base_yr):
    if df_base is None or df_focus is None or df_base.empty or df_focus.empty:
        return pd.DataFrame(), pd.DataFrame(), {}

    def extract_yr(df, yr, tag):
        out = df[["organisationunitname"]].copy()
        out[f"norm_{tag}"] = _sum_cols(df, "MOH 711 Normal Deliveries ", months, yr)
        out[f"cs_{tag}"] = _sum_cols(df, "MOH 711 Caesarian Sections ", months, yr)
        out[f"assisted_{tag}"] = _sum_cols(df, "MOH 711 Assisted vaginal delivery ", months, yr)
        out[f"breech_{tag}"] = _sum_cols(df, "MOH 711 Breach Delivery ", months, yr)
        out[f"deliv_{tag}"] = out[f"norm_{tag}"] + out[f"cs_{tag}"] + out[f"assisted_{tag}"] + out[f"breech_{tag}"]
        out[f"live_{tag}"] = _sum_cols(df, "MOH 711 Live birth ", months, yr)
        out[f"fsb_{tag}"] = _sum_cols(df, "MOH 711 Fresh Still Birth ", months, yr)
        out[f"msb_{tag}"] = _sum_cols(df, "MOH 711 Macerated still Birth ", months, yr)
        out[f"sb_{tag}"] = out[f"fsb_{tag}"] + out[f"msb_{tag}"]
        out[f"neo_d_{tag}"] = _sum_cols(df, "MOH 711 Neonatal deaths 0-28 Days ", months, yr)
        out[f"peri_d_{tag}"] = _sum_cols(df, "MOH 711 Rev 2020_Perinatal Deaths 0-7 days ", months, yr)
        out[f"pph_a_{tag}"] = _sum_cols(df, "MOH 711 PPH (Post Partum Haemorrage) A ", months, yr)
        out[f"pph_d_{tag}"] = _sum_cols(df, "MOH 711 PPH (Post Partum Haemorrage) D ", months, yr)
        out[f"apgar_{tag}"] = _sum_cols(df, "MOH 711 Births with low APGAR score ", months, yr)
        out[f"asph_d_{tag}"] = _sum_cols(df, "MOH 711 Neonatal death due to birth asphyxia ", months, yr)
        return out

    b_df = extract_yr(df_base, base_yr, "base")
    f_df = extract_yr(df_focus, focus_yr, "focus")
    fac = pd.merge(b_df, f_df, on="organisationunitname", how="outer").fillna(0)

    fac["deliv_diff"] = fac["deliv_focus"] - fac["deliv_base"]
    fac["deliv_pct"] = np.where(
        fac["deliv_base"] > 0,
        (fac["deliv_diff"] / fac["deliv_base"]) * 100,
        np.where(fac["deliv_focus"] > 0, 100.0, 0.0),
    )
    fac["cs_rate_focus"] = np.where(fac["deliv_focus"] > 0, (fac["cs_focus"] / fac["deliv_focus"]) * 100, 0.0)
    fac["sb_rate_1000"] = np.where(
        (fac["live_focus"] + fac["sb_focus"]) > 0,
        (fac["sb_focus"] / (fac["live_focus"] + fac["sb_focus"])) * 1000,
        0.0,
    )
    fac["nmr_1000"] = np.where(fac["live_focus"] > 0, (fac["neo_d_focus"] / fac["live_focus"]) * 1000, 0.0)
    fac["adverse_rate_1000"] = np.where(
        fac["deliv_focus"] > 0,
        ((fac["sb_focus"] + fac["neo_d_focus"]) / fac["deliv_focus"]) * 1000,
        0.0,
    )
    fac["unreconciled_focus"] = np.maximum(0, fac["deliv_focus"] - (fac["live_focus"] + fac["sb_focus"]))

    fac["Trajectory"] = np.where(
        fac["deliv_diff"] > 0,
        "Gaining (+)",
        np.where(fac["deliv_diff"] < 0, "Dropping (-)", "Stable (0)"),
    )

    # Build full available monthly context (all months present in columns) + flag selected months
    all_months_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    avail_months = [
        m for m in all_months_order
        if f"MOH 711 Normal Deliveries {m} {focus_yr}" in df_focus.columns
        or f"MOH 711 Normal Deliveries {m} {base_yr}" in df_base.columns
    ]
    if not avail_months:
        avail_months = list(months)

    monthly_rows = []
    for m in avail_months:
        b_deliv = (
            _sum_cols(df_base, "MOH 711 Normal Deliveries ", [m], base_yr).sum()
            + _sum_cols(df_base, "MOH 711 Caesarian Sections ", [m], base_yr).sum()
            + _sum_cols(df_base, "MOH 711 Assisted vaginal delivery ", [m], base_yr).sum()
            + _sum_cols(df_base, "MOH 711 Breach Delivery ", [m], base_yr).sum()
        )
        f_deliv = (
            _sum_cols(df_focus, "MOH 711 Normal Deliveries ", [m], focus_yr).sum()
            + _sum_cols(df_focus, "MOH 711 Caesarian Sections ", [m], focus_yr).sum()
            + _sum_cols(df_focus, "MOH 711 Assisted vaginal delivery ", [m], focus_yr).sum()
            + _sum_cols(df_focus, "MOH 711 Breach Delivery ", [m], focus_yr).sum()
        )
        b_sb = _sum_cols(df_base, "MOH 711 Fresh Still Birth ", [m], base_yr).sum() + _sum_cols(df_base, "MOH 711 Macerated still Birth ", [m], base_yr).sum()
        f_sb = _sum_cols(df_focus, "MOH 711 Fresh Still Birth ", [m], focus_yr).sum() + _sum_cols(df_focus, "MOH 711 Macerated still Birth ", [m], focus_yr).sum()
        f_live = _sum_cols(df_focus, "MOH 711 Live birth ", [m], focus_yr).sum()
        f_cs = _sum_cols(df_focus, "MOH 711 Caesarian Sections ", [m], focus_yr).sum()
        f_neo = _sum_cols(df_focus, "MOH 711 Neonatal deaths 0-28 Days ", [m], focus_yr).sum()

        if b_deliv > 0 or f_deliv > 0:
            monthly_rows.append({
                "Month": m[:3],
                "FullMonth": m,
                "IsSelected": m in months,
                f"{base_yr} Deliveries": b_deliv if b_deliv > 0 else None,
                f"{focus_yr} Deliveries": f_deliv if f_deliv > 0 else None,
                f"{base_yr} Stillbirths": b_sb,
                f"{focus_yr} Stillbirths": f_sb,
                f"{focus_yr} Live Births": f_live,
                f"{focus_yr} C-Section %": (f_cs / f_deliv * 100) if f_deliv > 0 else 0.0,
                f"{focus_yr} SBR (per 1k)": (f_sb / (f_live + f_sb) * 1000) if (f_live + f_sb) > 0 else 0.0,
                f"{focus_yr} NMR (per 1k)": (f_neo / f_live * 1000) if f_live > 0 else 0.0,
            })
    df_monthly = pd.DataFrame(monthly_rows)

    skip_cols = {"organisationunitname", "Trajectory", "deliv_pct", "cs_rate_focus", "sb_rate_1000", "nmr_1000", "adverse_rate_1000"}
    s = {col: fac[col].sum() for col in fac.columns if col not in skip_cols}
    s["gaining_sites"] = int((fac["deliv_diff"] > 0).sum())
    s["dropping_sites"] = int((fac["deliv_diff"] < 0).sum())
    s["stable_sites"] = int(((fac["deliv_diff"] == 0) & ((fac["deliv_focus"] > 0) | (fac["deliv_base"] > 0))).sum())
    s["total_gains"] = float(fac.loc[fac["deliv_diff"] > 0, "deliv_diff"].sum())
    s["total_drops"] = float(fac.loc[fac["deliv_diff"] < 0, "deliv_diff"].sum())

    s["deliv_growth_pct"] = ((s["deliv_focus"] - s["deliv_base"]) / s["deliv_base"] * 100) if s["deliv_base"] > 0 else 0.0
    s["live_pct_focus"] = (s["live_focus"] / s["deliv_focus"] * 100) if s["deliv_focus"] > 0 else 100.0
    s["live_pct_base"] = (s["live_base"] / s["deliv_base"] * 100) if s["deliv_base"] > 0 else 100.0
    s["cs_pct_focus"] = (s["cs_focus"] / s["deliv_focus"] * 100) if s["deliv_focus"] > 0 else 0.0
    s["cs_pct_base"] = (s["cs_base"] / s["deliv_base"] * 100) if s["deliv_base"] > 0 else 0.0

    tot_births_f = s["live_focus"] + s["sb_focus"]
    tot_births_b = s["live_base"] + s["sb_base"]
    s["sbr_focus"] = (s["sb_focus"] / tot_births_f * 1000) if tot_births_f > 0 else 0.0
    s["sbr_base"] = (s["sb_base"] / tot_births_b * 1000) if tot_births_b > 0 else 0.0

    s["nmr_focus"] = (s["neo_d_focus"] / s["live_focus"] * 1000) if s["live_focus"] > 0 else 0.0
    s["nmr_base"] = (s["neo_d_base"] / s["live_base"] * 1000) if s["live_base"] > 0 else 0.0

    s["pph_surv_focus"] = (s["pph_a_focus"] / (s["pph_a_focus"] + s["pph_d_focus"]) * 100) if (s["pph_a_focus"] + s["pph_d_focus"]) > 0 else 100.0
    s["asph_surv_focus"] = ((s["apgar_focus"] - s["asph_d_focus"]) / s["apgar_focus"] * 100) if s["apgar_focus"] > 0 else 100.0

    # Top gainer & dropper names for narrative callouts
    top_g = fac.sort_values("deliv_diff", ascending=False).iloc[0]
    top_d = fac.sort_values("deliv_diff", ascending=True).iloc[0]
    s["top_gainer_name"] = top_g["organisationunitname"]
    s["top_gainer_val"] = int(top_g["deliv_diff"])
    s["top_dropper_name"] = top_d["organisationunitname"]
    s["top_dropper_val"] = int(top_d["deliv_diff"])

    return fac, df_monthly, s


def render_story_card(col, title, icon, primary_val, rate_badge, badge_type, narrative):
    badge_bg = "#DCFCE7" if badge_type == "good" else ("#FEF3C7" if badge_type == "warn" else "#FEE2E2")
    badge_fg = "#166534" if badge_type == "good" else ("#92400E" if badge_type == "warn" else "#991B1B")
    border_accent = "#0D9488" if badge_type == "good" else ("#D97706" if badge_type == "warn" else "#DC2626")

    with col:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-top:4px solid {border_accent};
                        border-radius:10px; padding:14px 16px; box-shadow:0 2px 6px rgba(15,23,42,0.05); height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <span style="font-size:11px; font-weight:800; color:#475569; text-transform:uppercase; letter-spacing:0.6px;">{title}</span>
                    <span style="font-size:18px;">{icon}</span>
                </div>
                <div style="font-size:25px; font-weight:800; color:#0F172A; line-height:1.15; margin-bottom:6px;">{primary_val}</div>
                <div style="margin-bottom:8px;">
                    <span style="background:{badge_bg}; color:{badge_fg}; font-size:11px; font-weight:700;
                                 padding:3px 9px; border-radius:999px; display:inline-block;">{rate_badge}</span>
                </div>
                <div style="font-size:11.5px; color:#334155; line-height:1.45; border-top:1px dashed #E2E8F0; padding-top:7px;">
                    {narrative}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_kpi_v2_dashboard(df_base, df_focus, selected_months, focus_year, comparison_year, selected_period):
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg, #0F2C59 0%, #163E7A 100%); padding:18px 22px;
                    border-radius:10px; color:#FFFFFF; margin-bottom:16px;">
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:1.2px; color:#5EEAD4; font-weight:700;">
                M&E Executive Intelligence & Clinical Quality Governance
            </div>
            <div style="font-size:21px; font-weight:800; margin-top:2px;">
                Maternal & Newborn KPI Performance Story ({focus_year} Focus vs. {comparison_year} Baseline — {selected_period})
            </div>
            <div style="font-size:12.5px; color:#E2E8F0; margin-top:4px;">
                Synthesizing MOH 711 service volumes, standardized clinical mortality rates (per 1,000), WHO benchmark compliance, and facility-level gain/drop drivers.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fac_df, monthly_df, s = build_v2_kpi_datasets(df_base, df_focus, selected_months, focus_year, comparison_year)
    if fac_df.empty:
        st.warning("No MOH 711 KPI records found for the selected years and period.")
        return

    # ---------------------------------------------------------
    # ROW 1: 6 STORYTELLING EXECUTIVE KPI CARDS
    # ---------------------------------------------------------
    c1, c2, c3 = st.columns(3)
    deliv_delta = int(s["deliv_focus"] - s["deliv_base"])
    render_story_card(
        c1,
        f"Total Deliveries ({focus_year})",
        "👶",
        f"{int(s['deliv_focus']):,}",
        f"{'↑' if deliv_delta >= 0 else '↓'} {deliv_delta:+,} ({s['deliv_growth_pct']:+.1f}% YoY)",
        "good" if deliv_delta >= 0 else "bad",
        f"<b>Network Driver:</b> <b>{s['gaining_sites']} gaining sites</b> added +{int(s['total_gains']):,} births (led by <i>{s['top_gainer_name']}</i> {s['top_gainer_val']:+d}), while <b>{s['dropping_sites']} declining sites</b> lost {int(abs(s['total_drops'])):,}.",
    )

    live_delta = int(s["live_focus"] - s["live_base"])
    live_rate_diff = s["live_pct_focus"] - s["live_pct_base"]
    unrec = int(s["unreconciled_focus"])
    dq_note = (
        f" <span style='color:#B45309; font-weight:700;'>⚠️ {unrec} deliveries lack recorded birth outcome in KHIS.</span>"
        if unrec > 0
        else " 100% birth outcome reconciliation."
    )
    render_story_card(
        c2,
        "Live Births & Outcome Reconciliation",
        "🌱",
        f"{int(s['live_focus']):,} <span style='font-size:15px; color:#0D9488;'>({s['live_pct_focus']:.1f}%)</span>",
        f"{'↑' if live_delta >= 0 else '↓'} {live_delta:+,} Live Births ({live_rate_diff:+.2f} pp)",
        "good" if unrec == 0 and s["live_pct_focus"] >= 98.0 else "warn",
        f"<b>Clinical & DQA Check:</b> {s['live_pct_focus']:.1f}% recorded as live births vs. {s['live_pct_base']:.1f}% in {comparison_year}.{dq_note}",
    )

    cs_in_band = 10.0 <= s["cs_pct_focus"] <= 15.0
    cs_status = "Within WHO 10–15% Band" if cs_in_band else ("Above WHO 15% Band" if s["cs_pct_focus"] > 15.0 else "Below WHO 10% Band")
    render_story_card(
        c3,
        "Caesarean Section Rate",
        "🏥",
        f"{s['cs_pct_focus']:.1f}% <span style='font-size:15px; color:#475569;'>({int(s['cs_focus']):,})</span>",
        f"{cs_status} ({s['cs_pct_focus'] - s['cs_pct_base']:+.1f} pp YoY)",
        "good" if cs_in_band else "warn",
        f"<b>Surgical Access:</b> {int(s['cs_focus']):,} C-sections performed vs. {int(s['cs_base']):,} ({s['cs_pct_base']:.1f}%) in {comparison_year}; audit CEmONC referral readiness.",
    )

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)
    sbr_diff = s["sbr_focus"] - s["sbr_base"]
    render_story_card(
        c4,
        "Institutional Stillbirth Rate (SBR)",
        "🩺",
        f"{s['sbr_focus']:.1f} <span style='font-size:14px; color:#475569;'>/ 1,000 births</span>",
        f"{int(s['sb_focus'])} Total ({int(s['fsb_focus'])} FSB · {int(s['msb_focus'])} MSB) | {sbr_diff:+.1f} YoY",
        "good" if s["sbr_focus"] <= 12.0 and sbr_diff <= 0 else ("warn" if s["sbr_focus"] <= 20.0 else "bad"),
        f"<b>Intrapartum vs. Antenatal:</b> Fresh stillbirths (<b>{int(s['fsb_focus'])}</b>) reflect intrapartum monitoring quality, while macerated (<b>{int(s['msb_focus'])}</b>) point to ANC screening.",
    )

    nmr_diff = s["nmr_focus"] - s["nmr_base"]
    render_story_card(
        c5,
        "Neonatal Mortality Rate (NMR)",
        "📉",
        f"{s['nmr_focus']:.1f} <span style='font-size:14px; color:#475569;'>/ 1,000 live</span>",
        f"{int(s['neo_d_focus'])} Deaths (0–28d) | {nmr_diff:+.1f} vs {comparison_year}",
        "good" if s["nmr_focus"] <= 10.0 and nmr_diff <= 0 else ("warn" if s["nmr_focus"] <= 18.0 else "bad"),
        f"<b>Newborn Survival:</b> Shifted from <b>{s['nmr_base']:.1f}/1,000</b> ({int(s['neo_d_base'])} deaths) in {comparison_year} to <b>{s['nmr_focus']:.1f}/1,000</b> in {focus_year}.",
    )

    render_story_card(
        c6,
        "Obstetric & Newborn Rescue",
        "🛡️",
        f"{s['pph_surv_focus']:.1f}% <span style='font-size:14px; color:#0D9488;'>PPH Surv.</span>",
        f"Asphyxia Resuscitation: {s['asph_surv_focus']:.1f}% ({int(s['apgar_focus'])} cases)",
        "good" if s["pph_surv_focus"] >= 95.0 and s["asph_surv_focus"] >= 90.0 else "warn",
        f"<b>Emergency Readiness:</b> {int(s['pph_a_focus'])} PPH cases managed ({int(s['pph_d_focus'])} deaths) and {int(s['apgar_focus'] - s['asph_d_focus'])}/{int(s['apgar_focus'])} low-APGAR newborns saved.",
    )

    st.markdown("---")

    # ---------------------------------------------------------
    # SECTION 2: GAIN / DROP / OVERALL WATERFALL + CLINICAL CASCADE FUNNEL
    # ---------------------------------------------------------
    col_bridge, col_funnel = st.columns([1.15, 1.0])

    with col_bridge:
        st.markdown("#### 🌉 Network Volume Bridge: Baseline → Gaining → Dropping → Overall")
        fig_waterfall = go.Figure(
            go.Waterfall(
                name="Deliveries Bridge",
                orientation="v",
                measure=["absolute", "relative", "relative", "total"],
                x=[
                    f"{comparison_year} Overall",
                    f"Gaining Sites (+{s['gaining_sites']})",
                    f"Dropping Sites (-{s['dropping_sites']})",
                    f"{focus_year} Overall",
                ],
                textposition="outside",
                textfont=dict(color=TEXT_DARK, size=12, weight="bold"),
                text=[
                    f"{int(s['deliv_base']):,}",
                    f"+{int(s['total_gains']):,}",
                    f"{int(s['total_drops']):,}",
                    f"{int(s['deliv_focus']):,}",
                ],
                y=[s["deliv_base"], s["total_gains"], s["total_drops"], 0],
                connector={"line": {"color": "#64748B", "width": 1.5, "dash": "dot"}},
                increasing={"marker": {"color": "#0D9488"}},
                decreasing={"marker": {"color": "#DC2626"}},
                totals={"marker": {"color": "#0F2C59"}},
            )
        )
        max_y = max(s["deliv_base"] + s["total_gains"], s["deliv_focus"]) * 1.18
        _apply_clean_theme(fig_waterfall, height=370)
        fig_waterfall.update_yaxes(title=dict(text="Total Deliveries", font=dict(color=TEXT_DARK, size=12, weight="bold")), range=[0, max_y])
        fig_waterfall.update_layout(showlegend=False)
        st.plotly_chart(fig_waterfall, use_container_width=True)

    with col_funnel:
        st.markdown("#### 🔻 Clinical Delivery & Survival Cascade Funnel")
        vaginal_total = s["norm_focus"] + s["assisted_focus"] + s["breech_focus"]
        funnel_labels = [
            f"Total Institutional Deliveries ({int(s['deliv_focus']):,})",
            f"Vaginal Deliveries ({int(vaginal_total):,})",
            f"Recorded Live Births ({int(s['live_focus']):,})",
            f"Gaining-Site Births ({int(fac_df.loc[fac_df['deliv_diff'] > 0, 'deliv_focus'].sum()):,})",
            f"Dropping-Site Births ({int(fac_df.loc[fac_df['deliv_diff'] < 0, 'deliv_focus'].sum()):,})",
        ]
        funnel_values = [
            s["deliv_focus"],
            vaginal_total,
            s["live_focus"],
            float(fac_df.loc[fac_df["deliv_diff"] > 0, "deliv_focus"].sum()),
            float(fac_df.loc[fac_df["deliv_diff"] < 0, "deliv_focus"].sum()),
        ]
        fig_fnl = go.Figure(
            go.Funnel(
                y=funnel_labels,
                x=funnel_values,
                textinfo="value+percent initial",
                textfont=dict(color="#FFFFFF", size=12, weight="bold"),
                marker=dict(color=["#0F2C59", "#1E40AF", "#0D9488", "#059669", "#E11D48"]),
                connector=dict(fillcolor="#F1F5F9", line=dict(color="#CBD5E1", width=1)),
            )
        )
        _apply_clean_theme(fig_fnl, height=370, margin=dict(l=10, r=20, t=35, b=25))
        fig_fnl.update_layout(plot_bgcolor="#FFFFFF")
        st.plotly_chart(fig_fnl, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # SECTION 3: M&E ANALYST CHARTS (TRAJECTORY + RISK QUADRANT)
    # ---------------------------------------------------------
    t1, t2 = st.columns([1.15, 1.0])

    with t1:
        st.markdown(f"#### 📈 Monthly Trajectory & Control Band ({comparison_year} vs. {focus_year})")
        trend_metric = st.selectbox(
            "Select Trajectory Metric (full available year shown; selected period highlighted):",
            ["Deliveries Volume", "Stillbirth Rate (per 1,000)", "C-Section %"],
            key="v2_trend_metric",
        )
        fig_trend = go.Figure()
        if trend_metric == "Deliveries Volume":
            y_base = monthly_df[f"{comparison_year} Deliveries"]
            y_focus = monthly_df[f"{focus_year} Deliveries"]
            mean_b = y_base.mean()
            std_b = y_base.std() if len(y_base) > 1 else 0

            if len(monthly_df) > 1 and std_b > 0:
                fig_trend.add_trace(
                    go.Scatter(
                        x=list(monthly_df["Month"]) + list(monthly_df["Month"][::-1]),
                        y=[mean_b + std_b] * len(monthly_df) + [max(0, mean_b - std_b)] * len(monthly_df),
                        fill="toself",
                        fillcolor="rgba(148, 163, 184, 0.18)",
                        line=dict(color="rgba(255,255,255,0)"),
                        name=f"{comparison_year} ±1 SD Band",
                        hoverinfo="skip",
                    )
                )

            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_df["Month"],
                    y=y_base,
                    mode="lines+markers",
                    name=f"{comparison_year} Baseline",
                    line=dict(color="#64748B", width=2.5, dash="dash"),
                    marker=dict(size=7, color="#64748B"),
                    hovertemplate="%{y:,.0f}",
                )
            )
            marker_sizes = [13 if sel else 8 for sel in monthly_df["IsSelected"]]
            marker_colors = ["#0D9488" if sel else "#0F2C59" for sel in monthly_df["IsSelected"]]
            txt_positions = [
                "top center" if (pd.isna(b) or (pd.notna(f) and f >= b)) else "bottom center"
                for f, b in zip(y_focus, y_base)
            ]
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_df["Month"],
                    y=y_focus,
                    mode="lines+markers+text",
                    text=[
                        f"<b>{int(v):,}</b>" if (pd.notna(v) and sel) else (f"{int(v):,}" if pd.notna(v) else "")
                        for v, sel in zip(y_focus, monthly_df["IsSelected"])
                    ],
                    textposition=txt_positions,
                    textfont=dict(color=TEXT_DARK, size=11.5),
                    name=f"{focus_year} Focus (Highlighted = Selected)",
                    line=dict(color="#0F2C59", width=3.5),
                    marker=dict(size=marker_sizes, color=marker_colors, line=dict(width=1.5, color="#FFFFFF")),
                    hovertemplate="<b>%{y:,.0f}</b>",
                )
            )
            all_vals = pd.concat([y_base.dropna(), y_focus.dropna()])
            if not all_vals.empty:
                y_min, y_max = all_vals.min(), all_vals.max()
                span = max(50, y_max - y_min)
                fig_trend.update_yaxes(range=[max(0, y_min - span * 0.28), y_max + span * 0.25])
        elif trend_metric == "Stillbirth Rate (per 1,000)":
            y_sbr = monthly_df[f"{focus_year} SBR (per 1k)"]
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_df["Month"],
                    y=y_sbr,
                    mode="lines+markers+text",
                    text=[f"{v:.1f}" for v in y_sbr],
                    textposition="top center",
                    textfont=dict(color=TEXT_DARK, size=11),
                    name=f"{focus_year} SBR / 1,000",
                    line=dict(color="#DC2626", width=3),
                    fill="tozeroy",
                    fillcolor="rgba(220, 38, 38, 0.08)",
                )
            )
            fig_trend.add_hline(
                y=12.0,
                line_dash="dot",
                line_color="#0D9488",
                annotation_text="ENAP Target (≤12/1,000)",
                annotation_font=dict(color="#0F766E", size=11),
            )
        else:
            y_cs = monthly_df[f"{focus_year} C-Section %"]
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_df["Month"],
                    y=y_cs,
                    mode="lines+markers+text",
                    text=[f"{v:.1f}%" for v in y_cs],
                    textposition="top center",
                    textfont=dict(color=TEXT_DARK, size=11),
                    name=f"{focus_year} C-Section %",
                    line=dict(color="#2563EB", width=3),
                )
            )
            fig_trend.add_hrect(
                y0=10,
                y1=15,
                fillcolor="rgba(13,148,136,0.12)",
                line_width=0,
                annotation_text="WHO Optimal (10–15%)",
                annotation_font=dict(color="#0F766E", size=11),
            )

        _apply_clean_theme(fig_trend, height=370)
        fig_trend.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_trend, use_container_width=True)

    with t2:
        st.markdown("#### 🎯 Clinical Quality Quadrant (Volume vs. Adverse Perinatal Rate)")
        active_fac = fac_df[fac_df["deliv_focus"] > 0].copy()
        if not active_fac.empty:
            med_vol = active_fac["deliv_focus"].median()
            fig_quad = px.scatter(
                active_fac,
                x="deliv_focus",
                y="adverse_rate_1000",
                size="deliv_focus",
                color="Trajectory",
                hover_name="organisationunitname",
                hover_data={
                    "deliv_focus": ":,.0f",
                    "deliv_diff": ":+,.0f",
                    "sb_focus": ":.0f",
                    "neo_d_focus": ":.0f",
                    "adverse_rate_1000": ":.1f",
                },
                color_discrete_map={
                    "Gaining (+)": "#0D9488",
                    "Dropping (-)": "#DC2626",
                    "Stable (0)": "#64748B",
                },
                labels={
                    "deliv_focus": f"{focus_year} Delivery Volume",
                    "adverse_rate_1000": "Stillbirth + Neonatal Death Rate (per 1,000)",
                },
            )
            # Label high-risk / high-volume outlier facilities directly on chart
            outliers = active_fac[active_fac["adverse_rate_1000"] > 15.0]
            fig_quad.add_trace(
                go.Scatter(
                    x=outliers["deliv_focus"],
                    y=outliers["adverse_rate_1000"],
                    mode="text",
                    text=outliers["organisationunitname"].str.slice(0, 22),
                    textposition="top center",
                    textfont=dict(color=TEXT_DARK, size=10),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
            fig_quad.add_vline(
                x=med_vol,
                line_dash="dash",
                line_color="#64748B",
                annotation_text=f"Median Vol ({int(med_vol)})", annotation_position="bottom right",
                annotation_font=dict(color=TEXT_DARK, size=11),
            )
            fig_quad.add_hline(
                y=15.0,
                line_dash="dash",
                line_color="#D97706",
                annotation_text="CQI Alert Threshold (15/1k)",
                annotation_font=dict(color="#B45309", size=11),
            )
            _apply_clean_theme(fig_quad, height=405)
            fig_quad.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_quad, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # SECTION 4: DIVERGING LOLLIPOP CHART (GAINING VS DROPPING FACILITIES)
    # ---------------------------------------------------------
    st.markdown(f"#### 🍭 Facility Gain / Drop Diverging Lollipop Analysis ({comparison_year} → {focus_year})")
    l1, l2 = st.columns([1.3, 1.0])
    with l1:
        lolli_ind = st.selectbox(
            "Select Indicator for Facility Gain/Drop Ranking:",
            [
                ("Total Deliveries", "deliv_base", "deliv_focus"),
                ("Live Births", "live_base", "live_focus"),
                ("Normal Deliveries", "norm_base", "norm_focus"),
                ("Caesarian Sections", "cs_base", "cs_focus"),
                ("Total Stillbirths (FSB + MSB)", "sb_base", "sb_focus"),
                ("Neonatal Deaths (0–28d)", "neo_d_base", "neo_d_focus"),
            ],
            format_func=lambda x: x[0],
            key="v2_lolli_ind",
        )
    with l2:
        lolli_filter = st.radio(
            "Filter Sites:",
            ["All Active Sites", "Gaining Only (+)", "Dropping Only (-)"],
            horizontal=True,
            key="v2_lolli_filter",
        )

    label_ind, col_b, col_f = lolli_ind
    rank_df = fac_df[["organisationunitname", col_b, col_f]].copy()
    rank_df["Variance"] = rank_df[col_f] - rank_df[col_b]
    rank_df = rank_df[(rank_df[col_b] > 0) | (rank_df[col_f] > 0)]

    if lolli_filter == "Gaining Only (+)":
        rank_df = rank_df[rank_df["Variance"] > 0]
    elif lolli_filter == "Dropping Only (-)":
        rank_df = rank_df[rank_df["Variance"] < 0]

    rank_df = rank_df.sort_values("Variance", ascending=True)

    if not rank_df.empty:
        is_adverse = col_f in ["sb_focus", "neo_d_focus"]
        colors = [
            ("#DC2626" if v > 0 else "#0D9488") if is_adverse else ("#0D9488" if v >= 0 else "#DC2626")
            for v in rank_df["Variance"]
        ]

        fig_lolli = go.Figure()
        for _, row in rank_df.iterrows():
            c_line = ("#DC2626" if row["Variance"] > 0 else "#0D9488") if is_adverse else ("#0D9488" if row["Variance"] >= 0 else "#DC2626")
            fig_lolli.add_trace(
                go.Scatter(
                    x=[0, row["Variance"]],
                    y=[row["organisationunitname"], row["organisationunitname"]],
                    mode="lines",
                    line=dict(color=c_line, width=2.8),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        labels_txt = [
            f" {int(v):+d} ({int(b)}→{int(f)})" if v >= 0 else f"{int(v):+d} ({int(b)}→{int(f)}) "
            for v, b, f in zip(rank_df["Variance"], rank_df[col_b], rank_df[col_f])
        ]
        fig_lolli.add_trace(
            go.Scatter(
                x=rank_df["Variance"],
                y=rank_df["organisationunitname"],
                mode="markers+text",
                text=labels_txt,
                textposition=["middle right" if v >= 0 else "middle left" for v in rank_df["Variance"]],
                textfont=dict(color=TEXT_DARK, size=11, weight="bold"),
                marker=dict(size=10, color=colors),
                customdata=np.stack([rank_df[col_b], rank_df[col_f]], axis=-1),
                showlegend=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    f"{comparison_year}: %{{customdata[0]:,.0f}}<br>"
                    f"{focus_year}: %{{customdata[1]:,.0f}}<br>"
                    "Net Change: <b>%{x:+d}</b><extra></extra>"
                ),
            )
        )
        min_v = min(0, rank_df["Variance"].min())
        max_v = max(0, rank_df["Variance"].max())
        pad = max(10, (max_v - min_v) * 0.22)

        fig_lolli.add_vline(x=0, line_color="#0F172A", line_width=1.4)
        _apply_clean_theme(fig_lolli, height=max(420, len(rank_df) * 28), margin=dict(l=10, r=40, t=20, b=30))
        fig_lolli.update_xaxes(
            title=dict(text=f"Net Change ({focus_year} vs. {comparison_year})", font=dict(color=TEXT_DARK, size=12, weight="bold")),
            range=[min_v - pad, max_v + pad],
            zeroline=False,
        )
        fig_lolli.update_yaxes(tickfont=dict(color=TEXT_DARK, size=12))
        st.plotly_chart(fig_lolli, use_container_width=True)
    else:
        st.info("No facilities match the selected filter for this indicator.")
