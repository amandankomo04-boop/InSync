import streamlit as st
import json
from pathlib import Path
import extra_streamlit_components as stx
import time
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="InSync", layout="wide", initial_sidebar_state="collapsed")

# 2. Path Handling
current_file = Path(__file__).resolve()
root_path = current_file.parent.parent.parent
data_path = root_path / "data" / "users.json"
logo_path = root_path / "assets" / "insync_logo.png"

# Initialize Cookie Manager
cookie_manager = stx.CookieManager()

# 3. CSS (Matching your Login Figma Precision)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #A78BFA 0%, #34D399 100%) !important; }
    .hero-container { color: white !important; padding-top: 80px; margin-left: 40px; }
    .hero-container h1 { font-size: 80px !important; font-weight: 900 !important; line-height: 0.9 !important; color: white !important; }
    
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
    .stTextInput div div input { background-color: #f8fafc !important; border-radius: 12px !important; padding: 12px !important; }
    
    /* Signup Card Styling */
    .signup-card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
    
    /* Buttons */
    button[kind="primary"] { background-color: #34D399 !important; border: none !important; color: white !important; border-radius: 12px !important; height: 3.5em !important; font-weight: 700 !important; }
    button[kind="secondary"] { border-radius: 12px !important; height: 3.5em !important; }
    
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

# 4. Layout
col1, col2 = st.columns([1.2, 1], gap="large")

with col1:
    st.markdown("""
        <div class="hero-container">
            <h1>Sync Your<br>Brand<br>Match With<br>Authenticity</h1>
            <p style='font-size: 24px; opacity: 0.9;'>Sign Up To Find Your Perfect<br>Aesthetic Match</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    if logo_path.exists():
        st.image(str(logo_path), width=360)
    
    st.write("---")
    
    with st.container():
        new_name = st.text_input("Full Name", placeholder="Amanda Nkomo")
        new_brand = st.text_input("Brand Name", placeholder="Beauty Inc.")
        new_email = st.text_input("Email Address", placeholder="amanda@beautyinc.mu")
        new_position = st.text_input("Position Title", placeholder="Marketing Manager")
        new_pass = st.text_input("Password", type="password", placeholder="••••••••")
        confirm_pass = st.text_input("Confirm Password", type="password", placeholder="••••••••")

        st.write(" ")
        
        if st.button("Create Account", use_container_width=True, type="primary"):
            if not new_name or not new_email or not new_pass:
                st.error("Fields cannot be empty.")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match.")
            else:
                # Load existing users
                users = []
                if data_path.exists():
                    with open(data_path, "r") as f:
                        try:
                            users = json.load(f)
                        except:
                            users = []
                
                if any(u['email'] == new_email for u in users):
                    st.error("This email is already registered.")
                else:
                    # Create user object
                    user_obj = {
                        "name": new_name,
                        "email": new_email,
                        "password": new_pass, # Note: In production, hash this!
                        "role": "Brand Manager" 
                    }
                    users.append(user_obj)
                    
                    # Save to JSON
                    data_path.parent.mkdir(exist_ok=True)
                    with open(data_path, "w") as f:
                        json.dump(users, f, indent=4)
                    
                    # 5. IMPLEMENT COOKIE MANAGER ON SIGNUP
                    # This allows immediate transition to Dashboard without re-login
                    st.session_state["user_data"] = user_obj
                    expiry = datetime.now() + timedelta(days=1)
                    cookie_manager.set("insync_user", user_obj, expires_at=expiry)
                    
                    st.success(f"Welcome, {new_name}!")
                    st.switch_page("pages/2_dashboard.py")

        #redirection to log in page
        st.markdown("""
            <div style="text-align: center; color: #64748B; font-size: 14px;">
            Already got an account? 
                <a href="../" target="_self" style="color: #A78BFA; text-decoration: none; font-weight: 700;">
                Log in
                </a>
            </div>
        """, unsafe_allow_html=True)

# FOOTER SECTION 
st.markdown("""
    <div class="footer">
        <p>© 2026 InSync | Powered by BSc Computer Science (Systems Engineering) | Mauritius</p>
    </div>
""", unsafe_allow_html=True)