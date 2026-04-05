import streamlit as st
import pandas as pd
import io
import json
import plotly.graph_objects as go
from pathlib import Path
import time

# 1. Page Configuration
st.set_page_config(page_title="InSync", layout="wide", initial_sidebar_state="collapsed")

# 2. Path Handling
current_file = Path(__file__).resolve()
root_path = current_file.parent.parent.parent
logo_path = root_path / "assets" / "insync_logo.png"
data_path = root_path / "data" / "users.json"

# --- 2.5 AUTHENTICATION GATEKEEPER ---
if "user_email" not in st.session_state:
    st.error("⚠️ Security Access Denied: User session not found.")
    st.info("Redirecting to Login Page...")
    time.sleep(2) # Give the user a moment to read the message
    st.switch_page("login.py")
    st.stop() # Prevents the rest of the code from running

current_email = st.session_state["user_email"]

# 3. CSS for Figma Cards
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #A78BFA 0%, #34D399 100%) !important; }
            
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
            
    [data-testid="stPopover"] {
        text-align: right;
        display: flex;
        justify-content: flex-end;
    }
    button[kind="secondary"] {
        background-color: rgba(255, 255, 255, 0.2);
        color: #0F172A;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 10px;
    }
    
    .white-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        color: #1E293B;
    }
    .alt-item {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #F1F5F9;
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

# 4. Helper: Donut Chart
def render_donut(score):
    # Ensure score is an integer for display
    display_score = int(float(score))
    
    fig = go.Figure(go.Pie(
        values=[display_score, 100 - display_score],
        hole=.75, # Slightly larger hole for better text fit
        marker_colors=['#6366F1', 'rgba(0,0,0,0)'], #Blue colour
        textinfo='none',
        hoverinfo='none'
    ))
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=220, # Fixed height for consistency
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        # THE FIX: Centered Annotation
        annotations=[{
            'text': f"{display_score}%",
            'x': 0.5, 'y': 0.5,
            'font_size': 45,
            'font_family': 'sans-serif',
            'font_color': '#F8FAFC',
            'font_weight': 'bold',
            'showarrow': False
        }]
    )
    return fig

#5. Header
def render_user_menu():
    # 1. Fetch User Data from Session State
    # Ensure these were set during your login.py process
    user_name = st.session_state.get("user_name", "Amanda Nkomo")
    user_role = st.session_state.get("user_role", "Brand Manager")
    
    # 2. Layout for the Header
    col_logo, col_menu = st.columns([1, 1])
    
    with col_logo:
        if logo_path.exists():
            st.image(str(logo_path), width=360)

    with col_menu:
        # This creates the "Clickable" profile area in the top right
        with st.popover(f"👤 {user_name}", use_container_width=True):
            st.markdown(f"**{user_name}**")
            st.caption(f"Role: {user_role}")
            st.divider()
            
            # Option 1: Switch Account
            if st.button("🔄 Switch Account", use_container_width=True):
                # Clear session but keep the app running
                st.session_state.clear()
                st.switch_page("login.py")
            
            # Option 2: Log Out
            if st.button("🚪 Log Out", use_container_width=True):
                st.session_state.clear()
                st.switch_page("login.py")

render_user_menu()

# Data Standardization
results_df = pd.DataFrame()
if "current_campaign" in st.session_state:
    camp = st.session_state["current_campaign"]
    results_df = pd.DataFrame(camp["alternatives"])
    results_df.rename(columns={
        "account_id": "Name", "match_score": "Match Score",
        "follower_count": "Followers", "engagement_rate": "Engagement"
    }, inplace=True)
    # Convert to integers to remove the .0 decimal
    results_df["Match Score"] = pd.to_numeric(results_df["Match Score"])
    results_df["Name"] = results_df["Name"].astype(str).str.replace(".0", "", regex=False)
    results_df["Followers"] = pd.to_numeric(results_df["Followers"], errors='coerce').fillna(0).astype(int)


# 6. UI Rendering
if results_df.empty:
    st.warning("No active results found.")
    if st.button("Back to Dashboard"): st.switch_page("pages/2_dashboard.py")
else:
    # --- TOP SECTION: FIGMA LAYOUT ---
    col_main, col_side = st.columns([1.5, 1], gap="large")

    with col_main:
        with st.container():
            c1, c2 = st.columns([1, 1.5])
            with c1:
                st.plotly_chart(render_donut(results_df.iloc[0]['Match Score']), use_container_width=True)
                st.markdown("<p style='text-align:center; font-weight:bold;'>Match Score</p>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"### {camp['name']}")
                st.caption(f"{camp['aesthetic']} Aesthetic | {camp['niche']} Niche")
                st.write(f"Your best matched influencer is Influencer {results_df.iloc[0]['Name']}")

            st.write("---")
            st.subheader("Match Score Distribution")
            st.bar_chart(results_df.set_index('Name')['Match Score'], color="#6366F1")
            st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        # Top Influencer Card
        st.markdown(f"""
            <div class="white-card" style="border-left: 10px solid #6366F1; margin-bottom:20px;">
                <p style="color: #64748B; margin: 0;">Top Candidate:</p>
                <h3 style="margin: 0;">{results_df.iloc[0]['Name']}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Initialize the selection if not set
        if "selected_idx" not in st.session_state:
            st.session_state.selected_idx = 0

        # Get the currently selected influencer data
        current_choice = results_df.iloc[st.session_state.selected_idx]

        # --- Top Influencer Card (Now dynamic based on selection) ---
        st.markdown(f"""
            <div class="white-card" style="border-left: 10px solid #6366F1; margin-bottom:20px;">
                <p style="color: #64748B; margin: 0; font-size: 14px;">Current Selection:</p>
                <h3 style="margin: 0;">{current_choice['Name']}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # --- Alternatives List with Selection Buttons ---
        with st.container():
            st.subheader("Select Alternative")
            
            # We loop through the top 5 matches
            for idx, row in results_df.head(5).iterrows():
                col_name, col_btn = st.columns([3, 1])
                with col_name:
                    # Highlight if currently selected
                    label = f"**{row['Name']}**" if idx == st.session_state.selected_idx else row['Name']
                    st.markdown(f"<div style='padding-top:5px;'>{label} ({row['Match Score']}%)</div>", unsafe_allow_html=True)
                with col_btn:
                    if st.button("Select", key=f"sel_{idx}", use_container_width=True):
                        st.session_state.selected_idx = idx
                        st.rerun() # Refresh to update the Donut and Confirmation data

            st.write("<br>", unsafe_allow_html=True)
            
            # --- Confirm Button (Saves the SPECIFIC selection) ---
            if st.button("✅ Confirm Influencer for Campaign", use_container_width=True, type="primary"):
                current_email = st.session_state.get("user_email")
                
                if not current_email:
                    st.error("❌ Logic Error: User Email not found in session. Please log in again.")
                elif data_path.exists():
                    with open(data_path, "r") as f:
                        users = json.load(f)
                    
                    found_user = False
                    for user in users:
                        if user['email'] == current_email:
                            if "campaign_history" not in user:
                                user["campaign_history"] = []
                            
                            # Create the entry
                            user["campaign_history"].append({
                                "campaign_name": camp['name'],
                                "niche": camp['niche'],
                            "aesthetic": camp['aesthetic'],
                                "influencer": current_choice['Name'],
                                "score": int(current_choice['Match Score']),
                                "date": "2026-04-03",
                                "status": "Confirmed",
                                "leaderboard": results_df.head(5).to_dict('records')
                            })
                            found_user = True
                            break
                    
                    if found_user:
                        with open(data_path, "w") as f:
                            json.dump(users, f, indent=4)
                        st.success(f"✔️ Campaign '{camp['name']}' saved to {current_email}!")
                    else:
                        st.error(f"❌ User '{current_email}' not found in users.json database.")
                else:
                    st.error(f"❌ File Not Found: {data_path}")

            if st.button("🔄 Start New Campaign Match", use_container_width=True):
                st.switch_page("pages/3_matching.py")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- BOTTOM SECTION: DETAILED TABLE ---
    st.write("---")
    st.subheader("Detailed Creator Breakdown")
    st.dataframe(results_df.style.background_gradient(subset=['Match Score'], cmap='BuGn'), use_container_width=True, hide_index=True)

# Footer
st.markdown("<div class='footer'><p>© 2026 InSync | Systems Engineering | Mauritius</p></div>", unsafe_allow_html=True)