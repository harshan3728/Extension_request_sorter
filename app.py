"""
Extension Request Sorter — CIT Academic Portal
Ultra-Premium Enterprise SaaS Edition
Design Targets:
- Zero gimmicky emojis; unified professional inline SVG Lucide-style icon system (16-20px, 1.75 stroke-width)
- Typography: Plus Jakarta Sans (Headings), Inter (Body), Space Grotesk (KPI Numbers), JetBrains Mono (Code)
- Sophisticated Layered Palette: Deep Midnight Navy (#080c16), Royal Blue (#1d4ed8), Electric Indigo (#4f46e5), Lavender (#c7d2fe), Crisp Ivory/White (#f8fafc)
- Clean pill-style status badges with subtle border rings and translucent tints
- Streamlined sidebar with crisp enterprise hierarchy
- 100% preservation of Groq AI extraction, Python deterministic validation, policy enforcement, privacy redaction, and CSV/TXT exports
"""

import os
import io
import csv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

# Tested backend modules (Strictly Preserved)
from extractor import classify, load_system_prompt, DEFAULT_MODEL
from validator import is_valid
from policy import (
    recommend,
    MAX_DAYS_WITHIN_POLICY,
    ELIGIBLE_REASONS,
    VALID_REASONS,
    STATUS_WITHIN_POLICY,
    STATUS_NEEDS_MORE_INFO,
    STATUS_NEEDS_FACULTY_REVIEW
)
from reporter import write_reports, sanitize_csv_value

# Load environment variables
load_dotenv()

# Assets
LOGO_PATH = os.path.join("assets", "logo.png")

# Page Configuration
st.set_page_config(
    page_title="CIT Academic Portal — Extension Request Sorter",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================================================================
# INLINE SVG ICON SYSTEM (LUCIDE-STYLE, 18px, STROKE 1.75, UNIFIED DESIGN)
# =================================================================================================
def icon_svg(name: str, color: str = "currentColor", size: int = 18) -> str:
    """Returns clean, professional Lucide-style SVG markup."""
    icons = {
        "layout-dashboard": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
        "cpu": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>',
        "clipboard-check": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg>',
        "file-text": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>',
        "sliders": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="4" y1="21" y2="14"/><line x1="4" x2="4" y1="10" y2="3"/><line x1="12" x2="12" y1="21" y2="12"/><line x1="12" x2="12" y1="8" y2="3"/><line x1="20" x2="20" y1="21" y2="16"/><line x1="20" x2="20" y1="12" y2="3"/><line x1="1" x2="7" y1="14" y2="14"/><line x1="9" x2="15" y1="8" y2="8"/><line x1="17" x2="23" y1="16" y2="16"/></svg>',
        "log-out": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>',
        "shield-check": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>',
        "activity": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
        "check-circle-2": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>',
        "alert-circle": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>',
        "alert-triangle": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>',
        "download": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>',
        "lock": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
        "upload-cloud": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>',
        "pie-chart": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
        "bar-chart-3": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>'
    }
    return icons.get(name, "")


# =================================================================================================
# MASTER ENTERPRISE DESIGN SYSTEM CSS
# =================================================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Color Tokens */
    :root {
        --bg-canvas: #070b14;
        --bg-surface: #0c1220;
        --bg-surface-elevated: #111a2e;
        --border-subtle: rgba(255, 255, 255, 0.08);
        --border-accent: rgba(99, 102, 241, 0.25);
        --primary-blue: #2563eb;
        --primary-indigo: #4f46e5;
        --accent-lavender: #818cf8;
        --text-headline: #f8fafc;
        --text-body: #94a3b8;
        --text-muted: #64748b;
        --success-emerald: #10b981;
        --warning-amber: #f59e0b;
        --danger-rose: #f43f5e;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-headline);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700;
        letter-spacing: -0.025em;
    }

    .kpi-figure {
        font-family: 'Space Grotesk', sans-serif !important;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Seamless Dark Header Bar */
    header[data-testid="stHeader"] {
        background: transparent !important;
        background-color: var(--bg-canvas) !important;
        height: 2.2rem;
    }

    [data-testid="stToolbar"] {
        right: 1.2rem;
    }

    .stApp {
        background-color: var(--bg-canvas);
        background-image: 
            radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.22) 0px, transparent 55%),
            radial-gradient(at 100% 0%, rgba(79, 70, 229, 0.16) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(14, 23, 42, 0.7) 0px, transparent 65%);
        background-attachment: fixed;
    }

    /* Enterprise Sidebar */
    [data-testid="stSidebar"] {
        background: #090e1a !important;
        border-right: 1px solid var(--border-subtle) !important;
        box-shadow: 2px 0 16px rgba(0, 0, 0, 0.4);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
        color: #cbd5e1 !important;
        font-weight: 500;
    }

    [data-testid="stSidebar"] .stRadio label {
        color: #e2e8f0 !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        padding: 0.45rem 0.75rem !important;
        border-radius: 8px !important;
        transition: all 0.2s ease;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(99, 102, 241, 0.12) !important;
        color: #c7d2fe !important;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background: rgba(79, 70, 229, 0.18) !important;
        border-left: 3px solid var(--accent-lavender) !important;
        color: #ffffff !important;
    }

    /* Header Banner */
    .enterprise-banner {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.75) 0%, rgba(30, 41, 59, 0.5) 100%);
        border: 1px solid var(--border-accent);
        border-radius: 14px;
        padding: 1.6rem 2rem;
        margin-bottom: 1.8rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 30px -4px rgba(0, 0, 0, 0.35);
    }

    .enterprise-title {
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin: 0;
        color: #ffffff;
    }

    .enterprise-subtitle {
        color: var(--text-body);
        font-size: 0.92rem;
        margin-top: 0.35rem;
        font-weight: 400;
        line-height: 1.5;
    }

    /* KPI Cards */
    .kpi-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.2rem;
        margin-bottom: 1.8rem;
    }

    .kpi-box {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.3rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        position: relative;
    }

    .kpi-box:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.35);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    }

    .kpi-label {
        color: var(--text-muted);
        font-size: 0.76rem;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.08em;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .kpi-figure {
        font-size: 2.3rem;
        font-weight: 700;
        margin: 0.35rem 0 0.15rem 0;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }

    .kpi-meta {
        font-size: 0.76rem;
        color: var(--text-muted);
        font-weight: 500;
    }

    /* Pill-Style Badges */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }

    .badge-pill-policy {
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-pill-review {
        background: rgba(245, 158, 11, 0.12);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .badge-pill-info {
        background: rgba(244, 63, 94, 0.12);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.3);
    }

    /* Enterprise Login Card */
    .login-box {
        background: var(--bg-surface);
        border: 1px solid var(--border-accent);
        border-radius: 16px;
        padding: 2.2rem;
        backdrop-filter: blur(16px);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
        max-width: 480px;
        margin: 0 auto;
    }

    .feature-item {
        display: flex;
        align-items: flex-start;
        gap: 0.9rem;
        background: rgba(17, 24, 39, 0.5);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 0.95rem 1.15rem;
        margin-bottom: 0.85rem;
        transition: border-color 0.2s ease;
    }

    .feature-item:hover {
        border-color: rgba(99, 102, 241, 0.35);
    }

    /* Primary Action Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #2563eb 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.4rem !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.5) !important;
    }

    /* Form Inputs */
    .stTextInput input {
        background-color: #0b111e !important;
        border: 1px solid var(--border-accent) !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
        font-size: 0.92rem !important;
    }

    .stTextInput input:focus {
        border-color: var(--accent-lavender) !important;
        box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.25) !important;
    }

    /* Clean Dataframe Box */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid var(--border-subtle);
    }
</style>
""", unsafe_allow_html=True)


def get_courses_dict():
    """Reads course registry from courses.csv."""
    courses = {}
    if os.path.exists("courses.csv"):
        with open("courses.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row.get("code", "").strip().upper()
                name = row.get("name", "").strip()
                if code:
                    courses[code] = name
    return courses


# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "admin_user" not in st.session_state:
    st.session_state.admin_user = ""

if "processed_data" not in st.session_state:
    if os.path.exists("results.csv") and os.path.exists("review_queue.csv"):
        try:
            df_results = pd.read_csv("results.csv")
            df_review = pd.read_csv("review_queue.csv")
            merged = df_results.merge(df_review[["id", "request"]], on="id", how="left")
            st.session_state.processed_data = merged.to_dict("records")
        except Exception:
            st.session_state.processed_data = []
    else:
        st.session_state.processed_data = []


# =================================================================================================
# GATEWAY VIEW: ENTERPRISE LOGIN & CIT ACADEMIC PORTAL LANDING
# =================================================================================================
if not st.session_state.authenticated:
    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    c_left, c_right = st.columns([1.15, 1], gap="large")

    with c_left:
        # High-Resolution Official Brand Logo
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=440)
        else:
            st.markdown("""
            <div style="font-weight:700; font-size:1.6rem; color:#ffffff; margin-bottom:0.6rem;">
                CIT ACADEMIC PORTAL
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <p style="color:#94a3b8; font-size:1rem; line-height:1.6; margin: 1.2rem 0 1.6rem 0;">
            Flagship academic administration platform. Delivers automated student extension request triage by pairing high-throughput Groq LPU information extraction with deterministic departmental policy rules.
        </p>
        """, unsafe_allow_html=True)

        # Technical Feature System
        st.markdown(f"""
        <div class="feature-item">
            <span style="color:#60a5fa; margin-top:0.2rem;">{icon_svg("cpu", "#60a5fa", 20)}</span>
            <div>
                <div style="font-weight:600; color:#f8fafc; font-size:0.92rem;">Groq LPU Information Extraction</div>
                <div style="color:#94a3b8; font-size:0.8rem; line-height:1.45;">Sub-second structured fact parsing using openai/gpt-oss-120b constrained by a five-role prompt architecture.</div>
            </div>
        </div>

        <div class="feature-item">
            <span style="color:#818cf8; margin-top:0.2rem;">{icon_svg("shield-check", "#818cf8", 20)}</span>
            <div>
                <div style="font-weight:600; color:#f8fafc; font-size:0.92rem;">Deterministic Policy Engine</div>
                <div style="color:#94a3b8; font-size:0.8rem; line-height:1.45;">Strictly Python-governed recommendations. The AI system never approves or rejects requests; academic staff retain final authority.</div>
            </div>
        </div>

        <div class="feature-item">
            <span style="color:#34d399; margin-top:0.2rem;">{icon_svg("lock", "#34d399", 20)}</span>
            <div>
                <div style="font-weight:600; color:#f8fafc; font-size:0.92rem;">Data Privacy & Integrity Safeguards</div>
                <div style="color:#94a3b8; font-size:0.8rem; line-height:1.45;">Personal health terms scrubbed from public summaries; CSV injection vulnerabilities actively neutralized.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_right:
        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="login-box">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.1rem;">
                <div style="font-weight:700; font-size:1.2rem; color:#f8fafc;">Faculty Sign In</div>
                <span style="background:rgba(37,99,235,0.18); color:#93c5fd; padding:3px 10px; border-radius:9999px; font-size:0.72rem; font-weight:600; border:1px solid rgba(37,99,235,0.4);">
                    LOCAL ACCESS GATE
                </span>
            </div>
            <div style="color:#94a3b8; font-size:0.85rem; margin-bottom:1.3rem; line-height:1.45;">
                Enter your administrative credentials or faculty access code to open the assignment extension triage workspace.
            </div>
        """, unsafe_allow_html=True)

        # Clean Login Form
        with st.form("admin_login_form"):
            admin_id = st.text_input("Faculty ID / Username", value="faculty.cit@univ.edu")
            access_code_input = st.text_input("Access Code", type="password", placeholder="Enter access code...")
            remember_me = st.checkbox("Keep session active in current browser tab", value=True)
            submit_login = st.form_submit_button("Authenticate Workspace", use_container_width=True)

            if submit_login:
                configured_code = os.getenv("FACULTY_ACCESS_CODE", "citadmin2026")
                if access_code_input == configured_code:
                    st.session_state.authenticated = True
                    st.session_state.admin_user = admin_id
                    st.toast("Authentication confirmed.", icon="✅")
                    st.rerun()
                else:
                    st.error("Invalid access code. Please check your credentials or .env configuration.")

        st.markdown("""
            <div style="margin-top:1.3rem; padding-top:0.9rem; border-top:1px solid rgba(255,255,255,0.06); font-size:0.75rem; color:#64748b; text-align:center;">
                Academic Demonstration Gateway &mdash; Configured via <code>FACULTY_ACCESS_CODE</code> in <code>.env</code>
            </div>
        </div>
        """, unsafe_allow_html=True)


# =================================================================================================
# MAIN APPLICATION INTERFACE (AUTHENTICATED FACULTY VIEW)
# =================================================================================================
else:
    # Enterprise Sidebar Navigation
    with st.sidebar:
        # Compact Brand Logo
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, use_container_width=True)
        else:
            st.markdown("""
            <div style="font-weight:700; font-size:1.15rem; color:#ffffff;">CIT ACADEMIC PORTAL</div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:rgba(15,23,42,0.85); border:1px solid rgba(99,102,241,0.25); border-radius:8px; padding:0.6rem 0.8rem; margin:0.8rem 0;">
            <div style="font-size:0.68rem; color:#94a3b8; text-transform:uppercase; font-weight:700; letter-spacing:0.06em;">Signed in as</div>
            <div style="font-size:0.82rem; color:#e0e7ff; font-weight:600; word-break:break-all;">{st.session_state.admin_user}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Process Requests",
                "Faculty Review Queue",
                "Reports & Exports",
                "System Settings"
            ],
            index=0
        )

        st.markdown("---")

        # Working Logout Button
        if st.button("Sign Out of Portal", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.admin_user = ""
            st.toast("Signed out successfully.")
            st.rerun()

        st.markdown("---")
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); padding:0.8rem; border-radius:8px;">
            <div style="font-size:0.72rem; font-weight:700; color:#cbd5e1; margin-bottom:0.25rem; display:flex; align-items:center; gap:0.4rem;">
                {icon_svg("shield-check", "#818cf8", 15)} ACADEMIC GOVERNANCE
            </div>
            <div style="font-size:0.72rem; color:#94a3b8; line-height:1.45;">
                AI performs extraction only. Policy recommendations are 100% deterministic. Faculty hold sole academic decision authority.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------------------------------------------
    # PAGE 1: DASHBOARD
    # ---------------------------------------------------------------------------------------------
    if page == "Dashboard":
        col_h1, col_h2 = st.columns([1, 4.5])
        with col_h1:
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=160)
        with col_h2:
            st.markdown(f"""
            <div class="enterprise-banner" style="margin-bottom:1.2rem; padding:1.2rem 1.8rem;">
                <h1 class="enterprise-title">Academic Extension Analytics</h1>
                <div class="enterprise-subtitle">Batch triage status, category distributions, and deterministic policy recommendation analytics</div>
            </div>
            """, unsafe_allow_html=True)

        data = st.session_state.processed_data
        if not data:
            st.info("No student requests currently loaded. Navigate to **Process Requests** to execute or upload a batch.")
        else:
            df = pd.DataFrame(data)
            total = len(df)
            within = len(df[df["recommendation"] == STATUS_WITHIN_POLICY])
            review = len(df[df["recommendation"] == STATUS_NEEDS_FACULTY_REVIEW])
            missing = len(df[df["recommendation"] == STATUS_NEEDS_MORE_INFO])

            # Modern Clean KPI Row
            st.markdown(f"""
            <div class="kpi-row">
                <div class="kpi-box" style="border-top: 3px solid #3b82f6;">
                    <div class="kpi-label">{icon_svg("activity", "#60a5fa", 14)} Total Batch Volume</div>
                    <div class="kpi-figure" style="color:#60a5fa;">{total}</div>
                    <div class="kpi-meta">Processed student requests</div>
                </div>
                <div class="kpi-box" style="border-top: 3px solid #10b981;">
                    <div class="kpi-label">{icon_svg("check-circle-2", "#34d399", 14)} Within Policy</div>
                    <div class="kpi-figure" style="color:#34d399;">{within}</div>
                    <div class="kpi-meta">Eligible categories (≤ 3 days)</div>
                </div>
                <div class="kpi-box" style="border-top: 3px solid #f59e0b;">
                    <div class="kpi-label">{icon_svg("alert-triangle", "#fbbf24", 14)} Faculty Review</div>
                    <div class="kpi-figure" style="color:#fbbf24;">{review}</div>
                    <div class="kpi-meta">> 3 days or complex grounds</div>
                </div>
                <div class="kpi-box" style="border-top: 3px solid #f43f5e;">
                    <div class="kpi-label">{icon_svg("alert-circle", "#fb7185", 14)} Needs More Info</div>
                    <div class="kpi-figure" style="color:#fb7185;">{missing}</div>
                    <div class="kpi-meta">Missing course code or days</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Analytics Visualizations
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.markdown(f"#### {icon_svg('pie-chart', '#818cf8', 18)} Policy Recommendation Breakdown", unsafe_allow_html=True)
                rec_df = df["recommendation"].value_counts().reset_index()
                rec_df.columns = ["Recommendation", "Count"]

                fig_donut = px.pie(
                    rec_df,
                    values="Count",
                    names="Recommendation",
                    color="Recommendation",
                    color_discrete_map={
                        STATUS_WITHIN_POLICY: "#10b981",
                        STATUS_NEEDS_FACULTY_REVIEW: "#f59e0b",
                        STATUS_NEEDS_MORE_INFO: "#f43f5e"
                    },
                    hole=0.55
                )
                fig_donut.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    marker=dict(line=dict(color='#070b14', width=2))
                )
                fig_donut.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#f8fafc", family="Plus Jakarta Sans"),
                    margin=dict(t=15, b=15, l=10, r=10),
                    showlegend=False
                )
                st.plotly_chart(fig_donut, use_container_width=True)

            with col_chart2:
                st.markdown(f"#### {icon_svg('bar-chart-3', '#60a5fa', 18)} Course Distribution", unsafe_allow_html=True)
                df["course_clean"] = df["course"].fillna("Unspecified")
                course_df = df["course_clean"].value_counts().reset_index()
                course_df.columns = ["Course", "Count"]

                fig_bar = px.bar(
                    course_df,
                    x="Course",
                    y="Count",
                    color="Course",
                    color_discrete_sequence=["#2563eb", "#4f46e5", "#7c3aed", "#9333ea", "#06b6d4", "#64748b"]
                )
                fig_bar.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#f8fafc", family="Plus Jakarta Sans"),
                    margin=dict(t=15, b=15, l=10, r=10),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
                    showlegend=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # Recent Activity Table
            st.markdown(f"#### {icon_svg('file-text', '#cbd5e1', 18)} Recent Batch Records", unsafe_allow_html=True)
            display_df = df[["id", "date", "course", "days", "reason", "recommendation", "summary"]].copy()
            display_df["course"] = display_df["course"].fillna("—")
            display_df["days"] = display_df["days"].fillna("—")
            st.dataframe(display_df, use_container_width=True, height=270)

    # ---------------------------------------------------------------------------------------------
    # PAGE 2: PROCESS REQUESTS
    # ---------------------------------------------------------------------------------------------
    elif page == "Process Requests":
        st.markdown(f"""
        <div class="enterprise-banner">
            <h1 class="enterprise-title">Process Student Requests</h1>
            <div class="enterprise-subtitle">Execute batch triage using Groq API extraction and deterministic Python policy validation</div>
        </div>
        """, unsafe_allow_html=True)

        col_up1, col_up2 = st.columns(2)
        with col_up1:
            st.markdown(f"##### {icon_svg('upload-cloud', '#60a5fa', 17)} Student Requests Dataset", unsafe_allow_html=True)
            req_file = st.file_uploader("Upload requests.csv (Optional)", type=["csv"], help="Expected columns: id, date, request")
        with col_up2:
            st.markdown(f"##### {icon_svg('clipboard-check', '#818cf8', 17)} Course Registry Dataset", unsafe_allow_html=True)
            courses_file = st.file_uploader("Upload courses.csv (Optional)", type=["csv"], help="Expected columns: code, name")

        courses_dict = get_courses_dict()
        valid_courses = set(courses_dict.keys())

        run_btn = st.button("Execute Pipeline", type="primary", use_container_width=True)

        if run_btn:
            requests_to_process = []
            if req_file is not None:
                content = req_file.getvalue().decode("utf-8")
                reader = csv.DictReader(io.StringIO(content))
                for row in reader:
                    if row.get("id"):
                        requests_to_process.append({
                            "id": row.get("id", "").strip(),
                            "date": row.get("date", "").strip(),
                            "request": row.get("request", "").strip()
                        })
            elif os.path.exists("requests.csv"):
                with open("requests.csv", "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get("id"):
                            requests_to_process.append({
                                "id": row.get("id", "").strip(),
                                "date": row.get("date", "").strip(),
                                "request": row.get("request", "").strip()
                            })

            if not requests_to_process:
                st.error("No valid requests found in uploaded or local requests.csv.")
            else:
                prog_bar = st.progress(0)
                status_text = st.empty()
                processed_records = []
                system_prompt = load_system_prompt()
                total_count = len(requests_to_process)

                for idx, item in enumerate(requests_to_process):
                    status_text.markdown(f"**Verifying & Classifying ({idx+1}/{total_count}):** `{item['id']}`...")
                    extracted = classify(item["request"], valid_courses, system_prompt=system_prompt)

                    valid, _ = is_valid(extracted, item["request"], valid_courses)
                    if not valid:
                        course = None
                        days = None
                        reason = "other"
                        summary = "Validation error: unverified"
                    else:
                        course = extracted.get("course")
                        days = extracted.get("days")
                        reason = extracted.get("reason")
                        summary = extracted.get("summary")

                    rec_status = recommend(course, days, reason)

                    processed_records.append({
                        "id": item["id"],
                        "date": item["date"],
                        "course": course,
                        "days": days,
                        "reason": reason,
                        "recommendation": rec_status,
                        "summary": summary,
                        "request": item["request"]
                    })
                    prog_bar.progress((idx + 1) / total_count)

                # Persist output files
                write_reports(processed_records)
                st.session_state.processed_data = processed_records

                status_text.success(f"Processing complete. {total_count} requests evaluated and persisted.")
                st.markdown("#### Processing Output")
                res_df = pd.DataFrame(processed_records)[["id", "date", "course", "days", "reason", "recommendation", "summary"]]
                st.dataframe(res_df, use_container_width=True)

    # ---------------------------------------------------------------------------------------------
    # PAGE 3: FACULTY REVIEW QUEUE
    # ---------------------------------------------------------------------------------------------
    elif page == "Faculty Review Queue":
        st.markdown(f"""
        <div class="enterprise-banner">
            <h1 class="enterprise-title">Faculty Review Queue</h1>
            <div class="enterprise-subtitle">Protected queue containing requests requiring human academic evaluation</div>
        </div>
        """, unsafe_allow_html=True)

        data = st.session_state.processed_data
        if not data:
            st.info("No records loaded.")
        else:
            df = pd.DataFrame(data)
            review_df = df[df["recommendation"] != STATUS_WITHIN_POLICY].copy()

            if review_df.empty:
                st.success("All requests in this batch comply with within-policy criteria.")
            else:
                col_f1, col_f2, col_f3 = st.columns([1, 1, 1.5])
                with col_f1:
                    status_choices = st.multiselect(
                        "Filter Status",
                        options=[STATUS_NEEDS_FACULTY_REVIEW, STATUS_NEEDS_MORE_INFO],
                        default=[STATUS_NEEDS_FACULTY_REVIEW, STATUS_NEEDS_MORE_INFO]
                    )
                with col_f2:
                    available_courses = sorted(list(review_df["course"].dropna().unique()))
                    course_choices = st.multiselect("Filter Course", options=available_courses, default=available_courses)
                with col_f3:
                    search_term = st.text_input("Search ID, Course, or Keyword", "")

                filtered = review_df[review_df["recommendation"].isin(status_choices)]
                if course_choices:
                    filtered = filtered[filtered["course"].isin(course_choices) | filtered["course"].isna()]
                if search_term:
                    filtered = filtered[
                        filtered["id"].str.contains(search_term, case=False, na=False) |
                        filtered["request"].str.contains(search_term, case=False, na=False) |
                        filtered["summary"].str.contains(search_term, case=False, na=False)
                    ]

                st.markdown(f"**Showing {len(filtered)} flagged requests requiring action:**")

                for _, row in filtered.iterrows():
                    badge_cls = "badge-pill-review" if row["recommendation"] == STATUS_NEEDS_FACULTY_REVIEW else "badge-pill-info"
                    with st.expander(f"{row['id']} — {row['course'] or 'MISSING COURSE'} ({row['days'] or '?'} Days) | {row['recommendation'].upper()}"):
                        c1, c2 = st.columns([1.2, 2])
                        with c1:
                            st.markdown(f"**Request ID:** `{row['id']}`")
                            st.markdown(f"**Submission Date:** `{row['date']}`")
                            st.markdown(f"**Course Code:** `{row['course'] or 'Not Provided'}`")
                            st.markdown(f"**Requested Days:** `{row['days'] or 'Not Provided'}`")
                            st.markdown(f"**Extracted Category:** `{row['reason']}`")
                            st.markdown(f"**Policy Status:** <span class='badge-pill {badge_cls}'>{row['recommendation']}</span>", unsafe_allow_html=True)
                            st.markdown(f"**Privacy Summary:** *{row['summary']}*")
                        with c2:
                            st.markdown("**Original Student Submission (Confidential):**")
                            st.info(row.get("request", "No text recorded"))
                            if row["recommendation"] == STATUS_NEEDS_MORE_INFO:
                                st.warning("Action Required: Request clarification from student for missing course code or explicit day count.")
                            else:
                                st.success("Action Required: Course coordinator reviews documentation to decide on extension request.")

    # ---------------------------------------------------------------------------------------------
    # PAGE 4: REPORTS & EXPORTS
    # ---------------------------------------------------------------------------------------------
    elif page == "Reports & Exports":
        st.markdown(f"""
        <div class="enterprise-banner">
            <h1 class="enterprise-title">Download Official Reports</h1>
            <div class="enterprise-subtitle">Export de-identified public summaries, faculty review records, and aggregate metric reports</div>
        </div>
        """, unsafe_allow_html=True)

        r_col1, r_col2, r_col3 = st.columns(3)

        with r_col1:
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">{icon_svg("file-text", "#60a5fa", 16)} Results CSV</div>
                <div style="font-size:0.85rem; color:#94a3b8; margin:0.6rem 0;">Public report with neutral summaries. Raw request text strictly excluded.</div>
            </div>
            """, unsafe_allow_html=True)
            if os.path.exists("results.csv"):
                with open("results.csv", "rb") as f:
                    st.download_button(
                        label="Download results.csv",
                        data=f.read(),
                        file_name="results.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

        with r_col2:
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">{icon_svg("lock", "#818cf8", 16)} Review Queue CSV</div>
                <div style="font-size:0.85rem; color:#94a3b8; margin:0.6rem 0;">Faculty-only queue containing all exceptions with raw request text preserved.</div>
            </div>
            """, unsafe_allow_html=True)
            if os.path.exists("review_queue.csv"):
                with open("review_queue.csv", "rb") as f:
                    st.download_button(
                        label="Download review_queue.csv",
                        data=f.read(),
                        file_name="review_queue.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

        with r_col3:
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">{icon_svg("bar-chart-3", "#34d399", 16)} Summary TXT</div>
                <div style="font-size:0.85rem; color:#94a3b8; margin:0.6rem 0;">De-identified administrative report with aggregated metric counts.</div>
            </div>
            """, unsafe_allow_html=True)
            if os.path.exists("summary.txt"):
                with open("summary.txt", "rb") as f:
                    st.download_button(
                        label="Download summary.txt",
                        data=f.read(),
                        file_name="summary.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

        st.markdown("---")
        st.markdown(f"#### {icon_svg('file-text', '#cbd5e1', 17)} Live Summary Report Preview (`summary.txt`)", unsafe_allow_html=True)
        if os.path.exists("summary.txt"):
            with open("summary.txt", "r", encoding="utf-8") as f:
                st.code(f.read(), language="text")

    # ---------------------------------------------------------------------------------------------
    # PAGE 5: SYSTEM SETTINGS
    # ---------------------------------------------------------------------------------------------
    elif page == "System Settings":
        st.markdown(f"""
        <div class="enterprise-banner">
            <h1 class="enterprise-title">System Settings & Architecture</h1>
            <div class="enterprise-subtitle">Active AI configuration, deterministic policy constants, and architectural invariants</div>
        </div>
        """, unsafe_allow_html=True)

        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY", "")
        has_key = bool(api_key and api_key != "your_key_here")
        active_model = os.getenv("GROQ_MODEL", DEFAULT_MODEL)

        s1, s2 = st.columns(2)

        with s1:
            st.markdown(f"#### {icon_svg('cpu', '#60a5fa', 18)} AI Model Configuration", unsafe_allow_html=True)
            st.markdown(f"**Target Model:** `{active_model}`")
            if has_key:
                st.success(f"Groq API Connected (`***...{api_key[-4:] if len(api_key)>4 else '****'}`)")
            else:
                st.info("Running in Offline Mock Mode (No live Groq API key set in .env)")

            st.markdown(f"#### {icon_svg('file-text', '#818cf8', 18)} Five-Role Prompt Architecture", unsafe_allow_html=True)
            st.caption("Configured in `system_prompt.txt`")
            if os.path.exists("system_prompt.txt"):
                with st.expander("Inspect Five-Role Prompt"):
                    st.text(load_system_prompt())

        with s2:
            st.markdown(f"#### {icon_svg('shield-check', '#34d399', 18)} Policy Rules & Constants", unsafe_allow_html=True)
            st.markdown(f"- **Max Days Within Policy:** `{MAX_DAYS_WITHIN_POLICY}` days")
            st.markdown(f"- **Eligible Categories:** `{', '.join(sorted(ELIGIBLE_REASONS))}`")
            st.markdown(f"- **Allowed Reason Taxonomy:** `{', '.join(sorted(VALID_REASONS))}`")

            st.markdown(f"#### {icon_svg('lock', '#cbd5e1', 18)} Governance Guardrails", unsafe_allow_html=True)
            st.markdown("""
            1. **Extraction Only**: AI never decides approvals or rejections.
            2. **Deterministic Rules**: Extension policies are executed purely in Python.
            3. **Zero Hallucinated Dates**: Days must explicitly appear in student requests.
            4. **Formula Injection Sanitization**: CSV fields starting with `=, +, -, @` are escaped.
            """)
