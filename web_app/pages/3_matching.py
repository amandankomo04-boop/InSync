import streamlit as st
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import time
import sys
import json
import torch # or tensorflow
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import joblib
import torch.nn.functional as F
import pickle

def clamp(n, minn, maxn):
    return max(minn, min(n, maxn))

# Initialize session state keys if they don't exist
if 'uploaded_image' not in st.session_state:
    st.session_state['uploaded_image'] = None

# 1. Page Configuration
st.set_page_config(page_title="InSync", layout="wide", initial_sidebar_state="expanded")

# 2. Path Handling
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))
logo_path = root_path / "assets" / "insync_logo.png"
dna_path = root_path / "models" / "system_dna.pkl"
csv_path = root_path / "data" / "metadata" / "Instagram_Analytics_Enriched.csv"
data_path = root_path / "data" / "users.json"
upload_dir = root_path / "data" / "images" / "uploads"
upload_dir.mkdir(parents=True, exist_ok=True)

import pickle
import torch

from src.utils import calculate_cosine_similarity

# 1. Use the path you defined
dna_path = root_path / "models" / "system_dna.pkl"

if dna_path.exists():
    try:
        # We use standard 'rb' (read-binary) mode as seen in trainer scripts
        with open(dna_path, 'rb') as f:
            # This bypasses torch.load's magic number check
            raw_data = pickle.load(f)
            
        if isinstance(raw_data, dict):
            # Extract the centroids we found during your inspection
            niche_centroids = raw_data.get('niche_centroids', {})
            aesthetic_centroids = raw_data.get('aesthetic_centroids', {})
            
            # 2. Convert centroids to PyTorch Tensors 
            # (Because pickle loads them as standard lists/numpy arrays)
            for k, v in niche_centroids.items():
                niche_centroids[k] = torch.tensor(v).float()
            for k, v in aesthetic_centroids.items():
                aesthetic_centroids[k] = torch.tensor(v).float()
                
            st.success("✅ DNA Centroids successfully mapped to Tensors.")
        else:
            st.error("❌ DNA file is not a dictionary. Check trainer export.")
            
    except Exception as e:
        st.error(f"❌ Pickle Load Failed: {e}")
else:
    st.error(f"❌ File not found at {dna_path}")

# 1. Initialize the architecture (Must match what the trainer used!)
# If they used ResNet18, use models.resnet18(). If ResNet50, use resnet50().
encoder_model = models.resnet18(weights=None) 

# 2. Adjust the final layer to match your embedding size (usually 512 or 1024)
# This removes the 'classification' head so we get the 'Visual DNA' instead
encoder_model.fc = torch.nn.Identity()

# 3. Load the weights if they are in a separate file
# weights_path = root_path / "models" / "encoder_weights.pth"
# if weights_path.exists():
#     encoder_model.load_state_dict(torch.load(str(weights_path), map_location='cpu'))

encoder_model.eval()
model = encoder_model # This connects the 'engine' to your 'user_embedding' line



# --- 2.5 AUTHENTICATION GATEKEEPER ---
if "user_email" not in st.session_state:
    st.error("⚠️ Security Access Denied: User session not found.")
    st.info("Redirecting to Login Page...")
    time.sleep(2) # Give the user a moment to read the message
    st.switch_page("login.py")
    st.stop() # Prevents the rest of the code from running

current_email = st.session_state["user_email"]

# 3. Custom CSS
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
    
    .stTextInput div div input, .stSelectbox div div {
        background-color: #F1F5F9 !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
    }
    .user-profile { text-align: right; color: white; padding: 10px; }
    .upload-container {
        border: 2px dashed #A78BFA;
        border-radius: 20px;
        padding: 40px;
        background: #F8FAFC;
        text-align: center;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #A78BFA 0%, #34D399 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 15px !important;
        height: 3.5em !important;
        border: none !important;
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

# 4. Helper Function: Load Trained DNA
@st.cache_resource
def load_dna():
    if dna_path.exists():
        try:
            with open(dna_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            st.error(f"❌ Error unpickling DNA: {e}")
            return None
    else:
        # This will show you exactly where the app is looking for the file
        st.error(f"❌ DNA Model NOT found at: {dna_path.absolute()}")
        return None

# .csv file
@st.cache_data
def load_influencer_data():
    if csv_path.exists():
        try:
            return pd.read_csv(csv_path)
        except Exception as e:
            st.error(f"❌ Error reading CSV: {e}")
            return None
    else:
        st.error(f"❌ CSV File NOT found at: {csv_path.absolute()}")
        return None

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

# 6. Main Card Content
st.markdown('<div class="main-card">', unsafe_allow_html=True)
col_left, col_right = st.columns([1.1, 1], gap="large")

with col_left:
    st.write("### Campaign Details")
    campaign_name = st.text_input("Campaign Name", placeholder="e.g. Autumn Campaign '26")
    niche_list = ["Travel", "Fashion", "Tech", "Beauty", "Fitness", "Food", "Photography", "Lifestyle", "Music"]
    selected_niche = st.selectbox("Niche", niche_list)
    aesthetic_list = ["Luxury", "Minimalist", "Boho", "Streetwear", "Corporate"]
    selected_aesthetic = st.selectbox("Aesthetic", aesthetic_list)
    type_list = ["viral", "high", "medium", "low"]
    influencer_type = st.selectbox("Influencer Type", type_list)

with col_right:
    st.write("### Brand Inspiration")
    # 1. CSS to Center the internal Streamlit Browse button and text
    st.markdown("""
        <style>
        /* Center the entire uploader content */
        div[data-testid="stFileUploader"] section {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            background-color: #F8FAFC !important;
            border: 2px dashed #A78BFA !important;
            border-radius: 20px !important;
            padding: 40px !important;
            text-align: center !important;
        }

        /* Target the 'Browse files' button specifically */
        div[data-testid="stFileUploader"] section button {
            background: linear-gradient(90deg, #A78BFA 0%, #34D399 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 24px !important;
            font-weight: bold !important;
            margin-top: 10px !important;
            cursor: pointer !important;
        }
        
        /* Center the "Drag and drop" text */
        div[data-testid="stFileUploader"] section div {
            text-align: center !important;
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. The Uploader
    uploaded_files = st.file_uploader(
        "Upload images", 
        type=["png", "jpg", "jpeg", "jfif"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    # 3. File Processing Logic (Saves to /data/images/uploads)
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} Images received.")
        upload_dir = root_path / "data" / "images" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        for uploaded_file in uploaded_files:
            file_path = upload_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
    else:
        # Display the visual guide if nothing is uploaded yet
        st.info("💡 Click 'Browse files' above or drag images onto the box to begin.")

    
    # Process the user's reference image
    preprocess = transforms.Compose([
        transforms.Resize(256),                  # Resize smaller side to 256
        transforms.CenterCrop(224),              # Crop the center to 224x224
        transforms.ToTensor(),                   # Convert image to a Tensor (0 to 1)
        transforms.Normalize(                    # Standard ImageNet normalization
            mean=[0.485, 0.456, 0.406], 
            std=[0.229, 0.224, 0.225]
        )
    ])

    # 1. Only try to process images if the user has actually uploaded something
    if uploaded_files:
        uploaded_file = uploaded_files[0]
        
        
        # 2. Process for the UI/AI
        img = Image.open(uploaded_file).convert('RGB')
        
        # We define the tensor here so it's ready for the button click later
        user_tensor = preprocess(img).unsqueeze(0)
        
        # 3. Optional: Save to session state ONLY AFTER it's uploaded
        st.session_state['uploaded_image'] = uploaded_file

        with torch.no_grad():
            user_embedding = model(user_tensor) 

            # 2. Find the Centroid for the user's SELECTED Niche/Aesthetic
            target_niche_vec = niche_centroids.get(selected_niche)
            target_aesthetic_vec = aesthetic_centroids.get(selected_aesthetic)

            # 3. Calculate Cosine Similarity (How close is the photo to the 'Perfect' version?)
            if target_niche_vec is not None:
                # We compare the user's vector to the 'Luxury' centroid vector
                ai_niche_conf = float(F.cosine_similarity(user_embedding, target_niche_vec))
            else:
                ai_niche_conf = 0.5 # Fallback

            if target_aesthetic_vec is not None:
                ai_aesthetic_conf = float(F.cosine_similarity(user_embedding, target_aesthetic_vec))
            else:
                ai_aesthetic_conf = 0.5
    else:
        # Handle the case where no image is uploaded
        st.error("Please upload a reference image to use the AI matching features.")

    

# 7. Run Button Logic
if st.button("Run Matching Algorithm", use_container_width=True):
    # Check for empty campaign name first
    if not campaign_name:
        st.error("⚠️ Please enter a Campaign Name before running the algorithm.")
    else:
        st.write("🔍 Step 1: Loading DNA and Influencer Database...")
        knowledge = load_dna()
        df = load_influencer_data()
        
        if knowledge is not None and df is not None:
            st.write("✅ Step 2: Files Loaded successfully.")
            n_key = selected_niche.lower()
            a_key = selected_aesthetic.lower()
            
            n_centroids = knowledge.get('niche_centroids', {})
            a_centroids = knowledge.get('aesthetic_centroids', {})

            target_n_vec = n_centroids.get(n_key)
            target_a_vec = a_centroids.get(a_key)

            if target_n_vec is not None and target_a_vec is not None:
                st.write(f"🎯 Step 3: DNA found for {n_key}. Filtering creators...")
                
                # Filter CSV based on user selection
                filtered_df = df[
                    (df['content_category'].str.lower() == n_key) & 
                    (df['performance_bucket_label'] == influencer_type)
                ].copy()

                if not filtered_df.empty:
                    st.write(f"📈 Step 4: Found {len(filtered_df)} candidates. Processing scores...")
                    
                    if uploaded_file is not None:
                        # 1. Load and Clean the image
                        img = Image.open(uploaded_file).convert('RGB')
                        
                        # 2. Transform the image into a Tensor (This clears the 'user_tensor' error)
                        # The .unsqueeze(0) adds a 'batch' dimension because models expect a list of images
                        user_tensor = preprocess(img).unsqueeze(0)

                    # Assuming your model outputs a combined vector or you have two models
                        with torch.no_grad():
                            outputs = model(user_tensor)
                            probs = torch.nn.functional.softmax(outputs, dim=1)
                            
                            # AI checks: "How much does this image look like the chosen Niche?"
                            niche_index = niche_centroids.get(selected_niche, 0)
                            ai_niche_conf = float(probs[0][niche_index])
                            
                            # AI checks: "How much does this image look like the chosen Aesthetic?"
                            aesthetic_index = aesthetic_centroids.get(selected_aesthetic, 0)
                            ai_aesthetic_conf = float(probs[0][aesthetic_index])


                    def calculate_match_score(row, target_niche, target_aesthetic, ai_niche_conf, ai_aesthetic_conf):
                        score = 0
                        
                        # --- 1. NICHE MATCH (30 pts) ---
                        if str(row.get('content_category', '')).strip().lower() == target_niche.strip().lower():
                            score += (30 * ai_niche_conf)
                            
                        # --- 2. AESTHETIC MATCH (30 pts) ---
                        if str(row.get('assigned_aesthetic', '')).strip().lower() == target_aesthetic.strip().lower():
                            score += (30 * ai_aesthetic_conf)
                            
                        # --- 3. PERFORMANCE METRICS (15 pts total) ---
                        eng_val = float(row.get('engagement_rate', 0))
                        score += (min(eng_val, 1000) * 1000) / 7.5 
                        
                        bucket = str(row.get('performance_bucket_label', '')).lower()
                        bucket_scores = {'viral': 7.5, 'high': 5.0, 'medium': 2.5, 'low': 1.0}
                        score += bucket_scores.get(bucket, 0) 
                        
                        # --- 4. VISUAL SIMILARITY / STYLE ALIGNMENT (25 pts) ---
                        score += ((ai_niche_conf + ai_aesthetic_conf) / 2) * 25

                        boosted = np.sqrt(score) * 10
                        return round(boosted)

                    # Apply the expert logic
                    filtered_df['match_score'] = filtered_df.apply(
                    lambda x: calculate_match_score(
                        x, 
                        selected_niche, 
                        selected_aesthetic, 
                        ai_niche_conf,      
                        ai_aesthetic_conf   
                    ), 
                    axis=1
                )

                    top_matches = filtered_df.sort_values(by=['match_score', 'account_id'], ascending=[False, True]).head(5)
                    top_influencer = top_matches.iloc[0]
                    leaderboard_data = top_matches[['account_id', 'match_score', 'follower_count', 'engagement_rate']].to_dict('records')

                    # 1. SAVE TO SESSION STATE
                    st.session_state["current_campaign"] = {
                        "name": campaign_name,
                        "niche": selected_niche,
                        "aesthetic": selected_aesthetic,
                        "type": influencer_type,
                        "score": top_influencer['match_score'],
                        "top_influencer": str(top_influencer['account_id']),
                        "alternatives": leaderboard_data
                    }

                    # 3. FILE SYSTEM STORAGE (Images)
                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            file_path = upload_dir / uploaded_file.name
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                    
                    # 4. REDIRECT (Outside the image loop so it always triggers)
                    st.write("🚀 Step 6: Analysis Complete. Redirecting...")
                    time.sleep(3)
                    st.switch_page("pages/4_results.py")
                else:
                    st.error(f"❌ No {influencer_type} influencers found in the {selected_niche} niche.")
            else:
                st.error(f"❌ DNA keys missing. Available: {list(n_centroids.keys())}")
        else:
            st.error("❌ Critical Failure: Could not load DNA or CSV. Check file paths!")

    
# FOOTER SECTION 
st.markdown("""
    <div class="footer">
        <p>© 2026 InSync | Powered by BSc Computer Science (Systems Engineering) | Mauritius</p>
    </div>
""", unsafe_allow_html=True)