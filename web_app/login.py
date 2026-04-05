import streamlit as st
import json
from pathlib import Path
import extra_streamlit_components as stx
import streamlit.components.v1 as components
import time
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="InSync", layout="wide", initial_sidebar_state="expanded")

# 2. Path Handling & Cookie Initialisation
current_file = Path(__file__).resolve()  # login.py
web_app_path = current_file.parent       # web_app folder
root_path = web_app_path.parent          # IPCoursework folder 
logo_path = root_path / "assets" / "insync_logo.png"
data_path = root_path / "data" / "users.json"

# Initialize Cookie Manager
cookie_manager = stx.CookieManager()
# Cookie Logic
if "user_data" not in st.session_state:
    all_cookies = cookie_manager.get_all()
    if all_cookies and "insync_user" in all_cookies:
        cookie_manager.delete("insync_user")

# 3. Enhanced CSS (Figma Precision)
st.markdown("""
    <style>
    /* Force Background Gradient to fill the whole screen */
    .stApp {
        background: linear-gradient(135deg, #A78BFA 0%, #34D399 100%) !important;
    }
    
    /*Menu*/
    [data-testid="stSidebar"] {
    background-color: #A78BFA !important; 
    background: linear-gradient(180deg, #A78BFA 0%, #34D399 100%) !important;
    }

    [data-testid="stSidebar"] * {
    color: white !important;
    }
            
    /*Top Header bar*/
    header[data-testid="stHeader"] {
    background-color: rgba(0, 0, 0, 0) !important; /* Makes it transparent */
    }

    /*Menu Arrow*/
    button[kind="headerNoContext"] svg {
    fill: white !important;
    }
    
    /*Buttons in the Side Bar Menu*/
    section[data-testid="stSidebar"] .stButton > button {
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    border-radius: 10px;
    transition: all 0.3s ease;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #34D399 !important; 
    border-color: white !important;
    transform: scale(1.02);
    }        
    
    /* Hero Text Styling */
    .hero-container {
        color: white !important;
        padding-top: 100px;
        margin-left: 40px;
    }
    
    .hero-container h1 {
        font-size: 100px !important;
        font-weight: 900 !important;
        line-height: 0.9 !important;
        color: white !important;
    }
    
    .hero-container p {
        font-size: 24px !important;
        opacity: 0.9;
    }


    /* Logo Container */
    [data-testid="stImage"] {
    display: flex !important;
    justify-content: center !important; 
    }

    /* Logo Image*/
    [data-testid="stImage"] img { 
    height: auto;
    }

    /* Input Field Styling */
    .stTextInput label {
        color: #475569 !important;
        font-weight: 600 !important;
        margin-bottom: 8px;
    }
    
    .stTextInput div div input {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }

    /* Primary Button (Log In) */
    button[kind="primary"] {
        background-color: #6366F1 !important;
        color: white !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
        margin-top: 10px;
    }

    /* Secondary Button (Create Account) */
    button[kind="secondary"] {
        border-radius: 12px !important;
        height: 3.5em !important;
    }
            
    /* Footer Container */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(255, 255, 255, 0.1); /* Semi-transparent white */
        backdrop-filter: blur(10px); /* Glassmorphism effect */
        color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
        letter-spacing: 1px;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        z-index: 999;
    }

    /* Adjusting the main content so it doesn't get hidden behind the footer */
    .main .block-container {
        padding-bottom: 60px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. App Layout
col1, col2 = st.columns([1.6, 1], gap="large")

with col1:
    st.markdown("""
        <div class="hero-container">
            <h1>Welcome<br>Back!</h1>
            <p>Your next perfect match is waiting.<br>
            <span style='font-size: 18px; opacity: 0.7;'>Sign in to continue syncing brands with creators.</span></p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    # Display Logo if it exists
    if logo_path.exists():
        st.image(str(logo_path), width=360)
    else:
        st.markdown("<h1 style='color: #6366F1;'>InSync</h1>", unsafe_allow_html=True)
        
    st.write("---")
    
    email_in = st.text_input("Email Address", placeholder="amanda@mdx.mu", key="l_email")
    pass_in = st.text_input("Password", type="password", placeholder="••••••••", key="l_pass")
    
    st.write(" ")
    
    if st.button("Log In", use_container_width=True, type="primary"):
        # Load and Search Logic
        users = []
        if data_path.exists():
            with open(data_path, "r") as f:
                try:
                    users = json.load(f)
                except:
                    users = []
        
        authenticated_user = next((u for u in users if u.get('email') == email_in and u.get('password') == pass_in), None)
        
        if authenticated_user:
            # 1. Save to Session State
            st.session_state["user_data"] = authenticated_user
            st.session_state["logged_in"] = True  # Add this for your 'Gatekeeper'
            st.session_state["user_name"] = authenticated_user.get('name', 'User')
            st.session_state["user_email"] = email_in
            
            # 2. Set Cookie
            expiry_date = datetime.now() + timedelta(days=1)
            cookie_manager.set("insync_user", authenticated_user, expires_at=expiry_date)
            
            # 3. Redirect Immediately 
            # (Removing time.sleep ensures the redirect hits before the footer/JS loads)
            st.success(f"Verified: {authenticated_user.get('name')}. Redirecting...")
            st.switch_page("pages/2_dashboard.py")
            
    st.write("---")
    st.markdown("""
    <div style="text-align: center; color: #64748B; font-size: 14px; font-family: 'Inter', sans-serif;">
        Don't have an account yet? 
        <a href="signup" target="_self" style="color: #A78BFA; text-decoration: none; font-weight: 700;">
            Sign Up
        </a>
    </div>
""", unsafe_allow_html=True)

#Leave page popup
if "user_data" not in st.session_state:
    components.html(
        """
        <script>
        window.onbeforeunload = function() {
            return "Are you sure you want to leave?";
        };
        </script>
        """,
        height=0,
    )

# FOOTER SECTION 
st.markdown("""
    <div class="footer">
        <p>© 2026 InSync | Powered by BSc Computer Science (Systems Engineering) | Mauritius</p>
    </div>
""", unsafe_allow_html=True)