import streamlit as st


def render_executive_header_and_nav(tabs, focus_year, comparison_year, selected_period):
    st.markdown(
        """
        <style>
        /* Tighten top page padding for a crisp executive masthead */
        .block-container {
            padding-top: 2.6rem !important;
        }

        /* High-contrast Sign Out button styling */
        div[data-testid="stButton"] > button[kind="secondary"] {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            padding: 0.45rem 0.9rem !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06) !important;
            transition: all 0.15s ease !important;
        }
        div[data-testid="stButton"] > button[kind="secondary"]:hover {
            background-color: #FEF2F2 !important;
            color: #991B1B !important;
            border-color: #FCA5A5 !important;
        }

        /* Transform st.radio navigation into executive segmented pill tabs */
        div[data-testid="stRadio"] > div[role="radiogroup"] {
            background: #F1F5F9 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 12px !important;
            padding: 6px !important;
            gap: 6px !important;
            display: flex !important;
            flex-wrap: wrap !important;
            box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.04) !important;
        }

        div[data-testid="stRadio"] > label { display: none !important; }
        div[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child { display: none !important; }
        /* Hide dot */
        div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child, div[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {
            display: none !important;
        }

        /* Base pill style */
        div[data-testid="stRadio"] div[role="radiogroup"] label {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 7px 13px !important;
            margin: 0 !important;
            cursor: pointer !important;
            transition: all 0.15s ease !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label p {
            color: #334155 !important;
            font-size: 12.5px !important;
            font-weight: 600 !important;
            margin: 0 !important;
            white-space: nowrap !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            border-color: #94A3B8 !important;
            background: #F8FAFC !important;
        }

        /* Active selected tab pill */
        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(135deg, #C8102E 0%, #9F1239 100%) !important;
            border-color: #C8102E !important;
            box-shadow: 0 3px 8px rgba(200, 16, 46, 0.22) !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([4.2, 1.15], gap="medium")

    with col_left:
        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
                        border:1px solid #CBD5E1; border-left:5px solid #C8102E;
                        border-radius:12px; padding:22px 26px;
                        box-shadow:0 2px 8px rgba(15, 23, 42, 0.04);">
                <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:6px;">
                    <span style="font-size:10.5px; font-weight:800; letter-spacing:1.1px;
                                 color:#C8102E; text-transform:uppercase;">
                        LIFENET INTERNATIONAL • HEALTH SYSTEMS INTELLIGENCE
                    </span>
                    <span style="background:#DCFCE7; color:#166534; border:1px solid #86EFAC;
                                 font-size:10px; font-weight:800; padding:2px 8px;
                                 border-radius:999px; letter-spacing:0.4px;">
                        ● EXECUTIVE SESSION ACTIVE
                    </span>
                </div>
                <div style="font-size:29px; font-weight:900; color:#0F172A;
                            letter-spacing:-0.4px; line-height:1.18; margin-bottom:4px;">
                    LifeNet Program Analytics &amp; Executive Dashboard
                </div>
                <div style="font-size:14px; font-weight:500; color:#475569; margin-bottom:14px;">
                    Network Comparative Performance &amp; Facility Intelligence
                    (<b style="color:#C8102E;">{focus_year} Focus</b> vs.
                    <b style="color:#334155;">{comparison_year} Baseline</b>)
                </div>
                <div style="border-top:1px solid #E2E8F0; padding-top:11px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;"><div style="display:flex; align-items:center; gap:9px;"><span style="background:#C8102E; color:#FFFFFF; font-size:10px; font-weight:800; padding:3px 9px; border-radius:4px; letter-spacing:0.8px; text-transform:uppercase;">🌍 OUR MISSION</span><span style="font-size:13.5px; font-weight:800; color:#0F172A; letter-spacing:0.2px;">Transforming Health Across Africa</span></div><span style="font-size:11.5px; font-weight:600; color:#64748B;">Evidence-Driven Quality • Sustainable Partner Health Facilities</span></div></div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        if st.button("🚪 Sign Out", key="btn_logout_native_clean", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

        st.markdown(
            f"""
            <div style="background:#1E293B; color:#FFFFFF; border-top:3px solid #C8102E; border-radius:10px;
                        padding:10px 14px; margin-top:6px;
                        box-shadow:0 2px 6px rgba(200, 16, 46, 0.16);">
                <div style="font-size:9.5px; font-weight:800; letter-spacing:0.9px;
                            color:#FCA5A5; text-transform:uppercase; margin-bottom:2px;">
                    REPORTING WINDOW
                </div>
                <div style="font-size:13.5px; font-weight:800; color:#FFFFFF; line-height:1.25;">
                    📅 {selected_period}
                </div>
                <div style="font-size:11px; color:#CBD5E1; margin-top:2px;">
                    Baseline: <b>{comparison_year}</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    active_tab = st.radio(
        "Navigation",
        options=tabs,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    return active_tab
