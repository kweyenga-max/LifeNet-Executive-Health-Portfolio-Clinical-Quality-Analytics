import os
import sys
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import finance_analytics as fa


def render_financial_performance_view():
    # Enforce crisp light-mode contrast for native Streamlit radios & download buttons
    st.markdown(
        """
        <style>
            div[data-testid="stRadio"] > label,
            div[data-testid="stRadio"] > label p,
            div[data-testid="stRadio"] div[role="radiogroup"] label,
            div[data-testid="stRadio"] div[role="radiogroup"] label p,
            div[data-testid="stRadio"] div[role="radiogroup"] span {
                color: #0F172A !important;
                font-weight: 700 !important;
                opacity: 1 !important;
            }
            div[data-testid="stRadio"] div[role="radiogroup"] {
                background: #FFFFFF !important;
                border: 1px solid #CBD5E1 !important;
                border-radius: 10px !important;
                padding: 6px 12px !important;
                gap: 14px !important;
            }
            div[data-testid="stDownloadButton"] > button {
                background: #0F2C59 !important;
                color: #FFFFFF !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 700 !important;
                font-size: 12.5px !important;
                padding: 10px 14px !important;
            }
            div[data-testid="stDownloadButton"] > button p,
            div[data-testid="stDownloadButton"] > button span {
                color: #FFFFFF !important;
            }
            div[data-testid="stDownloadButton"] > button:hover {
                background: #163E7A !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0B2244 0%, #153B73 100%);
            border-top: 5px solid #C8102E;
            border-radius: 14px;
            padding: 22px 26px;
            margin-bottom: 20px;
            box-shadow: 0 10px 24px -8px rgba(15, 44, 89, 0.22);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 14px;
        ">
            <div>
                <div style="color:#93C5FD; font-size:11px; font-weight:800; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:4px;">
                    LifeNet International Kenya · Financial Solvency &amp; Sustainability
                </div>
                <h2 style="color:#FFFFFF; font-size:23px; font-weight:800; margin:0 0 4px 0; line-height:1.25;">
                    💼 Financial Performance &amp; Operational Breakeven Analytics (FY2026)
                </h2>
                <p style="color:#CBD5E1; font-size:13.5px; margin:0;">
                    Monitoring health center operating income, cost-coverage breakeven capacity, deficit exposure, and MoniTrac reporting compliance across 38 partner facilities.
                </p>
            </div>
            <div style="
                background: rgba(255,255,255,0.12);
                border: 1px solid rgba(255,255,255,0.22);
                border-radius: 20px;
                padding: 7px 15px;
                color: #F8FAFC;
                font-size: 12px;
                font-weight: 700;
                white-space: nowrap;
            ">
                ● MoniTrac FY2026 Live Ledger
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_fin_monthly = fa.get_monthly_finance_summary()
    df_fin_fac = fa.get_facility_finance_breakdown()

    if df_fin_monthly.empty or df_fin_fac.empty:
        st.warning("No financial reporting records found for FY2026.")
        return

    total_hfs = len(df_fin_fac)
    tot_net_rev = float(df_fin_monthly["Revenue"].sum())
    tot_net_exp = float(df_fin_monthly["Expense"].sum())
    net_surplus = tot_net_rev - tot_net_exp
    margin_pct = (net_surplus / tot_net_rev * 100.0) if tot_net_rev > 0 else 0.0

    df_solvent = df_fin_fac[df_fin_fac["Status"] == "Surplus / Breakeven"].sort_values(
        by="Net_Margin", ascending=False
    )
    df_deficit = df_fin_fac[df_fin_fac["Status"] == "Operating Deficit"].sort_values(
        by="Net_Margin", ascending=True
    )
    df_unreported = df_fin_fac[df_fin_fac["Months_Reported"] == 0].sort_values(by="Facility")
    df_partial = df_fin_fac[
        (df_fin_fac["Missing_Months_Count"] > 0) & (df_fin_fac["Months_Reported"] > 0)
    ].sort_values(by="Missing_Months_Count", ascending=False)

    breakeven_count = len(df_solvent)
    deficit_fac_count = len(df_deficit)
    zero_sub_count = len(df_unreported)
    solvent_share = (breakeven_count / total_hfs * 100.0) if total_hfs > 0 else 0.0

    # 1. Executive KPI Scorecard Strip
    surplus_accent = "#0D9488" if net_surplus >= 0 else "#C8102E"
    surplus_badge_bg = "#ECFDF5" if net_surplus >= 0 else "#FEF2F2"
    surplus_badge_fg = "#047857" if net_surplus >= 0 else "#B91C1C"

    st.markdown(
        f"""
        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:16px; margin-bottom:20px;">
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:4px solid #0F2C59; border-radius:12px; padding:16px 18px; box-shadow:0 4px 12px rgba(15,44,89,0.05);">
                <div style="color:#64748B; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">Total Operating Income</div>
                <div style="color:#0F2C59; font-size:23px; font-weight:800; margin:6px 0 6px 0; white-space:nowrap;">Ksh {tot_net_rev/1e6:,.2f}M</div>
                <span style="background:#EFF6FF; color:#1D4ED8; font-size:11.5px; font-weight:700; padding:3px 9px; border-radius:12px;">{tot_net_rev:,.0f} Ksh Gross</span>
            </div>
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:4px solid #C8102E; border-radius:12px; padding:16px 18px; box-shadow:0 4px 12px rgba(15,44,89,0.05);">
                <div style="color:#64748B; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">Total Expenditure</div>
                <div style="color:#0F172A; font-size:23px; font-weight:800; margin:6px 0 6px 0; white-space:nowrap;">Ksh {tot_net_exp/1e6:,.2f}M</div>
                <span style="background:#FEF2F2; color:#B91C1C; font-size:11.5px; font-weight:700; padding:3px 9px; border-radius:12px;">{tot_net_exp:,.0f} Ksh Outflow</span>
            </div>
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:4px solid {surplus_accent}; border-radius:12px; padding:16px 18px; box-shadow:0 4px 12px rgba(15,44,89,0.05);">
                <div style="color:#64748B; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">Net Margin Buffer</div>
                <div style="color:{surplus_accent}; font-size:23px; font-weight:800; margin:6px 0 6px 0; white-space:nowrap;">{'+' if net_surplus >= 0 else ''}Ksh {net_surplus/1e6:,.2f}M</div>
                <span style="background:{surplus_badge_bg}; color:{surplus_badge_fg}; font-size:11.5px; font-weight:700; padding:3px 9px; border-radius:12px;">{margin_pct:.1f}% Portfolio Margin</span>
            </div>
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:4px solid #2563EB; border-radius:12px; padding:16px 18px; box-shadow:0 4px 12px rgba(15,44,89,0.05);">
                <div style="color:#64748B; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">Breakeven Solvency</div>
                <div style="color:#0F2C59; font-size:23px; font-weight:800; margin:6px 0 6px 0; white-space:nowrap;">{breakeven_count} / {total_hfs} Solvent</div>
                <span style="background:#FFFBEB; color:#B45309; font-size:11.5px; font-weight:700; padding:3px 9px; border-radius:12px;">{solvent_share:.1f}% · {deficit_fac_count} Deficit · {zero_sub_count} Unrep.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Executive Layered Area Chart (Income vs. Expenditure) & Live M&E Narrative
    col_chart, col_narrative = st.columns([1.62, 1.0], gap="medium")

    with col_chart:
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:12px 12px 0 0; padding:14px 18px 6px 18px; border-bottom:none;">
                <div style="text-align:center; color:#0F172A; font-size:17px; font-weight:800;">LNI Partner HFs' FY2026 Monthly Income and Expenditure</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        fig_area = go.Figure()
        fig_area.add_trace(
            go.Scatter(
                x=df_fin_monthly["Month"],
                y=df_fin_monthly["Expense"],
                mode="lines",
                name="Expenditure",
                line=dict(width=1.5, color="#E61C24"),
                fill="tozeroy",
                fillcolor="#E61C24",
                hovertemplate="<b>%{x} Expenditure</b>: Ksh %{y:,.0f}<extra></extra>",
            )
        )
        fig_area.add_trace(
            go.Scatter(
                x=df_fin_monthly["Month"],
                y=df_fin_monthly["Revenue"],
                mode="lines",
                name="Income",
                line=dict(width=1.5, color="#0A2540"),
                fill="tonexty",
                fillcolor="#0A2540",
                hovertemplate="<b>%{x} Income</b>: Ksh %{y:,.0f}<extra></extra>",
            )
        )

        fig_area.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            height=442,
            font=dict(family="Inter", color="#0F172A", size=12),
            xaxis=dict(
                showgrid=False,
                linecolor="#64748B",
                linewidth=1.5,
                tickfont=dict(color="#0F172A", size=12, weight="bold"),
                title=dict(text="<b>Month</b>", font=dict(size=14, color="#0F172A")),
            ),
            yaxis=dict(
                title=dict(text="<b>Amount (Ksh)</b>", font=dict(size=14, color="#0F172A")),
                showgrid=False,
                linecolor="#64748B",
                linewidth=1.5,
                tickfont=dict(color="#0F172A", size=12, weight="bold"),
                tickformat=",d",
            ),
            legend=dict(
                title=dict(text="<b>Type</b>", font=dict(size=13, color="#0F172A")),
                font=dict(color="#0F172A", size=12, weight="bold"),
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02,
            ),
            margin=dict(l=40, r=90, t=12, b=40),
        )
        st.plotly_chart(fig_area, use_container_width=True)

    with col_narrative:
        top1_name = df_solvent.iloc[0]["Facility"] if len(df_solvent) > 0 else "N/A"
        top1_val = df_solvent.iloc[0]["Net_Margin"] / 1e6 if len(df_solvent) > 0 else 0.0
        top2_name = df_solvent.iloc[1]["Facility"] if len(df_solvent) > 1 else "N/A"
        top2_val = df_solvent.iloc[1]["Net_Margin"] / 1e6 if len(df_solvent) > 1 else 0.0

        first_m = df_fin_monthly.iloc[0]
        last_m = df_fin_monthly.iloc[-1]
        unrep_names = (
            ", ".join(
                df_unreported["Facility"]
                .str.replace(" Health Centre| Healthcare Centre| Mission", "", regex=True)
                .tolist()
            )
            or "None"
        )

        st.markdown(
            f"""
            <div style="
                background: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-left: 5px solid #0F2C59;
                border-radius: 12px;
                padding: 20px 22px;
                height: 492px;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-shadow: 0 4px 12px rgba(15,44,89,0.05);
            ">
                <div>
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
                        <h4 style="color:#0F2C59; margin:0; font-size:15.5px; font-weight:800;">🔍 M&amp;E Executive Financial Brief</h4>
                        <span style="background:#F1F5F9; color:#0F2C59; font-size:10.5px; font-weight:700; padding:3px 8px; border-radius:8px;">LIVE SYNTHESIS</span>
                    </div>
                    <ul style="color:#1E293B; font-size:13px; line-height:1.58; padding-left:18px; margin:0;">
                        <li style="margin-bottom:9px;"><b>Breakeven Solvency:</b> <b>{breakeven_count} of {total_hfs} facilities ({solvent_share:.1f}%)</b> generate positive operating surpluses, led by <i>{top1_name} (+{top1_val:.1f}M Ksh)</i> and <i>{top2_name} (+{top2_val:.1f}M Ksh)</i>.</li>
                        <li style="margin-bottom:9px;"><b>Aggregate Surplus Buffer:</b> Portfolio revenue exceeds expenditure by <b>+{net_surplus/1e6:.1f}M Ksh</b> ({margin_pct:.1f}% net margin across reported periods).</li>
                        <li style="margin-bottom:9px;"><b>Deficit Vulnerability:</b> <b>{deficit_fac_count} facilities ({deficit_fac_count/total_hfs*100:.1f}%)</b> operate at a cumulative net deficit, requiring targeted cost-containment &amp; tariff review.</li>
                        <li style="margin-bottom:9px;"><b>Reporting Attrition:</b> Monthly volume drop reflects reporting lag from <b>{int(first_m['Reporting_HFs'])} active HFs in {first_m['Month']}</b> to <b>{int(last_m['Reporting_HFs'])} HFs in {last_m['Month']}</b>.</li>
                        <li><b>Zero-Disclosure Audit:</b> <b>{zero_sub_count} facilities ({zero_sub_count/total_hfs*100:.1f}%)</b> have zero 2026 financial submissions (<i>{unrep_names}</i>).</li>
                    </ul>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px; font-size:11.5px; color:#475569;">
                    <b style="color:#0F2C59;">DDIU Action:</b> Prioritize Q3/Q4 MoniTrac ledger reconciliation for the {len(df_partial)} partial-reporting and {zero_sub_count} unreported facilities.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border:none; border-top:1px solid #CBD5E1; margin:20px 0;'>", unsafe_allow_html=True)

    # 3. Dual Facility View: Breakeven/Deficit Ranking & Light-Mode Navy Disclosure Audit Table
    c_fac_chart, c_audit = st.columns([1.08, 1.12], gap="medium")

    with c_fac_chart:
        fac_view_type = st.radio(
            "Select Facility Solvency Cohort:",
            [
                f"✅ Breaking Even / Surplus ({breakeven_count} HFs)",
                f"🚨 Operating Deficit ({deficit_fac_count} HFs)",
            ],
            horizontal=True,
            key="fin_cohort_radio",
        )

        if "Breaking Even" in fac_view_type:
            st.markdown(
                "<div style='color:#0F2C59; font-size:15px; font-weight:800; margin:6px 0 8px 0;'>✅ Top 10 Solvent Facilities (Net Operating Surplus)</div>",
                unsafe_allow_html=True,
            )
            df_top_surplus = df_solvent.head(10)
            max_s = float(df_top_surplus["Net_Margin"].max()) if not df_top_surplus.empty else 1.0

            fig_fac = go.Figure(
                go.Bar(
                    x=df_top_surplus["Net_Margin"],
                    y=df_top_surplus["Facility"],
                    orientation="h",
                    text=[
                        f"+{m/1e6:,.2f}M Ksh ({c:.0f}%)"
                        for m, c in zip(
                            df_top_surplus["Net_Margin"],
                            df_top_surplus["Cost_Coverage_Pct"],
                        )
                    ],
                    textposition="outside",
                    textfont=dict(size=11, color="#0F2C59", family="Inter"),
                    marker_color="#0F2C59",
                    hovertemplate="<b>%{y}</b><br>Surplus: Ksh %{x:,.0f}<extra></extra>",
                )
            )
            fig_fac.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                height=440,
                font=dict(family="Inter", color="#0F172A"),
                xaxis=dict(
                    range=[0, max_s * 1.44],
                    showgrid=True,
                    gridcolor="#F1F5F9",
                    tickformat="~s",
                    tickfont=dict(color="#334155", size=11),
                ),
                yaxis=dict(
                    autorange="reversed",
                    tickfont=dict(color="#0F172A", size=11),
                ),
                margin=dict(l=210, r=30, t=10, b=24),
            )
            st.plotly_chart(fig_fac, use_container_width=True)
        else:
            st.markdown(
                "<div style='color:#B91C1C; font-size:15px; font-weight:800; margin:6px 0 8px 0;'>🚨 Operating Deficit Facilities (Cost Exceeds Income)</div>",
                unsafe_allow_html=True,
            )
            df_def_top = df_deficit.head(10)
            max_d = float(df_def_top["Net_Margin"].abs().max()) if not df_def_top.empty else 1.0

            fig_fac = go.Figure(
                go.Bar(
                    x=df_def_top["Net_Margin"].abs(),
                    y=df_def_top["Facility"],
                    orientation="h",
                    text=[
                        f"-{abs(m)/1e6:,.2f}M Ksh ({d} def mos)"
                        for m, d in zip(
                            df_def_top["Net_Margin"], df_def_top["Deficit_Months"]
                        )
                    ],
                    textposition="outside",
                    textfont=dict(size=11, color="#B91C1C", family="Inter"),
                    marker_color="#C8102E",
                    hovertemplate="<b>%{y}</b><br>Deficit: -Ksh %{x:,.0f}<extra></extra>",
                )
            )
            fig_fac.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                height=440,
                font=dict(family="Inter", color="#0F172A"),
                xaxis=dict(
                    range=[0, max_d * 1.48],
                    showgrid=True,
                    gridcolor="#F1F5F9",
                    tickformat="~s",
                    tickfont=dict(color="#334155", size=11),
                ),
                yaxis=dict(
                    autorange="reversed",
                    tickfont=dict(color="#0F172A", size=11),
                ),
                margin=dict(l=210, r=30, t=10, b=24),
            )
            st.plotly_chart(fig_fac, use_container_width=True)

    with c_audit:
        st.markdown(
            f"<div style='color:#0F2C59; font-size:15.5px; font-weight:800; margin-bottom:2px;'>⚠️ Facility Financial Disclosure Audit &amp; Missing Months</div>"
            f"<div style='color:#64748B; font-size:12px; margin-bottom:8px;'>Submission completeness audit across all {total_hfs} partner facilities</div>",
            unsafe_allow_html=True,
        )

        audit_filter = st.radio(
            "Filter Audit Scope:",
            [
                f"100% Unreported ({zero_sub_count} HFs)",
                f"Partial Submissions ({len(df_partial)} HFs)",
                f"All {total_hfs} Facilities",
            ],
            horizontal=True,
            key="fin_audit_radio",
        )

        if "100% Unreported" in audit_filter:
            df_show = df_unreported
        elif "Partial Submissions" in audit_filter:
            df_show = df_partial
        else:
            df_show = df_fin_fac.sort_values(
                by=["Missing_Months_Count", "Facility"], ascending=[False, True]
            )

        rows_html = []
        for idx, (_, r) in enumerate(df_show.iterrows()):
            bg = "#FFFFFF" if idx % 2 == 0 else "#F8FAFC"
            miss_cnt = int(r["Missing_Months_Count"])
            rep_cnt = int(r["Months_Reported"])
            if rep_cnt == 0:
                badge = f"<span style='background:#FEF2F2;color:#B91C1C;border:1px solid #FECACA;padding:2px 8px;border-radius:10px;font-weight:700;font-size:11px;'>{miss_cnt} Missing (0%)</span>"
            elif miss_cnt > 0:
                badge = f"<span style='background:#FFFBEB;color:#B45309;border:1px solid #FDE68A;padding:2px 8px;border-radius:10px;font-weight:700;font-size:11px;'>{miss_cnt} Missing</span>"
            else:
                badge = "<span style='background:#ECFDF5;color:#047857;border:1px solid #A7F3D0;padding:2px 8px;border-radius:10px;font-weight:700;font-size:11px;'>Complete</span>"

            rows_html.append(
                f"<tr style='background:{bg};border-bottom:1px solid #E2E8F0;'>"
                f"<td style='padding:8px 10px;font-weight:600;color:#0F172A;white-space:nowrap;'>{r['Facility']}</td>"
                f"<td style='padding:8px 10px;text-align:center;font-weight:700;color:#0F2C59;'>{rep_cnt}</td>"
                f"<td style='padding:8px 10px;text-align:center;white-space:nowrap;'>{badge}</td>"
                f"<td style='padding:8px 10px;color:#475569;font-size:11.5px;'>{r['Missing_Months_List']}</td>"
                f"</tr>"
            )

        table_html = f"""
        <div style="max-height:335px; overflow-y:auto; border:1px solid #CBD5E1; border-radius:10px; background:#FFFFFF; box-shadow:0 2px 8px rgba(15,44,89,0.04);">
            <table style="width:100%; border-collapse:collapse; font-family:Inter,sans-serif; font-size:12.5px;">
                <thead style="position:sticky; top:0; z-index:2; background:#0F2C59; color:#FFFFFF;">
                    <tr>
                        <th style="padding:9px 10px; text-align:left; font-weight:700;">Health Facility</th>
                        <th style="padding:9px 10px; text-align:center; font-weight:700;">Reported</th>
                        <th style="padding:9px 10px; text-align:center; font-weight:700;">Audit Status</th>
                        <th style="padding:9px 10px; text-align:left; font-weight:700;">Specific Missing Months</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows_html)}
                </tbody>
            </table>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)

        c_note, c_dl = st.columns([2.2, 1.0])
        with c_note:
            st.markdown(
                """
                <div style="background:#FFFBEB; border:1px solid #FCD34D; border-left:4px solid #D97706; border-radius:8px; padding:9px 12px; margin-top:10px;">
                    <p style="color:#92400E; font-size:12px; font-weight:600; margin:0;">
                        ⚠️ <b>M&amp;E Compliance Action:</b> Late-Q3 reporting attrition detected. Issue immediate MoniTrac submission reminders prior to year-end audits.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c_dl:
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            st.download_button(
                "📥 Export Audit CSV",
                data=df_show.to_csv(index=False).encode("utf-8"),
                file_name="LifeNet_FY2026_Financial_Disclosure_Audit.csv",
                mime="text/csv",
                use_container_width=True,
            )


if __name__ == "__main__":
    st.set_page_config(
        page_title="LifeNet Kenya · Financial Executive Preview",
        page_icon="💼",
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
    render_financial_performance_view()
