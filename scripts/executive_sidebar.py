import os
import streamlit as st


def render_executive_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <style>
            /* Eliminate excess top blank gap in sidebar */
            section[data-testid="stSidebar"] > div:first-child {
                padding-top: 0.75rem !important;
            }
            section[data-testid="stSidebar"] .block-container {
                padding-top: 0.5rem !important;
                padding-bottom: 1.2rem !important;
            }
            .ln-sb-card {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 10px;
                padding: 12px 13px 10px 13px;
                margin-bottom: 12px;
            }
            .ln-sb-eyebrow {
                font-size: 10.5px;
                font-weight: 800;
                letter-spacing: 0.9px;
                color: #FCA5A5;
                text-transform: uppercase;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Brand Logo Container
        logo_png = os.path.join("assets", "Logo.png")
        st.markdown(
            '<div style="border-bottom:2px solid #C8102E; padding-bottom:10px; margin-bottom:14px;">',
            unsafe_allow_html=True,
        )
        if os.path.exists(logo_png):
            st.image(logo_png, use_container_width=True)
        else:
            st.markdown(
                """
                <div style="text-align:center; padding:6px 0;">
                    <div style="color:#FFFFFF; font-size:18px; font-weight:900; letter-spacing:0.5px;">
                        LN • LIFENET INTERNATIONAL
                    </div>
                    <div style="color:#CBD5E1; font-size:10px; font-weight:600; letter-spacing:0.8px;">
                        TRANSFORMING HEALTH ACROSS AFRICA
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Section 1: Side-by-Side Year Comparison Pair
        st.markdown(
            """
            <div class="ln-sb-card">
                <div class="ln-sb-eyebrow">📅 Year &amp; Comparison Pair</div>
            """,
            unsafe_allow_html=True,
        )
        y_col1, y_col2 = st.columns(2, gap="small")
        with y_col1:
            focus_year = st.selectbox("Focus Year", ["2026", "2025"], index=0)
        with y_col2:
            comparison_year = st.selectbox(
                "Baseline",
                ["2025", "2026"],
                index=0 if focus_year == "2026" else 1,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Section 2: Granularity & Period Selection
        st.markdown(
            """
            <div class="ln-sb-card">
                <div class="ln-sb-eyebrow">🔀 Reporting Granularity</div>
            """,
            unsafe_allow_html=True,
        )
        time_frame_type = st.selectbox(
            "Granularity Level",
            ["Monthly / Multi-Month", "Quarterly", "Biannual (H1/H2)", "Annual Summary"],
        )

        all_months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ]

        if time_frame_type == "Monthly / Multi-Month":
            chosen_months = st.multiselect(
                "Select Month(s)",
                options=all_months,
                default=["October"],
                help="Pick a single month or combine any custom months (e.g., Jan, Feb, Mar).",
            )
            if not chosen_months:
                st.warning("Select at least one month (defaulting to October).")
                chosen_months = ["October"]
            selected_months = [m for m in all_months if m in chosen_months]
            if len(selected_months) == 1:
                selected_period = f"{selected_months[0]} ({focus_year})"
            else:
                short_names = ", ".join(m[:3] for m in selected_months)
                selected_period = f"{short_names} ({focus_year})"
        elif time_frame_type == "Quarterly":
            selected_period = st.selectbox(
                "Select Quarter", ["Q1", "Q2", "Q3", "Q4"], index=2
            )
            selected_months = {
                "Q1": ["January", "February", "March"],
                "Q2": ["April", "May", "June"],
                "Q3": ["July", "August", "September"],
                "Q4": ["October", "November", "December"],
            }[selected_period]
            selected_period = f"{selected_period} ({focus_year})"
        elif time_frame_type == "Biannual (H1/H2)":
            selected_period = st.selectbox(
                "Select Half-Year", ["H1 (Jan - Jun)", "H2 (Jul - Dec)"]
            )
            selected_months = (
                ["January", "February", "March", "April", "May", "June"]
                if "H1" in selected_period
                else ["July", "August", "September", "October", "November", "December"]
            )
            selected_period = f"{selected_period} ({focus_year})"
        else:
            selected_period = f"Full Year ({focus_year})"
            selected_months = all_months

        st.markdown("</div>", unsafe_allow_html=True)

        # Section 3: Active Scope & System Readiness Summary Card
        m_count = len(selected_months)
        m_label = f"{m_count} month" if m_count == 1 else f"{m_count} months"
        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg, rgba(200,16,46,0.16) 0%, rgba(15,23,42,0.6) 100%);
                        border:1px solid rgba(252,165,165,0.28); border-left:3px solid #C8102E;
                        border-radius:10px; padding:11px 13px; margin-top:4px;">
                <div style="font-size:10px; font-weight:800; letter-spacing:0.8px;
                            color:#FCA5A5; text-transform:uppercase; margin-bottom:4px;">
                    ACTIVE SCOPE SUMMARY
                </div>
                <div style="font-size:12.5px; font-weight:700; color:#FFFFFF; line-height:1.35;">
                    {selected_period} vs. {comparison_year}
                </div>
                <div style="font-size:11px; color:#CBD5E1; margin-top:3px;">
                    Window: <b>{m_label}</b> • Mode: <b>YoY Delta</b>
                </div>
                <div style="margin-top:8px; padding-top:7px; border-top:1px solid rgba(255,255,255,0.10);
                            font-size:10.5px; font-weight:700; color:#86EFAC; display:flex; align-items:center; gap:6px;">
                    <span>●</span> <span>PORTFOLIO DATA READY</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return focus_year, comparison_year, time_frame_type, selected_months, selected_period
