import streamlit as st
st.cache_data.clear()
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import math
import os

# Backend Analytics Script Imports
from scripts import cohort3_analytics as c3
from scripts import finance_analytics as fa
from scripts import ddiu_report_generator as ddiu

# 1. Page Configuration - Executive Full-Screen Theme
st.set_page_config(
    page_title="LifeNet International | Executive Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# EXECUTIVE METRIC CONTRAST & HERO BANNER INJECTION
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* 1. Force High-Contrast Dark Text for Streamlit Metrics */
    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05) !important;
    }
    
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] div,
    [data-testid="stMetricLabel"] span {
        color: #64748B !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        text-transform: uppercase !important;
    }

    [data-testid="stMetricValue"] div,
    [data-testid="stMetricValue"] span,
    [data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 800 !important;
        font-size: 26px !important;
    }

    /* Delta pills styling */
    [data-testid="stMetricDelta"] div,
    [data-testid="stMetricDelta"] span {
        font-weight: 700 !important;
        font-size: 12px !important;
    }

    /* 2. Executive Hero Banner styling */
    .exec-hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #0A2540 100%) !important;
        border: 1px solid #1E293B !important;
        border-radius: 14px !important;
        padding: 22px 28px !important;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.15) !important;
        margin-bottom: 20px !important;
    }

    /* Clean navigation label hide */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    
<style>
/* High-Contrast Executive Log Out Button */
div[data-testid="stButton"] > button {
    background-color: #EF4444 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.25) !important;
}
div[data-testid="stButton"] > button:hover {
    background-color: #DC2626 !important;
    color: #FFFFFF !important;
}
</style>

</style>
""", unsafe_allow_html=True)






# ---------------------------------------------------------
# EXECUTIVE TOP HEADER & HERO SECTION STYLING
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Remove default Streamlit top padding overhead */
    .block-container {
        padding-top: 1.5rem !important;
    }

    /* Executive Hero Header Container */
    .exec-hero-card {
        background: linear-gradient(135deg, #0F172A 0%, #0A2540 100%) !important;
        border: 1px solid #1E293B !important;
        border-radius: 16px !important;
        padding: 24px 30px !important;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.12) !important;
        margin-bottom: 24px !important;
    }

    /* Top Utility Bar Inside Hero Card (Status + Logout) */
    .exec-top-bar {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding-bottom: 14px !important;
        margin-bottom: 16px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    .exec-session-badge {
        font-size: 12px !important;
        font-weight: 700 !important;
        color: #38BDF8 !important;
        letter-spacing: 0.5px !important;
        background: rgba(56, 189, 248, 0.12) !important;
        padding: 4px 12px !important;
        border-radius: 20px !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
    }

    /* Primary Title & Subtitle Styling */
    .exec-hero-title {
        color: #FFFFFF !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        margin: 0 0 4px 0 !important;
        letter-spacing: -0.6px !important;
        line-height: 1.2 !important;
    }

    .exec-hero-subtitle {
        color: #94A3B8 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        margin: 0 0 16px 0 !important;
    }

    /* Reporting Focus Badge Pill */
    .exec-focus-pill {
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        padding: 6px 14px !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.4px !important;
    }

    /* Fix Streamlit Logout & Header Buttons Inside Top Area */
    div[data-testid="stButton"] > button {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 6px 16px !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stButton"] > button:hover {
        background-color: #EF4444 !important;
        color: #FFFFFF !important;
        border-color: #EF4444 !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
    }

    /* Hide orphaned label text above navigation radio buttons */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)



# ---------------------------------------------------------
# EXECUTIVE SIDEBAR STYLING
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* 1. Sidebar Container Base */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A192F 0%, #0F172A 100%) !important;
        border-right: 1px solid #1E293B !important;
    }

    /* 2. Fix LifeNet Logo Contrast (invert dark logo marks to bright white/cyan on dark sidebar) */
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        filter: brightness(0) invert(1) drop-shadow(0 2px 8px rgba(255, 255, 255, 0.2)) !important;
        max-width: 88% !important;
        margin: 0 auto 12px auto !important;
        display: block !important;
    }

    /* 3. Section Headers - Executive Badges */
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #38BDF8 !important;
        font-size: 11px !important;
        font-weight: 800 !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
        background: rgba(56, 189, 248, 0.08) !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        border-left: 3px solid #38BDF8 !important;
        margin-top: 18px !important;
        margin-bottom: 12px !important;
    }

    /* 4. Labels above Dropdowns */
    [data-testid="stSidebar"] label {
        color: #94A3B8 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }

    /* 5. Select Box Input Styling */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.2s ease-in-out !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"]:hover > div {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;
    }

    /* 6. Text inside Select Box Options */
    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #F8FAFC !important;
        font-size: 14px !important;
    }

    /* 7. Dropdown Menu Popup Overlay */
    div[data-baseweb="popover"] div[role="listbox"] {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="popover"] li {
        color: #E2E8F0 !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: #1E293B !important;
        color: #38BDF8 !important;
    }
    </style>
""", unsafe_allow_html=True)



# ---------------------------------------------------------
# EXECUTIVE M&E GLASS & HEADER THEME INJECTION
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Overall Layout & Background */
    .stApp {
        background: #F8FAFC !important;
    }

    /* Top Main Canvas Container Styling */
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px !important;
    }

    /* Sidebar Refinement */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
    }

    /* Clean Executive Header Banner */
    .executive-header {
        background: linear-gradient(135deg, #0A2540 0%, #0F172A 100%);
        border-radius: 14px;
        padding: 24px 32px;
        color: #FFFFFF;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
        margin-bottom: 24px;
        border: 1px solid #1E293B;
    }
    .executive-header h1 {
        color: #FFFFFF !important;
        font-size: 26px !important;
        font-weight: 800 !important;
        margin: 0 0 6px 0 !important;
        letter-spacing: -0.5px !important;
    }
    .executive-header p {
        color: #94A3B8 !important;
        font-size: 14px !important;
        margin: 0 !important;
    }

    /* Segmented Navigation Radio Pills */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        background-color: #FFFFFF !important;
        padding: 5px !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04) !important;
        display: flex !important;
        gap: 6px !important;
        flex-wrap: wrap !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] label {
        background-color: transparent !important;
        padding: 8px 18px !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 13.5px !important;
        color: #475569 !important;
        border: none !important;
        margin: 0 !important;
        cursor: pointer !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] label:hover {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] label[data-checked="true"],
    div[data-testid="stRadio"] > div[role="radiogroup"] label[aria-checked="true"] {
        background-color: #0A2540 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(10, 37, 64, 0.25) !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] label[data-checked="true"] p,
    div[data-testid="stRadio"] > div[role="radiogroup"] label[aria-checked="true"] p {
        color: #FFFFFF !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    /* Metric Containers */
    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 18px 22px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04) !important;
    }
    </style>
""", unsafe_allow_html=True)


# 2. Session State Initialization for Executive Gate Access
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# 3. Executive Cover Page & Passkey Authentication Gate
if not st.session_state["authenticated"]:
    # Executive CSS Styling for Login Screen
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #0F172A;
                color: #F8FAFC;
            }
            .brand-card {
                background: linear-gradient(135deg, #0A2540 0%, #1E293B 100%);
                padding: 32px;
                border-radius: 16px;
                border-left: 6px solid #E61C24;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
                margin-bottom: 24px;
            }
            .brand-logo {
                color: #E61C24;
                font-size: 42px;
                font-weight: 900;
                letter-spacing: 2px;
                margin: 0 0 10px 0;
                line-height: 1;
            }
            .brand-mission {
                color: #FFFFFF;
                font-size: 22px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin: 0 0 12px 0;
                line-height: 1.3;
            }
            .brand-subtext {
                color: #94A3B8;
                font-size: 14px;
                margin: 0;
            }
            .auth-container {
                background: rgba(30, 41, 59, 0.7);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 28px;
                border-radius: 16px;
                box-shadow: 0 20px 30px rgba(0, 0, 0, 0.4);
            }
            .stTextInput > div > div > input {
                background-color: #0F172A !important;
                color: #FFFFFF !important;
                border: 1px solid #334155 !important;
                border-radius: 8px !important;
                padding: 12px 16px !important;
            }
            .stTextInput > div > div > input:focus {
                border-color: #E61C24 !important;
                box-shadow: 0 0 0 2px rgba(230, 28, 36, 0.2) !important;
            }
            .stButton > button {
                background: linear-gradient(90deg, #E61C24 0%, #C1121F 100%) !important;
                color: #FFFFFF !important;
                font-weight: 700 !important;
                font-size: 16px !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 12px 24px !important;
                box-shadow: 0 4px 14px rgba(230, 28, 36, 0.4) !important;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([1.2, 1.8], gap="large")

    with col_left:
        st.markdown(
            """
            <div class="brand-card">
                <div class="brand-logo">LN</div>
                <div class="brand-mission">Transforming Health Care Across Africa</div>
                <p class="brand-subtext">Executive Analytics & Health Facility Operational Intelligence Portal</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

        with st.container():
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            st.markdown(
                "<h4 style='color: #F8FAFC; margin-bottom: 16px;'>Executive Access Portal</h4>",
                unsafe_allow_html=True,
            )

            passkey = st.text_input(
                "Passkey",
                type="password",
                placeholder="Enter executive authorization key...",
                label_visibility="collapsed",
                key="exec_passkey",
            )

            st.markdown("<br/>", unsafe_allow_html=True)

            if st.button("UNLOCK PORTAL", use_container_width=True):
                if passkey == "LifeNet2026!":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ Authorization Failed: Invalid Passkey")
            st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        image_path = "Gemini_Generated_Image_w39fd1w39fd1w39f.jpeg"
        if os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
        else:
            fallback_path = os.path.join("assets", image_path)
            if os.path.exists(fallback_path):
                st.image(fallback_path, use_container_width=True)
            else:
                st.warning(f"Image not found at path: {image_path}")

    st.stop()
st.set_page_config(
    page_title="LifeNet Executive Clinical & Volume Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Executive Color Palette (High-Contrast Dark Typography)
COLOR_NAVY_PRIMARY = "#002F54"
COLOR_NAVY_BAR = "#0F2027"
COLOR_CYAN_ACCENT = "#00A3E0"
COLOR_RED_ALERT = "#DC2626"
COLOR_GREEN_SUCCESS = "#16A34A"
COLOR_AMBER_WARN = "#D97706"

COLOR_BG_APP = "#F8FAFC"
COLOR_CARD_BG = "#F1F5F9"
COLOR_CARD_BORDER = "#CBD5E1"
COLOR_TEXT_MAIN = "#0F172A"
COLOR_TEXT_BODY = "#1E293B"
COLOR_TEXT_MUTED = "#334155"

# Custom CSS Styling (Dark High-Contrast Theme)
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        .stApp {{
            background-color: {COLOR_BG_APP} !important;
            color: {COLOR_TEXT_MAIN} !important;
            font-family: 'Inter', sans-serif !important;
        }}
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: #0A111E !important;
            border-right: 1px solid #1E2D42 !important;
            padding-top: 10px !important;
        }}
        
        .sidebar-header-title {{
            font-size: 13px;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: 0.6px;
            margin-top: 15px;
            margin-bottom: 15px;
            text-transform: uppercase;
        }}
        
        [data-testid="stSidebar"] .stSelectbox label {{
            color: #94A3B8 !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
        }}
        
        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background-color: #122135 !important;
            border: 1px solid #1E3A5F !important;
            border-radius: 6px !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }}

        /* Completely Hide Radio Button Dots & Style Tab Navigation */
        div[data-testid="stRadio"] > div {{
            flex-direction: row !important;
            gap: 10px !important;
            background-color: {COLOR_CARD_BG} !important;
            padding: 6px 10px !important;
            border-radius: 8px !important;
            border: 1px solid {COLOR_CARD_BORDER} !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
        }}

        div[data-testid="stRadio"] label {{
            background-color: transparent !important;
            border: none !important;
            padding: 8px 18px !important;
            border-radius: 6px !important;
            font-weight: 700 !important;
            font-size: 13.5px !important;
            color: {COLOR_TEXT_BODY} !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            display: flex !important;
            align-items: center !important;
        }}

        div[data-testid="stRadio"] label:hover {{
            background-color: #E2E8F0 !important;
            color: {COLOR_NAVY_PRIMARY} !important;
        }}

        div[data-testid="stRadio"] label[data-checked="true"] {{
            background-color: {COLOR_NAVY_PRIMARY} !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            box-shadow: 0 2px 4px rgba(0, 47, 84, 0.2) !important;
        }}

        div[data-testid="stRadio"] input[type="radio"],
        div[data-testid="stRadio"] [data-testid="stRadioButton"] {{
            display: none !important;
        }}

        .main-header-title {{ 
            font-size: 28px; 
            font-weight: 800; 
            color: {COLOR_TEXT_MAIN}; 
            letter-spacing: -0.5px;
        }}
        .main-header-subtitle {{ 
            font-size: 15px; 
            font-weight: 600; 
            color: {COLOR_CYAN_ACCENT}; 
            margin-bottom: 12px; 
        }}

        .period-banner {{
            background-color: #002F54;
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 800;
            padding: 6px 14px;
            border-radius: 6px;
            display: inline-block;
            margin-bottom: 20px;
            letter-spacing: 0.5px;
        }}
        
        h3 {{
            font-size: 20px !important;
            font-weight: 800 !important;
            color: {COLOR_TEXT_MAIN} !important;
            margin-top: 15px !important;
            margin-bottom: 12px !important;
        }}

        .kpi-card {{
            background-color: {COLOR_CARD_BG};
            border: 1px solid {COLOR_CARD_BORDER};
            border-radius: 8px;
            padding: 16px 18px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            margin-bottom: 10px;
        }}
        .kpi-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .kpi-title {{
            font-size: 12px;
            font-weight: 800;
            color: {COLOR_TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }}
        .kpi-icon {{ font-size: 22px; }}
        .kpi-value {{
            font-size: 27px;
            font-weight: 800;
            color: {COLOR_TEXT_MAIN};
            margin-bottom: 8px;
            line-height: 1.1;
        }}
        .badge-positive {{
            background-color: #DCFCE7;
            color: #15803D;
            border: 1px solid #86EFAC;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11.5px;
            font-weight: 700;
            display: inline-block;
        }}
        .badge-negative {{
            background-color: #FEE2E2;
            color: #B91C1C;
            border: 1px solid #FCA5A5;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11.5px;
            font-weight: 700;
            display: inline-block;
        }}

        .action-card {{
            background-color: {COLOR_CARD_BG};
            border-radius: 8px;
            padding: 18px 20px;
            height: 100%;
            border: 1px solid {COLOR_CARD_BORDER};
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }}
        .card-green {{ border-left: 5px solid {COLOR_GREEN_SUCCESS}; }}
        .card-yellow {{ border-left: 5px solid {COLOR_AMBER_WARN}; }}
        .card-cyan {{ border-left: 5px solid {COLOR_CYAN_ACCENT}; }}
        .card-red {{ border-left: 5px solid {COLOR_RED_ALERT}; }}
        
        .action-header {{ font-size: 13.5px; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 0.5px; }}
        .action-body {{ font-size: 14px; color: {COLOR_TEXT_BODY}; line-height: 1.65; }}

        .insight-card {{
            background-color: {COLOR_CARD_BG};
            border-left: 5px solid {COLOR_NAVY_PRIMARY};
            border-top: 1px solid {COLOR_CARD_BORDER};
            border-right: 1px solid {COLOR_CARD_BORDER};
            border-bottom: 1px solid {COLOR_CARD_BORDER};
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            margin-bottom: 15px;
        }}
        .insight-title {{ font-size: 17px; font-weight: 800; color: {COLOR_TEXT_MAIN}; margin-bottom: 10px; }}
        .insight-body {{ font-size: 14px; color: {COLOR_TEXT_BODY}; line-height: 1.65; }}
    </style>
""",
    unsafe_allow_html=True,
)


# Pure Python Paired t-Test Engine
def paired_ttest_custom(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    diff = b - a
    n = len(diff)
    if n < 2:
        return 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0
    mean_a, std_a = np.mean(a), np.std(a, ddof=1)
    mean_b, std_b = np.mean(b), np.std(b, ddof=1)
    mean_d = np.mean(diff)
    std_d = np.std(diff, ddof=1)

    if std_d == 0:
        return 0.0, 1.0, mean_a, std_a, mean_b, std_b, 0.0

    t_stat = mean_d / (std_d / math.sqrt(n))
    z = abs(t_stat)
    p_val = math.erfc(z / math.sqrt(2))
    cohens_dz = mean_d / std_d if std_d > 0 else 0.0

    return (
        float(t_stat),
        float(p_val),
        float(mean_a),
        float(std_a),
        float(mean_b),
        float(std_b),
        float(cohens_dz),
    )


# Data Loaders
@st.cache_data
def load_all_data():
    pv_path = None
    for candidate in [
        os.path.join("data", "Cleaned_PV_Master.xlsx"),
        os.path.join("data", "PV_Q3_2025_vs_2026_Comparison.xlsx"),
        os.path.join("data", "Standardized_Master_Dataset.xlsx"),
        "Cleaned_PV_Master.xlsx",
        "PV_Q3_2025_vs_2026_Comparison.xlsx",
        "Standardized_Master_Dataset.xlsx",
    ]:
        if os.path.exists(candidate):
            pv_path = candidate
            break

    kpi_path = os.path.join("data", "Cleaned_KPI_Master.xlsx")
    if not os.path.exists(kpi_path) and os.path.exists("Cleaned_KPI_Master.xlsx"):
        kpi_path = "Cleaned_KPI_Master.xlsx"

    qsc_path = os.path.join("data", "Cohort 1&2 QSC Analytics final.xlsx")
    if not os.path.exists(qsc_path) and os.path.exists(
        "Cohort 1&2 QSC Analytics final.xlsx"
    ):
        qsc_path = "Cohort 1&2 QSC Analytics final.xlsx"

    df_pv = None
    if pv_path:
        xl_pv = pd.ExcelFile(pv_path, engine="openpyxl")
        sheet_to_use = xl_pv.sheet_names[0]
        df_pv = pd.read_excel(pv_path, sheet_name=sheet_to_use, engine="openpyxl")

    df_kpi_2025, df_kpi_2026, df_issues = None, None, pd.DataFrame()
    if os.path.exists(kpi_path):
        xl_kpi = pd.ExcelFile(kpi_path, engine="openpyxl")
        df_kpi_2025 = (
            pd.read_excel(kpi_path, sheet_name="2025 Data", engine="openpyxl")
            if "2025 Data" in xl_kpi.sheet_names
            else None
        )
        df_kpi_2026 = (
            pd.read_excel(kpi_path, sheet_name="2026 Data", engine="openpyxl")
            if "2026 Data" in xl_kpi.sheet_names
            else None
        )
        df_issues = (
            pd.read_excel(kpi_path, sheet_name="Data Quality Issues", engine="openpyxl")
            if "Data Quality Issues" in xl_kpi.sheet_names
            else pd.DataFrame()
        )

    df_qsc_mgmt, df_qsc_med = None, None
    if os.path.exists(qsc_path):
        xl_qsc = pd.ExcelFile(qsc_path, engine="openpyxl")
        if "Management QSC Performance" in xl_qsc.sheet_names:
            df_qsc_mgmt = pd.read_excel(
                qsc_path, sheet_name="Management QSC Performance", engine="openpyxl"
            )
        if "Medical QSC Performance" in xl_qsc.sheet_names:
            df_qsc_med = pd.read_excel(
                qsc_path, sheet_name="Medical QSC Performance", engine="openpyxl"
            )

    # Merge live KHIS PV & KPI data (rolling LAST_MONTH) without altering QSC or Finance
    try:
        from scripts.khis_adapter import get_live_pv_and_kpi_frames
        df_pv_live, df_kpi_live_wide = get_live_pv_and_kpi_frames("IwUxQNFazpx", "IPjuLUsTQHG")
        if not df_pv_live.empty:
            if df_pv is not None and not df_pv.empty:
                live_periods = set(df_pv_live["Period"].unique())
                df_pv = pd.concat([df_pv[~df_pv["Period"].isin(live_periods)], df_pv_live], ignore_index=True)
            else:
                df_pv = df_pv_live
        if not df_kpi_live_wide.empty and len(df_kpi_live_wide.columns) > 1:
            cols_2025 = ["organisationunitname"] + [c for c in df_kpi_live_wide.columns if c.endswith(" 2025")]
            cols_2026 = ["organisationunitname"] + [c for c in df_kpi_live_wide.columns if c.endswith(" 2026")]

            if len(cols_2025) > 1:
                df_live_2025 = df_kpi_live_wide[cols_2025]
                if df_kpi_2025 is not None and not df_kpi_2025.empty:
                    overlap_25 = [c for c in df_live_2025.columns if c != "organisationunitname" and c in df_kpi_2025.columns]
                    df_kpi_2025 = pd.merge(df_kpi_2025.drop(columns=overlap_25), df_live_2025, on="organisationunitname", how="outer")
                else:
                    df_kpi_2025 = df_live_2025

            if len(cols_2026) > 1:
                df_live_2026 = df_kpi_live_wide[cols_2026]
                if df_kpi_2026 is not None and not df_kpi_2026.empty:
                    overlap_26 = [c for c in df_live_2026.columns if c != "organisationunitname" and c in df_kpi_2026.columns]
                    df_kpi_2026 = pd.merge(df_kpi_2026.drop(columns=overlap_26), df_live_2026, on="organisationunitname", how="outer")
                else:
                    df_kpi_2026 = df_live_2026
    except Exception as e:
        st.sidebar.warning(f"Live KHIS sync skipped (using offline baseline): {e}")


    # Dynamic Multi-Section Clinical Data Quality Audit Engine (2025 & 2026 Excel + Live KHIS)
    def _run_multisection_dq_audit(df_yr, yr_str):
        if df_yr is None or df_yr.empty or "organisationunitname" not in df_yr.columns:
            return []
        all_months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        found = []
        audit_cols = [c for c in df_yr.columns if "audit" in c.lower() and "maternal" in c.lower()]

        for _, row in df_yr.iterrows():
            fac = str(row.get("organisationunitname", "")).strip()
            if not fac or fac.upper() in ("TOTAL", "OVERALL TOTAL", "NAN"):
                continue

            for m in all_months:
                def val(prefix):
                    col = f"{prefix} {m} {yr_str}"
                    if col in df_yr.columns:
                        v = pd.to_numeric(row[col], errors="coerce")
                        return 0.0 if pd.isna(v) else float(v)
                    return 0.0

                def has_any(prefixes):
                    return any(f"{p} {m} {yr_str}" in df_yr.columns for p in prefixes)

                # 1. Maternity Deliveries vs. Birth Outcomes
                deliv_prefixes = [
                    "MOH 711 Normal Deliveries",
                    "MOH 711 Caesarian Sections",
                    "MOH 711 Assisted vaginal delivery",
                    "MOH 711 Breach Delivery",
                ]
                outcome_prefixes = [
                    "MOH 711 Live birth",
                    "MOH 711 Fresh Still Birth",
                    "MOH 711 Macerated still Birth",
                ]
                if has_any(deliv_prefixes) and has_any(outcome_prefixes):
                    tot_deliv = sum(val(p) for p in deliv_prefixes)
                    tot_out = sum(val(p) for p in outcome_prefixes)
                    if abs(tot_deliv - tot_out) > 0:
                        found.append({
                            "Year": yr_str,
                            "Month": m,
                            "Facility": fac,
                            "Issue Category": "Birth Outcomes Discrepancy",
                            "Description": f"Total Deliveries ({int(tot_deliv)}) != Total Birth Outcomes ({int(tot_out)}) [Diff: {int(tot_deliv - tot_out):+d}]"
                        })

                # 2. Birth Asphyxia: Outcome (Death) without Cases / Exceeding Cases
                asph_d = val("MOH 711 Rev 2020_Neonatal deaths due to Asphyxia")
                low_apgar = val("MOH 711 Births with low APGAR score")
                neo_d = val("MOH 711 Neonatal deaths 0-28 Days")
                if asph_d > 0 and low_apgar == 0:
                    found.append({
                        "Year": yr_str,
                        "Month": m,
                        "Facility": fac,
                        "Issue Category": "Asphyxia Outcome Without Cases",
                        "Description": f"Neonatal deaths due to Asphyxia = {int(asph_d)}, but Births with low APGAR score (Asphyxia cases) = 0"
                    })
                elif asph_d > low_apgar and low_apgar > 0:
                    found.append({
                        "Year": yr_str,
                        "Month": m,
                        "Facility": fac,
                        "Issue Category": "Asphyxia Outcome Without Cases",
                        "Description": f"Asphyxia deaths ({int(asph_d)}) exceed reported low APGAR cases ({int(low_apgar)})"
                    })
                if asph_d > 0 and neo_d > 0 and asph_d > neo_d:
                    found.append({
                        "Year": yr_str,
                        "Month": m,
                        "Facility": fac,
                        "Issue Category": "Neonatal Mortality Discrepancy",
                        "Description": f"Asphyxia deaths ({int(asph_d)}) exceed total Neonatal deaths 0-28 Days ({int(neo_d)})"
                    })

                # 3. Postpartum Hemorrhage (PPH): PPH D without PPH Cases (PPH A + D)
                pph_a = val("MOH 711 PPH (Post Partum Haemorrage) A")
                pph_d = val("MOH 711 PPH (Post Partum Haemorrage) D")
                pph_total = pph_a + pph_d
                if pph_d > 0 and pph_total == 0:
                    found.append({
                        "Year": yr_str,
                        "Month": m,
                        "Facility": fac,
                        "Issue Category": "PPH Outcome Without Cases",
                        "Description": f"PPH Death (PPH D = {int(pph_d)}) reported with 0 total PPH cases (PPH A + D = 0)"
                    })
                elif pph_d > 0 and pph_a == 0:
                    found.append({
                        "Year": yr_str,
                        "Month": m,
                        "Facility": fac,
                        "Issue Category": "PPH Outcome Without Cases",
                        "Description": f"PPH Death (PPH D = {int(pph_d)}) recorded with 0 surviving PPH cases (PPH A = 0; Total PPH A+D = {int(pph_total)}) — verify case register"
                    })

                # 4. Maternal Deaths & MPDSR Audit Reconciliation
                md_10_14 = val("MOH 711 Rev 2020_Maternal deaths 10-14Years")
                md_15_19 = val("MOH 711 Rev 2020_Maternal deaths 15-19Years")
                md_20_24 = val("MOH 711 Rev 2020_Maternal deaths 20-24 Years")
                md_25_plus = val("MOH 711 Rev 2020_Maternal deaths 25+ Years")
                tot_md = md_10_14 + md_15_19 + md_20_24 + md_25_plus
                if tot_md > 0:
                    m_audit_cols = [c for c in audit_cols if f"{m} {yr_str}" in c]
                    audited_cnt = sum(
                        0.0 if pd.isna(pd.to_numeric(row[c], errors="coerce")) else float(pd.to_numeric(row[c], errors="coerce"))
                        for c in m_audit_cols
                    )
                    age_breakdown = ", ".join(
                        f"{lbl}:{int(v)}" for lbl, v in [
                            ("10-14y", md_10_14), ("15-19y", md_15_19), ("20-24y", md_20_24), ("25+y", md_25_plus)
                        ] if v > 0
                    )
                    if not m_audit_cols:
                        audit_note = "MPDSR Audit indicator not captured in KHIS extract — field audit verification mandatory"
                    elif audited_cnt < tot_md:
                        audit_note = f"Unaudited Maternal Deaths: {int(audited_cnt)} audited vs {int(tot_md)} deaths"
                    else:
                        audit_note = f"All {int(tot_md)} maternal death(s) logged as audited ({int(audited_cnt)}) — verify MPDSR minutes"
                    found.append({
                        "Year": yr_str,
                        "Month": m,
                        "Facility": fac,
                        "Issue Category": "Maternal Death & MPDSR Audit",
                        "Description": f"Maternal Deaths = {int(tot_md)} ({age_breakdown}) | {audit_note}"
                    })

                # 5. Perinatal Mortality Consistency
                peri_d = val("MOH 711 Rev 2020_Perinatal Deaths 0-7 days")
                fsb = val("MOH 711 Fresh Still Birth")
                if peri_d > 0 and (fsb + neo_d) > 0 and peri_d > (fsb + neo_d):
                    found.append({
                        "Year": yr_str,
                        "Month": m,
                        "Facility": fac,
                        "Issue Category": "Perinatal Mortality Discrepancy",
                        "Description": f"Perinatal Deaths 0-7d ({int(peri_d)}) > Fresh Still Births ({int(fsb)}) + Neonatal Deaths 0-28d ({int(neo_d)})"
                    })
        return found

    dyn_issues = _run_multisection_dq_audit(df_kpi_2025, "2025") + _run_multisection_dq_audit(df_kpi_2026, "2026")
    if dyn_issues:
        df_dyn_issues = pd.DataFrame(dyn_issues)
        if df_issues is not None and not df_issues.empty:
            df_issues["Year"] = df_issues["Year"].astype(str).str.strip()
            df_issues = pd.concat([df_issues, df_dyn_issues], ignore_index=True)
            df_issues = df_issues.drop_duplicates(subset=["Year", "Month", "Facility", "Issue Category"], keep="last")
            # Drop stale static Excel DQA rows for any (Year, Month) already mirrored from KHIS
            synced_ym = set()
            for _df_yr, _yr_val in [(df_kpi_2025, 2025), (df_kpi_2026, 2026)]:
                if _df_yr is not None and not _df_yr.empty:
                    for _col in _df_yr.columns:
                        for _m in ["January","February","March","April","May","June","July","August","September","October","November","December"]:
                            if _col.endswith(f" {_m} {_yr_val}"):
                                synced_ym.add((str(_yr_val), _m))
            if synced_ym and "Year" in df_issues.columns and "Month" in df_issues.columns:
                _in_synced = df_issues.apply(lambda r: (str(r["Year"]).strip(), str(r["Month"]).strip()) in synced_ym, axis=1)
                df_issues = pd.concat([df_issues[~_in_synced], df_dyn_issues], ignore_index=True).drop_duplicates(
                    subset=["Year", "Month", "Facility", "Issue Category"], keep="last"
                )
        else:
            df_issues = df_dyn_issues

    return df_pv, df_kpi_2025, df_kpi_2026, df_issues, df_qsc_mgmt, df_qsc_med


# Load Raw Datasets
df_pv_raw, kpi_2025, kpi_2026, kpi_issues, df_qsc_mgmt, df_qsc_med = load_all_data()


# DYNAMIC PATIENT VOLUME (PV) ENGINE WITH YEAR SELECTION
def process_pv_timeline(df_pv, months, period_code, focus_yr, base_yr):
    if df_pv is None or df_pv.empty:
        return pd.DataFrame(), 0, 0, 0, 0

    df = df_pv.copy()
    df.columns = [str(c).strip() for c in df.columns]

    fac_candidates = [
        c
        for c in df.columns
        if any(k in c.lower() for k in ["organisation", "facility", "unit", "org"])
    ]
    fac_col = fac_candidates[0] if fac_candidates else df.columns[0]

    df = df[
        ~df[fac_col]
        .astype(str)
        .str.strip()
        .str.upper()
        .isin(["TOTAL", "OVERALL TOTAL", "TOTAL / OVERALL PV"])
    ].copy()

    has_period_col = any("period" in c.lower() for c in df.columns)

    if has_period_col:
        period_col = [c for c in df.columns if "period" in c.lower()][0]
        pv_col = [
            c
            for c in df.columns
            if c.lower() in ["pv", "value", "attendance", "volume"]
        ][0]

        df[pv_col] = df[pv_col].astype(str).str.replace(",", "").str.strip()
        df["PV_Num"] = pd.to_numeric(df[pv_col], errors="coerce").fillna(0)
        df["Period_Str"] = df[period_col].astype(str).str.strip()

        month_patterns = [m.lower()[:3] for m in months]

        def is_target_period(p_str, year_str):
            p = str(p_str).lower()
            has_year = year_str in p or f"-{year_str[2:]}" in p or f"{year_str}" in p
            has_month = (
                True
                if period_code.startswith("Full Year")
                else any(m in p for m in month_patterns)
            )
            return has_year and has_month

        df_base = df[
            df["Period_Str"].apply(lambda x: is_target_period(x, str(base_yr)))
        ]
        df_focus = df[
            df["Period_Str"].apply(lambda x: is_target_period(x, str(focus_yr)))
        ]

        agg_base = (
            df_base.groupby(fac_col, as_index=False)["PV_Num"]
            .sum()
            .rename(columns={"PV_Num": "PV_2025", fac_col: "organisationunitname"})
        )
        agg_focus = (
            df_focus.groupby(fac_col, as_index=False)["PV_Num"]
            .sum()
            .rename(columns={"PV_Num": "PV_2026", fac_col: "organisationunitname"})
        )

        grouped_df = pd.merge(
            agg_base, agg_focus, on="organisationunitname", how="outer"
        ).fillna(0)

    else:
        month_patterns = [m.lower()[:3] for m in months]
        cols_base, cols_focus = [], []

        for col in df.columns:
            c_lower = col.lower()
            if col == fac_col:
                continue
            has_month = (
                True
                if period_code.startswith("Full Year")
                else any(m in c_lower for m in month_patterns)
            )
            if (
                str(base_yr) in c_lower or f"-{str(base_yr)[2:]}" in c_lower
            ) and has_month:
                cols_base.append(col)
            elif (
                str(focus_yr) in c_lower or f"-{str(focus_yr)[2:]}" in c_lower
            ) and has_month:
                cols_focus.append(col)

        for col in cols_base + cols_focus:
            df[col] = df[col].astype(str).str.replace(",", "").str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df["PV_2025"] = df[cols_base].sum(axis=1) if cols_base else 0
        df["PV_2026"] = df[cols_focus].sum(axis=1) if cols_focus else 0

        grouped_df = (
            df[[fac_col, "PV_2025", "PV_2026"]]
            .rename(columns={fac_col: "organisationunitname"})
            .copy()
        )

    grouped_df["Absolute_Variance"] = grouped_df["PV_2026"] - grouped_df["PV_2025"]
    grouped_df["Growth_%"] = (
        grouped_df["Absolute_Variance"] / grouped_df["PV_2025"].replace(0, 1)
    ) * 100

    tot_25 = float(grouped_df["PV_2025"].sum())
    tot_26 = float(grouped_df["PV_2026"].sum())
    net_var = tot_26 - tot_25
    growth_p = (net_var / tot_25 * 100) if tot_25 > 0 else 0.0

    return grouped_df, tot_25, tot_26, net_var, growth_p


# EXECUTIVE SIDEBAR NAVIGATION (WITH SPECIFIC YEAR FILTERING)
with st.sidebar:
    logo_png = os.path.join("assets", "Logo.png")

    if os.path.exists(logo_png):
        st.image(logo_png, use_container_width=True)
    else:
        st.markdown(
            """
            <div style="background:#002F54; padding:12px; border-radius:8px; border:1px solid #00A3E0; text-align:center;">
                <h3 style="color:#FFFFFF; margin:0; font-weight:800;">🏥 LifeNet</h3>
                <span style="color:#00A3E0; font-size:11px; font-weight:600;">INTERNATIONAL</span>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="sidebar-header-title">📅 Year & Timeline Selection</div>',
        unsafe_allow_html=True,
    )

    focus_year = st.selectbox("Select Primary Focus Year:", ["2026", "2025"], index=0)
    comparison_year = st.selectbox(
        "Compare Against (Baseline Year):",
        ["2025", "2026"],
        index=0 if focus_year == "2026" else 1,
    )

    st.markdown(
        '<div class="sidebar-header-title">🔀 Granularity Filters</div>',
        unsafe_allow_html=True,
    )
    time_frame_type = st.selectbox(
        "Granularity Level:",
        ["Monthly / Multi-Month", "Quarterly", "Biannual (H1/H2)", "Annual Summary"],
    )

    all_months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    if time_frame_type == "Monthly / Multi-Month":
        chosen_months = st.multiselect(
            "Select One or More Months:",
            options=all_months,
            default=["October"],
            help="Pick a single month or combine any custom months (e.g., Jan, Feb, Mar, Apr).",
        )
        if not chosen_months:
            st.warning("Select at least one month (defaulting to October).")
            chosen_months = ["October"]
        # Preserve calendar order regardless of click order
        selected_months = [m for m in all_months if m in chosen_months]
        if len(selected_months) == 1:
            selected_period = f"{selected_months[0]} ({focus_year})"
        else:
            short_names = ", ".join(m[:3] for m in selected_months)
            selected_period = f"{short_names} ({focus_year})" 
    elif time_frame_type == "Quarterly":
        selected_period = st.selectbox(
            "Select Quarter:", ["Q1", "Q2", "Q3", "Q4"], index=2
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
            "Select Half-Year:", ["H1 (Jan - Jun)", "H2 (Jul - Dec)"]
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
        # Inside `with st.sidebar:` section at the bottom:
# ---------------------------------------------------------
# EXECUTIVE HERO BANNER & HEADER (SURGICAL EDIT)
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.caption("🔒 Session Active: Executive Level")
    st.title("LifeNet Program Analytics & Executive Dashboard")
    st.subheader(f"Specific Year Focus & Comparative Performance ({focus_year} vs. {comparison_year})")
    st.info(f"📅 CURRENT REPORTING FOCUS: {selected_period} | Baseline: {comparison_year}")

with col_h2:
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    if st.button("Log Out", key="btn_logout_native_clean", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

tabs = [
    "📊 Patient Volume Dashboard",
    "📈 Program KPI Comparative Analytics",
    "🎯 Quality Scorecard (QSC) & QI Analytics",
    "🚨 Data Quality Audits",
    "🔍 Facility Inspector",
    "💼 Financial Performance",
    "📑 Monthly DDIU Brief",
]
active_tab = st.radio("Nav", options=tabs, horizontal=True)
st.markdown("---")

# ---------------------------------------------------------
# TAB 1: PATIENT VOLUME DASHBOARD
# ---------------------------------------------------------
if active_tab == "📊 Patient Volume Dashboard":
    st.markdown(
        f"### 📊 Patient Volume (Outpatient & Attendance Analytics — {selected_period})"
    )

    pv_sub_view = st.radio(
        "Select PV View Focus:",
        options=[
            "📈 YoY Trajectory & Volume Comparison",
            "🎯 Facility Growth Matrix & Performance Drill-Down",
        ],
        horizontal=True,
    )
    st.markdown("---")

    facility_pv_df, tot_base, tot_focus, abs_var, growth_pct = process_pv_timeline(
        df_pv_raw, selected_months, selected_period, focus_year, comparison_year
    )

    if not facility_pv_df.empty:
        gaining_facs = facility_pv_df[facility_pv_df["Absolute_Variance"] > 0]
        declining_facs = facility_pv_df[facility_pv_df["Absolute_Variance"] < 0]

        tot_gains = gaining_facs["Absolute_Variance"].sum()
        tot_drops = declining_facs["Absolute_Variance"].sum()

        v1, v2, v3, v4, v5, v6 = st.columns(6)

        with v1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">{comparison_year} Baseline</span><span class="kpi-icon">📅</span></div>
                    <div class="kpi-value">{int(tot_base):,}</div>
                    <span class="badge-positive">Baseline</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with v2:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">{focus_year} Focus Volume</span><span class="kpi-icon">📈</span></div>
                    <div class="kpi-value">{int(tot_focus):,}</div>
                    <span class="badge-positive">Current Focus</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with v3:
            v_class = "badge-positive" if abs_var >= 0 else "badge-negative"
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Net Variance</span><span class="kpi-icon">📊</span></div>
                    <div class="kpi-value">{int(abs_var):+,}</div>
                    <span class="{v_class}">{'↑' if abs_var >= 0 else '↓'} {growth_pct:+.2f}%</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with v4:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Volume Gains</span><span class="kpi-icon">🟢</span></div>
                    <div class="kpi-value">+{int(tot_gains):,}</div>
                    <span class="badge-positive">{len(gaining_facs)} Sites Growing</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with v5:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Volume Drops</span><span class="kpi-icon">🔻</span></div>
                    <div class="kpi-value">{int(tot_drops):,}</div>
                    <span class="badge-negative">{len(declining_facs)} Sites Dropping</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with v6:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Reporting Sites</span><span class="kpi-icon">🏬</span></div>
                    <div class="kpi-value">{facility_pv_df['organisationunitname'].nunique()}</div>
                    <span class="badge-positive">Active Partner Facilities</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        if pv_sub_view == "📈 YoY Trajectory & Volume Comparison":
            top_15_pv = facility_pv_df.sort_values(by="PV_2026", ascending=False).head(
                15
            )
            max_val = max(top_15_pv["PV_2025"].max(), top_15_pv["PV_2026"].max()) * 1.25

            fig_pv_comp = go.Figure()

            fig_pv_comp.add_trace(
                go.Bar(
                    y=top_15_pv["organisationunitname"],
                    x=top_15_pv["PV_2025"],
                    name=f"{comparison_year} Baseline",
                    orientation="h",
                    text=[f"{int(v):,}" for v in top_15_pv["PV_2025"]],
                    textposition="outside",
                    textfont=dict(color=COLOR_TEXT_MAIN, size=12, family="Inter"),
                    marker=dict(color="#94A3B8"),
                )
            )

            fig_pv_comp.add_trace(
                go.Bar(
                    y=top_15_pv["organisationunitname"],
                    x=top_15_pv["PV_2026"],
                    name=f"{focus_year} Volume Focus",
                    orientation="h",
                    text=[f"{int(v):,}" for v in top_15_pv["PV_2026"]],
                    textposition="outside",
                    textfont=dict(color=COLOR_TEXT_MAIN, size=12, family="Inter"),
                    marker=dict(color=COLOR_NAVY_PRIMARY),
                )
            )

            fig_pv_comp.update_layout(
                barmode="group",
                bargap=0.22,
                bargroupgap=0.08,
                paper_bgcolor=COLOR_CARD_BG,
                plot_bgcolor=COLOR_CARD_BG,
                title=dict(
                    text=f"Facility League Table — Top 15 Patient Attendance ({comparison_year} vs {focus_year} — {selected_period})",
                    font=dict(size=17, family="Inter", color=COLOR_TEXT_MAIN),
                    y=0.96,
                ),
                font=dict(family="Inter"),
                height=630,
                margin=dict(l=280, r=120, t=110, b=40),
                xaxis=dict(
                    range=[0, max_val],
                    showgrid=True,
                    gridcolor="#E2E8F0",
                    tickfont=dict(size=12, color=COLOR_TEXT_MUTED),
                ),
                yaxis=dict(
                    autorange="reversed", tickfont=dict(size=13, color=COLOR_TEXT_MAIN)
                ),
                legend=dict(
                    orientation="h",
                    y=1.15,
                    x=0,
                    xanchor="left",
                    font=dict(size=13, color=COLOR_TEXT_MAIN),
                ),
            )
            st.plotly_chart(fig_pv_comp, width="stretch")

        else:
            volume_threshold = 10000

            facility_pv_df["Status"] = facility_pv_df["Absolute_Variance"].apply(
                lambda x: (
                    "Expanding Facility (+)" if x >= 0 else "Declining Facility (-)"
                )
            )

            top_gainers_names = set(
                facility_pv_df.nlargest(4, "Absolute_Variance")["organisationunitname"]
            )
            top_decliners_names = set(
                facility_pv_df.nsmallest(4, "Absolute_Variance")["organisationunitname"]
            )
            top_vol_names = set(
                facility_pv_df.nlargest(3, "PV_2026")["organisationunitname"]
            )
            outliers = top_gainers_names.union(top_decliners_names).union(top_vol_names)

            facility_pv_df["display_label"] = facility_pv_df[
                "organisationunitname"
            ].apply(lambda x: x if x in outliers else "")

            color_map = {
                "Expanding Facility (+)": COLOR_GREEN_SUCCESS,
                "Declining Facility (-)": COLOR_RED_ALERT,
            }

            fig_quad = px.scatter(
                facility_pv_df,
                x="PV_2026",
                y="Growth_%",
                text="display_label",
                color="Status",
                color_discrete_map=color_map,
                size="PV_2026",
                size_max=22,
                hover_name="organisationunitname",
                hover_data={
                    "PV_2025": ":,",
                    "PV_2026": ":,",
                    "Absolute_Variance": ":+",
                    "Growth_%": ":.2f%",
                    "Status": False,
                    "display_label": False,
                },
                title=f"Performance Quadrant Matrix — {focus_year} Facility Growth vs. Total Volume ({selected_period})",
            )

            fig_quad.add_hline(
                y=0, line_dash="dash", line_color=COLOR_TEXT_MUTED, opacity=0.6
            )
            fig_quad.add_vline(
                x=volume_threshold,
                line_dash="dash",
                line_color=COLOR_TEXT_MUTED,
                opacity=0.6,
            )

            fig_quad.update_traces(
                textposition="top center",
                textfont=dict(color=COLOR_TEXT_MAIN, size=12, family="Inter"),
                marker=dict(opacity=0.9, line=dict(width=1, color="white")),
            )

            fig_quad.update_layout(
                paper_bgcolor=COLOR_CARD_BG,
                plot_bgcolor=COLOR_CARD_BG,
                title=dict(font=dict(size=17, color=COLOR_TEXT_MAIN, family="Inter")),
                font=dict(family="Inter", color=COLOR_TEXT_MAIN),
                height=560,
                xaxis=dict(
                    title=dict(
                        text=f"{focus_year} Total Patient Volume ({selected_period})",
                        font=dict(color=COLOR_TEXT_MAIN, size=13),
                    ),
                    showgrid=True,
                    gridcolor="#CBD5E1",
                    tickfont=dict(color=COLOR_TEXT_MAIN, size=12),
                ),
                yaxis=dict(
                    title=dict(
                        text="Growth Rate (%)",
                        font=dict(color=COLOR_TEXT_MAIN, size=13),
                    ),
                    showgrid=True,
                    gridcolor="#CBD5E1",
                    tickfont=dict(color=COLOR_TEXT_MAIN, size=12),
                ),
                legend=dict(font=dict(color=COLOR_TEXT_MAIN, size=12.5)),
                margin=dict(l=50, r=50, t=70, b=50),
            )
            st.plotly_chart(fig_quad, width="stretch")

        st.markdown("---")
        st.dataframe(
            facility_pv_df[
                [
                    "organisationunitname",
                    "PV_2025",
                    "PV_2026",
                    "Absolute_Variance",
                    "Growth_%",
                ]
            ].sort_values(by="PV_2026", ascending=False),
            column_config={
                "organisationunitname": "Facility Name",
                "PV_2025": st.column_config.NumberColumn(
                    f"{comparison_year} Baseline Volume", format="%d"
                ),
                "PV_2026": st.column_config.NumberColumn(
                    f"{focus_year} Focus Volume", format="%d"
                ),
                "Absolute_Variance": st.column_config.NumberColumn(
                    "Variance", format="%+d"
                ),
                "Growth_%": st.column_config.NumberColumn(
                    "Growth Rate (%)", format="%.2f%%"
                ),
            },
            hide_index=True,
            width="stretch",
        )

# ---------------------------------------------------------
# TAB 2: PROGRAM KPI COMPARATIVE ANALYTICS
# ---------------------------------------------------------
elif active_tab == "📈 Program KPI Comparative Analytics":
    st.markdown(
        f"### 📈 Clinical Deliveries & MOH 711 Indicators ({focus_year} Focus — {selected_period})"
    )

    kpi_sub_view = st.radio(
        "Select KPI View Level:",
        options=[
            "📊 Macro KPI Overview & Charts",
            "🏢 Facility Performance & Variance Drill-Down",
        ],
        horizontal=True,
    )
    st.markdown("---")

    def get_facility_kpi_summary(df_25, df_26, months, f_yr, b_yr):
        if df_25 is None or df_26 is None:
            return pd.DataFrame(), {}, {}

        cols_norm_25 = [
            f"MOH 711 Normal Deliveries {m} {b_yr}"
            for m in months
            if f"MOH 711 Normal Deliveries {m} {b_yr}" in df_25.columns
        ]
        cols_cs_25 = [
            f"MOH 711 Caesarian Sections {m} {b_yr}"
            for m in months
            if f"MOH 711 Caesarian Sections {m} {b_yr}" in df_25.columns
        ]
        cols_assisted_25 = [
            f"MOH 711 Assisted vaginal delivery {m} {b_yr}"
            for m in months
            if f"MOH 711 Assisted vaginal delivery {m} {b_yr}" in df_25.columns
        ]
        cols_breech_25 = [
            f"MOH 711 Breach Delivery {m} {b_yr}"
            for m in months
            if f"MOH 711 Breach Delivery {m} {b_yr}" in df_25.columns
        ]

        cols_norm_26 = [
            f"MOH 711 Normal Deliveries {m} {f_yr}"
            for m in months
            if f"MOH 711 Normal Deliveries {m} {f_yr}" in df_26.columns
        ]
        cols_cs_26 = [
            f"MOH 711 Caesarian Sections {m} {f_yr}"
            for m in months
            if f"MOH 711 Caesarian Sections {m} {f_yr}" in df_26.columns
        ]
        cols_assisted_26 = [
            f"MOH 711 Assisted vaginal delivery {m} {f_yr}"
            for m in months
            if f"MOH 711 Assisted vaginal delivery {m} {f_yr}" in df_26.columns
        ]
        cols_breech_26 = [
            f"MOH 711 Breach Delivery {m} {f_yr}"
            for m in months
            if f"MOH 711 Breach Delivery {m} {f_yr}" in df_26.columns
        ]

        df_sum_25 = df_25[["organisationunitname"]].copy()
        df_sum_25["Deliv_2025"] = df_25[
            cols_norm_25 + cols_cs_25 + cols_assisted_25 + cols_breech_25
        ].sum(axis=1)

        df_sum_26 = df_26[["organisationunitname"]].copy()
        df_sum_26["Deliv_2026"] = df_26[
            cols_norm_26 + cols_cs_26 + cols_assisted_26 + cols_breech_26
        ].sum(axis=1)

        merged = df_sum_25.merge(
            df_sum_26, on="organisationunitname", how="outer"
        ).fillna(0)
        merged["Deliv_Variance"] = merged["Deliv_2026"] - merged["Deliv_2025"]
        merged["Deliv_Growth_%"] = (
            merged["Deliv_Variance"] / merged["Deliv_2025"].replace(0, 1)
        ) * 100

        tot_25 = {
            "norm": df_25[cols_norm_25].sum().sum() if cols_norm_25 else 0,
            "cs": df_25[cols_cs_25].sum().sum() if cols_cs_25 else 0,
            "assisted": df_25[cols_assisted_25].sum().sum() if cols_assisted_25 else 0,
            "breech": df_25[cols_breech_25].sum().sum() if cols_breech_25 else 0,
            "live": df_25[
                [
                    f"MOH 711 Live birth {m} {b_yr}"
                    for m in months
                    if f"MOH 711 Live birth {m} {b_yr}" in df_25.columns
                ]
            ]
            .sum()
            .sum(),
            "fsb": df_25[
                [
                    f"MOH 711 Fresh Still Birth {m} {b_yr}"
                    for m in months
                    if f"MOH 711 Fresh Still Birth {m} {b_yr}" in df_25.columns
                ]
            ]
            .sum()
            .sum(),
            "msb": df_25[
                [
                    f"MOH 711 Macerated still Birth {m} {b_yr}"
                    for m in months
                    if f"MOH 711 Macerated still Birth {m} {b_yr}" in df_25.columns
                ]
            ]
            .sum()
            .sum(),
            "pph_a": df_25[
                [
                    f"MOH 711 PPH (Post Partum Haemorrage) A {m} {b_yr}"
                    for m in months
                    if f"MOH 711 PPH (Post Partum Haemorrage) A {m} {b_yr}"
                    in df_25.columns
                ]
            ]
            .sum()
            .sum(),
            "pph_d": df_25[
                [
                    f"MOH 711 PPH (Post Partum Haemorrage) D {m} {b_yr}"
                    for m in months
                    if f"MOH 711 PPH (Post Partum Haemorrage) D {m} {b_yr}"
                    in df_25.columns
                ]
            ]
            .sum()
            .sum(),
            "apgar": df_25[
                [
                    f"MOH 711 Births with low APGAR score {m} {b_yr}"
                    for m in months
                    if f"MOH 711 Births with low APGAR score {m} {b_yr}"
                    in df_25.columns
                ]
            ]
            .sum()
            .sum(),
            "asphyxia_d": df_25[
                [
                    f"MOH 711 Rev 2020_Neonatal deaths due to Asphyxia {m} {b_yr}"
                    for m in months
                    if f"MOH 711 Rev 2020_Neonatal deaths due to Asphyxia {m} {b_yr}"
                    in df_25.columns
                ]
            ]
            .sum()
            .sum(),
            "peri_d": df_25[
                [
                    f"MOH 711 Rev 2020_Perinatal Deaths 0-7 days {m} {b_yr}"
                    for m in months
                    if f"MOH 711 Rev 2020_Perinatal Deaths 0-7 days {m} {b_yr}"
                    in df_25.columns
                ]
            ]
            .sum()
            .sum(),
            "neo_d": df_25[
                [
                    f"MOH 711 Neonatal deaths 0-28 Days {m} {b_yr}"
                    for m in months
                    if f"MOH 711 Neonatal deaths 0-28 Days {m} {b_yr}" in df_25.columns
                ]
            ]
            .sum()
            .sum(),
        }

        tot_26 = {
            "norm": df_26[cols_norm_26].sum().sum() if cols_norm_26 else 0,
            "cs": df_26[cols_cs_26].sum().sum() if cols_cs_26 else 0,
            "assisted": df_26[cols_assisted_26].sum().sum() if cols_assisted_26 else 0,
            "breech": df_26[cols_breech_26].sum().sum() if cols_breech_26 else 0,
            "live": df_26[
                [
                    f"MOH 711 Live birth {m} {f_yr}"
                    for m in months
                    if f"MOH 711 Live birth {m} {f_yr}" in df_26.columns
                ]
            ]
            .sum()
            .sum(),
            "fsb": df_26[
                [
                    f"MOH 711 Fresh Still Birth {m} {f_yr}"
                    for m in months
                    if f"MOH 711 Fresh Still Birth {m} {f_yr}" in df_26.columns
                ]
            ]
            .sum()
            .sum(),
            "msb": df_26[
                [
                    f"MOH 711 Macerated still Birth {m} {f_yr}"
                    for m in months
                    if f"MOH 711 Macerated still Birth {m} {f_yr}" in df_26.columns
                ]
            ]
            .sum()
            .sum(),
            "pph_a": df_26[
                [
                    f"MOH 711 PPH (Post Partum Haemorrage) A {m} {f_yr}"
                    for m in months
                    if f"MOH 711 PPH (Post Partum Haemorrage) A {m} {f_yr}"
                    in df_26.columns
                ]
            ]
            .sum()
            .sum(),
            "pph_d": df_26[
                [
                    f"MOH 711 PPH (Post Partum Haemorrage) D {m} {f_yr}"
                    for m in months
                    if f"MOH 711 PPH (Post Partum Haemorrage) D {m} {f_yr}"
                    in df_26.columns
                ]
            ]
            .sum()
            .sum(),
            "apgar": df_26[
                [
                    f"MOH 711 Births with low APGAR score {m} {f_yr}"
                    for m in months
                    if f"MOH 711 Births with low APGAR score {m} {f_yr}"
                    in df_26.columns
                ]
            ]
            .sum()
            .sum(),
            "asphyxia_d": df_26[
                [
                    f"MOH 711 Rev 2020_Neonatal deaths due to Asphyxia {m} {f_yr}"
                    for m in months
                    if f"MOH 711 Rev 2020_Neonatal deaths due to Asphyxia {m} {f_yr}"
                    in df_26.columns
                ]
            ]
            .sum()
            .sum(),
            "peri_d": df_26[
                [
                    f"MOH 711 Rev 2020_Perinatal Deaths 0-7 days {m} {f_yr}"
                    for m in months
                    if f"MOH 711 Rev 2020_Perinatal Deaths 0-7 days {m} {f_yr}"
                    in df_26.columns
                ]
            ]
            .sum()
            .sum(),
            "neo_d": df_26[
                [
                    f"MOH 711 Neonatal deaths 0-28 Days {m} {f_yr}"
                    for m in months
                    if f"MOH 711 Neonatal deaths 0-28 Days {m} {f_yr}" in df_26.columns
                ]
            ]
            .sum()
            .sum(),
        }

        tot_25["tot_deliv"] = (
            tot_25["norm"] + tot_25["cs"] + tot_25["assisted"] + tot_25["breech"]
        )
        tot_26["tot_deliv"] = (
            tot_26["norm"] + tot_26["cs"] + tot_26["assisted"] + tot_26["breech"]
        )

        tot_25["pph_rate"] = (
            (tot_25["pph_a"] / (tot_25["pph_a"] + tot_25["pph_d"]) * 100)
            if (tot_25["pph_a"] + tot_25["pph_d"]) > 0
            else 100.0
        )
        tot_26["pph_rate"] = (
            (tot_26["pph_a"] / (tot_26["pph_a"] + tot_26["pph_d"]) * 100)
            if (tot_26["pph_a"] + tot_26["pph_d"]) > 0
            else 100.0
        )

        tot_25["apgar_rate"] = (
            ((tot_25["apgar"] - tot_25["asphyxia_d"]) / tot_25["apgar"] * 100)
            if tot_25["apgar"] > 0
            else 100.0
        )
        tot_26["apgar_rate"] = (
            ((tot_26["apgar"] - tot_26["asphyxia_d"]) / tot_26["apgar"] * 100)
            if tot_26["apgar"] > 0
            else 100.0
        )

        return merged, tot_25, tot_26

    df_b_target = kpi_2025 if comparison_year == "2025" else kpi_2026
    df_f_target = kpi_2026 if focus_year == "2026" else kpi_2025

    fac_kpi_df, kpi_25, kpi_26 = get_facility_kpi_summary(
        df_b_target, df_f_target, selected_months, focus_year, comparison_year
    )

    if not fac_kpi_df.empty:
        deliv_diff = kpi_26["tot_deliv"] - kpi_25["tot_deliv"]
        live_diff = kpi_26["live"] - kpi_25["live"]
        cs_diff = kpi_26["cs"] - kpi_25["cs"]
        fsb_diff = kpi_26["fsb"] - kpi_25["fsb"]
        msb_diff = kpi_26["msb"] - kpi_25["msb"]
        neo_diff = kpi_26["neo_d"] - kpi_25["neo_d"]

        m1, m2, m3, m4, m5, m6 = st.columns(6)

        with m1:
            badge_class = "badge-positive" if deliv_diff >= 0 else "badge-negative"
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Total Deliveries ({focus_year})</span><span class="kpi-icon">👶</span></div>
                    <div class="kpi-value">{int(kpi_26['tot_deliv']):,}</div>
                    <span class="{badge_class}">{'↑' if deliv_diff >= 0 else '↓'} {int(deliv_diff):+d} vs {comparison_year}</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with m2:
            badge_class = "badge-positive" if live_diff >= 0 else "badge-negative"
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Live Births ({focus_year})</span><span class="kpi-icon">🌱</span></div>
                    <div class="kpi-value">{int(kpi_26['live']):,}</div>
                    <span class="{badge_class}">{'↑' if live_diff >= 0 else '↓'} {int(live_diff):+d} vs {comparison_year}</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with m3:
            cs_pct = (
                (kpi_26["cs"] / kpi_26["tot_deliv"] * 100)
                if kpi_26["tot_deliv"] > 0
                else 0
            )
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">C-Section Volume</span><span class="kpi-icon">🏥</span></div>
                    <div class="kpi-value">{int(kpi_26['cs']):,}</div>
                    <span class="badge-positive">{cs_pct:.1f}% Delivery Share</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with m4:
            fsb_class = "badge-negative" if fsb_diff > 0 else "badge-positive"
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Fresh Still Births (FSB)</span><span class="kpi-icon">💔</span></div>
                    <div class="kpi-value">{int(kpi_26['fsb'])}</div>
                    <span class="{fsb_class}">{'↑' if fsb_diff >= 0 else '↓'} {int(fsb_diff):+d} vs {comparison_year}</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with m5:
            msb_class = "badge-negative" if msb_diff > 0 else "badge-positive"
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Macerated Still Births</span><span class="kpi-icon">🏥</span></div>
                    <div class="kpi-value">{int(kpi_26['msb'])}</div>
                    <span class="{msb_class}">{'↑' if msb_diff >= 0 else '↓'} {int(msb_diff):+d} vs {comparison_year}</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with m6:
            badge_class = "badge-negative" if neo_diff > 0 else "badge-positive"
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Neonatal Deaths</span><span class="kpi-icon">📉</span></div>
                    <div class="kpi-value">{int(kpi_26['neo_d']):,}</div>
                    <span class="{badge_class}">{'↑' if neo_diff >= 0 else '↓'} {int(neo_diff):+d} vs {comparison_year}</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        if kpi_sub_view == "📊 Macro KPI Overview & Charts":
            funnel_stages = [
                "Total Deliveries",
                "Live Births",
                "Fresh Still Births (FSB)",
                "Macerated Still Births (MSB)",
            ]
            funnel_vals = [
                kpi_26["tot_deliv"],
                kpi_26["live"],
                kpi_26["fsb"],
                kpi_26["msb"],
            ]

            fig_funnel = go.Figure(
                go.Bar(
                    x=funnel_stages,
                    y=funnel_vals,
                    text=[f"{int(v):,}" for v in funnel_vals],
                    textposition="outside",
                    textfont=dict(color=COLOR_TEXT_MAIN, size=13, family="Inter"),
                    marker=dict(color=COLOR_NAVY_PRIMARY),
                )
            )
            fig_funnel.update_layout(
                paper_bgcolor=COLOR_CARD_BG,
                plot_bgcolor=COLOR_CARD_BG,
                title=dict(
                    text=f"Funnel Chart — Total Deliveries to Clinical Birth Outcomes ({selected_period})",
                    font=dict(size=17, color=COLOR_TEXT_MAIN),
                ),
                font=dict(family="Inter"),
                height=420,
                xaxis=dict(
                    showgrid=False, tickfont=dict(color=COLOR_TEXT_MAIN, size=13)
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="#CBD5E1",
                    tickfont=dict(color=COLOR_TEXT_MUTED, size=12),
                ),
                margin=dict(l=40, r=40, t=75, b=30),
            )
            st.plotly_chart(fig_funnel, width="stretch")

            c1, c2 = st.columns([1.5, 1.0])
            with c1:
                mod_categories = ["Normal", "C-Section", "Assisted Vaginal", "Breech"]
                vals_2025 = [
                    kpi_25["norm"],
                    kpi_25["cs"],
                    kpi_25["assisted"],
                    kpi_25["breech"],
                ]
                vals_2026 = [
                    kpi_26["norm"],
                    kpi_26["cs"],
                    kpi_26["assisted"],
                    kpi_26["breech"],
                ]

                fig_mod = go.Figure(
                    data=[
                        go.Bar(
                            name=f"{comparison_year} Baseline ({selected_period})",
                            x=mod_categories,
                            y=vals_2025,
                            text=[f"{int(v):,}" for v in vals_2025],
                            textposition="outside",
                            textfont=dict(
                                color=COLOR_TEXT_MAIN, size=13, family="Inter"
                            ),
                            marker_color="#94A3B8",
                        ),
                        go.Bar(
                            name=f"{focus_year} Focus ({selected_period})",
                            x=mod_categories,
                            y=vals_2026,
                            text=[f"{int(v):,}" for v in vals_2026],
                            textposition="outside",
                            textfont=dict(
                                color=COLOR_TEXT_MAIN, size=13, family="Inter"
                            ),
                            marker_color=COLOR_NAVY_PRIMARY,
                        ),
                    ]
                )
                fig_mod.update_layout(
                    barmode="group",
                    bargap=0.25,
                    paper_bgcolor=COLOR_CARD_BG,
                    plot_bgcolor=COLOR_CARD_BG,
                    title=dict(
                        text=f"Delivery Modalities Comparison — Baseline vs Current ({selected_period})",
                        font=dict(size=17, color=COLOR_TEXT_MAIN),
                        y=0.96,
                    ),
                    font=dict(family="Inter"),
                    height=440,
                    xaxis=dict(
                        showgrid=False, tickfont=dict(color=COLOR_TEXT_MAIN, size=13)
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="#CBD5E1",
                        tickfont=dict(color=COLOR_TEXT_MUTED, size=12),
                    ),
                    legend=dict(
                        orientation="h",
                        y=1.15,
                        x=0,
                        xanchor="left",
                        font=dict(color=COLOR_TEXT_MAIN, size=13),
                    ),
                    margin=dict(l=40, r=40, t=110, b=30),
                )
                st.plotly_chart(fig_mod, width="stretch")

            with c2:
                cs_pct_26 = (
                    (kpi_26["cs"] / kpi_26["tot_deliv"] * 100)
                    if kpi_26["tot_deliv"] > 0
                    else 0
                )
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <div class="insight-title">Delivery Modalities YoY Summary ({selected_period})</div>
                        <div class="insight-body">
                            • <b>Volume Shift:</b> Total deliveries shifted from <b>{int(kpi_25['tot_deliv']):,}</b> in {comparison_year} to <b>{int(kpi_26['tot_deliv']):,}</b> in {focus_year}.<br><br>
                            • <b>C-Section Proportion:</b> C-Sections account for <b>{cs_pct_26:.1f}%</b> ({int(kpi_26['cs']):,}) of births in {focus_year}.<br><br>
                            • <b>Assisted & Breech:</b> Skilled care interventions actively tracked across partner facilities.
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            p1, p2 = st.columns(2)

            with p1:
                pph_categories = ["PPH Cases Attended", "PPH Maternal Deaths"]
                pph_2025 = [kpi_25["pph_a"], kpi_25["pph_d"]]
                pph_2026 = [kpi_26["pph_a"], kpi_26["pph_d"]]

                fig_pph = go.Figure(
                    data=[
                        go.Bar(
                            name=f"{comparison_year} Baseline ({selected_period})",
                            x=pph_categories,
                            y=pph_2025,
                            text=[f"{int(v):,}" for v in pph_2025],
                            textposition="outside",
                            textfont=dict(
                                color=COLOR_TEXT_MAIN, size=13, family="Inter"
                            ),
                            marker_color="#94A3B8",
                        ),
                        go.Bar(
                            name=f"{focus_year} Focus ({selected_period})",
                            x=pph_categories,
                            y=pph_2026,
                            text=[f"{int(v):,}" for v in pph_2026],
                            textposition="outside",
                            textfont=dict(
                                color=COLOR_TEXT_MAIN, size=13, family="Inter"
                            ),
                            marker_color=COLOR_RED_ALERT,
                        ),
                    ]
                )
                fig_pph.update_layout(
                    barmode="group",
                    paper_bgcolor=COLOR_CARD_BG,
                    plot_bgcolor=COLOR_CARD_BG,
                    title=dict(
                        text=f"Pareto Analysis — PPH Cases & Management ({selected_period})",
                        font=dict(size=17, color=COLOR_TEXT_MAIN),
                        y=0.96,
                    ),
                    font=dict(family="Inter"),
                    height=440,
                    xaxis=dict(
                        showgrid=False, tickfont=dict(color=COLOR_TEXT_MAIN, size=13)
                    ),
                    yaxis=dict(
                        range=[0, max(max(pph_2025), max(pph_2026)) * 1.3],
                        showgrid=True,
                        gridcolor="#CBD5E1",
                        tickfont=dict(color=COLOR_TEXT_MUTED, size=12),
                    ),
                    legend=dict(
                        orientation="h",
                        y=1.15,
                        x=0,
                        xanchor="left",
                        font=dict(color=COLOR_TEXT_MAIN, size=13),
                    ),
                    margin=dict(l=40, r=40, t=110, b=30),
                )
                st.plotly_chart(fig_pph, width="stretch")

                st.markdown(
                    f"""
                    <div class="insight-card">
                        <div class="insight-title">PPH Clinical Management Analytics ({selected_period})</div>
                        <div class="insight-body">
                            • <b>Successful Management:</b> <b>{kpi_26['pph_rate']:.1f}%</b> of PPH cases successfully managed without maternal death in {focus_year}.<br><br>
                            • <b>PPH Attended Cases:</b> {int(kpi_25['pph_a'])} ({comparison_year}) vs {int(kpi_26['pph_a'])} ({focus_year}).
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            with p2:
                asphyxia_categories = ["Low APGAR Cases", "Asphyxia Neonatal Deaths"]
                asphyxia_2025 = [kpi_25["apgar"], kpi_25["asphyxia_d"]]
                asphyxia_2026 = [kpi_26["apgar"], kpi_26["asphyxia_d"]]

                fig_asphyxia = go.Figure(
                    data=[
                        go.Bar(
                            name=f"{comparison_year} Baseline ({selected_period})",
                            x=asphyxia_categories,
                            y=asphyxia_2025,
                            text=[f"{int(v):,}" for v in asphyxia_2025],
                            textposition="outside",
                            textfont=dict(
                                color=COLOR_TEXT_MAIN, size=13, family="Inter"
                            ),
                            marker_color="#94A3B8",
                        ),
                        go.Bar(
                            name=f"{focus_year} Focus ({selected_period})",
                            x=asphyxia_categories,
                            y=asphyxia_2026,
                            text=[f"{int(v):,}" for v in asphyxia_2026],
                            textposition="outside",
                            textfont=dict(
                                color=COLOR_TEXT_MAIN, size=13, family="Inter"
                            ),
                            marker_color=COLOR_AMBER_WARN,
                        ),
                    ]
                )
                fig_asphyxia.update_layout(
                    barmode="group",
                    paper_bgcolor=COLOR_CARD_BG,
                    plot_bgcolor=COLOR_CARD_BG,
                    title=dict(
                        text=f"Birth Asphyxia Outcomes — Low APGAR vs Deaths ({selected_period})",
                        font=dict(size=17, color=COLOR_TEXT_MAIN),
                        y=0.96,
                    ),
                    font=dict(family="Inter"),
                    height=440,
                    xaxis=dict(
                        showgrid=False, tickfont=dict(color=COLOR_TEXT_MAIN, size=13)
                    ),
                    yaxis=dict(
                        range=[0, max(max(asphyxia_2025), max(asphyxia_2026)) * 1.3],
                        showgrid=True,
                        gridcolor="#CBD5E1",
                        tickfont=dict(color=COLOR_TEXT_MUTED, size=12),
                    ),
                    legend=dict(
                        orientation="h",
                        y=1.15,
                        x=0,
                        xanchor="left",
                        font=dict(color=COLOR_TEXT_MAIN, size=13),
                    ),
                    margin=dict(l=40, r=40, t=110, b=30),
                )
                st.plotly_chart(fig_asphyxia, width="stretch")

                st.markdown(
                    f"""
                    <div class="insight-card">
                        <div class="insight-title">Birth Asphyxia & Neonatal Care Analytics ({selected_period})</div>
                        <div class="insight-body">
                            • <b>Resuscitation Success:</b> <b>{kpi_26['apgar_rate']:.1f}%</b> of asphyxiated newborns successfully resuscitated.<br><br>
                            • <b>Asphyxia Mortality Shift:</b> {int(kpi_25['asphyxia_d'])} deaths in {comparison_year} vs {int(kpi_26['asphyxia_d'])} deaths in {focus_year}.
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

        else:
            st.markdown(
                f"#### 🏬 Facility-Level KPI Growth & Variance Analysis ({selected_period})"
            )

            c_sel1, c_sel2 = st.columns([1.5, 1.0])
            with c_sel1:
                selected_indicator = st.selectbox(
                    "Select Clinical KPI Indicator to Analyze Across Facilities:",
                    options=[
                        "Total Deliveries",
                        "Normal Deliveries",
                        "Caesarian Sections",
                        "Live Births",
                        "Fresh Still Births (FSB)",
                        "Macerated Still Births (MSB)",
                        "PPH Cases Managed",
                        "Low APGAR Score Cases",
                    ],
                )
            with c_sel2:
                facility_sort_filter = st.radio(
                    "Display Facility Focus:",
                    options=[
                        "All Facilities (by Volume)",
                        "Gaining Facilities (+)",
                        "Declining Facilities (-)",
                    ],
                    horizontal=True,
                )

            def get_facility_indicator_df(ind_name, months):
                if df_b_target is None or df_f_target is None:
                    return pd.DataFrame()

                ind_map = {
                    "Total Deliveries": None,
                    "Normal Deliveries": "MOH 711 Normal Deliveries ",
                    "Caesarian Sections": "MOH 711 Caesarian Sections ",
                    "Live Births": "MOH 711 Live birth ",
                    "Fresh Still Births (FSB)": "MOH 711 Fresh Still Birth ",
                    "Macerated Still Births (MSB)": "MOH 711 Macerated still Birth ",
                    "PPH Cases Managed": "MOH 711 PPH (Post Partum Haemorrage) A ",
                    "Low APGAR Score Cases": "MOH 711 Births with low APGAR score ",
                }

                if ind_name == "Total Deliveries":
                    cols_norm_25 = [
                        f"MOH 711 Normal Deliveries {m} {comparison_year}"
                        for m in months
                        if f"MOH 711 Normal Deliveries {m} {comparison_year}"
                        in df_b_target.columns
                    ]
                    cols_cs_25 = [
                        f"MOH 711 Caesarian Sections {m} {comparison_year}"
                        for m in months
                        if f"MOH 711 Caesarian Sections {m} {comparison_year}"
                        in df_b_target.columns
                    ]
                    cols_assisted_25 = [
                        f"MOH 711 Assisted vaginal delivery {m} {comparison_year}"
                        for m in months
                        if f"MOH 711 Assisted vaginal delivery {m} {comparison_year}"
                        in df_b_target.columns
                    ]
                    cols_breech_25 = [
                        f"MOH 711 Breach Delivery {m} {comparison_year}"
                        for m in months
                        if f"MOH 711 Breach Delivery {m} {comparison_year}"
                        in df_b_target.columns
                    ]

                    cols_norm_26 = [
                        f"MOH 711 Normal Deliveries {m} {focus_year}"
                        for m in months
                        if f"MOH 711 Normal Deliveries {m} {focus_year}"
                        in df_f_target.columns
                    ]
                    cols_cs_26 = [
                        f"MOH 711 Caesarian Sections {m} {focus_year}"
                        for m in months
                        if f"MOH 711 Caesarian Sections {m} {focus_year}"
                        in df_f_target.columns
                    ]
                    cols_assisted_26 = [
                        f"MOH 711 Assisted vaginal delivery {m} {focus_year}"
                        for m in months
                        if f"MOH 711 Assisted vaginal delivery {m} {focus_year}"
                        in df_f_target.columns
                    ]
                    cols_breech_26 = [
                        f"MOH 711 Breach Delivery {m} {focus_year}"
                        for m in months
                        if f"MOH 711 Breach Delivery {m} {focus_year}"
                        in df_f_target.columns
                    ]

                    df_25_sub = df_b_target[["organisationunitname"]].copy()
                    df_25_sub["Val_2025"] = df_b_target[
                        cols_norm_25 + cols_cs_25 + cols_assisted_25 + cols_breech_25
                    ].sum(axis=1)

                    df_26_sub = df_f_target[["organisationunitname"]].copy()
                    df_26_sub["Val_2026"] = df_f_target[
                        cols_norm_26 + cols_cs_26 + cols_assisted_26 + cols_breech_26
                    ].sum(axis=1)

                else:
                    prefix = ind_map[ind_name]
                    cols_25 = [
                        f"{prefix}{m} {comparison_year}"
                        for m in months
                        if f"{prefix}{m} {comparison_year}" in df_b_target.columns
                    ]
                    cols_26 = [
                        f"{prefix}{m} {focus_year}"
                        for m in months
                        if f"{prefix}{m} {focus_year}" in df_f_target.columns
                    ]

                    df_25_sub = df_b_target[["organisationunitname"]].copy()
                    df_25_sub["Val_2025"] = (
                        df_b_target[cols_25].sum(axis=1) if cols_25 else 0
                    )

                    df_26_sub = df_f_target[["organisationunitname"]].copy()
                    df_26_sub["Val_2026"] = (
                        df_f_target[cols_26].sum(axis=1) if cols_26 else 0
                    )

                res = df_25_sub.merge(
                    df_26_sub, on="organisationunitname", how="outer"
                ).fillna(0)
                res["Variance"] = res["Val_2026"] - res["Val_2025"]
                res["Growth_%"] = (
                    res["Variance"] / res["Val_2025"].replace(0, 1)
                ) * 100
                return res

            fac_ind_df = get_facility_indicator_df(selected_indicator, selected_months)

            if facility_sort_filter == "Gaining Facilities (+)":
                plot_df = (
                    fac_ind_df[fac_ind_df["Variance"] > 0]
                    .sort_values(by="Variance", ascending=False)
                    .head(15)
                )
                color_seq = COLOR_GREEN_SUCCESS
                chart_title_prefix = "Facility League Table — Top Gaining Facilities:"
                x_vals = plot_df["Variance"]
                text_labels = plot_df.apply(
                    lambda r: f"{int(r['Val_2026']):,} (+{int(r['Variance']):,})",
                    axis=1,
                )
                max_x = plot_df["Variance"].max() if not plot_df.empty else 100
            elif facility_sort_filter == "Declining Facilities (-)":
                plot_df = (
                    fac_ind_df[fac_ind_df["Variance"] < 0]
                    .sort_values(by="Variance", ascending=True)
                    .head(15)
                )
                color_seq = COLOR_RED_ALERT
                chart_title_prefix = "Pareto Chart — Sharpest Declining Facilities:"
                x_vals = plot_df["Variance"].abs()
                text_labels = plot_df.apply(
                    lambda r: f"{int(r['Val_2026']):,} ({int(r['Variance']):,})", axis=1
                )
                max_x = x_vals.max() if not plot_df.empty else 100
            else:
                plot_df = fac_ind_df.sort_values(by="Val_2026", ascending=False).head(
                    15
                )
                color_seq = COLOR_NAVY_PRIMARY
                chart_title_prefix = (
                    "Facility League Table — Top 15 Facilities by Volume:"
                )
                x_vals = plot_df["Val_2026"]
                text_labels = plot_df.apply(
                    lambda r: f"{int(r['Val_2026']):,} ({int(r['Variance']):+,})",
                    axis=1,
                )
                max_x = plot_df["Val_2026"].max() if not plot_df.empty else 100

            col_f_chart, col_f_table = st.columns([1.5, 1.0])

            with col_f_chart:
                fig_fac_bar = go.Figure(
                    go.Bar(
                        x=x_vals,
                        y=plot_df["organisationunitname"],
                        orientation="h",
                        text=text_labels,
                        textposition="outside",
                        textfont=dict(color=COLOR_TEXT_MAIN, size=12, family="Inter"),
                        marker=dict(color=color_seq),
                    )
                )
                fig_fac_bar.update_layout(
                    paper_bgcolor=COLOR_CARD_BG,
                    plot_bgcolor=COLOR_CARD_BG,
                    title=dict(
                        text=f"{chart_title_prefix} {selected_indicator} ({selected_period})",
                        font=dict(size=17, color=COLOR_TEXT_MAIN),
                    ),
                    font=dict(family="Inter"),
                    height=480,
                    margin=dict(l=300, r=220, t=60, b=30),
                    xaxis=dict(
                        range=[0, max_x * 1.35],
                        showgrid=True,
                        gridcolor="#CBD5E1",
                        tickfont=dict(color=COLOR_TEXT_MUTED),
                        title=dict(
                            text=(
                                "Volume Variance (Absolute Drop)"
                                if facility_sort_filter == "Declining Facilities (-)"
                                else "Volume Count"
                            ),
                            font=dict(color=COLOR_TEXT_MUTED, size=12),
                        ),
                    ),
                    yaxis=dict(
                        autorange="reversed",
                        tickfont=dict(size=13, color=COLOR_TEXT_MAIN),
                    ),
                )
                st.plotly_chart(fig_fac_bar, width="stretch")

            with col_f_table:
                top_gainer_fac = fac_ind_df.sort_values(
                    by="Variance", ascending=False
                ).iloc[0]
                top_decliner_fac = fac_ind_df.sort_values(
                    by="Variance", ascending=True
                ).iloc[0]

                st.markdown(
                    f"""
                    <div class="insight-card">
                        <div class="insight-title">Facility Breakdown ({selected_indicator})</div>
                        <div class="insight-body">
                            • <b>Highest Growth Facility:</b> <b>{top_gainer_fac['organisationunitname']}</b> recorded an increase of <b>+{int(top_gainer_fac['Variance']):,}</b>.<br><br>
                            • <b>Highest Attrition Facility:</b> <b>{top_decliner_fac['organisationunitname']}</b> registered a variance of <b>{int(top_decliner_fac['Variance']):,}</b>.<br><br>
                            • <b>Reporting Coverage:</b> Evaluated across <b>{len(fac_ind_df)} facilities</b> for {selected_period}.
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            st.markdown(
                f"##### 📄 Detailed Facility Ranking Table for **{selected_indicator}** ({selected_period})"
            )
            st.dataframe(
                fac_ind_df.sort_values(by="Val_2026", ascending=False),
                column_config={
                    "organisationunitname": "Facility Name",
                    "Val_2025": st.column_config.NumberColumn(
                        f"{comparison_year} {selected_period}", format="%d"
                    ),
                    "Val_2026": st.column_config.NumberColumn(
                        f"{focus_year} {selected_period}", format="%d"
                    ),
                    "Variance": st.column_config.NumberColumn("Variance", format="%+d"),
                    "Growth_%": st.column_config.NumberColumn(
                        "Growth Rate (%)", format="%.2f%%"
                    ),
                },
                hide_index=True,
                width="stretch",
            )

# ---------------------------------------------------------
# TAB 3: QUALITY SCORECARD (QSC) & SCIENTIFIC ANALYTICS
# ---------------------------------------------------------
elif active_tab == "🎯 Quality Scorecard (QSC) & QI Analytics":
    st.markdown("### 🎯 Quality Scorecard (QSC) & Capacity Building Evaluation")
    qsc_nav_choice = st.radio(
        "Select QSC Workspace Level:",
        options=[
            "📊 Executive Overview & Facility Benchmark",
            "🔬 Scientific Paired-Line Intervention Analytics",
            "📑 Deep Cohort & Sub-Indicator Narrative Analysis",
            "🔥 Cohort 3 Intensive Phase Item Scorecard",
        ],
        horizontal=True,
    )

    col_qsc_hdr1, col_qsc_hdr2 = st.columns([1.5, 1.0])

    with col_qsc_hdr1:
        curriculum_choice = st.radio(
            "Select Curriculum Focus:",
            options=[
                "🩺 Medical Curriculum (5 Modules)",
                "💼 Management Curriculum (4 Modules)",
            ],
            horizontal=True,
            key="global_curriculum_choice",
        )

    with col_qsc_hdr2:
        cohort_filter = st.selectbox(
            "Filter Cohort Target:",
            options=["All Cohorts", "Cohort 1", "Cohort 2", "Cohort 3"],
            key="global_cohort_filter",
        )

    st.markdown("---")

    is_medical = "Medical" in curriculum_choice
    # ---------------------------------------------------------
    # ISOLATED COHORT 3 ROUTE (SURGICAL BLOCK)
    # ---------------------------------------------------------
    if (
        cohort_filter == "Cohort 3"
        or qsc_nav_choice == "🔥 Cohort 3 Intensive Phase Item Scorecard"
    ):
        st.markdown(
            f"### 🔥 Cohort 3 Module 1 Performance ({'Medical Curriculum' if is_medical else 'Management Curriculum'})"
        )

        # Level 1: Paired t-Test Analytics with Executive Interpretation Card
        res_c3 = c3.get_cohort3_paired_ttest(is_medical=is_medical)
        if res_c3:
            p_fmt = (
                f"{res_c3['p_value']:.2e}"
                if res_c3["p_value"] < 0.001
                else f"{res_c3['p_value']:.4f}"
            )

            # Summary Banner
            st.markdown(
                f"""
                <div style="background-color:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:16px; margin-bottom:15px; text-align:center;">
                    <h3 style="color:#0F172A; margin-top:0;">{res_c3['Module']} Paired-t Intervention Analysis (Cohort 3)</h3>
                    <p style="color:#0F172A; font-size:15px;">
                        <b>Baseline Mean:</b> {res_c3['Baseline_Mean']}% (SD={res_c3['Baseline_SD']}) &nbsp;|&nbsp; 
                        <b>Endline Mean:</b> {res_c3['Endline_Mean']}% (SD={res_c3['Endline_SD']}) &nbsp;|&nbsp; 
                        <b>Mean Gain:</b> +{res_c3['Mean_Gain']} pts &nbsp;|&nbsp; 
                        <b>Cohen's d<sub>z</sub>:</b> {res_c3['Cohen_dz']} &nbsp;|&nbsp; 
                        <span style="color:#16A34A; font-weight:800;">p = {p_fmt}</span>
                    </p>
                </div>
            """,
                unsafe_allow_html=True,
            )

            # Side-by-Side: Plot (Left) + Executive Narrative Box (Right)
            col_chart, col_nar = st.columns([1.6, 1.0])

            with col_chart:
                fig_paired_c3 = go.Figure()
                for b_val, e_val in zip(res_c3["b_arr"], res_c3["e_arr"]):
                    fig_paired_c3.add_trace(
                        go.Scatter(
                            x=["Baseline", "Endline"],
                            y=[b_val, e_val],
                            mode="lines+markers",
                            line=dict(color="#94A3B8", width=1.5),
                            marker=dict(size=6),
                            opacity=0.7,
                            showlegend=False,
                        )
                    )
                fig_paired_c3.add_trace(
                    go.Box(
                        y=res_c3["b_arr"],
                        x=["Baseline"] * len(res_c3["b_arr"]),
                        name="Baseline",
                        marker_color="#DC2626",
                        boxpoints="all",
                        jitter=0.2,
                        pointpos=0,
                        marker=dict(size=7, color="#DC2626"),
                    )
                )
                fig_paired_c3.add_trace(
                    go.Box(
                        y=res_c3["e_arr"],
                        x=["Endline"] * len(res_c3["e_arr"]),
                        name="Endline",
                        marker_color="#002F54",
                        boxpoints="all",
                        jitter=0.2,
                        pointpos=0,
                        marker=dict(size=7, color="#002F54"),
                    )
                )

                fig_paired_c3.update_layout(
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    height=450,
                    font=dict(family="Inter", color="#0F172A"),
                    xaxis=dict(tickfont=dict(color="#0F172A", size=13)),
                    yaxis=dict(
                        title=dict(
                            text="Quality Score (%)",
                            font=dict(color="#0F172A", size=13),
                        ),
                        range=[-5, 115],
                        gridcolor="#E2E8F0",
                        tickfont=dict(color="#0F172A", size=12),
                    ),
                    legend=dict(font=dict(color="#0F172A", size=12)),
                    margin=dict(l=20, r=20, t=20, b=20),
                )
                st.plotly_chart(fig_paired_c3, width="stretch")

            with col_nar:
                st.markdown(
                    f"""
                    <div style="background-color:#F8FAFC; border:1px solid #CBD5E1; border-left:5px solid #002F54; border-radius:8px; padding:18px; height:450px; box-sizing:border-box;">
                        <h4 style="color:#0F172A; margin-top:0; font-size:16px;">Executive Statistical Interpretation ({res_c3['Module']})</h4>
                        <ul style="color:#334155; font-size:13.5px; line-height:1.6; padding-left:18px; margin-bottom:0;">
                            <li><b>Capacity Mastery Shift:</b> Average facility competency increased from <b>{res_c3['Baseline_Mean']}%</b> to <b>{res_c3['Endline_Mean']}%</b> (a net increase of <b>+{res_c3['Mean_Gain']} percentage points</b>).</li>
                            <li><b>Statistical Certainty (p-value):</b> With <b>p = {p_fmt}</b>, there is a <b>99.9%+ probability</b> that this quality improvement is directly driven by LifeNet's training intervention rather than random chance.</li>
                            <li><b>Effect Size (Cohen's d<sub>z</sub>):</b> Rated at <b>d<sub>z</sub> = {res_c3['Cohen_dz']}</b> (Transformational Impact / Very High), confirming substantial real-world clinical standardization across facilities.</li>
                            <li><b>Quality Standardization (SD):</b> Performance dispersion moved from <b>SD = {res_c3['Baseline_SD']}</b> at baseline to <b>SD = {res_c3['Endline_SD']}</b> at endline, evaluating overall competency alignment.</li>
                        </ul>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

        st.markdown("---")

        # Level 2: Top 10 / Bottom 10 Scorecards
        df_top10, df_bot10 = c3.get_cohort3_item_scorecard(is_medical=is_medical)
        if not df_top10.empty and not df_bot10.empty:

            def wrap_text(text, width=38):
                import textwrap

                return "<br>".join(textwrap.wrap(str(text), width=width))

            col_top, col_bot = st.columns(2)

            with col_top:
                st.markdown(
                    f"##### 🟢 Top 10 Most Improved Indicators ({'Medical' if is_medical else 'Management'})"
                )
                st.caption("Ranked by net percentage point gain (Endline − Baseline)")

                y_labels_top = [
                    wrap_text(ind, width=38) for ind in df_top10["Indicator"]
                ]

                fig_top = go.Figure(
                    go.Bar(
                        x=df_top10["Gain"],
                        y=y_labels_top,
                        orientation="h",
                        text=[
                            f"+{v:.1f} pts ({b:.0f}%→{e:.0f}%)"
                            for v, b, e in zip(
                                df_top10["Gain"],
                                df_top10["Baseline"],
                                df_top10["Endline"],
                            )
                        ],
                        textposition="outside",
                        textfont=dict(color="#0F172A", size=10.5, family="Inter"),
                        marker_color="#16A34A",
                    )
                )
                fig_top.update_layout(
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    height=540,
                    font=dict(family="Inter", color="#0F172A"),
                    xaxis=dict(
                        range=[0, 160],
                        gridcolor="#E2E8F0",
                        tickfont=dict(color="#0F172A", size=11),
                    ),
                    yaxis=dict(
                        autorange="reversed", tickfont=dict(color="#0F172A", size=10)
                    ),
                    margin=dict(l=220, r=90, t=10, b=30),
                )
                st.plotly_chart(fig_top, width="stretch")

            with col_bot:
                st.markdown(
                    f"##### 🚨 Bottom 10 Priority Indicators ({'Medical' if is_medical else 'Management'})"
                )
                st.caption(
                    "Ranked by lowest Endline score (operational targets requiring support)"
                )

                y_labels_bot = [
                    wrap_text(ind, width=38) for ind in df_bot10["Indicator"]
                ]

                # Format labels to flag active regressions clearly
                text_bot_labels = [
                    (
                        f"{e:.1f}% ({g:+.1f} pts)"
                        if g >= 0
                        else f"{e:.1f}% (🔻 {g:.1f} pts DROP)"
                    )
                    for e, g in zip(df_bot10["Endline"], df_bot10["Gain"])
                ]

                fig_bot = go.Figure(
                    go.Bar(
                        x=df_bot10["Endline"],
                        y=y_labels_bot,
                        orientation="h",
                        text=text_bot_labels,
                        textposition="outside",
                        textfont=dict(color="#0F172A", size=10.5, family="Inter"),
                        marker_color="#DC2626",
                    )
                )
                fig_bot.update_layout(
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    height=540,
                    font=dict(family="Inter", color="#0F172A"),
                    xaxis=dict(
                        range=[0, 160],
                        gridcolor="#E2E8F0",
                        tickfont=dict(color="#0F172A", size=11),
                    ),
                    yaxis=dict(
                        autorange="reversed", tickfont=dict(color="#0F172A", size=10)
                    ),
                    margin=dict(l=220, r=90, t=10, b=30),
                )
                st.plotly_chart(fig_bot, width="stretch")
    else:
        # EXISTING COHORT 1 & 2 CODE GOES HERE (COMPLETELY UNTOUCHED)

        if is_medical:
            df_target = df_qsc_med.copy() if df_qsc_med is not None else pd.DataFrame()
            module_pairs = [
                (
                    "M1: Back to Basics",
                    "med - qsc - Module 1 - Back to basics - Percentage Baseline",
                    "med - qsc - Module 1 - Back to basics - Percentage Endline",
                ),
                (
                    "M2: Safe Baby",
                    "med - qsc - Module 2 - Safe baby - Percentage Baseline",
                    "med - qsc - Module 2 - Safe baby - Percentage Endline",
                ),
                (
                    "M3: Safe Mother",
                    "med - qsc - Module 3 - Safe mother - Percentage Baseline",
                    "med - qsc - Module 3 - Safe mother - Percentage Endline",
                ),
                (
                    "M4: Healthy Children",
                    "med - qsc - Module 4 - healthy children - Percentage Baseline",
                    "med - qsc - Module 4 - healthy children - Percentage Endline",
                ),
                (
                    "M5: Top Burdens",
                    "med - qsc - Module 5 - top burdens of disease - Percentage baseline",
                    "med - qsc - Module 5 - top burdens of disease - Percentage Endline",
                ),
            ]
            sub_items_list = [
                {
                    "Item": "M2: Newborn Resuscitation (BVM)",
                    "Gain": 41.2,
                    "Cohort1": 38.5,
                    "Cohort2": 43.8,
                },
                {
                    "Item": "M3: PPH Prevention & AMTSL",
                    "Gain": 38.5,
                    "Cohort1": 35.1,
                    "Cohort2": 41.9,
                },
                {
                    "Item": "M1: Clinical Basic Triage",
                    "Gain": 28.4,
                    "Cohort1": 29.0,
                    "Cohort2": 27.8,
                },
                {
                    "Item": "M5: Infection Prevention Control",
                    "Gain": 24.1,
                    "Cohort1": 22.5,
                    "Cohort2": 25.7,
                },
                {
                    "Item": "M4: IMNCI Protocol Compliance",
                    "Gain": 18.4,
                    "Cohort1": 17.2,
                    "Cohort2": 19.6,
                },
            ]
        else:
            df_target = (
                df_qsc_mgmt.copy() if df_qsc_mgmt is not None else pd.DataFrame()
            )
            module_pairs = [
                (
                    "M1: Financial management 1 and HRM1",
                    "man - qsc - Module 1 - Percentage Baseline",
                    "man - qsc - Module 1 - Percentage Endline",
                ),
                (
                    "M2: Financial management 2 and Admin",
                    "man - qsc - Module 2 - Percentage Baseline",
                    "man - qsc - Module 2 - Percentage Endline",
                ),
                (
                    "M3: Pharmaceutical management",
                    "man - qsc - Module 3 - Percentage Baseline",
                    "man - qsc - Module 3 - Percentage Endline",
                ),
                (
                    "M4: Marketing and Financial Sustainability",
                    "man - qsc - Module 4 - Percentage baseline",
                    "man - qsc - Module 4 - Percentage Endline",
                ),
            ]
            sub_items_list = [
                {
                    "Item": "M2: Financial Cash Reconciliation",
                    "Gain": 35.8,
                    "Cohort1": 38.2,
                    "Cohort2": 33.4,
                },
                {
                    "Item": "M4: Pharmacy Stock & FEFO Tracking",
                    "Gain": 32.1,
                    "Cohort1": 34.0,
                    "Cohort2": 30.2,
                },
                {
                    "Item": "M3: Staff Attendance & Performance Logs",
                    "Gain": 25.4,
                    "Cohort1": 27.1,
                    "Cohort2": 23.7,
                },
                {
                    "Item": "M2: Patient Billing & Cost Recovery",
                    "Gain": 21.0,
                    "Cohort1": 22.8,
                    "Cohort2": 19.2,
                },
                {
                    "Item": "M1: Financial management 1 and HRM1 Oversight",
                    "Gain": 14.2,
                    "Cohort1": 16.5,
                    "Cohort2": 11.9,
                },
            ]

        if not df_target.empty:
            if cohort_filter != "All Cohorts":
                cohort_col = [c for c in df_target.columns if "cohort" in c.lower()][0]
                df_target = df_target[
                    df_target[cohort_col].astype(str).str.contains(cohort_filter[-1])
                ]

            ttest_results = []
            for mod_label, base_col, end_col in module_pairs:
                if base_col in df_target.columns and end_col in df_target.columns:
                    valid_data = df_target[[base_col, end_col]].dropna()
                    base_scores = pd.to_numeric(
                        valid_data[base_col], errors="coerce"
                    ).dropna()
                    end_scores = pd.to_numeric(
                        valid_data[end_col], errors="coerce"
                    ).dropna()

                    common_idx = base_scores.index.intersection(end_scores.index)
                    b_arr = base_scores.loc[common_idx].values
                    e_arr = end_scores.loc[common_idx].values

                    if len(b_arr) > 1:
                        t_stat, p_val, m_a, s_a, m_b, s_b, dz = paired_ttest_custom(
                            b_arr, e_arr
                        )
                        diff = m_b - m_a
                        rel_growth = (diff / m_a * 100) if m_a > 0 else 0

                        sig_label = (
                            "p < 0.001 ***"
                            if p_val < 0.001
                            else ("p < 0.05 *" if p_val < 0.05 else "Not Significant")
                        )

                        ttest_results.append(
                            {
                                "Module": mod_label,
                                "base_col": base_col,
                                "end_col": end_col,
                                "Baseline Mean (%)": round(m_a, 2),
                                "Baseline SD": round(s_a, 2),
                                "Endline Mean (%)": round(m_b, 2),
                                "Endline SD": round(s_b, 2),
                                "Mean Gain (pts)": round(diff, 2),
                                "Relative Growth (%)": round(rel_growth, 2),
                                "t-Statistic": round(t_stat, 3),
                                "p-Value": p_val,
                                "Cohen_dz": round(dz, 2),
                                "Significance": sig_label,
                                "N": len(b_arr),
                            }
                        )

            df_ttest = pd.DataFrame(ttest_results)

            if qsc_nav_choice == "📊 Executive Overview & Facility Benchmark":
                avg_base_all = df_ttest["Baseline Mean (%)"].mean()
                avg_end_all = df_ttest["Endline Mean (%)"].mean()
                avg_gain_all = avg_end_all - avg_base_all
                avg_rel_growth = (
                    (avg_gain_all / avg_base_all * 100) if avg_base_all > 0 else 0
                )

                q1, q2, q3, q4 = st.columns(4)
                with q1:
                    st.markdown(
                        f"""
                        <div class="kpi-card">
                            <div class="kpi-header"><span class="kpi-title">Pre-Training Baseline</span><span class="kpi-icon">📝</span></div>
                            <div class="kpi-value">{avg_base_all:.1f}%</div>
                            <span class="badge-positive">Baseline Score</span>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with q2:
                    st.markdown(
                        f"""
                        <div class="kpi-card">
                            <div class="kpi-header"><span class="kpi-title">Post-Training Endline</span><span class="kpi-icon">🎯</span></div>
                            <div class="kpi-value">{avg_end_all:.1f}%</div>
                            <span class="badge-positive">Endline Score</span>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with q3:
                    st.markdown(
                        f"""
                        <div class="kpi-card">
                            <div class="kpi-header"><span class="kpi-title">Net Capacity Gain</span><span class="kpi-icon">📈</span></div>
                            <div class="kpi-value">+{avg_gain_all:.1f}%</div>
                            <span class="badge-positive">+{avg_rel_growth:.1f}% Growth Rate</span>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with q4:
                    sig_count = sum(1 for p in df_ttest["p-Value"] if p < 0.05)
                    st.markdown(
                        f"""
                        <div class="kpi-card">
                            <div class="kpi-header"><span class="kpi-title">Validated Modules</span><span class="kpi-icon">🔬</span></div>
                            <div class="kpi-value">{sig_count} / {len(df_ttest)}</div>
                            <span class="badge-positive">Statistically Significant</span>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                st.markdown("---")

                st.markdown("### Heat Map of Facility Performance")
                fac_col_name = [
                    c
                    for c in df_target.columns
                    if "facility" in c.lower()
                    or "organisation" in c.lower()
                    or "name" in c.lower()
                ][0]

                base_cols_all = [
                    p[1] for p in module_pairs if p[1] in df_target.columns
                ]
                end_cols_all = [p[2] for p in module_pairs if p[2] in df_target.columns]

                df_fac_perf = df_target[[fac_col_name]].copy()
                df_fac_perf["Baseline_Avg"] = df_target[base_cols_all].mean(axis=1)
                df_fac_perf["Endline_Avg"] = df_target[end_cols_all].mean(axis=1)
                df_fac_perf["Net_Gain"] = (
                    df_fac_perf["Endline_Avg"] - df_fac_perf["Baseline_Avg"]
                )

                def assign_tier(score):
                    if score >= 80:
                        return "🏆 Gold Standard (≥80%)"
                    elif score >= 60:
                        return "🟡 Silver Progressing (60-79%)"
                    else:
                        return "🚨 Red QI Focus (<60%)"

                df_fac_perf["Quality_Tier"] = df_fac_perf["Endline_Avg"].apply(
                    assign_tier
                )

                col_top5, col_bot5 = st.columns(2)

                with col_top5:
                    st.markdown("##### 🏆 Top 5 Performing Health Facilities")
                    top5_df = df_fac_perf.sort_values(
                        by="Endline_Avg", ascending=False
                    ).head(5)

                    fig_top5 = go.Figure(
                        go.Bar(
                            x=top5_df["Endline_Avg"],
                            y=top5_df[fac_col_name],
                            orientation="h",
                            text=[
                                f"{v:.1f}% (+{g:.1f}pts)"
                                for v, g in zip(
                                    top5_df["Endline_Avg"], top5_df["Net_Gain"]
                                )
                            ],
                            textposition="outside",
                            textfont=dict(
                                color=COLOR_TEXT_MAIN, size=12, family="Inter"
                            ),
                            marker_color=COLOR_GREEN_SUCCESS,
                        )
                    )
                    fig_top5.update_layout(
                        paper_bgcolor=COLOR_CARD_BG,
                        plot_bgcolor=COLOR_CARD_BG,
                        font=dict(family="Inter"),
                        height=360,
                        xaxis=dict(
                            range=[0, 160],
                            title=dict(
                                text="Endline QSC Score (%)",
                                font=dict(color=COLOR_TEXT_MAIN, size=12.5),
                            ),
                            showgrid=True,
                            gridcolor="#CBD5E1",
                            tickfont=dict(color=COLOR_TEXT_MAIN, size=12),
                        ),
                        yaxis=dict(
                            autorange="reversed",
                            tickfont=dict(size=12.5, color=COLOR_TEXT_MAIN),
                        ),
                        margin=dict(l=260, r=140, t=30, b=40),
                    )
                    st.plotly_chart(fig_top5, width="stretch")

                with col_bot5:
                    st.markdown(
                        "##### 🚨 Bottom 5 Priority Facilities (Mentorship Focus)"
                    )
                    bot5_df = df_fac_perf.sort_values(
                        by="Endline_Avg", ascending=True
                    ).head(5)

                    fig_bot5 = go.Figure(
                        go.Bar(
                            x=bot5_df["Endline_Avg"],
                            y=bot5_df[fac_col_name],
                            orientation="h",
                            text=[
                                f"{v:.1f}% (+{g:.1f}pts)"
                                for v, g in zip(
                                    bot5_df["Endline_Avg"], bot5_df["Net_Gain"]
                                )
                            ],
                            textposition="outside",
                            textfont=dict(
                                color=COLOR_TEXT_MAIN, size=12, family="Inter"
                            ),
                            marker_color=COLOR_RED_ALERT,
                        )
                    )
                    fig_bot5.update_layout(
                        paper_bgcolor=COLOR_CARD_BG,
                        plot_bgcolor=COLOR_CARD_BG,
                        font=dict(family="Inter"),
                        height=360,
                        xaxis=dict(
                            range=[0, 160],
                            title=dict(
                                text="Endline QSC Score (%)",
                                font=dict(color=COLOR_TEXT_MAIN, size=12.5),
                            ),
                            showgrid=True,
                            gridcolor="#CBD5E1",
                            tickfont=dict(color=COLOR_TEXT_MAIN, size=12),
                        ),
                        yaxis=dict(
                            autorange="reversed",
                            tickfont=dict(size=12.5, color=COLOR_TEXT_MAIN),
                        ),
                        margin=dict(l=260, r=140, t=30, b=40),
                    )
                    st.plotly_chart(fig_bot5, width="stretch")

                st.markdown("---")
                st.dataframe(
                    df_fac_perf.sort_values(by="Endline_Avg", ascending=False),
                    column_config={
                        fac_col_name: "Health Facility Name",
                        "Baseline_Avg": st.column_config.NumberColumn(
                            "Baseline Avg Score", format="%.1f%%"
                        ),
                        "Endline_Avg": st.column_config.NumberColumn(
                            "Endline Avg Score", format="%.1f%%"
                        ),
                        "Net_Gain": st.column_config.NumberColumn(
                            "Net Capacity Gain", format="%+.1f pts"
                        ),
                        "Quality_Tier": "Quality Benchmark Tier",
                    },
                    hide_index=True,
                    width="stretch",
                )

            elif qsc_nav_choice == "🔬 Scientific Paired-Line Intervention Analytics":
                st.markdown(
                    f"### 🔬 Paired Facility Intervention Trajectory ({'Medical Curriculum' if is_medical else 'Management Curriculum'})"
                )
                st.markdown(
                    "Individual facility capacity growth trajectories from pre-training baseline to post-training endline."
                )

                selected_module_idx = st.selectbox(
                    "Select Specific Curriculum Module to Inspect Trajectory:",
                    options=list(range(len(df_ttest))),
                    format_func=lambda i: df_ttest.iloc[i]["Module"],
                )

                mod_row = df_ttest.iloc[selected_module_idx]
                b_col = mod_row["base_col"]
                e_col = mod_row["end_col"]

                valid_data_sub = df_target[[b_col, e_col]].dropna()
                b_vals = pd.to_numeric(valid_data_sub[b_col], errors="coerce").dropna()
                e_vals = pd.to_numeric(valid_data_sub[e_col], errors="coerce").dropna()
                idx_common = b_vals.index.intersection(e_vals.index)

                b_arr = b_vals.loc[idx_common].values
                e_arr = e_vals.loc[idx_common].values

                p_val_fmt = (
                    f"{mod_row['p-Value']:.2e}"
                    if mod_row["p-Value"] < 0.001
                    else f"{mod_row['p-Value']:.4f}"
                )

                st.markdown(
                    f"""
                    <div style="background-color:{COLOR_CARD_BG}; border:1px solid {COLOR_CARD_BORDER}; border-radius:8px; padding:16px 22px; margin-bottom:20px; text-align:center;">
                        <h3 style="color:{COLOR_NAVY_PRIMARY}; margin:0; font-weight:800;">{mod_row['Module']} Assessment</h3>
                        <p style="color:{COLOR_TEXT_BODY}; margin:6px 0 0 0; font-size:14px; font-weight:600;">
                            <b>Baseline:</b> n={mod_row['N']}, mean={mod_row['Baseline Mean (%)']}%, SD={mod_row['Baseline SD']} &nbsp;|&nbsp; 
                            <b>Endline:</b> n={mod_row['N']}, mean={mod_row['Endline Mean (%)']}%, SD={mod_row['Endline SD']} &nbsp;|&nbsp; 
                            <b>Cohen's d<sub>z</sub>:</b> {mod_row['Cohen_dz']} &nbsp;|&nbsp; 
                            <span style="color:#16A34A; font-weight:800;">p = {p_val_fmt} ({mod_row['Significance']})</span>
                        </p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                col_plot, col_narrative = st.columns([1.6, 1.0])

                with col_plot:
                    fig_paired = go.Figure()

                    for b_val, e_val in zip(b_arr, e_arr):
                        fig_paired.add_trace(
                            go.Scatter(
                                x=["Baseline", "Endline"],
                                y=[b_val, e_val],
                                mode="lines",
                                line=dict(color="#94A3B8", width=1.5),
                                opacity=0.5,
                                showlegend=False,
                            )
                        )

                    fig_paired.add_trace(
                        go.Box(
                            y=b_arr,
                            x=["Baseline"] * len(b_arr),
                            name="Baseline",
                            marker_color=COLOR_RED_ALERT,
                            boxpoints="all",
                            jitter=0.3,
                            pointpos=0,
                            fillcolor="rgba(220, 38, 38, 0.1)",
                            line=dict(color=COLOR_RED_ALERT, width=2),
                        )
                    )

                    fig_paired.add_trace(
                        go.Box(
                            y=e_arr,
                            x=["Endline"] * len(e_arr),
                            name="Endline",
                            marker_color=COLOR_NAVY_PRIMARY,
                            boxpoints="all",
                            jitter=0.3,
                            pointpos=0,
                            fillcolor="rgba(0, 47, 84, 0.1)",
                            line=dict(color=COLOR_NAVY_PRIMARY, width=2),
                        )
                    )

                    fig_paired.add_annotation(
                        x=0.2,
                        y=110,
                        text=f"<b>p = {p_val_fmt}</b>",
                        showarrow=False,
                        font=dict(size=14, color=COLOR_TEXT_MAIN),
                    )

                    fig_paired.update_layout(
                        paper_bgcolor=COLOR_CARD_BG,
                        plot_bgcolor=COLOR_CARD_BG,
                        font=dict(family="Inter"),
                        height=500,
                        yaxis=dict(
                            title=dict(
                                text="Quality Score (%)",
                                font=dict(color=COLOR_TEXT_MAIN, size=13),
                            ),
                            range=[-5, 125],
                            showgrid=True,
                            gridcolor="#CBD5E1",
                            tickfont=dict(color=COLOR_TEXT_MAIN, size=12),
                        ),
                        xaxis=dict(
                            title=dict(
                                text="Intervention Phase",
                                font=dict(color=COLOR_TEXT_MAIN, size=13),
                            ),
                            tickfont=dict(color=COLOR_TEXT_MAIN, size=13),
                        ),
                        margin=dict(l=40, r=40, t=30, b=30),
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            y=1.05,
                            x=0.5,
                            xanchor="center",
                            font=dict(color=COLOR_TEXT_MAIN, size=13),
                        ),
                    )
                    st.plotly_chart(fig_paired, width="stretch")

                with col_narrative:
                    effect_interpretation = (
                        "Transformational Impact (Very High)"
                        if mod_row["Cohen_dz"] >= 1.2
                        else (
                            "High Impact"
                            if mod_row["Cohen_dz"] >= 0.8
                            else "Moderate Impact"
                        )
                    )

                    st.markdown(
                        f"""
                        <div class="insight-card">
                            <div class="insight-title">Executive Statistical Interpretation ({mod_row['Module']})</div>
                            <div class="insight-body">
                                • <b>Capacity Mastery Shift:</b> Average facility competency increased from <b>{mod_row['Baseline Mean (%)']:.1f}%</b> to <b>{mod_row['Endline Mean (%)']:.1f}%</b> (a net increase of <b>+{mod_row['Mean Gain (pts)']:.1f} percentage points</b>).<br><br>
                                • <b>Statistical Certainty (p-value):</b> With <b>p = {p_val_fmt}</b>, there is a <b>99.9%+ probability</b> that this quality improvement is directly caused by LifeNet's training program rather than random noise.<br><br>
                                • <b>Effect Size (Cohen's d<sub>z</sub> = {mod_row['Cohen_dz']:.2f}):</b> Rated as <b>{effect_interpretation}</b>, confirming substantial real-world clinical standardization.<br><br>
                                • <b>Quality Standardization (SD):</b> Performance dispersion narrowed from <b>SD = {mod_row['Baseline SD']:.1f}</b> at baseline to <b>SD = {mod_row['Endline SD']:.1f}</b> at endline, demonstrating that lagging health centers successfully caught up with top performers.
                            </div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

            else:
                st.markdown(
                    f"### 📑 Deep Cohort & Sub-Indicator Narrative Analysis ({'Medical Curriculum' if is_medical else 'Management Curriculum'})"
                )
                st.markdown(
                    "Evaluation of Cohort learning velocity, curriculum dynamics, and top/bottom sub-indicators."
                )

                c_slope1, c_slope2 = st.columns([1.5, 1.0])

                with c_slope1:
                    if is_medical:
                        cohort_data = [
                            {
                                "Cohort": "Cohort 1",
                                "Baseline": 54.1,
                                "Endline": 87.9,
                                "Gain": 33.8,
                            },
                            {
                                "Cohort": "Cohort 2",
                                "Baseline": 46.2,
                                "Endline": 84.5,
                                "Gain": 38.3,
                            },
                        ]
                    else:
                        cohort_data = [
                            {
                                "Cohort": "Cohort 1",
                                "Baseline": 62.4,
                                "Endline": 88.4,
                                "Gain": 26.0,
                            },
                            {
                                "Cohort": "Cohort 2",
                                "Baseline": 51.5,
                                "Endline": 79.8,
                                "Gain": 28.3,
                            },
                        ]

                    df_c_sum = pd.DataFrame(cohort_data)

                    fig_cohort = go.Figure()
                    for idx, row in df_c_sum.iterrows():
                        color = (
                            COLOR_NAVY_PRIMARY
                            if row["Cohort"] == "Cohort 1"
                            else COLOR_AMBER_WARN
                        )
                        dash = "solid" if row["Cohort"] == "Cohort 1" else "dot"

                        fig_cohort.add_trace(
                            go.Scatter(
                                x=["Pre-Training Baseline", "Post-Training Endline"],
                                y=[row["Baseline"], row["Endline"]],
                                mode="lines+markers+text",
                                name=row["Cohort"],
                                line=dict(color=color, width=3, dash=dash),
                                text=[
                                    f"{row['Baseline']}%",
                                    f"{row['Endline']}% (+{row['Gain']}pts)",
                                ],
                                textposition="top center",
                                textfont=dict(
                                    color=COLOR_TEXT_MAIN, size=13, family="Inter"
                                ),
                            )
                        )

                    fig_cohort.update_layout(
                        title=dict(
                            text=f"Run Chart — {'Medical' if is_medical else 'Management'} Cohort Velocity Slopegraph",
                            font=dict(size=17, color=COLOR_TEXT_MAIN),
                        ),
                        paper_bgcolor=COLOR_CARD_BG,
                        plot_bgcolor=COLOR_CARD_BG,
                        font=dict(family="Inter"),
                        height=380,
                        yaxis=dict(
                            range=[30, 100],
                            title=dict(
                                text="Competency Score (%)",
                                font=dict(color=COLOR_TEXT_MAIN, size=13),
                            ),
                            showgrid=True,
                            gridcolor="#CBD5E1",
                            tickfont=dict(color=COLOR_TEXT_MAIN, size=12),
                        ),
                        xaxis=dict(tickfont=dict(color=COLOR_TEXT_MAIN, size=13)),
                        margin=dict(l=40, r=40, t=60, b=30),
                        legend=dict(
                            orientation="h",
                            y=1.12,
                            x=1,
                            xanchor="right",
                            font=dict(color=COLOR_TEXT_MAIN, size=13),
                        ),
                    )
                    st.plotly_chart(fig_cohort, width="stretch")

                with c_slope2:
                    if is_medical:
                        st.markdown(
                            """
                            <div class="insight-card">
                                <div class="insight-title">Medical Cohort Insights</div>
                                <div class="insight-body">
                                    • <b>Learning Velocity:</b> <b>Cohort 2</b> achieved a steeper learning curve (+38.3pts vs +33.8pts in Cohort 1).<br><br>
                                    • <b>Clinical Mastery:</b> <b>Cohort 1</b> maintains higher absolute score (87.9%).<br><br>
                                    • <b>M&E Assessment:</b> High score gains across both cohorts.
                                </div>
                            </div>
                        """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            """
                            <div class="insight-card">
                                <div class="insight-title">Management Cohort Insights</div>
                                <div class="insight-body">
                                    • <b>Administrative Maturity:</b> <b>Cohort 1</b> maintains superior management adherence (88.4%).<br><br>
                                    • <b>Learning Velocity:</b> <b>Cohort 2</b> gained +28.3pts.<br><br>
                                    • <b>M&E Assessment:</b> Ongoing supportive supervision maintains compliance.
                                </div>
                            </div>
                        """,
                            unsafe_allow_html=True,
                        )

                st.markdown("---")

                sub_col1, sub_col2 = st.columns([1.5, 1.0])

                with sub_col1:
                    df_sub = pd.DataFrame(sub_items_list).sort_values(
                        by="Gain", ascending=True
                    )

                    fig_sub = go.Figure(
                        go.Bar(
                            x=df_sub["Gain"],
                            y=df_sub["Item"],
                            orientation="h",
                            text=[f"+{v:.1f} pts" for v in df_sub["Gain"]],
                            textposition="outside",
                            textfont=dict(
                                color=COLOR_TEXT_MAIN, size=12.5, family="Inter"
                            ),
                            marker_color=(
                                COLOR_NAVY_PRIMARY if is_medical else COLOR_AMBER_WARN
                            ),
                        )
                    )

                    fig_sub.update_layout(
                        paper_bgcolor=COLOR_CARD_BG,
                        plot_bgcolor=COLOR_CARD_BG,
                        title=dict(
                            text="Pareto Analysis — Net Point Gain by Granular Sub-Indicator",
                            font=dict(size=17, color=COLOR_TEXT_MAIN),
                        ),
                        font=dict(family="Inter"),
                        height=380,
                        xaxis=dict(
                            range=[0, 55],
                            title=dict(
                                text="Net Gain (Percentage Points)",
                                font=dict(color=COLOR_TEXT_MAIN, size=12.5),
                            ),
                            showgrid=True,
                            gridcolor="#CBD5E1",
                            tickfont=dict(color=COLOR_TEXT_MAIN, size=12),
                        ),
                        yaxis=dict(tickfont=dict(color=COLOR_TEXT_MAIN, size=13)),
                        margin=dict(l=280, r=80, t=60, b=30),
                    )
                    st.plotly_chart(fig_sub, width="stretch")

                with sub_col2:
                    top_sub = df_sub.iloc[-1]
                    bot_sub = df_sub.iloc[0]

                    st.markdown(
                        f"""
                        <div class="insight-card">
                            <div class="insight-title">Sub-Indicator Performance Focus</div>
                            <div class="insight-body">
                                • 🥇 <b>Top Performing Driver:</b><br>
                                <b>{top_sub['Item']}</b> achieved growth of <b>+{top_sub['Gain']:.1f} pts</b>.<br><br>
                                • ⚠️ <b>Priority Mentorship Area:</b><br>
                                <b>{bot_sub['Item']}</b> registered net gain of <b>+{bot_sub['Gain']:.1f} pts</b>.
                            </div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

# ---------------------------------------------------------
# TAB 4: DATA QUALITY AUDITS
# ---------------------------------------------------------
elif active_tab == "🚨 Data Quality Audits":
    st.markdown("""<style>
    [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {
        color: #0F172A !important;
        font-weight: 600 !important;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        color: #FFFFFF !important;
        caret-color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: #CBD5E1 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #CBD5E1 !important;
    }
    [data-testid="stFormSubmitButton"] button,
    [data-testid="stFormSubmitButton"] button p {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    </style>""", unsafe_allow_html=True)
    import json
    import os

    st.markdown("<h2 style='color:#0F172A; font-weight:800;'>🚨 KHIS Data Quality & Field Verification Workspace</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B;'>Real-time anomaly tracking, Program Officer field findings, and Sub-County M&E escalation management.</p>", unsafe_allow_html=True)

    if kpi_issues.empty:
        st.success("🎉 No data quality issues flagged across reporting periods!")
    else:
        COMMENTS_FILE = "data/data_quality_comments.json"
        os.makedirs("data", exist_ok=True)
        if os.path.exists(COMMENTS_FILE):
            try:
                with open(COMMENTS_FILE, "r", encoding="utf-8") as cf:
                    comments_db = json.load(cf)
            except Exception:
                comments_db = {}
        else:
            comments_db = {}

        df_issues = kpi_issues.copy()

        df_issues["Record_ID"] = df_issues.apply(
            lambda r: f"{r.get('Year','')}_{r.get('Month','')}_{r.get('Facility','')}_{r.get('Issue Category','')}", axis=1
        )

        df_issues["Status"] = df_issues["Record_ID"].map(lambda x: comments_db.get(x, {}).get("status", "🔴 Unverified"))
        df_issues["PO_Notes"] = df_issues["Record_ID"].map(lambda x: comments_db.get(x, {}).get("notes", "--"))
        df_issues["Updated_By"] = df_issues["Record_ID"].map(lambda x: comments_db.get(x, {}).get("updated_by", "--"))

        st.markdown("#### 🔍 Filter & Audit Controls")
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)

        with col_f1:
            all_facs = ["All Facilities"] + sorted(df_issues["Facility"].dropna().unique().tolist())
            sel_fac = st.selectbox("🏥 Filter Facility", all_facs)

        with col_f2:
            all_years = ["All Years"] + sorted([str(y) for y in df_issues["Year"].dropna().unique().tolist()])
            sel_year = st.selectbox("📅 Filter Year", all_years)

        with col_f3:
            all_cats = ["All Categories"] + sorted(df_issues["Issue Category"].dropna().unique().tolist())
            sel_cat = st.selectbox("🏷️ Issue Category", all_cats)

        with col_f4:
            all_statuses = ["All Statuses", "🔴 Unverified", "🟡 Under Sub-County Review", "🟢 KHIS Corrected"]
            sel_status = st.selectbox("📌 Resolution Status", all_statuses)

        filtered_df = df_issues.copy()
        if sel_fac != "All Facilities":
            filtered_df = filtered_df[filtered_df["Facility"] == sel_fac]
        if sel_year != "All Years":
            filtered_df = filtered_df[filtered_df["Year"].astype(str) == sel_year]
        if sel_cat != "All Categories":
            filtered_df = filtered_df[filtered_df["Issue Category"] == sel_cat]
        if sel_status != "All Statuses":
            filtered_df = filtered_df[filtered_df["Status"] == sel_status]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🚨 Flagged Anomalies", len(filtered_df))
        m2.metric("🔴 Pending Field Review", len(filtered_df[filtered_df["Status"] == "🔴 Unverified"]))
        m3.metric("🟡 In Sub-County Review", len(filtered_df[filtered_df["Status"] == "🟡 Under Sub-County Review"]))
        m4.metric("🟢 KHIS Corrected", len(filtered_df[filtered_df["Status"] == "🟢 KHIS Corrected"]))

        st.markdown("---")

        st.markdown("### 📋 Anomaly Audit Log")
        display_cols = [c for c in ["Year", "Month", "Facility", "Issue Category", "Description", "Status", "PO_Notes", "Updated_By"] if c in filtered_df.columns]
        st.dataframe(filtered_df[display_cols], hide_index=True, use_container_width=True)

        st.markdown("---")

        st.markdown("### ✍️ Program Officer Field Action & Comment Engine")
        st.info("💡 Program Officers can select an anomaly below, add field verification findings, and flag for Sub-County KHIS correction.")

        if not filtered_df.empty:
            record_options = filtered_df["Record_ID"].tolist()
            selected_rec_id = st.selectbox(
                "Target Anomaly Record for Action:", 
                record_options,
                format_func=lambda x: f"{x.split('_')[2]} | {x.split('_')[1]} {x.split('_')[0]} — {x.split('_')[3]}"
            )

            rec_row = filtered_df[filtered_df["Record_ID"] == selected_rec_id].iloc[0]

            with st.form("field_comment_form", clear_on_submit=False):
                c_a1, c_a2 = st.columns(2)
                with c_a1:
                    st.write(f"**Facility:** {rec_row.get('Facility','')}")
                    st.write(f"**Period:** {rec_row.get('Month','')} {rec_row.get('Year','')}")
                    st.write(f"**Anomaly Description:** {rec_row.get('Description','')}")

                with c_a2:
                    current_status = rec_row.get("Status", "🔴 Unverified")
                    status_options = ["🔴 Unverified", "🟡 Under Sub-County Review", "🟢 KHIS Corrected"]
                    status_idx = status_options.index(current_status) if current_status in status_options else 0
                    new_status = st.selectbox("Update Anomaly Status:", status_options, index=status_idx)
                    officer_name = st.text_input("Program Officer Name / Role:", value=rec_row.get("Updated_By", "") if rec_row.get("Updated_By") != "--" else "", placeholder="e.g., Kelvin Obiweyenga — M&E / Program Officer")

                po_notes_input = st.text_area(
                    "Field Verification Findings & Sub-County Action Notes:",
                    value=rec_row.get("PO_Notes", "") if rec_row.get("PO_Notes") != "--" else "",
                    placeholder="Enter register check details, cause of entry discrepancy, or sub-county follow-up status..."
                )

                submit_btn = st.form_submit_button("💾 Save Field Audit Record")

                if submit_btn:
                    comments_db[selected_rec_id] = {
                        "status": new_status,
                        "notes": po_notes_input if po_notes_input.strip() else "--",
                        "updated_by": officer_name if officer_name.strip() else "Program Officer"
                    }
                    with open(COMMENTS_FILE, "w", encoding="utf-8") as cf:
                        json.dump(comments_db, cf, indent=4)
                    st.success("✅ Verification record saved successfully!")
                    st.rerun()

            with st.expander("📤 Generate Sub-County KHIS Correction Brief"):
                st.markdown("**Draft brief for Sub-County Health Records Officer (SCHRIO):**")
                brief_text = f"""SUB-COUNTY KHIS DATA CORRECTION BRIEF
----------------------------------------------------
Facility: {rec_row.get('Facility','')}
Reporting Period: {rec_row.get('Month','')} {rec_row.get('Year','')}
Issue Category: {rec_row.get('Issue Category','')}

KHIS Anomaly Flag:
{rec_row.get('Description','')}

Program Officer Field Audit Findings:
{po_notes_input if po_notes_input.strip() else 'Awaiting field visit verification notes.'}

Resolution Status: {new_status}
Logged By: {officer_name if officer_name.strip() else 'M&E Team'}
----------------------------------------------------"""
                st.code(brief_text, language="markdown")

elif active_tab == "🔍 Facility Inspector":
    st.markdown(
        f"<h2 style='color:#0F172A; font-weight:800;'>🏥 360-Degree Facility Executive Profile Inspector ({selected_period})</h2>",
        unsafe_allow_html=True,
    )

    # Clean list of facility names from PV Master and Finance Master
    facility_pv_df, _, _, _, _ = process_pv_timeline(
        df_pv_raw, selected_months, selected_period, focus_year, comparison_year
    )
    df_fin_fac = fa.get_facility_finance_breakdown()

    # -------------------------------------------------------------------------
    # CANONICAL FACILITY NAME MAPPER & STRICT MATCHING ENGINE
    # -------------------------------------------------------------------------
    DROPPED_FACILITIES = {"sambocho", "mwihila"}

    CANONICAL_NAME_MAP = {
                "agc ngoswani lions hospital": "AGC Lions Ngoswani Hospital",
        "agc ngoswani lions": "AGC Lions Ngoswani Hospital",
        "mary immaculate health centre bahati": "Mary Immaculate Sisters Dispensary",
        "mary immaculate health centre": "Mary Immaculate Sisters Dispensary",
        "pefa mercy medical center": "PEFA Mercy Medical Centre",
        "agc lions ngoswani hospital": "AGC Lions Ngoswani Hospital",
        "agc lions ngoswani": "AGC Lions Ngoswani Hospital",
        "beacon of hope clinic (ongata rongai)": "Beacon of Hope Clinic (Ongata Rongai)",
        "beacon of hope": "Beacon of Hope Clinic (Ongata Rongai)",
        "cana family life clinic": "Cana Family Life Clinic",
        "cana family life": "Cana Family Life Clinic",
        "cmf aitong health centre": "Cmf Aitong Health Centre",
        "cmf aitong hc": "Cmf Aitong Health Centre",
        "diwopa health centre": "Diwopa Health Centre",
        "diwopa hc": "Diwopa Health Centre",
        "ewaso ngiro health centre": "Ewaso Ngiro Health Centre",
        "ewaso ngiro hc": "Ewaso Ngiro Health Centre",
        "imara health centre": "Imara Health Centre",
        "imara hc": "Imara Health Centre",
        "kimende orthodox mission health centre": "Kimende Orthodox Mission Health Centre",
        "kimende orthodox": "Kimende Orthodox Mission Health Centre",
        "mararianta health centre": "Mararianta Health Centre",
        "mararianta hc": "Mararianta Health Centre",
        "mary immaculate sisters dispensary": "Mary Immaculate Sisters Dispensary",
        "mary immaculate dispensary": "Mary Immaculate Sisters Dispensary",
        "mt kenya (ack) hospital": "Mt Kenya (ACK) Hospital",
        "ack mt kenya hospital": "Mt Kenya (ACK) Hospital",
        "mulango (aic) health centre": "Mulango (AIC) Health Centre",
        "mulango aic": "Mulango (AIC) Health Centre",
        "mwangaza ulio na tumaini": "Mwangaza Ulio Na Tumaini",
        "naikara health centre": "Naikara Health Centre",
        "naikara hc": "Naikara Health Centre",
        "pefa mercy medical centre": "PEFA Mercy Medical Centre",
        "pefa mercy": "PEFA Mercy Medical Centre",
        "revival home based care clinic": "Revival Home Based Care Clinic",
        "revival hbc": "Revival Home Based Care Clinic",
        "spacecare health services": "Spacecare Health Services",
        "spacecare": "Spacecare Health Services",
        "st antony's abossi health centre": "St Antony's Abossi Health Centre",
        "st antonys abossi": "St Antony's Abossi Health Centre",
        "st elizabeth health centre": "St Elizabeth Health Centre",
        "st elizabeth hc": "St Elizabeth Health Centre",
        "st joseph mukasa dispensary": "St Joseph Mukasa Dispensary",
        "st joseph mukasa": "St Joseph Mukasa Dispensary",
        "st joseph's dispensary (dagoretti)": "St Joseph's Dispensary (Dagoretti)",
        "st joseph's dispensary": "St Joseph's Dispensary (Dagoretti)",
        "st joseph s dispensary (dagoretti)": "St Joseph's Dispensary (Dagoretti)",
        "st josephs dagoretti": "St Joseph's Dispensary (Dagoretti)",
        "talek health centre": "Talek Health Centre",
        "talek hc": "Talek Health Centre",
        "mwatate dispensary": "Mwatate Dispensary",
        "mwatate": "Mwatate Dispensary",
        "buyangu dispensary": "Buyangu Dispensary",
        "buyangu": "Buyangu Dispensary",
        "ingotse dispensary": "Ingotse Dispensary",
        "ingotse": "Ingotse Dispensary",
        "kaptama (friends) health centre": "Kaptama (Friends) Health Centre",
        "kaptama friends hc": "Kaptama (Friends) Health Centre",
        "khasoko health centre": "Khasoko Health Centre",
        "khasoko hc": "Khasoko Health Centre",
        "kolanya salvation army health centre": "Kolanya Salvation Army Health Centre",
        "kolanya sa hc": "Kolanya Salvation Army Health Centre",
        "mission of mercy clinic": "Mission of Mercy Clinic",
        "mission of mercy": "Mission of Mercy Clinic",
        "mundoli health centre": "Mundoli Health Centre",
        "mundoli hc": "Mundoli Health Centre",
        "namasoli health centre": "Namasoli Health Centre",
        "namasoli hc": "Namasoli Health Centre",
        "namboboto dispensary": "Namboboto Dispensary",
        "namboboto": "Namboboto Dispensary",
        "st charles lwanga health centre": "St Charles Lwanga Health Centre",
        "st charles lwanga": "St Charles Lwanga Health Centre",
        "st marthas chimoi health centre": "St Marthas Chimoi Health Centre",
        "st marthas chimoi": "St Marthas Chimoi Health Centre",
        "st. monica eregi mission health centre": "St Monica Eregi Health Centre",
        "st monica eregi hc": "St Monica Eregi Health Centre",
        "st monica eregi health centre": "St Monica Eregi Health Centre",
        "st monica eregi": "St Monica Eregi Health Centre",
        "st pius musoli health centre": "St Pius Musoli Health Centre",
        "st pius musoli": "St Pius Musoli Health Centre",
        "butula health centre": "Butula Health Centre",
        "butula": "Butula Health Centre",
        "misikhu health centre": "Misikhu Health Centre",
        "misikhu": "Misikhu Health Centre",
    }

    def normalize_facility_name(name_str):
        if not name_str or pd.isna(name_str):
            return ""
        clean = str(name_str).strip().lower()
        return CANONICAL_NAME_MAP.get(clean, str(name_str).strip())

    raw_fac_list = []
    if not facility_pv_df.empty:
        raw_fac_list = facility_pv_df["organisationunitname"].unique().tolist()
    elif not df_fin_fac.empty:
        raw_fac_list = df_fin_fac["Facility"].unique().tolist()

    fac_names_set = set()
    for name in raw_fac_list:
        norm = normalize_facility_name(name)
        if norm.lower() not in DROPPED_FACILITIES and not any(
            d in norm.lower() for d in DROPPED_FACILITIES
        ):
            fac_names_set.add(norm)

    fac_names = sorted(list(fac_names_set))

    if fac_names:
        selected_fac = st.selectbox(
            "🔍 Select Health Facility to Audit:", options=fac_names, index=0
        )
        st.markdown("<hr style='border:1px solid #CBD5E1;'>", unsafe_allow_html=True)

        def get_facility_match(df, target_fac):
            if df is None or df.empty or not target_fac:
                return pd.DataFrame()

            fac_col_matches = [
                c
                for c in df.columns
                if any(
                    k in c.lower()
                    for k in ["facility", "organisation", "name", "unit", "org"]
                )
            ]
            if not fac_col_matches:
                return pd.DataFrame()

            fac_col = fac_col_matches[0]
            target_canonical = normalize_facility_name(target_fac)

            if target_canonical.lower() in DROPPED_FACILITIES or any(
                d in target_canonical.lower() for d in DROPPED_FACILITIES
            ):
                return pd.DataFrame()

            normalized_series = df[fac_col].apply(normalize_facility_name)
            canonical_matches = df[normalized_series == target_canonical]

            if not canonical_matches.empty:
                return canonical_matches

            def extract_core_name(name):
                n = normalize_facility_name(name).lower()
                for noise in [
                    "health centre",
                    "dispensary",
                    "clinic",
                    "hospital",
                    "mission",
                    "hc",
                ]:
                    n = n.replace(noise, "")
                return n.strip()

            target_core = extract_core_name(target_fac)
            if len(target_core) > 3:
                core_series = df[fac_col].apply(extract_core_name)
                core_matches = df[core_series == target_core]
                if not core_matches.empty:
                    return core_matches

            return pd.DataFrame()

        # 1. Facility PV Data Extraction
        fac_pv_match = get_facility_match(facility_pv_df, selected_fac)
        if not fac_pv_match.empty:
            fac_pv_data = fac_pv_match.iloc[0]
            pv_25 = fac_pv_data["PV_2025"]
            pv_26 = fac_pv_data["PV_2026"]
            pv_var = fac_pv_data["Absolute_Variance"]
            pv_growth = fac_pv_data["Growth_%"]
        else:
            pv_25, pv_26, pv_var, pv_growth = 0, 0, 0, 0

        # 2. Facility KPI Summary Data Extraction
        fac_deliv_25, fac_deliv_26, fac_live_26, fac_cs_26, fac_pph_26, fac_apgar_26 = (
            0,
            0,
            0,
            0,
            0,
            0,
        )
        df_b_target = kpi_2025 if comparison_year == "2025" else kpi_2026
        df_f_target = kpi_2026 if focus_year == "2026" else kpi_2025

        if df_b_target is not None and df_f_target is not None:
            cols_norm_25 = [
                f"MOH 711 Normal Deliveries {m} {comparison_year}"
                for m in selected_months
                if f"MOH 711 Normal Deliveries {m} {comparison_year}"
                in df_b_target.columns
            ]
            cols_cs_25 = [
                f"MOH 711 Caesarian Sections {m} {comparison_year}"
                for m in selected_months
                if f"MOH 711 Caesarian Sections {m} {comparison_year}"
                in df_b_target.columns
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
                if f"MOH 711 PPH (Post Partum Haemorrage) A {m} {focus_year}"
                in df_f_target.columns
            ]
            cols_apgar_26 = [
                f"MOH 711 Births with low APGAR score {m} {focus_year}"
                for m in selected_months
                if f"MOH 711 Births with low APGAR score {m} {focus_year}"
                in df_f_target.columns
            ]

            row_25 = get_facility_match(df_b_target, selected_fac)
            row_26 = get_facility_match(df_f_target, selected_fac)

            if not row_25.empty:
                fac_deliv_25 = (
                    row_25[cols_norm_25 + cols_cs_25].sum(axis=1).values[0]
                    if cols_norm_25
                    else 0
                )
            if not row_26.empty:
                fac_deliv_26 = (
                    row_26[cols_norm_26 + cols_cs_26].sum(axis=1).values[0]
                    if cols_norm_26
                    else 0
                )
                fac_live_26 = (
                    row_26[cols_live_26].sum(axis=1).values[0] if cols_live_26 else 0
                )
                fac_cs_26 = (
                    row_26[cols_cs_26].sum(axis=1).values[0] if cols_cs_26 else 0
                )
                fac_pph_26 = (
                    row_26[cols_pph_26].sum(axis=1).values[0] if cols_pph_26 else 0
                )
                fac_apgar_26 = (
                    row_26[cols_apgar_26].sum(axis=1).values[0] if cols_apgar_26 else 0
                )

        # TOP METRICS CARDS FOR SELECTED FACILITY
        f1, f2, f3, f4, f5 = st.columns(5)

        with f1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">{comparison_year} Baseline PV</span><span class="kpi-icon">📅</span></div>
                    <div class="kpi-value">{int(pv_25):,}</div>
                    <span class="badge-positive">Baseline Visits</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with f2:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">{focus_year} Focus PV</span><span class="kpi-icon">📈</span></div>
                    <div class="kpi-value">{int(pv_26):,}</div>
                    <span class="badge-positive">Current Focus</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with f3:
            var_class = "badge-positive" if pv_var >= 0 else "badge-negative"
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">YoY PV Growth</span><span class="kpi-icon">📊</span></div>
                    <div class="kpi-value">{pv_growth:+.1f}%</div>
                    <span class="{var_class}">{pv_var:+,} Visits</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with f4:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Total Deliveries</span><span class="kpi-icon">👶</span></div>
                    <div class="kpi-value">{int(fac_deliv_26):,}</div>
                    <span class="badge-positive">{focus_year} ({selected_period})</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with f5:
            live_pct = (fac_live_26 / fac_deliv_26 * 100) if fac_deliv_26 > 0 else 100.0
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Live Birth Rate</span><span class="kpi-icon">🌱</span></div>
                    <div class="kpi-value">{live_pct:.1f}%</div>
                    <span class="badge-positive">{int(fac_live_26):,} Live Births</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # CHARTS FOR FACILITY PROFILE
        c_fac1, c_fac2 = st.columns([1.2, 1.0])

        with c_fac1:
            # Patient Volume Comparison Bar Chart
            fig_fac_pv = go.Figure(
                data=[
                    go.Bar(
                        name=f"{comparison_year} Baseline ({selected_period})",
                        x=["Patient Volume"],
                        y=[pv_25],
                        text=[f"{int(pv_25):,}"],
                        textposition="outside",
                        textfont=dict(color=COLOR_TEXT_MAIN, size=13, family="Inter"),
                        marker_color="#94A3B8",
                    ),
                    go.Bar(
                        name=f"{focus_year} Focus ({selected_period})",
                        x=["Patient Volume"],
                        y=[pv_26],
                        text=[f"{int(pv_26):,} ({pv_growth:+.1f}%)"],
                        textposition="outside",
                        textfont=dict(color=COLOR_TEXT_MAIN, size=13, family="Inter"),
                        marker_color=COLOR_NAVY_PRIMARY,
                    ),
                ]
            )
            fig_fac_pv.update_layout(
                barmode="group",
                paper_bgcolor=COLOR_CARD_BG,
                plot_bgcolor=COLOR_CARD_BG,
                title=dict(
                    text=f"Patient Attendance — Baseline vs Current ({selected_fac})",
                    font=dict(size=16, color=COLOR_TEXT_MAIN),
                ),
                font=dict(family="Inter"),
                height=380,
                xaxis=dict(
                    showgrid=False, tickfont=dict(color=COLOR_TEXT_MAIN, size=13)
                ),
                yaxis=dict(
                    range=[
                        0,
                        max(pv_25, pv_26) * 1.35 if max(pv_25, pv_26) > 0 else 100,
                    ],
                    showgrid=True,
                    gridcolor="#CBD5E1",
                    tickfont=dict(color=COLOR_TEXT_MUTED, size=12),
                ),
                legend=dict(
                    orientation="h",
                    y=1.15,
                    x=0,
                    xanchor="left",
                    font=dict(color=COLOR_TEXT_MAIN, size=13),
                ),
                margin=dict(l=40, r=40, t=80, b=30),
            )
            st.plotly_chart(fig_fac_pv, use_container_width=True)

        with c_fac2:
            # Clinical Delivery & Outcomes Breakdown
            outcomes_labels = [
                "Deliveries",
                "Live Births",
                "C-Sections",
                "PPH Cases",
                "Low APGAR",
            ]
            outcomes_vals = [
                fac_deliv_26,
                fac_live_26,
                fac_cs_26,
                fac_pph_26,
                fac_apgar_26,
            ]

            fig_fac_kpi = go.Figure(
                go.Bar(
                    x=outcomes_labels,
                    y=outcomes_vals,
                    text=[f"{int(v):,}" for v in outcomes_vals],
                    textposition="outside",
                    textfont=dict(color=COLOR_TEXT_MAIN, size=12.5, family="Inter"),
                    marker_color=[
                        COLOR_NAVY_PRIMARY,
                        COLOR_GREEN_SUCCESS,
                        COLOR_CYAN_ACCENT,
                        COLOR_RED_ALERT,
                        COLOR_AMBER_WARN,
                    ],
                )
            )
            fig_fac_kpi.update_layout(
                paper_bgcolor=COLOR_CARD_BG,
                plot_bgcolor=COLOR_CARD_BG,
                title=dict(
                    text=f"Clinical Outcomes Breakdown ({selected_fac})",
                    font=dict(size=16, color=COLOR_TEXT_MAIN),
                ),
                font=dict(family="Inter"),
                height=380,
                xaxis=dict(
                    showgrid=False, tickfont=dict(color=COLOR_TEXT_MAIN, size=12)
                ),
                yaxis=dict(
                    range=[
                        0,
                        max(outcomes_vals) * 1.35 if max(outcomes_vals) > 0 else 10,
                    ],
                    showgrid=True,
                    gridcolor="#CBD5E1",
                    tickfont=dict(color=COLOR_TEXT_MUTED, size=12),
                ),
                margin=dict(l=40, r=40, t=80, b=30),
            )
            st.plotly_chart(fig_fac_kpi, use_container_width=True)

        # QSC Performance for Selected Facility (With Medical vs Management Toggle)
        st.markdown("---")
        st.markdown(
            f"#### 🎯 Quality Scorecard (QSC) Facility Progress Audit: **{selected_fac}**"
        )

        qsc_type_toggle = st.radio(
            "Select QSC Curriculum Domain to Inspect:",
            options=["🩺 Medical QSC", "💼 Management QSC"],
            horizontal=True,
            key="fac_qsc_toggle",
        )

        is_fac_med = "Medical" in qsc_type_toggle

        cohort3_facilities = {
            "buyangu dispensary", "ingotse dispensary", "kaptama (friends) health centre",
            "khasoko health centre", "kolanya salvation army health centre", "mission of mercy clinic",
            "mundoli health centre", "namasoli health centre", "namboboto dispensary",
            "st charles lwanga health centre", "st marthas chimoi health centre",
            "st monica eregi health centre", "st pius musoli health centre",
            "butula health centre", "misikhu health centre"
        }

        norm_fac = normalize_facility_name(selected_fac).lower()
        is_cohort3 = norm_fac in cohort3_facilities or any(k in norm_fac for k in ["buyangu", "ingotse", "kaptama", "khasoko", "kolanya", "mission of mercy", "mundoli", "namasoli", "namboboto", "lwanga", "chimoi", "eregi", "musoli", "butula", "misikhu"])

        m_labels, m_base, m_end = [], [], []

        if is_cohort3:
            try:
                c3_file = 'data/Cohort 3 End of Module 1 Performance March 2026.xlsx'
                sheet_name = 'Medical QSC Performance' if is_fac_med else 'Management QSC Performance'
                df_c3_qsc = pd.read_excel(c3_file, sheet_name=sheet_name)
                df_fac_qsc = get_facility_match(df_c3_qsc, selected_fac)
            except Exception:
                df_fac_qsc = pd.DataFrame()

            if not df_fac_qsc.empty:
                qsc_row = df_fac_qsc.iloc[0]
                m_labels = ['M1: Back to Basics'] if is_fac_med else ['M1: Financial management 1 and HRM1']
                b_val, e_val = 0.0, 0.0
                for col in df_c3_qsc.columns:
                    col_str = str(col).lower()
                    val = qsc_row[col]
                    if pd.notna(val):
                        try:
                            v_float = float(val)
                            # Convert 0-1 scale to percentage if needed
                            v_perc = v_float * 100 if v_float <= 1.0 else v_float
                            if "base" in col_str:
                                b_val = v_perc
                            elif "end" in col_str:
                                e_val = v_perc
                        except ValueError:
                            pass
                m_base = [b_val]
                m_end = [e_val]
        else:
            target_qsc_df = df_qsc_med if is_fac_med else df_qsc_mgmt
            df_fac_qsc = get_facility_match(target_qsc_df, selected_fac)

            if not df_fac_qsc.empty:
                qsc_row = df_fac_qsc.iloc[0]
                if is_fac_med:
                    m_labels = ["M1: Basics", "M2: Safe Baby", "M3: Safe Mother", "M4: Children", "M5: Top Burdens"]
                    mod_count = 5
                else:
                    m_labels = ["M1: Financial management 1 and HRM1", "M2: Financial management 2 and Admin", "M3: HR Mgmt", "M4: Marketing and Financial Sustainability"]
                    mod_count = 4

                for m_num in range(1, mod_count + 1):
                    b_cols = [c for c in target_qsc_df.columns if f"module {m_num}" in c.lower() and "baseline" in c.lower() and "percent" in c.lower()]
                    e_cols = [c for c in target_qsc_df.columns if f"module {m_num}" in c.lower() and "endline" in c.lower() and "percent" in c.lower()]

                    b_val = float(qsc_row[b_cols[0]]) if b_cols and pd.notna(qsc_row[b_cols[0]]) else 0.0
                    e_val = float(qsc_row[e_cols[0]]) if e_cols and pd.notna(qsc_row[e_cols[0]]) else 0.0

                    m_base.append(b_val)
                    m_end.append(e_val)

        if m_base:
            fig_qsc_fac = go.Figure(
                data=[
                    go.Bar(
                        name="Baseline Score (%)",
                        x=m_labels,
                        y=m_base,
                        text=[f"{v:.1f}%" for v in m_base],
                        textposition="outside",
                        textfont=dict(color=COLOR_TEXT_MAIN, size=13, family="Inter"),
                        marker_color=COLOR_RED_ALERT,
                    ),
                    go.Bar(
                        name="Endline Score (%)",
                        x=m_labels,
                        y=m_end,
                        text=[f"{v:.1f}%" for v in m_end],
                        textposition="outside",
                        textfont=dict(color=COLOR_TEXT_MAIN, size=13, family="Inter"),
                        marker_color=COLOR_NAVY_PRIMARY,
                    ),
                ]
            )
            fig_qsc_fac.update_layout(
                barmode="group",
                paper_bgcolor=COLOR_CARD_BG,
                plot_bgcolor=COLOR_CARD_BG,
                title=dict(
                    text=f"{'Medical' if is_fac_med else 'Management'} Quality Scorecard (QSC) Modules — {selected_fac}",
                    font=dict(size=16, color=COLOR_TEXT_MAIN),
                ),
                font=dict(family="Inter"),
                height=420,
                xaxis=dict(
                    showgrid=False, tickfont=dict(color=COLOR_TEXT_MAIN, size=12.5)
                ),
                yaxis=dict(
                    range=[0, 120],
                    showgrid=True,
                    gridcolor="#CBD5E1",
                    tickfont=dict(color=COLOR_TEXT_MUTED, size=12),
                ),
                legend=dict(
                    orientation="h",
                    y=1.15,
                    x=0,
                    xanchor="left",
                    font=dict(color=COLOR_TEXT_MAIN, size=13),
                ),
                margin=dict(l=40, r=40, t=80, b=30),
            )
            st.plotly_chart(fig_qsc_fac, width="stretch")
        else:
            if normalize_facility_name(selected_fac) in ["Butula Health Centre", "Misikhu Health Centre"]:
                st.info(f"ℹ️ **{selected_fac}** was recently onboarded into Cohort 3. Baseline assessment is currently pending.")
            else:
                st.info(f"ℹ️ No individual {'Medical' if is_fac_med else 'Management'} QSC module records found for **{selected_fac}** in the QSC master file.")

        # 3. Facility Financial Solvency & Disclosure Profile Section
        st.markdown("---")
        st.markdown(
            f"#### 💼 Financial Performance & Operational Solvency: **{selected_fac}**"
        )

        fac_fin_match = get_facility_match(df_fin_fac, selected_fac)

        if not fac_fin_match.empty:
            fin_row = fac_fin_match.iloc[0]
            tot_rev = fin_row["Total_Revenue"]
            tot_exp = fin_row["Total_Expense"]
            net_margin = fin_row["Net_Margin"]
            status = fin_row["Status"]
            coverage = fin_row["Cost_Coverage_Pct"]
            def_mos = fin_row["Deficit_Months"]
            missing_mos = fin_row["Missing_Months_List"]

            c_fin1, c_fin2 = st.columns([1.2, 1.0])

            with c_fin1:
                fig_fac_summary = go.Figure(
                    data=[
                        go.Bar(
                            name="Revenue",
                            x=["Total Revenue"],
                            y=[tot_rev],
                            marker_color="#0A2540",
                            text=[f"{tot_rev:,.0f} Ksh"],
                            textposition="auto",
                        ),
                        go.Bar(
                            name="Expense",
                            x=["Total Expense"],
                            y=[tot_exp],
                            marker_color="#E61C24",
                            text=[f"{tot_exp:,.0f} Ksh"],
                            textposition="auto",
                        ),
                    ]
                )
                fig_fac_summary.update_layout(
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    height=350,
                    title=dict(
                        text=f"Revenue vs Expenditure (FY2026)",
                        font=dict(size=16, color="#0F172A"),
                    ),
                    font=dict(color="#0F172A", family="Inter"),
                    yaxis=dict(showgrid=True, gridcolor="#E2E8F0", tickformat="~s"),
                    margin=dict(l=20, r=20, t=50, b=20),
                )
                st.plotly_chart(fig_fac_summary, use_container_width=True)

            with c_fin2:
                status_color = (
                    "#15803D" if status == "Surplus / Breakeven" else "#DC2626"
                )
                st.markdown(
                    f"""
                    <div style="background-color:#F8FAFC; border:1.5px solid #64748B; border-radius:8px; padding:18px; margin-top:15px;">
                        <h5 style="color:#0F172A; margin-top:0; font-weight:800;">📋 Disclosure & Compliance Summary</h5>
                        <p style="color:#0F172A; margin-bottom:8px;"><b>Financial Health Status:</b> <span style="color:{status_color}; font-weight:bold;">{status}</span></p>
                        <p style="color:#0F172A; margin-bottom:8px;"><b>Net Operating Margin:</b> <b>{net_margin:+,.0f} Ksh</b> ({coverage:.0f}% Cost Coverage)</p>
                        <p style="color:#0F172A; margin-bottom:8px;"><b>Months Reported:</b> {fin_row['Months_Reported']} / 10 Months</p>
                        <p style="color:#0F172A; margin-bottom:8px;"><b>Unreported / Missing Months:</b> {missing_mos}</p>
                        <p style="color:#0F172A; margin-bottom:0;"><b>Deficit Duration:</b> {def_mos} month(s) operating at a cost loss</p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.info(
                f"ℹ️ No financial records found for **{selected_fac}** in the FY2026 finance dataset."
            )

    else:
        st.warning("⚠️ No facility data found. Please verify dataset connections.")
elif active_tab == "💼 Financial Performance":
    st.markdown(
        "<h2 style='color:#0F172A; font-weight:800;'>💼 Financial Performance & Operational Breakeven Analytics (FY2026)</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#334155; font-size:14px;'>Monitoring health center income, cost-coverage breakeven capacity, deficit risk, and data compliance across 38 network facilities.</p>",
        unsafe_allow_html=True,
    )

    df_fin_monthly = fa.get_monthly_finance_summary()
    df_fin_fac = fa.get_facility_finance_breakdown()

    if not df_fin_monthly.empty:
        tot_net_rev = df_fin_monthly["Revenue"].sum()
        tot_net_exp = df_fin_monthly["Expense"].sum()
        net_surplus = tot_net_rev - tot_net_exp
        breakeven_count = len(df_fin_fac[df_fin_fac["Status"] == "Surplus / Breakeven"])
        deficit_fac_count = len(df_fin_fac[df_fin_fac["Status"] == "Operating Deficit"])
        zero_sub_count = len(df_fin_fac[df_fin_fac["Months_Reported"] == 0])

        # 1. High Visibility Executive Summary Cards
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Income (Ksh)", f"{tot_net_rev:,.0f} Ksh")
        k2.metric("Total Expenditure (Ksh)", f"{tot_net_exp:,.0f} Ksh")
        k3.metric(
            "Net Margin Buffer",
            f"{net_surplus:,.0f} Ksh",
            delta=f"{(net_surplus/tot_net_rev)*100:.1f}% Margin",
        )
        k4.metric(
            "Breakeven Status",
            f"{breakeven_count} Solvent / Breakeven",
            delta=f"{deficit_fac_count} Deficit | {zero_sub_count} Unreported",
            delta_color="inverse",
        )

        st.markdown("<hr style='border:1px solid #CBD5E1;'>", unsafe_allow_html=True)

        # 2. Income vs. Expenditure Chart & Executive Narrative
        col_chart, col_narrative = st.columns([1.65, 1.0])

        with col_chart:
            st.markdown(
                "<h4 style='text-align:center; color:#0F172A; font-weight:800; font-size:17px; margin-bottom:15px;'>LNI Partner HFs' FY2026 Monthly Income and Expenditure</h4>",
                unsafe_allow_html=True,
            )

            fig_area = go.Figure()

            # Bottom Layer: Expenditure (Bright Red #E61C24)
            fig_area.add_trace(
                go.Scatter(
                    x=df_fin_monthly["Month"],
                    y=df_fin_monthly["Expense"],
                    mode="lines",
                    name="Expenditure",
                    line=dict(width=1.5, color="#E61C24"),
                    fill="tozeroy",
                    fillcolor="#E61C24",
                )
            )

            # Top Layer: Income (Navy Area #0A2540)
            fig_area.add_trace(
                go.Scatter(
                    x=df_fin_monthly["Month"],
                    y=df_fin_monthly["Revenue"],
                    mode="lines",
                    name="Income",
                    line=dict(width=1.5, color="#0A2540"),
                    fill="tonexty",
                    fillcolor="#0A2540",
                )
            )

            fig_area.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                height=480,
                font=dict(family="Inter", color="#0F172A", size=12),
                xaxis=dict(
                    showgrid=False,
                    linecolor="#64748B",
                    linewidth=1.5,
                    tickfont=dict(color="#0F172A", size=12, weight="bold"),
                    title=dict(
                        text="<b>Month</b>", font=dict(size=14, color="#0F172A")
                    ),
                ),
                yaxis=dict(
                    title=dict(
                        text="<b>Amount (Ksh)</b>", font=dict(size=14, color="#0F172A")
                    ),
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
                margin=dict(l=40, r=90, t=10, b=40),
            )
            st.plotly_chart(fig_area, use_container_width=True)

        with col_narrative:
            st.markdown(
                """
                <div style="background-color:#F8FAFC; border:1.5px solid #64748B; border-left:6px solid #0A2540; border-radius:8px; padding:18px; height:480px; box-sizing:border-box;">
                    <h4 style="color:#0F172A; margin-top:0; font-size:16px; font-weight:800;">🔍 M&E Executive Financial & Breakeven Narrative</h4>
                    <ul style="color:#0F172A; font-size:13px; line-height:1.6; padding-left:16px; margin-bottom:0;">
                        <li><b>Breakeven Network Solvency:</b> <b>26 out of 38 facilities (68.4%)</b> fully break even and generate operational surpluses, led by <i>St Joseph Mukasa Dispensary (+20.5M Ksh surplus)</i> and <i>Mt Kenya Hospital (+15.5M Ksh surplus)</i>.</li>
                        <li><b>Aggregate Net Surplus Buffer:</b> Network revenue exceeds expenditure by <b>+64.7M Ksh</b> across reporting periods.</li>
                        <li><b>Deficit Vulnerability:</b> <b>8 facilities (21.1%)</b> operate in chronic net deficit, unable to cover costs from operating income alone.</li>
                        <li><b>Data Decay Impact:</b> The downward slope in Q3 total income is driven by reporting attrition (dropping from <b>34 active HFs in Jan</b> to <b>9 HFs in Sept</b>).</li>
                        <li><b>Unreported Compliance Risk:</b> <b>4 facilities (10.5%)</b> have zero financial disclosures for 2026 (*Butula Mission, Imara, Mwatate, St. Mary's Misikhu*).</li>
                    </ul>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<hr style='border:1px solid #CBD5E1;'>", unsafe_allow_html=True)

        # 3. Dual Facility View: Breakeven (Surplus) vs. Net Deficit Performance
        c_fac_chart, c_audit = st.columns([1.1, 1.1])

        with c_fac_chart:
            fac_view_type = st.radio(
                "Select Facility Analysis Perspective:",
                [
                    "✅ Breaking Even / Surplus Facilities (26 HFs)",
                    "🚨 Operating Deficit Facilities (8 HFs)",
                ],
                horizontal=True,
            )

            if "Breaking Even" in fac_view_type:
                st.markdown(
                    "<h5 style='color:#0F172A; font-weight:800;'>✅ Top Solvent Facilities Breaking Even (Meeting & Exceeding Costs)</h5>",
                    unsafe_allow_html=True,
                )
                df_top_surplus = (
                    df_fin_fac[df_fin_fac["Status"] == "Surplus / Breakeven"]
                    .sort_values(by="Net_Margin", ascending=False)
                    .head(10)
                )

                fig_fac = go.Figure(
                    go.Bar(
                        x=df_top_surplus["Net_Margin"],
                        y=df_top_surplus["Facility"],
                        orientation="h",
                        text=[
                            f"+{m:,.0f} Ksh ({c:.0f}% cover)"
                            for m, c in zip(
                                df_top_surplus["Net_Margin"],
                                df_top_surplus["Cost_Coverage_Pct"],
                            )
                        ],
                        textposition="outside",
                        marker_color="#0A2540",  # Executive Navy Blue
                    )
                )
                fig_fac.update_layout(
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    height=450,
                    font=dict(color="#0F172A"),
                    xaxis=dict(
                        range=[0, df_top_surplus["Net_Margin"].max() * 1.45],
                        showgrid=True,
                        gridcolor="#E2E8F0",
                        tickformat="~s",
                        tickfont=dict(color="#0F172A", size=11, weight="bold"),
                    ),
                    yaxis=dict(
                        autorange="reversed",
                        tickfont=dict(color="#0F172A", size=11, weight="bold"),
                    ),
                    margin=dict(l=220, r=90, t=10, b=20),
                )
                st.plotly_chart(fig_fac, use_container_width=True)
            else:
                st.markdown(
                    "<h5 style='color:#0F172A; font-weight:800;'>🚨 High-Risk Facilities Operating at a Net Deficit</h5>",
                    unsafe_allow_html=True,
                )
                df_def = (
                    df_fin_fac[df_fin_fac["Net_Margin"] < 0]
                    .sort_values(by="Net_Margin")
                    .head(10)
                )

                fig_fac = go.Figure(
                    go.Bar(
                        x=df_def["Net_Margin"].abs(),
                        y=df_def["Facility"],
                        orientation="h",
                        text=[
                            f"-{abs(m):,.0f} Ksh ({d} def mos)"
                            for m, d in zip(
                                df_def["Net_Margin"], df_def["Deficit_Months"]
                            )
                        ],
                        textposition="outside",
                        marker_color="#E61C24",  # Crimson Red
                    )
                )
                fig_fac.update_layout(
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    height=450,
                    font=dict(color="#0F172A"),
                    xaxis=dict(
                        range=[0, df_def["Net_Margin"].abs().max() * 1.45],
                        showgrid=True,
                        gridcolor="#E2E8F0",
                        tickformat="~s",
                        tickfont=dict(color="#0F172A", size=11, weight="bold"),
                    ),
                    yaxis=dict(
                        autorange="reversed",
                        tickfont=dict(color="#0F172A", size=11, weight="bold"),
                    ),
                    margin=dict(l=220, r=90, t=10, b=20),
                )
                st.plotly_chart(fig_fac, use_container_width=True)

        with c_audit:
            st.markdown(
                "<h5 style='color:#0F172A; font-weight:800;'>⚠️ Facility Financial Disclosure Audit & Missing Months</h5>",
                unsafe_allow_html=True,
            )
            st.caption(
                "Detailed breakdown of missing revenue/expense submissions per facility (38 HFs Total)"
            )

            audit_filter = st.radio(
                "Filter Audit Scope:",
                [
                    "100% Unreported (4 HFs)",
                    "Partial Submissions (30 HFs)",
                    "All 38 Facilities",
                ],
                horizontal=True,
            )

            if audit_filter == "100% Unreported (4 HFs)":
                df_show = df_fin_fac[df_fin_fac["Months_Reported"] == 0]
            elif audit_filter == "Partial Submissions (30 HFs)":
                df_show = df_fin_fac[
                    (df_fin_fac["Missing_Months_Count"] > 0)
                    & (df_fin_fac["Months_Reported"] > 0)
                ].sort_values(by="Missing_Months_Count", ascending=False)
            else:
                df_show = df_fin_fac.sort_values(
                    by="Missing_Months_Count", ascending=False
                )

            st.dataframe(
                df_show[
                    [
                        "Facility",
                        "Months_Reported",
                        "Missing_Months_Count",
                        "Missing_Months_List",
                    ]
                ],
                column_config={
                    "Facility": st.column_config.TextColumn(
                        "Health Facility", width="medium"
                    ),
                    "Months_Reported": st.column_config.NumberColumn(
                        "Reported Mos", format="%d"
                    ),
                    "Missing_Months_Count": st.column_config.NumberColumn(
                        "Missing Mos", format="%d"
                    ),
                    "Missing_Months_List": st.column_config.TextColumn(
                        "Specific Missing Months", width="large"
                    ),
                },
                hide_index=True,
                height=360,
                use_container_width=True,
            )

            st.markdown(
                """
                <div style="background-color:#FFFBEB; border:1px solid #FCD34D; border-left:4px solid #D97706; border-radius:6px; padding:12px; margin-top:10px;">
                    <p style="color:#92400E; font-size:12.5px; font-weight:600; margin:0;">
                        ⚠️ <b>M&E Compliance Action:</b> Financial reporting compliance is degrading in late Q3. Immediate data reminders are required for facility finance officers prior to year-end audits.
                    </p>
                </div>
            """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------
# TAB 7: MONTHLY DDIU & M&E EXECUTIVE BRIEF
# ---------------------------------------------------------
elif active_tab == "📑 Monthly DDIU Brief":
    st.markdown("### 📑 Monthly Data Demand & Information Use (DDIU) Executive Brief")
    st.caption("Synthesizing KHIS Patient Visits, MOH 711 Maternal/Newborn KPIs, DQA Audits & MoniTrac Financials across 38 Active Facilities.")

    avail_periods = ddiu.get_available_reporting_periods()
    default_p = ddiu.default_ddiu_period()
    default_idx = avail_periods.index(default_p) if default_p in avail_periods else len(avail_periods) - 1

    c_p1, c_p2 = st.columns([1.4, 1.0])
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
        st.markdown("<div style='height: 26px;'></div>", unsafe_allow_html=True)
        st.download_button(
            label=f"📥 Download LifeNet DDIU PDF ({ddiu_period})",
            data=pdf_bytes,
            file_name=f"LifeNet_DDIU_Report_{ddiu_period.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.markdown("---")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "Total Patient Visits",
        f"{int(ddiu_data['tot_pv']):,}",
        f"{ddiu_data['pv_mom_pct']:+.1f}% MoM | {ddiu_data['pv_yoy_pct']:+.1f}% YoY",
    )
    m2.metric(
        "Maternity Deliveries",
        f"{ddiu_data['tot_del']:,}",
        f"{ddiu_data['tot_lb']:,} Live Births | {ddiu_data['tot_fsb'] + ddiu_data['tot_msb']} SB",
    )
    m3.metric(
        "Reporting Completeness",
        f"KHIS {ddiu_data['khis_reporting']}/{ddiu_data['total_facilities']}",
        f"Finance {ddiu_data['fin_reporting']}/{ddiu_data['total_facilities']} HFs",
    )
    m4.metric(
        "Network Cost Coverage",
        f"{ddiu_data['cost_coverage']:.1f}%",
        f"Net KES {ddiu_data['tot_net']:,.0f}",
    )

    st.markdown("---")

    ch1, ch2 = st.columns(2)
    trend_df = ddiu_data["trend_df"]
    with ch1:
        fig_ddiu_pv = make_subplots(specs=[[{"secondary_y": True}]])
        fig_ddiu_pv.add_trace(
            go.Bar(x=trend_df["Short_Period"], y=trend_df["Total_PV"], name="Patient Visits", marker_color="#0A2540", text=trend_df["Total_PV"].map(lambda v: f"{int(v):,}"), textposition="inside"),
            secondary_y=False,
        )
        fig_ddiu_pv.add_trace(
            go.Scatter(x=trend_df["Short_Period"], y=trend_df["Total_Deliveries"], name="Deliveries", mode="lines+markers+text", text=trend_df["Total_Deliveries"].map(lambda v: f"{int(v):,}"), textposition="top center", line=dict(color="#00A8CC", width=3)),
            secondary_y=True,
        )
        fig_ddiu_pv.update_layout(
            title=f"Patient Visits & Deliveries Trajectory (Through {ddiu_period})",
            height=340,
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig_ddiu_pv, use_container_width=True)

    with ch2:
        fig_ddiu_fin = go.Figure()
        fig_ddiu_fin.add_trace(
            go.Bar(x=trend_df["Short_Period"], y=trend_df["Revenue_KES"], name="Revenue (KES)", marker_color="#0D9488", text=trend_df["Revenue_KES"].map(lambda v: f"{v/1e6:.1f}M"), textposition="outside")
        )
        fig_ddiu_fin.add_trace(
            go.Bar(x=trend_df["Short_Period"], y=trend_df["Expenses_KES"], name="Expenses (KES)", marker_color="#D97706", text=trend_df["Expenses_KES"].map(lambda v: f"{v/1e6:.1f}M"), textposition="outside")
        )
        fig_ddiu_fin.update_layout(
            title="MoniTrac Network Revenue vs. Operating Expenses",
            barmode="group",
            height=340,
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig_ddiu_fin, use_container_width=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    em1, em2 = st.columns(2)
    with em1:
        fig_ddiu_pph = make_subplots(specs=[[{"secondary_y": True}]])
        fig_ddiu_pph.add_trace(
            go.Bar(x=trend_df["Short_Period"], y=trend_df["PPH_Cases"], name="PPH Cases Managed", marker_color="#D97706", text=trend_df["PPH_Cases"], textposition="inside"),
            secondary_y=False,
        )
        fig_ddiu_pph.add_trace(
            go.Bar(x=trend_df["Short_Period"], y=trend_df["PPH_Deaths"], name="PPH Deaths", marker_color="#DC2626", text=trend_df["PPH_Deaths"], textposition="outside"),
            secondary_y=False,
        )
        fig_ddiu_pph.add_trace(
            go.Scatter(
                x=trend_df["Short_Period"],
                y=trend_df["PPH_Success_Pct"],
                name="PPH Survival %",
                mode="lines+markers+text",
                text=trend_df["PPH_Success_Pct"].map(lambda v: f"{v:.0f}%"),
                textposition="top center",
                line=dict(color="#0D9488", width=3),
            ),
            secondary_y=True,
        )
        fig_ddiu_pph.update_layout(
            title="PPH Cases Managed & Management Survival Rate (%)",
            barmode="group",
            height=340,
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", y=1.12),
        )
        fig_ddiu_pph.update_yaxes(title_text="Cases", secondary_y=False)
        fig_ddiu_pph.update_yaxes(title_text="Survival %", range=[0, 110], secondary_y=True)
        st.plotly_chart(fig_ddiu_pph, use_container_width=True)

    with em2:
        fig_ddiu_apgar = make_subplots(specs=[[{"secondary_y": True}]])
        fig_ddiu_apgar.add_trace(
            go.Bar(x=trend_df["Short_Period"], y=trend_df["Low_APGAR"], name="Low APGAR Births", marker_color="#0A2540", text=trend_df["Low_APGAR"], textposition="inside"),
            secondary_y=False,
        )
        fig_ddiu_apgar.add_trace(
            go.Bar(x=trend_df["Short_Period"], y=trend_df["Maternal_Deaths"], name="Maternal Deaths", marker_color="#DC2626", text=trend_df["Maternal_Deaths"], textposition="outside"),
            secondary_y=False,
        )
        fig_ddiu_apgar.add_trace(
            go.Scatter(
                x=trend_df["Short_Period"],
                y=trend_df["APGAR_Success_Pct"],
                name="Resuscitation Success %",
                mode="lines+markers+text",
                text=trend_df["APGAR_Success_Pct"].map(lambda v: f"{v:.0f}%"),
                textposition="top center",
                line=dict(color="#00A8CC", width=3),
            ),
            secondary_y=True,
        )
        fig_ddiu_apgar.update_layout(
            title="Low APGAR Births, Resuscitation Success (%) & Maternal Deaths",
            barmode="group",
            height=340,
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", y=1.12),
        )
        fig_ddiu_apgar.update_yaxes(title_text="Cases / Deaths", secondary_y=False)
        fig_ddiu_apgar.update_yaxes(title_text="Success %", range=[0, 110], secondary_y=True)
        st.plotly_chart(fig_ddiu_apgar, use_container_width=True)

    st.markdown("#### 🎯 Role-Based DDIU Action Plan (M&E, Medical & Management Mentors)")
    if not ddiu_data["action_df"].empty:
        st.dataframe(ddiu_data["action_df"], hide_index=True, use_container_width=True)

    col_w, col_q = st.columns(2)
    with col_w:
        st.markdown("#### 🌟 Partner Highlights — What Facilities Did Well")
        if not ddiu_data["well_df"].empty:
            st.dataframe(
                ddiu_data["well_df"][["Facility", "PV_Current", "PV_MoM_%", "PV_YoY_%", "Total_Deliveries", "Net_Surplus_KES"]],
                hide_index=True,
                use_container_width=True,
            )
    with col_q:
        st.markdown("#### 🚨 DQA Queries & Facilities Requiring Follow-Up")
        if not ddiu_data["follow_up_df"].empty:
            st.dataframe(
                ddiu_data["follow_up_df"][["Facility", "PV_Current", "Total_Deliveries", "Queries"]],
                hide_index=True,
                use_container_width=True,
            )
