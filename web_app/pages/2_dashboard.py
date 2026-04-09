import streamlit as st
import json
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import extra_streamlit_components as stx
import time

# 1. Page Configuration
st.set_page_config(page_title="InSync", layout="wide", initial_sidebar_state="expanded")

# 2. Path Handling
current_file = Path(__file__).resolve()
root_path = current_file.parent.parent.parent
data_path = root_path / "data" / "users.json"
logo_path = root_path / "assets" / "insync_logo.png"

# 3. Authentication & Cookie Check
cookie_manager = stx.CookieManager()

if "user_data" not in st.session_state:
    all_cookies = cookie_manager.get_all()
    if all_cookies and "insync_user" in all_cookies:
        st.session_state["user_data"] = all_cookies["insync_user"]
    else:
        st.warning("Please log in to access the dashboard.")
        time.sleep(1)
        st.switch_page("login.py")
        st.stop()

user = st.session_state.get("user_data", {})
current_email = st.session_state["user_email"]

# Updated Helper Function with dynamic height
def render_donut(score, custom_height=180, custom_font=35):
    display_score = int(float(score))
    
    fig = go.Figure(go.Pie(
        values=[display_score, 100 - display_score],
        hole=.75,
        marker_colors=['#6366F1', 'rgba(0,0,0,0)'], 
        textinfo='none',
        hoverinfo='none'
    ))
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=custom_height, # Use the parameter here
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[{
            'text': f"{display_score}%",
            'x': 0.5, 'y': 0.5,
            'font_size': custom_font, # Use the parameter here
            'font_family': 'sans-serif',
            'font_color': '#6366F1',
            'font_weight': 'bold',
            'showarrow': False
        }]
    )
    return fig

# 4. CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #A7F3D0 0%, #A5B4FC 100%);
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
            
    .main-card {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 40px;
        border-radius: 24px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin: auto;
        max-width: 600px;
    }
    .history-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #A78BFA;
    }
    .title-text {
        color: #1E293B;
        font-weight: 800;
        font-size: 28px;
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

# --- 5. Data Logic (FETCH FROM JSON) ---
campaign_history = []
user_name = "User"
if data_path.exists():
    with open(data_path, "r") as f:
        users_db = json.load(f)
    # Find the logged-in user in the JSON database
    current_user_data = next((u for u in users_db if u['email'] == current_email), None)
    if current_user_data:
        campaign_history = current_user_data.get("campaign_history", [])
        user_name = current_user_data.get("name", "User")
        st.session_state["user_name"] = user_name
        st.session_state["user_role"] = current_user_data.get("role", "Brand Manager")


# 8. UI Rendering
if not campaign_history:
    # --- 8A. THE EMPTY STATE ---
    st.markdown("""
        <div style="background-color: white; padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-top: 50px; margin-bottom: 20px;">
            <h3 style="color: #1E293B; margin-bottom: 10px;">Welcome to InSync!</h3>
            <p style="color: #64748B; font-size: 16px;">You currently don't have any previous matches available. Make your first match now!</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Navigate to matching page to start", type="primary", use_container_width=True):
            st.switch_page("pages/3_matching.py")

else:
    col_left, col_right = st.columns([1, 1.2], gap="large")

    with col_left:
        st.markdown("<h2 style='color: white; margin-bottom: 20px;'>Previous Matches</h2>", unsafe_allow_html=True)
        
        for campaign in reversed(campaign_history):
            name = str(campaign.get('campaign_name', 'Unnamed'))
            aesthetic = str(campaign.get('aesthetic', 'Minimalist'))
            inf = str(campaign.get('influencer') or campaign.get('top_influencer', 'TBD'))
            score_val = float(campaign.get('score') or campaign.get('match_score', 0))
            dash = (score_val / 100) * 251.2

            # Robust HTML Card with SVG Donut
            card_html = f"""
            <div style="background: white; padding: 20px; border-radius: 25px; margin-bottom: 25px; 
                        box-shadow: 0 10px 20px rgba(0,0,0,0.1); border-left: 10px solid #6366F1;
                        display: flex; align-items: center; justify-content: space-between;">
                <div style="flex: 1.5;">
                    <h3 style="margin: 0; color: #1E293B; font-size: 20px;">{name}</h3>
                    <p style="margin: 0; color: #64748B; font-size: 13px;">{aesthetic}</p>
                    <p style="margin: 15px 0 0 0; font-size: 13px; color: #1E293B;">Influencer: <strong>{inf}</strong></p>
                </div>
                <div style="flex: 1; text-align: right;">
                    <svg width="80" height="80" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="40" stroke="#F1F5F9" stroke-width="12" fill="none" />
                        <circle cx="50" cy="50" r="40" stroke="#6366F1" stroke-width="12" fill="none" 
                                stroke-dasharray="{dash} 251.2" stroke-linecap="round" transform="rotate(-90 50 50)" />
                        <text x="50" y="57" text-anchor="middle" font-family="sans-serif" font-size="22" font-weight="bold" fill="#6366F1">{int(score_val)}%</text>
                    </svg>
                </div>
            </div>
            """
            st.write(card_html, unsafe_allow_html=True)

    with col_right:
        st.markdown("<h1 style='color: white; text-align: center;'>Latest Match</h1>", unsafe_allow_html=True)
        if campaign_history:
            latest = campaign_history[-1]
            l_score = latest.get('score') or latest.get('match_score', 0)
            
            st.markdown(f"<h1 style='text-align: center; color: #10B981;'>{int(l_score)}% <span style='color: white;'>Match Score</span></h1>", unsafe_allow_html=True)
            
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"<h2 style='color: white;'>{latest['campaign_name']}</h2>", unsafe_allow_html=True)
                # 1. First, find the current user in your JSON database
                # (Assuming you've already loaded 'users' from users.json)
                current_user = None
                if data_path.exists():
                    with open(data_path, "r") as f:
                        users = json.load(f)

                    # 2. Safety Check: Is 'users' a list of dicts?
                    if isinstance(users, list):
                        for u in users:
                            if u['email'] == st.session_state.get("user_email"):
                                current_user = u
                                break

                # 2. Strategy: Priority to Session State, Fallback to JSON History
                campaign_data = None

                # Priority: Check if a match was JUST run in this session
                if "current_campaign" in st.session_state:
                    campaign_data = st.session_state["current_campaign"]
                # Fallback: Get the last saved campaign from users.json
                elif current_user and "campaign_history" in current_user and current_user["campaign_history"]:
                    campaign_data = current_user["campaign_history"][-1] # Get the most recent entry

                # 3. Render the Chart if data exists
                if campaign_data:
                    # Use .get() to find 'leaderboard' (JSON key) or 'alternatives' (Session key)
                    leaderboard = campaign_data.get("leaderboard") or campaign_data.get("alternatives")

                if leaderboard:
                    # 1. Create the DataFrame
                    chart_df = pd.DataFrame(leaderboard)
                    
                    # 2. THE COLUMN NORMALIZER: 
                    # This maps 'account_id' or 'Name' to a single standard 'ID' column
                    # And 'match_score' or 'Match Score' to a standard 'Score' column
                    
                    # Map for X-Axis (The Names/IDs)
                    if 'Name' in chart_df.columns:
                        chart_df.rename(columns={'Name': 'ID'}, inplace=True)
                    elif 'account_id' in chart_df.columns:
                        chart_df.rename(columns={'account_id': 'ID'}, inplace=True)
                        
                    # Map for Y-Axis (The Scores)
                    if 'Match Score' in chart_df.columns:
                        chart_df.rename(columns={'Match Score': 'Score'}, inplace=True)
                    elif 'match_score' in chart_df.columns:
                        chart_df.rename(columns={'match_score': 'Score'}, inplace=True)

                    # 3. Final Safety Check: Do we have an 'ID' column now?
                    if 'ID' in chart_df.columns:
                        # Convert to string to prevent gaps in the chart
                        chart_df['ID'] = chart_df['ID'].astype(str).str.replace(".0", "", regex=False)
                    # 3. Render the Bar Chart
                    st.write(f"##### 📊 Top Candidates: {campaign['campaign_name']}")
                    st.bar_chart(
                        data=chart_df, 
                        x='ID',      # This must match the name we created: 'ID'
                        y='Score',   # This must match the name we created: 'Score'
                        color="#6366F1", 
                        use_container_width=True,
                        height=230
                    )
                    st.caption("Showing top 5 suggested influencers for this campaign.")
                else:
                    st.info("No active campaign data found. Run a match to see the performance chart.")

                st.markdown(f"<p style='color: white;'>Top Candidate: <strong>{latest.get('influencer') or latest.get('top_influencer')}</strong></p>", unsafe_allow_html=True)
            with c2:
                st.plotly_chart(render_donut(l_score, 180, 35), use_container_width=True, config={'displayModeBar': False})
            
            if campaign_history:
                latest = campaign_history[-1]
                # 1. PREPARE THE DATA FOR DOWNLOAD
                if "current_campaign" in st.session_state:
                    report_df = pd.DataFrame(st.session_state["current_campaign"]["alternatives"])
                else:
                    # Fallback: Create a simple one-row dataframe from the JSON history
                    report_df = pd.DataFrame([latest])

                csv_data = report_df.to_csv(index=False).encode('utf-8')

                # 2. THE BUTTONS
                st.markdown("<br>", unsafe_allow_html=True)

                # Download .csv
                st.download_button(
                    label=f"📥 Download {latest['campaign_name']} Report (.csv)",
                    data=csv_data,
                    file_name=f"{latest['campaign_name']}_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            if st.button("🚀 Start New Campaign Match", use_container_width=True, type="primary"):
                st.switch_page("pages/3_matching.py")
                
# FOOTER SECTION 
st.markdown("""
    <div class="footer">
        <p>© 2026 InSync | Powered by BSc Computer Science (Systems Engineering) | Mauritius</p>
    </div>
""", unsafe_allow_html=True)