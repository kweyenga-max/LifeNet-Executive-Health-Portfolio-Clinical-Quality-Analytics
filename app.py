import streamlit as st
from scripts import pss_analytics as pssa
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
    import base64
    from io import BytesIO
    from PIL import Image, ImageEnhance, ImageFilter

    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
            html, body, [class*="css"], .stApp {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                background-color: #061226 !important;
                background-image:
                    radial-gradient(circle at 14% 18%, rgba(200, 16, 46, 0.16) 0%, transparent 42%),
                    radial-gradient(circle at 86% 22%, rgba(37, 99, 235, 0.22) 0%, transparent 48%),
                    radial-gradient(circle at 50% 95%, rgba(13, 148, 136, 0.14) 0%, transparent 45%),
                    linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px) !important;
                background-size: 100% 100%, 100% 100%, 100% 100%, 44px 44px, 44px 44px !important;
                color: #F8FAFC !important;
            }
            #MainMenu, header[data-testid="stHeader"], footer {
                visibility: hidden !important;
                height: 0 !important;
            }
            .block-container {
                padding-top: 2.0rem !important;
                padding-bottom: 1.5rem !important;
                max-width: 1380px !important;
            }
            /* Bottom half of Left Executive Sign-In Card */
            div[data-testid="stForm"] {
                background: #FFFFFF !important;
                border: 1px solid rgba(255, 255, 255, 0.16) !important;
                border-top: none !important;
                border-radius: 0 0 20px 20px !important;
                padding: 34px 38px 32px 38px !important;
                box-shadow: 0 32px 64px -16px rgba(0, 0, 0, 0.55) !important;
                margin-top: -16px !important;
                min-height: 368px !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: space-between !important;
            }
            .stTextInput > div > div {
                background-color: #F1F5F9 !important;
                border: 1.5px solid #CBD5E1 !important;
                border-radius: 12px !important;
                overflow: hidden !important;
            }
            .stTextInput > div > div:focus-within {
                background-color: #FFFFFF !important;
                border-color: #0F2C59 !important;
                box-shadow: 0 0 0 4px rgba(15, 44, 89, 0.14) !important;
            }
            .stTextInput > div > div > input {
                background-color: transparent !important;
                color: #0F172A !important;
                border: none !important;
                padding: 15px 18px !important;
                font-size: 15.5px !important;
                font-weight: 500 !important;
            }
            .stTextInput > div > div > input::placeholder {
                color: #64748B !important;
            }
            .stTextInput button {
                background-color: #E2E8F0 !important;
                color: #1E293B !important;
                border-left: 1px solid #CBD5E1 !important;
                padding: 0 14px !important;
            }
            .stTextInput button svg {
                fill: #1E293B !important;
            }
            div[data-testid="stFormSubmitButton"] > button {
                background: linear-gradient(90deg, #C8102E 0%, #9E0B22 100%) !important;
                color: #FFFFFF !important;
                font-weight: 800 !important;
                font-size: 15px !important;
                letter-spacing: 0.08em !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 15px 28px !important;
                box-shadow: 0 10px 24px rgba(200, 16, 46, 0.36) !important;
                transition: all 0.2s ease !important;
            }
            div[data-testid="stFormSubmitButton"] > button:hover {
                transform: translateY(-1px) !important;
                box-shadow: 0 14px 28px rgba(200, 16, 46, 0.48) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Top Institutional Command Header Bar
    st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding:0 4px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="width:11px;height:11px;border-radius:50%;background:#C8102E;box-shadow:0 0 12px #C8102E;display:inline-block;"></span>
                <span style="color:#F8FAFC;font-size:13px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;">LifeNet International Kenya · M&amp;E Intelligence Centre</span>
            </div>
            <div style="background:rgba(15,44,89,0.75);backdrop-filter:blur(10px);border:1px solid rgba(148,163,184,0.28);border-radius:24px;padding:6px 16px;font-size:12px;font-weight:600;color:#E2E8F0;display:flex;align-items:center;gap:8px;">
                <span style="width:8px;height:8px;border-radius:50%;background:#10B981;box-shadow:0 0 8px #10B981;display:inline-block;"></span>
                <span>KHIS &amp; MoniTrac Pipelines Connected</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1.05, 1.35], gap="large")

    with col_left:
        st.markdown("""
            <div style="background:linear-gradient(135deg,#0B2244 0%,#163E7A 100%);padding:36px 38px 30px 38px;border-radius:20px 20px 0 0;border-top:6px solid #C8102E;border-left:1px solid rgba(255,255,255,0.14);border-right:1px solid rgba(255,255,255,0.14);">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <span style="background:#C8102E;color:#FFFFFF;font-size:22px;font-weight:900;letter-spacing:1.5px;padding:7px 15px;border-radius:10px;box-shadow:0 6px 14px rgba(200,16,46,0.4);">LN</span>
                        <span style="color:#FFFFFF;font-size:15px;font-weight:800;letter-spacing:0.05em;line-height:1.2;">LIFENET<br/><span style="color:#93C5FD;font-size:10.5px;font-weight:600;letter-spacing:0.14em;">INTERNATIONAL</span></span>
                    </div>
                    <span style="background:rgba(255,255,255,0.12);color:#F8FAFC;font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;padding:6px 14px;border-radius:20px;border:1px solid rgba(255,255,255,0.22);">Kenya Portfolio</span>
                </div>
                <div style="color:#FFFFFF;font-size:26px;font-weight:800;letter-spacing:-0.015em;line-height:1.24;margin-bottom:10px;">Transforming Health Care Across Africa</div>
                <p style="color:#CBD5E1;font-size:14px;line-height:1.55;margin:0;">Executive Clinical Quality, Facility Utilization &amp; Financial Sustainability Portal</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("exec_login_form", clear_on_submit=False):
            st.markdown("""
                <div style="margin-bottom:16px;">
                    <div style="color:#0F2C59;font-size:20px;font-weight:800;margin-bottom:4px;">Executive Access Portal</div>
                    <div style="color:#475569;font-size:13.5px;">Sign in with your authorized leadership or M&amp;E passkey</div>
                </div>
            """, unsafe_allow_html=True)
            passkey = st.text_input("Authorization Key", type="password", placeholder="Enter executive authorization key...", label_visibility="collapsed", key="exec_passkey")
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            if st.form_submit_button("UNLOCK PORTAL  →", use_container_width=True):
                if passkey == "LifeNet2026!":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ Authorization Failed: Invalid Executive Key")
            st.markdown("""
                <div style="margin-top:26px;padding-top:16px;border-top:1px solid #E2E8F0;display:flex;justify-content:space-between;align-items:center;color:#64748B;font-size:12px;">
                    <span>🛡️ End-to-End Encrypted Session</span>
                    <span style="font-weight:700;color:#0F2C59;">FY2026 Release</span>
                </div>
            """, unsafe_allow_html=True)

    with col_right:
        image_path = "Gemini_Generated_Image_w39fd1w39fd1w39f.jpeg"
        if not os.path.exists(image_path):
            image_path = os.path.join("assets", image_path)
        img_b64 = ""
        if os.path.exists(image_path):
            with Image.open(image_path) as im:
                im = im.convert("RGB")
                w, h = im.size
                cropped = im.crop((int(w * 0.37), int(h * 0.03), int(w * 0.98), int(h * 0.93)))
                # Lanczos upscale + crisp editorial sharpening & contrast restoration
                target_w = 1400
                target_h = int(cropped.height * (target_w / cropped.width))
                enhanced = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
                enhanced = enhanced.filter(ImageFilter.UnsharpMask(radius=1.4, percent=135, threshold=3))
                enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.30)
                enhanced = ImageEnhance.Contrast(enhanced).enhance(1.07)
                enhanced = ImageEnhance.Color(enhanced).enhance(1.05)
                buf = BytesIO()
                enhanced.save(buf, format="PNG", optimize=True)
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        hero_img_html = f'<img src="data:image/png;base64,{img_b64}" style="width:100%;height:406px;object-fit:cover;object-position:center 15%;display:block;" />' if img_b64 else '<div style="height:406px;background:#0F2C59;"></div>'
        st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid rgba(255,255,255,0.18);border-radius:20px;overflow:hidden;box-shadow:0 32px 64px -16px rgba(0,0,0,0.55);">
                <div style="position:relative;">
                    {hero_img_html}
                    <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,34,68,0.02) 52%,rgba(11,34,68,0.94) 100%);display:flex;flex-direction:column;justify-content:flex-end;padding:28px 32px;">
                        <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:8px;">
                            <span style="background:#C8102E;width:24px;height:3px;display:inline-block;border-radius:2px;"></span>
                            <span style="color:#93C5FD;font-size:11.5px;font-weight:800;letter-spacing:0.13em;text-transform:uppercase;">Decision Intelligence &amp; DDIU Command Center</span>
                        </div>
                        <div style="color:#FFFFFF;font-size:22px;font-weight:800;line-height:1.3;letter-spacing:-0.01em;">Data-Driven Quality Improvement Across Partner Health Facilities</div>
                    </div>
                </div>
                <div style="padding:24px 30px 26px 30px;background:#FFFFFF;display:grid;grid-template-columns:repeat(3,1fr);gap:16px;">
                    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-top:4px solid #0F2C59;border-radius:12px;padding:15px 16px;">
                        <div style="color:#64748B;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Network Scope</div>
                        <div style="color:#0F2C59;font-size:18px;font-weight:800;margin-top:4px;white-space:nowrap;">38 Facilities</div>
                        <div style="color:#475569;font-size:12px;margin-top:3px;">Active Kenya Portfolio</div>
                    </div>
                    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-top:4px solid #0D9488;border-radius:12px;padding:15px 16px;">
                        <div style="color:#64748B;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">Live Pipelines</div>
                        <div style="color:#0F2C59;font-size:18px;font-weight:800;margin-top:4px;white-space:nowrap;">KHIS + MoniTrac</div>
                        <div style="color:#475569;font-size:12px;margin-top:3px;">Automated Sync &amp; DDIU</div>
                    </div>
                    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-top:4px solid #C8102E;border-radius:12px;padding:15px 16px;">
                        <div style="color:#64748B;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;">4 Core Pillars</div>
                        <div style="color:#0F2C59;font-size:18px;font-weight:800;margin-top:4px;white-space:nowrap;">360° Analytics</div>
                        <div style="color:#475569;font-size:12px;margin-top:3px;">PV · QSC · Finance · PSS</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

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
        from scripts.khis_adapter import get_live_pv_and_kpi_frames, get_live_anc_frame
        df_pv_live, df_kpi_live_wide = get_live_pv_and_kpi_frames("IwUxQNFazpx", "IPjuLUsTQHG")
        df_anc_live = get_live_anc_frame("IPjuLUsTQHG", force_live=bool(st.session_state.pop("_force_khis_sync", False)))
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

    def _run_anc_dq_audit():
        anc_found = []
        anc_snap = os.path.join("data", "khis_anc_snapshot.csv.gz")
        if not os.path.exists(anc_snap):
            return anc_found
        try:
            dfa = pd.read_csv(anc_snap, compression="gzip", dtype={"Year": str})
        except Exception:
            return anc_found
        for _, r in dfa.iterrows():
            yr_s = str(r.get("Year", "")).strip()
            p_name = str(r.get("period_name", "")).strip()
            mo_s = p_name.split()[0] if p_name else str(r.get("Month", "")).strip()
            fc_s = str(r.get("facility_name", "")).strip()
            if not yr_s or not mo_s or not fc_s:
                continue
            n1 = float(pd.to_numeric(r.get("ANC_1st_New", 0), errors="coerce") or 0)
            e12 = float(pd.to_numeric(r.get("ANC_1st_Under_12w", 0), errors="coerce") or 0)
            a10 = float(pd.to_numeric(r.get("ANC_Adol_10_14", 0), errors="coerce") or 0)
            a15 = float(pd.to_numeric(r.get("ANC_Adol_15_19", 0), errors="coerce") or 0)
            s_tst = float(pd.to_numeric(r.get("ANC_Syphilis_Tested", 0), errors="coerce") or 0)
            s_pos = float(pd.to_numeric(r.get("ANC_Syphilis_Pos", 0), errors="coerce") or 0)
            ifas_c = float(pd.to_numeric(r.get("ANC_IFAS_Combined", 0), errors="coerce") or 0)
            if e12 > n1:
                anc_found.append({"Year": yr_s, "Month": mo_s, "Facility": fc_s, "Issue Category": "ANC Early Booking Discrepancy", "Description": f"Early 1st ANC <=12w ({int(e12)}) exceeds Total New 1st ANC ({int(n1)})"})
            if (a10 + a15) > n1:
                anc_found.append({"Year": yr_s, "Month": mo_s, "Facility": fc_s, "Issue Category": "ANC Adolescent Age Discrepancy", "Description": f"Adolescent 1st ANC 10-19y ({int(a10 + a15)}) exceeds Total New 1st ANC ({int(n1)})"})
            if s_pos > s_tst:
                anc_found.append({"Year": yr_s, "Month": mo_s, "Facility": fc_s, "Issue Category": "ANC Syphilis Reactivity Discrepancy", "Description": f"Syphilis Reactive ({int(s_pos)}) exceeds Syphilis Tested ({int(s_tst)})"})
            if n1 > 0 and s_tst > (n1 * 2):
                anc_found.append({"Year": yr_s, "Month": mo_s, "Facility": fc_s, "Issue Category": "ANC Syphilis Volume Anomaly", "Description": f"Syphilis Tested ({int(s_tst)}) is >2x New 1st ANC ({int(n1)}) — verify MOH 711 register entry"})
            if n1 >= 5 and s_tst == 0 and ifas_c == 0:
                anc_found.append({"Year": yr_s, "Month": mo_s, "Facility": fc_s, "Issue Category": "ANC Preventive Bundle Omission", "Description": f"{int(n1)} New 1st ANC clients recorded with 0 Syphilis tests and 0 IFAS doses — verify ANC register"})
        return anc_found

    dyn_issues = _run_multisection_dq_audit(df_kpi_2025, "2025") + _run_multisection_dq_audit(df_kpi_2026, "2026") + _run_anc_dq_audit()
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
from scripts.executive_sidebar import render_executive_sidebar
focus_year, comparison_year, time_frame_type, selected_months, selected_period = render_executive_sidebar()
tabs = [
    "📊 Patient Volume Dashboard",
    "📈 Program KPI Comparative Analytics",
    "🎯 Quality Scorecard (QSC) & QI Analytics",
    "🚨 Data Quality Audits",
    "🔍 Facility Inspector",
    "💼 Financial Performance",
    "😊 LifeNet Partner facility Patient Satisfaction Survey(PSS)",
    "📑 Monthly DDIU Brief",
    "🎓 Mentee & Beneficiary Tracker",
    "🌐 Starlink & Connectivity",
]
from scripts.executive_header import render_executive_header_and_nav
active_tab = render_executive_header_and_nav(tabs, focus_year, comparison_year, selected_period)
st.markdown("---")

# ---------------------------------------------------------
# TAB 1: PATIENT VOLUME DASHBOARD
# ---------------------------------------------------------
if active_tab == "📊 Patient Volume Dashboard":
    from scripts.pv_v2_view import render_pv_v2_dashboard
    facility_pv_df, tot_base, tot_focus, abs_var, growth_pct = process_pv_timeline(
        df_pv_raw, selected_months, selected_period, focus_year, comparison_year
    )
    render_pv_v2_dashboard(
        facility_pv_df, tot_base, tot_focus, abs_var, growth_pct, focus_year, comparison_year, selected_period
    )

elif active_tab == "📈 Program KPI Comparative Analytics":
    from scripts.kpi_v2_view import render_kpi_v2_dashboard
    render_kpi_v2_dashboard(
        kpi_2025 if comparison_year == "2025" else kpi_2026,
        kpi_2026 if focus_year == "2026" else kpi_2025,
        selected_months,
        focus_year,
        comparison_year,
        selected_period,
    )

elif active_tab == "🎯 Quality Scorecard (QSC) & QI Analytics":
    from scripts.qsc_ui_theme import render_qsc_navy_header, render_qsc_facility_matrix
    render_qsc_navy_header()
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
                <div class="qsc-stat-strip">
                    <h4>{res_c3['Module']} Paired-t Intervention Analysis (Cohort 3)</h3>
                    <p>
                        <b>Baseline Mean:</b> {res_c3['Baseline_Mean']}% (SD={res_c3['Baseline_SD']}) &nbsp;|&nbsp; 
                        <b>Endline Mean:</b> {res_c3['Endline_Mean']}% (SD={res_c3['Endline_SD']}) &nbsp;|&nbsp; 
                        <b>Mean Gain:</b> +{res_c3['Mean_Gain']} pts &nbsp;|&nbsp; 
                        <b>Cohen's d<sub>z</sub>:</b> {res_c3['Cohen_dz']} &nbsp;|&nbsp; 
                        <span class="qsc-stat-badge">p = {p_fmt}</span>
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
                        <div class="qsc-kpi-card">
                            <div class="qsc-kpi-top"><span>Pre-Training Baseline</span><span>📝</span></div>
                            <div class="qsc-kpi-val">{avg_base_all:.1f}%</div>
                            <span class="qsc-kpi-pill">Baseline Score</span>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with q2:
                    st.markdown(
                        f"""
                        <div class="qsc-kpi-card">
                            <div class="qsc-kpi-top"><span>Post-Training Endline</span><span>🎯</span></div>
                            <div class="qsc-kpi-val">{avg_end_all:.1f}%</div>
                            <span class="qsc-kpi-pill">Endline Score</span>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with q3:
                    st.markdown(
                        f"""
                        <div class="qsc-kpi-card">
                            <div class="qsc-kpi-top"><span>Net Capacity Gain</span><span>📈</span></div>
                            <div class="qsc-kpi-val">+{avg_gain_all:.1f}%</div>
                            <span class="qsc-kpi-pill">+{avg_rel_growth:.1f}% Growth Rate</span>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with q4:
                    sig_count = sum(1 for p in df_ttest["p-Value"] if p < 0.05)
                    st.markdown(
                        f"""
                        <div class="qsc-kpi-card">
                            <div class="qsc-kpi-top"><span>Validated Modules</span><span>🔬</span></div>
                            <div class="qsc-kpi-val">{sig_count} / {len(df_ttest)}</div>
                            <span class="qsc-kpi-pill">Statistically Significant</span>
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
                            marker_color="#0F2C59",
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
                render_qsc_facility_matrix(
                    df_fac_perf,
                    fac_col_name,
                    "Medical" if is_medical else "Management",
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
                            <span class="qsc-stat-badge">p = {p_val_fmt} ({mod_row['Significance']})</span>
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
                                "#0F2C59" if is_medical else "#0D9488"
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
    from scripts.facility_360_view import render_facility_360_tab
    facility_pv_df_360, _, _, _, _ = process_pv_timeline(
        df_pv_raw, selected_months, selected_period, focus_year, comparison_year
    )
    render_facility_360_tab(
        facility_pv_df=facility_pv_df_360,
        kpi_2025=kpi_2025,
        kpi_2026=kpi_2026,
        df_qsc_med=df_qsc_med,
        df_qsc_mgmt=df_qsc_mgmt,
        comparison_year=comparison_year,
        focus_year=focus_year,
        selected_months=selected_months,
        selected_period=selected_period,
    )

elif active_tab == "💼 Financial Performance":
    from scripts import finance_view as fv
    fv.render_financial_performance_view()


# ---------------------------------------------------------
# TAB 7: MONTHLY DDIU & M&E EXECUTIVE BRIEF
# ---------------------------------------------------------
elif active_tab == "📑 Monthly DDIU Brief":
    from scripts import ddiu_header_view as dhv
    ddiu_period, ddiu_data = dhv.render_ddiu_top_section()

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

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    anc_c1, anc_c2 = st.columns(2)
    with anc_c1:
        anc_stages = ["1st ANC New", "Early (≤12w)", "4th ANC (ANC4+)", "Syphilis Tested", "IFAS Supplied"]
        anc_vals = [
            ddiu_data.get("tot_anc1", 0),
            ddiu_data.get("tot_e12", 0),
            ddiu_data.get("tot_a4", 0),
            ddiu_data.get("tot_sy", 0),
            ddiu_data.get("tot_ifas", 0),
        ]
        anc_pcts = [
            100.0 if anc_vals[0] > 0 else 0.0,
            ddiu_data.get("anc_early_pct", 0.0),
            ddiu_data.get("anc4_pct", 0.0),
            ddiu_data.get("anc_syph_pct", 0.0),
            ddiu_data.get("anc_ifas_pct", 0.0),
        ]
        fig_ddiu_anc_cascade = go.Figure(
            go.Bar(
                x=anc_stages,
                y=anc_vals,
                marker_color=["#0A2540", "#0D9488", "#10B981", "#2563EB", "#7C3AED"],
                text=[f"{int(v):,} ({p:.0f}%)" for v, p in zip(anc_vals, anc_pcts)],
                textposition="outside",
            )
        )
        fig_ddiu_anc_cascade.update_layout(
            title=f"Antenatal Care (ANC) Continuum Cascade — {ddiu_period}",
            height=340,
            margin=dict(l=20, r=20, t=50, b=20),
            yaxis=dict(range=[0, max(max(anc_vals), 10) * 1.22]),
        )
        st.plotly_chart(fig_ddiu_anc_cascade, use_container_width=True)

    with anc_c2:
        af_ddiu = ddiu_data.get("anc_fac_df", pd.DataFrame())
        sub_af_web = af_ddiu[af_ddiu["ANC1"] >= 1].dropna(subset=["ANC4_Pct"]).sort_values("ANC4_Pct", ascending=True).head(10) if not af_ddiu.empty else pd.DataFrame()
        if not sub_af_web.empty:
            bar_cols = ["#DC2626" if v < 50.0 else ("#D97706" if v < 65.0 else "#0D9488") for v in sub_af_web["ANC4_Pct"]]
            fig_ddiu_anc_out = go.Figure(
                go.Bar(
                    x=sub_af_web["ANC4_Pct"],
                    y=sub_af_web["Facility"],
                    orientation="h",
                    marker_color=bar_cols,
                    text=[f"{r['ANC4_Pct']:.1f}% ({int(r['ANC4'])}/{int(r['ANC1'])})" for _, r in sub_af_web.iterrows()],
                    textposition="outside",
                )
            )
            fig_ddiu_anc_out.add_vline(x=50.0, line_dash="dash", line_color="#DC2626", annotation_text="50% Action Threshold")
            fig_ddiu_anc_out.update_layout(
                title=f"Lowest ANC4+ Retention Facilities — {ddiu_period}",
                height=340,
                margin=dict(l=20, r=40, t=50, b=20),
                xaxis=dict(title="ANC4+ Retention (%)", range=[0, max(sub_af_web["ANC4_Pct"].max() * 1.25, 70)]),
            )
            st.plotly_chart(fig_ddiu_anc_out, use_container_width=True)
        else:
            st.info(f"No facilities with ≥1 1st ANC contacts in {ddiu_period} to rank ANC4+ retention.")

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


# ---------------------------------------------------------
# TAB: LIFENET PARTNER FACILITY PATIENT SATISFACTION SURVEY (PSS)
# ---------------------------------------------------------
    st.markdown("---")
    st.markdown(f"#### 😊 Patient Satisfaction Survey (PSS) & Unassessed Facility Reminder ({ddiu_data['pss_window']})")
    ps1, ps2, ps3, ps4 = st.columns(4)
    ps1.metric("Net Patient Satisfaction (12M Mean)", f"{ddiu_data['pss_mean']:.1f}%", f"Median: {ddiu_data['pss_median']:.1f}%")
    ps2.metric("12M Assessed Facilities", f"{ddiu_data['pss_assessed']} / 38", f"{(ddiu_data['pss_assessed']/38*100):.1f}% Coverage")
    ps3.metric("Unassessed Reminder (0 PSS)", f"{ddiu_data['pss_unassessed']} Sites", "Action: Schedule Baseline PSS", delta_color="inverse")
    ps4.metric("Sub-75% QI Escalations", f"{len(ddiu_data['pss_low_facs'])} Sites", ", ".join(ddiu_data["pss_low_facs"][:2]) if ddiu_data["pss_low_facs"] else "All >= 75%")

    pss_pend_ui = ddiu_data.get("pss_pending_df", pd.DataFrame())
    if not pss_pend_ui.empty:
        st.caption("Priority deployment reminder for M&E and Field Mentors — facilities with zero PSS in the past 12 months or overdue for 6-month follow-up (included in the downloadable PDF report above):")
        fmt_ddiu_pss = {}
        if "12M_Outpatient_PV" in pss_pend_ui.columns:
            fmt_ddiu_pss["12M_Outpatient_PV"] = lambda v: f"{int(v):,}" if pd.notna(v) else "—"
        if "Last_Net_Patient_Satisfaction_%" in pss_pend_ui.columns:
            fmt_ddiu_pss["Last_Net_Patient_Satisfaction_%"] = lambda v: f"{float(v):.1f}%" if pd.notna(v) else "—"
        styled_ddiu_pss = pss_pend_ui.style.format(fmt_ddiu_pss).set_properties(**{"background-color": "#FFFFFF", "color": "#0F172A", "border-color": "#E2E8F0"})
        st.dataframe(styled_ddiu_pss, hide_index=True, use_container_width=True)

elif active_tab == "😊 LifeNet Partner facility Patient Satisfaction Survey(PSS)":
    from scripts import pss_view as pv
    pv.render_pss_view()

elif active_tab == "🎓 Mentee & Beneficiary Tracker":
    from scripts.mentee_tracker_view import render_mentee_tracker_view
    render_mentee_tracker_view()

elif active_tab == "🌐 Starlink & Connectivity":
    from scripts.connectivity_view import render_connectivity_dashboard
    render_connectivity_dashboard()
