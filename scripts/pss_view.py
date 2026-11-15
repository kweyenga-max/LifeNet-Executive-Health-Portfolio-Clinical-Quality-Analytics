import os
import sys
import html
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import pss_analytics as pssa


def _editorial_callout(text_md: str, accent_hex: str = "#0F2C59", min_h: int = 165):
    """Render a clean, neutral white/slate editorial analytical note (replacing heavy blue st.info boxes)."""
    # Convert bold **...** markdown to <b>...</b> safely
    parts = text_md.split("**")
    formatted = []
    for i, part in enumerate(parts):
        esc = html.escape(part)
        if i % 2 == 1:
            formatted.append(f"<b style='color:#0F2C59;'>{esc}</b>")
        else:
            formatted.append(esc)
    body_html = "".join(formatted)

    st.markdown(
        f"""
        <div style="
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-left: 4px solid {accent_hex};
            border-radius: 10px;
            padding: 14px 16px;
            margin-top: 8px;
            min-height: {min_h}px;
            box-sizing: border-box;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            color: #1E293B;
            font-size: 12.8px;
            line-height: 1.58;
        ">
            {body_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_light_html_table(df_in: pd.DataFrame, max_height: int = 380):
    """Render a crisp light-mode Navy HTML scorecard table with high-contrast typography."""
    if df_in.empty:
        st.info("No records available for this register.")
        return

    cols = list(df_in.columns)
    headers = []
    for c in cols:
        lbl = c.replace("_", " ").replace("%", "(%)")
        align = "right" if ("PV" in c or "%" in c or "Delta" in c or "Surveys" in c or "Rounds" in c) else "left"
        headers.append(f"<th style='padding:9px 11px; text-align:{align}; font-weight:700; white-space:nowrap;'>{html.escape(lbl)}</th>")

    rows_html = []
    for idx, (_, r) in enumerate(df_in.iterrows()):
        bg = "#FFFFFF" if idx % 2 == 0 else "#F8FAFC"
        cells = []
        for c in cols:
            val = r[c]
            if pd.isna(val):
                disp = "—"
            elif "PV" in c:
                disp = f"{int(val):,}"
            elif "%" in c:
                disp = f"{float(val):.1f}%"
            elif c == "Delta":
                disp = f"{float(val):+.1f} pp"
            else:
                disp = str(val)

            if c == "Priority_Tier":
                if str(disp).startswith("P1"):
                    cell_html = f"<span style='background:#FEF2F2;color:#B91C1C;border:1px solid #FECACA;padding:2px 8px;border-radius:10px;font-weight:700;font-size:11px;white-space:nowrap;'>{html.escape(disp)}</span>"
                elif str(disp).startswith("P2"):
                    cell_html = f"<span style='background:#FFFBEB;color:#B45309;border:1px solid #FDE68A;padding:2px 8px;border-radius:10px;font-weight:700;font-size:11px;white-space:nowrap;'>{html.escape(disp)}</span>"
                else:
                    cell_html = f"<span style='background:#F1F5F9;color:#334155;border:1px solid #CBD5E1;padding:2px 8px;border-radius:10px;font-weight:700;font-size:11px;white-space:nowrap;'>{html.escape(disp)}</span>"
                cells.append(f"<td style='padding:8px 11px;'>{cell_html}</td>")
            elif c == "Facility":
                cells.append(f"<td style='padding:8px 11px;font-weight:700;color:#0F172A;white-space:nowrap;'>{html.escape(disp)}</td>")
            elif "PV" in c or "%" in c or c in ("Delta", "Surveys", "Rounds"):
                color = "#047857" if (c == "Delta" and pd.notna(val) and float(val) >= 2.0) else ("#B91C1C" if (c == "Delta" and pd.notna(val) and float(val) <= -2.0) else "#0F172A")
                cells.append(f"<td style='padding:8px 11px;text-align:right;font-weight:600;color:{color};white-space:nowrap;'>{html.escape(disp)}</td>")
            else:
                cells.append(f"<td style='padding:8px 11px;color:#334155;font-size:12px;'>{html.escape(disp)}</td>")

        rows_html.append(f"<tr style='background:{bg}; border-bottom:1px solid #E2E8F0;'>{''.join(cells)}</tr>")

    st.markdown(
        f"""
        <div style="max-height:{max_height}px; overflow:auto; border:1px solid #CBD5E1; border-radius:10px; background:#FFFFFF; box-shadow:0 2px 8px rgba(15,23,42,0.04);">
            <table style="width:100%; border-collapse:collapse; font-family:Inter,sans-serif; font-size:12.5px;">
                <thead style="position:sticky; top:0; z-index:2; background:#0F2C59; color:#FFFFFF;">
                    <tr>{''.join(headers)}</tr>
                </thead>
                <tbody>{''.join(rows_html)}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pss_view():
    st.markdown(
        """
        <style>
            div[data-testid="stTabs"] button[role="tab"] {
                color: #334155 !important;
                font-weight: 700 !important;
                font-size: 13px !important;
            }
            div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
                color: #0F2C59 !important;
                border-bottom-color: #C8102E !important;
            }
            div[data-testid="stDownloadButton"] > button {
                background: #0F2C59 !important;
                color: #FFFFFF !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 700 !important;
                font-size: 12.5px !important;
                padding: 8px 14px !important;
            }
            div[data-testid="stDownloadButton"] > button p,
            div[data-testid="stDownloadButton"] > button span {
                color: #FFFFFF !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    pss_data = pssa.get_pss_me_analytics(force_live=False)
    win_lbl = pss_data.get("window_label", "Past 12 Months")

    # Refined Architectural Editorial Header (Warm White/Crimson Accent + Deep Navy Typography)
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #FFFFFF 0%, #FFF9FA 100%);
            border: 1px solid #F3D1D6;
            border-left: 5px solid #C8102E;
            border-radius: 12px;
            padding: 18px 24px;
            margin-bottom: 18px;
            box-shadow: 0 2px 10px rgba(200, 16, 46, 0.04);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 14px;
        ">
            <div>
                <div style="color:#C8102E; font-size:11px; font-weight:800; letter-spacing:0.11em; text-transform:uppercase; margin-bottom:4px;">
                    LifeNet International Kenya · Patient Experience &amp; Quality Surveillance
                </div>
                <h2 style="color:#0F2C59; font-size:22px; font-weight:800; margin:0 0 4px 0; line-height:1.25; letter-spacing:-0.01em;">
                    😊 Patient Satisfaction Survey (PSS) — Past 12 Months ({win_lbl})
                </h2>
                <p style="color:#1E3A5F; font-size:13px; margin:0;">
                    Live MoniTrac DHIS2 Rolling 12-Month Interoperability Layer (<code style="background:#FFF1F2;color:#0F2C59;border:1px solid #FECDD3;padding:1px 5px;border-radius:4px;">pe:LAST_12_MONTHS</code>) · Scoped to 38 Active Partner Facilities
                </p>
            </div>
            <div style="
                background: #FFF1F2;
                border: 1px solid #FECDD3;
                border-radius: 20px;
                padding: 6px 14px;
                color: #0F2C59;
                font-size: 12px;
                font-weight: 700;
                white-space: nowrap;
            ">
                <span style="color:#C8102E; margin-right:5px;">●</span>Rolling 12M Audit Window
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if pss_data.get("empty", True):
        st.warning("⚠️ No PSS records available in the past 12 months. Run `./sync_khis.sh` to pull live MoniTrac PSS data.")
        return

    insights = pssa.generate_pss_chart_insights(pss_data)
    df_pss = pss_data["df"]
    s_p6 = pss_data["s_prior6"]
    s_r6 = pss_data["s_recent6"]
    m_spc = pss_data["m_spc"]
    cohort_df = pss_data["cohort_df"]
    pending_df = pss_data["pending_df"]
    fac_summary_df = pss_data["fac_summary_df"]

    mean_12m = float(df_pss["Net_Satisfaction_Score"].mean())
    med_12m = float(df_pss["Net_Satisfaction_Score"].median())
    mean_r6 = float(s_r6.mean()) if len(s_r6) else 0.0
    mean_p6 = float(s_p6.mean()) if len(s_p6) else 0.0
    delta_6m = mean_r6 - mean_p6 if (len(s_r6) and len(s_p6)) else 0.0
    iqr_p6 = float(s_p6.quantile(0.75) - s_p6.quantile(0.25)) if len(s_p6) else 0.0
    assessed_cnt = int(pss_data["assessed_count"])
    never_cnt = int(pss_data["never_count"])
    only_p6_cnt = int(pss_data["only_p6_count"])

    # 1. Executive 5-Card KPI Strip (Warm Crimson-Tinted Surfaces + Deep Navy Typography)
    st.markdown(
        f"""
        <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:14px; margin-bottom:20px;">
            <div style="background:linear-gradient(180deg, #FFF5F6 0%, #FFFBFB 100%); border:1px solid #F5C2C7; border-top:3.5px solid #C8102E; border-radius:12px; padding:15px 17px; box-shadow:0 2px 8px rgba(200,16,46,0.05);">
                <div style="color:#0F2C59; opacity:0.78; font-size:10.5px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">Past 12M Network Mean</div>
                <div style="color:#0F2C59; font-size:24px; font-weight:800; margin:6px 0; letter-spacing:-0.02em;">{mean_12m:.2f}%</div>
                <span style="background:#FFFFFF; border:1px solid #F3D1D6; color:#0F2C59; font-size:11px; font-weight:700; padding:3px 8px; border-radius:6px;">Median: {med_12m:.2f}% (n={len(df_pss)})</span>
            </div>
            <div style="background:linear-gradient(180deg, #FFF5F6 0%, #FFFBFB 100%); border:1px solid #F5C2C7; border-top:3.5px solid #C8102E; border-radius:12px; padding:15px 17px; box-shadow:0 2px 8px rgba(200,16,46,0.05);">
                <div style="color:#0F2C59; opacity:0.78; font-size:10.5px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">Recent 6M Mean (n={len(s_r6)})</div>
                <div style="color:#0F2C59; font-size:24px; font-weight:800; margin:6px 0; letter-spacing:-0.02em;">{mean_r6:.2f}%</div>
                <span style="background:#ECFDF5; border:1px solid #A7F3D0; color:#065F46; font-size:11px; font-weight:700; padding:3px 8px; border-radius:6px;">{delta_6m:+.2f} pp vs Prior 6M (p={pss_data['p_val_t']:.2f})</span>
            </div>
            <div style="background:linear-gradient(180deg, #FFF5F6 0%, #FFFBFB 100%); border:1px solid #F5C2C7; border-top:3.5px solid #C8102E; border-radius:12px; padding:15px 17px; box-shadow:0 2px 8px rgba(200,16,46,0.05);">
                <div style="color:#0F2C59; opacity:0.78; font-size:10.5px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">Prior 6M Mean (n={len(s_p6)})</div>
                <div style="color:#0F2C59; font-size:24px; font-weight:800; margin:6px 0; letter-spacing:-0.02em;">{mean_p6:.2f}%</div>
                <span style="background:#FFFFFF; border:1px solid #F3D1D6; color:#0F2C59; font-size:11px; font-weight:700; padding:3px 8px; border-radius:6px;">IQR: {iqr_p6:.1f} pp Spread</span>
            </div>
            <div style="background:linear-gradient(180deg, #FFF5F6 0%, #FFFBFB 100%); border:1px solid #F5C2C7; border-top:3.5px solid #C8102E; border-radius:12px; padding:15px 17px; box-shadow:0 2px 8px rgba(200,16,46,0.05);">
                <div style="color:#0F2C59; opacity:0.78; font-size:10.5px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">12M Surveillance Reach</div>
                <div style="color:#0F2C59; font-size:24px; font-weight:800; margin:6px 0; letter-spacing:-0.02em;">{assessed_cnt} / 38 Sites</div>
                <span style="background:#FFFFFF; border:1px solid #F3D1D6; color:#0F2C59; font-size:11px; font-weight:700; padding:3px 8px; border-radius:6px;">{(assessed_cnt/38*100):.1f}% Assessed in 12M</span>
            </div>
            <div style="background:linear-gradient(180deg, #FEE2E2 0%, #FFF5F5 100%); border:1px solid #FCA5A5; border-top:3.5px solid #991B1B; border-radius:12px; padding:15px 17px; box-shadow:0 2px 8px rgba(200,16,46,0.07);">
                <div style="color:#0F2C59; opacity:0.85; font-size:10.5px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">Unassessed in Past 12M</div>
                <div style="color:#0F2C59; font-size:24px; font-weight:800; margin:6px 0; letter-spacing:-0.02em;">{never_cnt} Facilities</div>
                <span style="background:#FFFFFF; border:1px solid #FCA5A5; color:#991B1B; font-size:11px; font-weight:700; padding:3px 8px; border-radius:6px;">+ {only_p6_cnt} Due for 6M Follow-Up</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ROW 1: Violin + Boxplot Distribution & Longitudinal Paired Cohort Slopegraph (Charts preserved verbatim)
    col_g1, col_g2 = st.columns(2, gap="medium")

    with col_g1:
        st.markdown(
            "<div style='background:#FFFFFF; border:1px solid #CBD5E1; border-bottom:none; border-radius:12px 12px 0 0; padding:13px 16px 4px 16px;'>"
            "<div style='color:#0F2C59; font-size:15.5px; font-weight:800;'>A. Score Density, IQR &amp; Semi-Annual Shift (Prior 6M vs. Recent 6M)</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        fig_violin = go.Figure()
        for lbl_6m, s_vals, col_hex in [
            (pss_data["first_6m_label"], s_p6, "#0A2540"),
            (pss_data["recent_6m_label"], s_r6, "#00A8CC"),
        ]:
            if len(s_vals) > 0:
                fig_violin.add_trace(
                    go.Violin(
                        y=s_vals,
                        name=f"{lbl_6m} (n={len(s_vals)})",
                        box_visible=True,
                        meanline_visible=True,
                        points="all",
                        jitter=0.25,
                        pointpos=-1.4,
                        fillcolor=col_hex,
                        opacity=0.65,
                        line_color=col_hex,
                    )
                )
        fig_violin.add_hline(y=80.0, line_dash="dash", line_color="#0D9488", annotation_text="80% Quality Benchmark")
        fig_violin.update_layout(
            height=385,
            font=dict(color="#0F172A", size=12),
            xaxis=dict(tickfont=dict(color="#0F172A", size=12)),
            yaxis=dict(title=dict(text="Net Satisfaction Score (%)", font=dict(color="#0F172A")), tickfont=dict(color="#0F172A"), range=[55, 106], gridcolor="#E2E8F0"),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            margin=dict(l=20, r=20, t=24, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig_violin, use_container_width=True)
        _editorial_callout(insights["chart_a"], accent_hex="#0F2C59", min_h=175)

    with col_g2:
        st.markdown(
            f"<div style='background:#FFFFFF; border:1px solid #CBD5E1; border-bottom:none; border-radius:12px 12px 0 0; padding:13px 16px 4px 16px;'>"
            f"<div style='color:#0F2C59; font-size:15.5px; font-weight:800;'>B. Intra-Year Paired Trajectory (n={pss_data['both_count']} Sites Assessed in Both Halves)</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        fig_slope = go.Figure()
        if not cohort_df.empty:
            for _, r in cohort_df.iterrows():
                line_col = "#0D9488" if r["Delta"] >= 2.0 else ("#DC2626" if r["Delta"] <= -2.0 else "#64748B")
                fig_slope.add_trace(
                    go.Scatter(
                        x=["Prior 6M Mean", "Recent 6M Mean"],
                        y=[r["Prior_6M_Mean"], r["Recent_6M_Mean"]],
                        mode="lines+markers",
                        name=f"{r['Facility']} ({r['Delta']:+.1f}%)",
                        line=dict(color=line_col, width=2.4 if abs(r["Delta"]) >= 4 else 1.4),
                        marker=dict(size=8, color=line_col),
                        hovertemplate=f"<b>{r['Facility']}</b><br>Prior 6M: {r['Prior_6M_Mean']:.1f}%<br>Recent 6M: {r['Recent_6M_Mean']:.1f}%<br>Delta: {r['Delta']:+.1f} pp<extra></extra>",
                    )
                )
        fig_slope.add_hline(y=80.0, line_dash="dot", line_color="#94A3B8", annotation_text="80% Target")
        fig_slope.update_layout(
            height=385,
            font=dict(color="#0F172A", size=12),
            xaxis=dict(tickfont=dict(color="#0F172A", size=12)),
            yaxis=dict(title=dict(text="Facility Mean Score (%)", font=dict(color="#0F172A")), tickfont=dict(color="#0F172A"), range=[58, 103], gridcolor="#E2E8F0"),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            margin=dict(l=20, r=20, t=24, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig_slope, use_container_width=True)
        _editorial_callout(insights["chart_b"], accent_hex="#0D9488", min_h=175)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ROW 2: Network Surveillance Coverage Donut & Monthly SPC Control Chart
    col_g3, col_g4 = st.columns([0.95, 1.25], gap="medium")

    with col_g3:
        st.markdown(
            "<div style='background:#FFFFFF; border:1px solid #CBD5E1; border-bottom:none; border-radius:12px 12px 0 0; padding:13px 16px 4px 16px;'>"
            "<div style='color:#0F2C59; font-size:15.5px; font-weight:800;'>C. 12-Month Surveillance Coverage (38 Facilities)</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        fig_donut = go.Figure(
            data=[
                go.Pie(
                    labels=[
                        f"Both 6M Halves ({pss_data['both_count']})",
                        f"Recent 6M Only ({pss_data['only_r6_count']})",
                        f"Prior 6M Only ({pss_data['only_p6_count']})",
                        f"Unassessed in 12M ({pss_data['never_count']})",
                    ],
                    values=[
                        pss_data["both_count"],
                        pss_data["only_r6_count"],
                        pss_data["only_p6_count"],
                        pss_data["never_count"],
                    ],
                    hole=0.52,
                    marker=dict(colors=["#0D9488", "#00A8CC", "#D97706", "#DC2626"]),
                    textinfo="label+percent",
                    textposition="outside",
                    textfont=dict(color="#0F172A", size=11),
                )
            ]
        )
        fig_donut.update_traces(pull=[0.02, 0.02, 0.02, 0.04], automargin=True)
        fig_donut.update_layout(
            height=385,
            margin=dict(l=45, r=45, t=42, b=50),
            paper_bgcolor="#FFFFFF",
            showlegend=False,
            annotations=[dict(text="<b>38</b><br>Partner<br>Sites", x=0.5, y=0.5, font=dict(size=15, color="#0F172A"), showarrow=False)],
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        _editorial_callout(insights["chart_c"], accent_hex="#C8102E", min_h=175)

    with col_g4:
        st.markdown(
            f"<div style='background:#FFFFFF; border:1px solid #CBD5E1; border-bottom:none; border-radius:12px 12px 0 0; padding:13px 16px 4px 16px;'>"
            f"<div style='color:#0F2C59; font-size:15.5px; font-weight:800;'>D. Monthly Statistical Process Control (SPC ±1 SD Band — {win_lbl})</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        fig_spc = go.Figure()
        fig_spc.add_trace(
            go.Scatter(
                x=list(m_spc["periodname"]) + list(m_spc["periodname"])[::-1],
                y=list(m_spc["Upper_1SD"]) + list(m_spc["Lower_1SD"])[::-1],
                fill="toself",
                fillcolor="rgba(15, 44, 89, 0.10)",
                line=dict(color="rgba(255,255,255,0)"),
                name="±1 SD Dispersion Band",
                hoverinfo="skip",
            )
        )
        fig_spc.add_trace(
            go.Scatter(
                x=m_spc["periodname"],
                y=m_spc["Mean"],
                mode="lines+markers+text",
                name="Monthly Mean (%)",
                line=dict(color="#0A2540", width=3),
                marker=dict(size=9, color="#0A2540"),
                text=[f"{m:.1f}% (n={n})" for m, n in zip(m_spc["Mean"], m_spc["Surveys"])],
                textposition="top center",
            )
        )
        fig_spc.add_trace(
            go.Scatter(
                x=m_spc["periodname"],
                y=m_spc["Median"],
                mode="lines+markers",
                name="Monthly Median (%)",
                line=dict(color="#0D9488", width=2, dash="dash"),
                marker=dict(size=7, symbol="square"),
            )
        )
        fig_spc.add_hline(y=80.0, line_dash="dot", line_color="#DC2626", annotation_text="80% Quality Floor")
        fig_spc.update_layout(
            height=385,
            font=dict(color="#0F172A", size=12),
            xaxis=dict(tickfont=dict(color="#0F172A", size=11.5)),
            yaxis=dict(title=dict(text="Net Satisfaction Score (%)", font=dict(color="#0F172A")), tickfont=dict(color="#0F172A"), range=[55, 106], gridcolor="#E2E8F0"),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            margin=dict(l=20, r=20, t=44, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.0, font=dict(color="#0F172A", size=11.5)),
        )
        st.plotly_chart(fig_spc, use_container_width=True)
        _editorial_callout(insights["chart_d"], accent_hex="#475569", min_h=175)

    st.markdown("<hr style='border:none; border-top:1px solid #CBD5E1; margin:20px 0;'>", unsafe_allow_html=True)

    # Executive Synthesis Card (White/Slate Executive Framing instead of plain markdown)
    exec_lines = [ln.strip() for ln in insights["exec_summary"].splitlines() if ln.strip()]
    exec_title = exec_lines[0].replace("###", "").strip() if exec_lines else "M&E Specialist Executive Synthesis & Decision Brief"
    bullets_html = []
    for ln in exec_lines[1:]:
        clean_ln = ln.lstrip("-•* ").strip()
        parts = clean_ln.split("**")
        fmt_parts = []
        for i, p in enumerate(parts):
            esc = html.escape(p)
            fmt_parts.append(f"<b style='color:#0F2C59;'>{esc}</b>" if i % 2 == 1 else esc)
        bullets_html.append(f"<li style='margin-bottom:7px;'>{''.join(fmt_parts)}</li>")

    st.markdown(
        f"""
        <div style="
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-left: 5px solid #0F2C59;
            border-radius: 12px;
            padding: 18px 22px;
            margin-bottom: 20px;
            box-shadow: 0 3px 10px rgba(15,23,42,0.04);
        ">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <h4 style="color:#0F2C59; margin:0; font-size:16px; font-weight:800;">{html.escape(exec_title)}</h4>
                <span style="background:#F1F5F9; color:#0F2C59; font-size:10.5px; font-weight:800; padding:3px 9px; border-radius:8px;">EXECUTIVE BRIEF</span>
            </div>
            <ul style="color:#1E293B; font-size:13px; line-height:1.58; padding-left:18px; margin:0;">
                {''.join(bullets_html)}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ROW 3: Light-Mode Actionable Registers with CSV Exports
    tab_sub1, tab_sub2, tab_sub3 = st.tabs([
        f"⏳ Unassessed & Overdue Decision Register ({len(pending_df)} Sites)",
        "🏥 Complete 38-Facility 12M PSS Directory",
        "📈 Paired 6M Trajectory Table",
    ])

    with tab_sub1:
        c_h1, c_b1 = st.columns([3.2, 1.0])
        with c_h1:
            st.markdown(f"<div style='color:#0F2C59; font-size:15px; font-weight:800;'>Risk-Prioritized Facilities With Zero PSS in Past 12 Months or Due for 6M Follow-Up ({win_lbl})</div>", unsafe_allow_html=True)
            st.caption("Ranked by Priority Tier (P1 = High-Volume Blind Spots & Sub-75% Follow-Ups) and 12-Month Outpatient Volume so Mentor & M&E teams deploy where patient exposure is highest.")
        with c_b1:
            st.download_button("📥 Export Decision CSV", data=pending_df.to_csv(index=False).encode("utf-8"), file_name=f"LifeNet_PSS_Decision_Register_{win_lbl.replace(' ', '_')}.csv", mime="text/csv", use_container_width=True)
        _render_light_html_table(pending_df, max_height=380)

    with tab_sub2:
        c_h2, c_b2 = st.columns([3.2, 1.0])
        with c_h2:
            st.markdown(f"<div style='color:#0F2C59; font-size:15px; font-weight:800;'>Master Past-12-Month PSS Performance Directory (All 38 LifeNet Kenya Facilities)</div>", unsafe_allow_html=True)
        with c_b2:
            st.download_button("📥 Export Directory CSV", data=fac_summary_df.to_csv(index=False).encode("utf-8"), file_name=f"LifeNet_PSS_38_Facilities_{win_lbl.replace(' ', '_')}.csv", mime="text/csv", use_container_width=True)
        _render_light_html_table(fac_summary_df, max_height=400)

    with tab_sub3:
        c_h3, c_b3 = st.columns([3.2, 1.0])
        with c_h3:
            st.markdown("<div style='color:#0F2C59; font-size:15px; font-weight:800;'>Paired Semi-Annual Trajectory (Facilities Assessed in Both Prior 6M &amp; Recent 6M)</div>", unsafe_allow_html=True)
        with c_b3:
            st.download_button("📥 Export Paired CSV", data=cohort_df.to_csv(index=False).encode("utf-8"), file_name=f"LifeNet_PSS_Paired_6M_{win_lbl.replace(' ', '_')}.csv", mime="text/csv", use_container_width=True)
        _render_light_html_table(cohort_df, max_height=360)


if __name__ == "__main__":
    st.set_page_config(
        page_title="LifeNet Kenya · PSS Executive Preview",
        page_icon="😊",
        layout="wide",
    )
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            html, body, [class*="css"], .stApp {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                background-color: #F1F5F9 !important;
                color: #0F172A !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    render_pss_view()
