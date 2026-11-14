import pandas as pd
import streamlit as st


def render_qsc_navy_header():
    """Inject Deep Navy (#0F2C59) executive styling scoped to QSC and render the masthead."""
    st.markdown(
        """
        <style>
        .qsc-navy-hero {
            background: linear-gradient(135deg, #091E3E 0%, #0F2C59 55%, #1E3A8A 100%);
            border-radius: 12px;
            padding: 20px 26px;
            border-bottom: 3px solid #D97706;
            box-shadow: 0 8px 24px rgba(15, 44, 89, 0.16);
            margin-bottom: 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }
        .qsc-navy-kicker {
            color: #93C5FD;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.4px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .qsc-navy-title {
            color: #FFFFFF;
            font-size: 22px;
            font-weight: 800;
            letter-spacing: -0.3px;
            margin: 0;
        }
        .qsc-navy-sub {
            color: #CBD5E1;
            font-size: 13px;
            margin-top: 4px;
        }
        .qsc-navy-pill {
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(147, 197, 253, 0.35);
            color: #F8FAFC;
            font-size: 11.5px;
            font-weight: 700;
            padding: 6px 14px;
            border-radius: 999px;
            letter-spacing: 0.4px;
        }

        /* High-Contrast Dropdown Labels & Light Selectboxes */
        div[data-testid="stSelectbox"] label,
        div[data-testid="stRadio"] > label {
            color: #0F2C59 !important;
            font-size: 12px !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.6px !important;
        }
        [data-testid="stMain"] div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            border: 1.5px solid #0F2C59 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(15, 44, 89, 0.08) !important;
        }
        [data-testid="stMain"] div[data-testid="stSelectbox"] [data-baseweb="select"] * {
            color: #0F2C59 !important;
            -webkit-text-fill-color: #0F2C59 !important;
            font-weight: 700 !important;
            opacity: 1 !important;
        }
        [data-testid="stMain"] div[data-testid="stSelectbox"] svg {
            fill: #0F2C59 !important;
            color: #0F2C59 !important;
        }
        div[data-baseweb="popover"] div[role="listbox"],
        div[data-baseweb="popover"] ul[data-baseweb="menu"] {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
        }
        div[data-baseweb="popover"] li[role="option"],
        div[data-baseweb="popover"] li[role="option"] * {
            background-color: #FFFFFF !important;
            color: #0F2C59 !important;
            -webkit-text-fill-color: #0F2C59 !important;
            font-weight: 600 !important;
        }
        div[data-baseweb="popover"] li[role="option"]:hover,
        div[data-baseweb="popover"] li[role="option"]:hover * {
            background-color: #EFF6FF !important;
            color: #0F2C59 !important;
        }
        div[data-testid="stRadio"] > div[role="radiogroup"] label > div:first-child {
            display: none !important;
        }

        /* Deep Navy Segmented Radio Pills */
        div[data-testid="stRadio"] > div[role="radiogroup"] {
            background: #F1F5F9 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
            padding: 4px !important;
            gap: 6px !important;
        }
        div[data-testid="stRadio"] > div[role="radiogroup"] label {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 7px !important;
            padding: 6px 13px !important;
        }
        div[data-testid="stRadio"] > div[role="radiogroup"] label p {
            color: #1E293B !important;
            font-weight: 700 !important;
            font-size: 12.5px !important;
        }
        div[data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) {
            background: #0F2C59 !important;
            border-color: #0F2C59 !important;
            box-shadow: 0 2px 8px rgba(15, 44, 89, 0.25) !important;
        }
        div[data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) p {
            color: #FFFFFF !important;
        }

        /* Executive Navy KPI Cards */
        .qsc-kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: 4px solid #0F2C59;
            border-radius: 10px;
            padding: 16px 18px;
            box-shadow: 0 2px 10px rgba(15, 44, 89, 0.05);
        }
        .qsc-kpi-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            color: #475569;
            margin-bottom: 8px;
        }
        .qsc-kpi-val {
            font-size: 28px;
            font-weight: 800;
            color: #0F2C59;
            line-height: 1.1;
            margin-bottom: 10px;
        }
        .qsc-kpi-pill {
            display: inline-block;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 999px;
            background: #ECFDF5;
            color: #065F46;
            border: 1px solid #A7F3D0;
        }

        /* Navy Statistical Strip Banner */
        .qsc-stat-strip {
            background: linear-gradient(90deg, #0F2C59 0%, #1E3A8A 100%);
            color: #FFFFFF;
            border-radius: 10px;
            padding: 16px 22px;
            margin-bottom: 16px;
            border-left: 5px solid #D97706;
            box-shadow: 0 4px 14px rgba(15, 44, 89, 0.14);
        }
        .qsc-stat-strip h4 {
            color: #FFFFFF !important;
            margin: 0 0 6px 0 !important;
            font-size: 16px !important;
            font-weight: 800 !important;
        }
        .qsc-stat-strip p {
            color: #E2E8F0 !important;
            margin: 0 !important;
            font-size: 13.5px !important;
        }
        .qsc-stat-badge {
            background: rgba(16, 185, 129, 0.22);
            border: 1px solid #34D399;
            color: #6EE7B7;
            padding: 2px 9px;
            border-radius: 6px;
            font-weight: 800;
        }

        /* Executive M&E Huddle Card */
        .qsc-huddle-card {
            background: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-left: 4px solid #0F2C59;
            border-radius: 10px;
            padding: 18px 20px;
            height: 100%;
        }

        /* Light-Mode Executive Benchmark Table */
        .qsc-matrix-wrap {
            max-height: 460px;
            overflow-y: auto;
            border: 1px solid #CBD5E1;
            border-radius: 10px;
            background: #FFFFFF;
            box-shadow: 0 3px 12px rgba(15, 44, 89, 0.06);
        }
        .qsc-matrix {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            color: #0F172A;
        }
        .qsc-matrix thead th {
            position: sticky;
            top: 0;
            z-index: 2;
            background: #0F2C59;
            color: #FFFFFF;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.6px;
            padding: 12px 14px;
            text-align: left;
            border-bottom: 2px solid #D97706;
        }
        .qsc-matrix thead th.num, .qsc-matrix tbody td.num {
            text-align: right;
        }
        .qsc-matrix tbody tr:nth-child(even) {
            background: #F8FAFC;
        }
        .qsc-matrix tbody tr:hover {
            background: #EFF6FF;
        }
        .qsc-matrix tbody td {
            padding: 10px 14px;
            border-bottom: 1px solid #E2E8F0;
            vertical-align: middle;
        }
        .qsc-bar-bg {
            width: 90px;
            height: 7px;
            background: #E2E8F0;
            border-radius: 999px;
            display: inline-block;
            vertical-align: middle;
            margin-right: 8px;
            overflow: hidden;
        }
        .qsc-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #0F2C59, #2563EB);
            border-radius: 999px;
        }
        .tier-pill {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11.5px;
            font-weight: 700;
        }
        .tier-gold { background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }
        .tier-silver { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
        .tier-red { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
        </style>

        <div class="qsc-navy-hero">
            <div>
                <div class="qsc-navy-kicker">Clinical &amp; Management Quality Assurance</div>
                <div class="qsc-navy-title">Quality Scorecard (QSC) &amp; Capacity Building Evaluation</div>
                <div class="qsc-navy-sub">Paired pre/post training competency benchmarks, cohort learning velocity, and facility mentorship priorities</div>
            </div>
            <div class="qsc-navy-pill">QSC EXECUTIVE SUITE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_qsc_facility_matrix(df_fac_perf: pd.DataFrame, fac_col_name: str, curriculum_label: str):
    """Render a light-mode executive facility benchmark table with inline score bars and CSV export."""
    df_sorted = df_fac_perf.sort_values(by="Endline_Avg", ascending=False).reset_index(drop=True)

    hdr_l, hdr_r = st.columns([3, 1])
    with hdr_l:
        st.markdown(
            f"<div style='font-size:16px; font-weight:800; color:#0F2C59; margin-top:4px;'>"
            f"Facility Quality Benchmark Registry ({len(df_sorted)} Partner Facilities)</div>",
            unsafe_allow_html=True,
        )
    with hdr_r:
        csv_bytes = df_sorted.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇ Export Benchmark CSV",
            data=csv_bytes,
            file_name=f"lifenet_qsc_benchmark_{curriculum_label.lower()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    rows_html = []
    for idx, row in df_sorted.iterrows():
        fac = str(row[fac_col_name])
        base_v = float(row["Baseline_Avg"])
        end_v = float(row["Endline_Avg"])
        gain_v = float(row["Net_Gain"])
        tier_txt = str(row["Quality_Tier"])
        tier_cls = "tier-gold" if end_v >= 80 else ("tier-silver" if end_v >= 60 else "tier-red")
        gain_color = "#059669" if gain_v >= 0 else "#DC2626"
        bar_w = max(0, min(100, end_v))

        rows_html.append(
            f"<tr>"
            f"<td style='font-weight:700; color:#64748B; width:44px;'>#{idx + 1}</td>"
            f"<td style='font-weight:700; color:#0F172A;'>{fac}</td>"
            f"<td class='num' style='color:#475569;'>{base_v:.1f}%</td>"
            f"<td class='num'>"
            f"<span class='qsc-bar-bg'><span class='qsc-bar-fill' style='width:{bar_w:.1f}%;'></span></span>"
            f"<b style='color:#0F2C59;'>{end_v:.1f}%</b>"
            f"</td>"
            f"<td class='num' style='font-weight:800; color:{gain_color};'>{gain_v:+.1f} pts</td>"
            f"<td><span class='tier-pill {tier_cls}'>{tier_txt}</span></td>"
            f"</tr>"
        )

    table_html = f"""
    <div class="qsc-matrix-wrap">
        <table class="qsc-matrix">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Health Facility Name</th>
                    <th class="num">Baseline Avg</th>
                    <th class="num">Endline Avg Score</th>
                    <th class="num">Net Gain</th>
                    <th>Quality Benchmark Tier</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)
