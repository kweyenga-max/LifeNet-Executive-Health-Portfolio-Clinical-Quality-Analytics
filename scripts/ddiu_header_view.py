import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import ddiu_report_generator as ddiu


def render_ddiu_top_section():
    """Render the Deep Navy executive header, high-contrast control bar, and Deep Navy KPI strip for DDIU."""
    st.markdown(
        """
        <style>
            /* High-contrast light selectbox & visible label/value for DDIU control bar */
            div[data-testid="stSelectbox"] label,
            div[data-testid="stSelectbox"] label p {
                color: #0F2C59 !important;
                -webkit-text-fill-color: #0F2C59 !important;
                font-weight: 700 !important;
                font-size: 12.5px !important;
            }
            div[data-testid="stSelectbox"] > div > div,
            div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
            div[data-testid="stSelectbox"] [data-baseweb="select"] span,
            div[data-testid="stSelectbox"] [data-baseweb="select"] div,
            div[data-testid="stSelectbox"] input {
                background-color: #FFFFFF !important;
                color: #0F2C59 !important;
                -webkit-text-fill-color: #0F2C59 !important;
                border-color: #CBD5E1 !important;
                border-radius: 10px !important;
                font-weight: 700 !important;
            }
            div[data-testid="stSelectbox"] svg {
                fill: #0F2C59 !important;
            }
            /* Crisp Deep Navy PDF Download Button with guaranteed white text */
            div[data-testid="stDownloadButton"] > button {
                background: linear-gradient(135deg, #0F2C59 0%, #1B4382 100%) !important;
                color: #FFFFFF !important;
                border: 1px solid #0F2C59 !important;
                border-radius: 10px !important;
                font-weight: 700 !important;
                font-size: 13.5px !important;
                padding: 10px 18px !important;
                box-shadow: 0 3px 10px rgba(15, 44, 89, 0.16) !important;
            }
            div[data-testid="stDownloadButton"] > button:hover {
                background: linear-gradient(135deg, #163E7A 0%, #0B2244 100%) !important;
                border-color: #38BDF8 !important;
            }
            div[data-testid="stDownloadButton"] > button p,
            div[data-testid="stDownloadButton"] > button span,
            div[data-testid="stDownloadButton"] > button div {
                color: #FFFFFF !important;
                -webkit-text-fill-color: #FFFFFF !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 1. Executive Deep Navy Header Banner
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0B2244 0%, #0F2C59 60%, #163E7A 100%);
            border-left: 5px solid #38BDF8;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 16px;
            box-shadow: 0 6px 18px rgba(15, 44, 89, 0.16);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 14px;
        ">
            <div>
                <div style="color:#93C5FD; font-size:11px; font-weight:800; letter-spacing:0.11em; text-transform:uppercase; margin-bottom:4px;">
                    LifeNet International Kenya · Integrated M&amp;E &amp; Quality Intelligence
                </div>
                <h2 style="color:#FFFFFF; font-size:22px; font-weight:800; margin:0 0 4px 0; line-height:1.25; letter-spacing:-0.01em;">
                    📑 Monthly Data Demand &amp; Information Use (DDIU) Executive Brief
                </h2>
                <p style="color:#E2E8F0; font-size:13px; margin:0;">
                    Synthesizing KHIS Patient Visits, MOH 711 Maternal/Newborn KPIs, DQA Audits &amp; MoniTrac Financials across 38 Active Facilities
                </p>
            </div>
            <div style="
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 20px;
                padding: 6px 14px;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 700;
                white-space: nowrap;
            ">
                <span style="color:#38BDF8; margin-right:5px;">●</span>15th-of-Month Cycle · 38 Sites
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. High-Contrast Reporting Period Selector & PDF Download Control Bar
    avail_periods = ddiu.get_available_reporting_periods()
    default_p = ddiu.default_ddiu_period()
    default_idx = avail_periods.index(default_p) if default_p in avail_periods else len(avail_periods) - 1

    c_p1, c_p2 = st.columns([1.45, 1.0], gap="medium")
    with c_p1:
        ddiu_period = st.selectbox(
            "Select Reporting Month (15th-of-Month Cycle):",
            options=avail_periods,
            index=default_idx,
            key="ddiu_period_select",
        )
    ddiu_data = ddiu.build_ddiu_dataset(ddiu_period)
    pdf_bytes = ddiu.generate_ddiu_pdf_bytes(ddiu_period)

    with c_p2:
        st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
        st.download_button(
            label=f"📥 Download LifeNet DDIU PDF ({ddiu_period})",
            data=pdf_bytes,
            file_name=f"LifeNet_DDIU_Report_{ddiu_period.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Compute KPI Values & Semantic Badges
    tot_pv = int(ddiu_data["tot_pv"])
    pv_mom = float(ddiu_data["pv_mom_pct"])
    pv_yoy = float(ddiu_data["pv_yoy_pct"])
    tot_del = int(ddiu_data["tot_del"])
    tot_lb = int(ddiu_data["tot_lb"])
    tot_sb = int(ddiu_data["tot_fsb"] + ddiu_data["tot_msb"])
    khis_rep = int(ddiu_data["khis_reporting"])
    fin_rep = int(ddiu_data["fin_reporting"])
    tot_fac = int(ddiu_data["total_facilities"])
    cov_pct = float(ddiu_data["cost_coverage"])
    tot_net = float(ddiu_data["tot_net"])

    pv_badge_bg = "#FEF2F2" if pv_mom < 0 else "#ECFDF5"
    pv_badge_bd = "#FECACA" if pv_mom < 0 else "#A7F3D0"
    pv_badge_fg = "#991B1B" if pv_mom < 0 else "#065F46"
    pv_arrow = "↓" if pv_mom < 0 else "↑"

    net_badge_bg = "#FEF2F2" if tot_net < 0 else "#ECFDF5"
    net_badge_bd = "#FECACA" if tot_net < 0 else "#A7F3D0"
    net_badge_fg = "#991B1B" if tot_net < 0 else "#065F46"
    net_arrow = "↓" if tot_net < 0 else "↑"

    # 4. Deep Navy Blue 4-Card KPI Strip
    st.markdown(
        f"""
        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:16px; margin-bottom:18px;">
            <div style="background:linear-gradient(145deg, #0B2244 0%, #0F2C59 100%); border:1px solid #1E40AF; border-top:3.5px solid #38BDF8; border-radius:12px; padding:16px 18px; box-shadow:0 4px 14px rgba(15,44,89,0.14);">
                <div style="color:#BFDBFE; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">Total Patient Visits</div>
                <div style="color:#FFFFFF; font-size:26px; font-weight:800; margin:6px 0; letter-spacing:-0.02em;">{tot_pv:,}</div>
                <span style="background:{pv_badge_bg}; border:1px solid {pv_badge_bd}; color:{pv_badge_fg}; font-size:11.5px; font-weight:700; padding:3px 9px; border-radius:6px;">
                    {pv_arrow} {pv_mom:+.1f}% MoM | {pv_yoy:+.1f}% YoY
                </span>
            </div>
            <div style="background:linear-gradient(145deg, #0B2244 0%, #0F2C59 100%); border:1px solid #1E40AF; border-top:3.5px solid #38BDF8; border-radius:12px; padding:16px 18px; box-shadow:0 4px 14px rgba(15,44,89,0.14);">
                <div style="color:#BFDBFE; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">Maternity Deliveries</div>
                <div style="color:#FFFFFF; font-size:26px; font-weight:800; margin:6px 0; letter-spacing:-0.02em;">{tot_del:,}</div>
                <span style="background:#ECFDF5; border:1px solid #A7F3D0; color:#065F46; font-size:11.5px; font-weight:700; padding:3px 9px; border-radius:6px;">
                    ↑ {tot_lb:,} Live Births | {tot_sb} SB
                </span>
            </div>
            <div style="background:linear-gradient(145deg, #0B2244 0%, #0F2C59 100%); border:1px solid #1E40AF; border-top:3.5px solid #38BDF8; border-radius:12px; padding:16px 18px; box-shadow:0 4px 14px rgba(15,44,89,0.14);">
                <div style="color:#BFDBFE; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">Reporting Completeness</div>
                <div style="color:#FFFFFF; font-size:26px; font-weight:800; margin:6px 0; letter-spacing:-0.02em;">KHIS {khis_rep}/{tot_fac}</div>
                <span style="background:#EFF6FF; border:1px solid #BFDBFE; color:#0F2C59; font-size:11.5px; font-weight:700; padding:3px 9px; border-radius:6px;">
                    Finance {fin_rep}/{tot_fac} HFs
                </span>
            </div>
            <div style="background:linear-gradient(145deg, #0B2244 0%, #0F2C59 100%); border:1px solid #1E40AF; border-top:3.5px solid #38BDF8; border-radius:12px; padding:16px 18px; box-shadow:0 4px 14px rgba(15,44,89,0.14);">
                <div style="color:#BFDBFE; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em;">Network Cost Coverage</div>
                <div style="color:#FFFFFF; font-size:26px; font-weight:800; margin:6px 0; letter-spacing:-0.02em;">{cov_pct:.1f}%</div>
                <span style="background:{net_badge_bg}; border:1px solid {net_badge_bd}; color:{net_badge_fg}; font-size:11.5px; font-weight:700; padding:3px 9px; border-radius:6px;">
                    {net_arrow} Net KES {tot_net:,.0f}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return ddiu_period, ddiu_data


if __name__ == "__main__":
    st.set_page_config(page_title="DDIU Executive Header Preview", page_icon="📑", layout="wide")
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            html, body, [class*="css"], .stApp {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                background-color: #F8FAFC !important;
                color: #0F2C59 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    render_ddiu_top_section()
