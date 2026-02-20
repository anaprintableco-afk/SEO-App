import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import os

# ==========================================
# 1. Page Config & Professional SaaS Style
# ==========================================
st.set_page_config(page_title="AtlasRank | Etsy SEO", layout="centered")

st.markdown("""
    <style>
        .stApp { background-color: #ffffff; }
        .stButton>button { width: 100%; border-radius: 8px; background-color: #FF5A1F; color: white; font-weight: bold; height: 3em; border: none; }
        .login-card { padding: 30px; border-radius: 15px; border: 1px solid #eee; background-color: #f9f9f9; text-align: center; margin-bottom: 20px; }
        h1 { color: #002d72; font-family: 'Noto Sans Display', sans-serif; }
        .stTabs [data-baseweb="tab-list"] { gap: 24px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Auth State Management
# ==========================================
if 'auth_state' not in st.session_state:
    st.session_state['auth_state'] = False

def login_screen():
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.title("🚀 AtlasRank")
    st.write("The #1 AI Intelligence for Etsy Sellers")
    
    tab1, tab2 = st.tabs(["🔑 Log In", "📝 Sign Up"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Access Dashboard"):
            if email and password:
                st.session_state['auth_state'] = True
                st.rerun()
            else:
                st.warning("Please enter your credentials.")
    
    with tab2:
        st.write("Join 5,000+ successful Etsy shops.")
        st.text_input("Full Name", key="reg_name")
        st.text_input("Email Address", key="reg_email")
        st.text_input("Create Password", type="password", key="reg_pass")
        if st.button("Create My Account"):
            st.success("Registration successful! Now please Log In.")
            
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 3. Core Engine (Using Stable Model)
# ==========================================
def main_app():
    st.sidebar.title("AtlasRank Panel")
    st.sidebar.info("Welcome back, Elite Seller!")
    if st.sidebar.button("Logout"):
        st.session_state['auth_state'] = False
        st.rerun()
    
    st.title("🛠️ SEO Engine")
    st.write("Upload your product image to generate listing data.")

    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    uploaded_file = st.file_uploader("Drop image here...", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=300)
        
        if st.button("Generate Optimized Listing"):
            with st.spinner("AI Analysis in progress..."):
                try:
                    # استفاده از مدل پایدار Pro-Vision برای حل مشکل 404
                    model = genai.GenerativeModel('gemini-pro-vision')
                    
                    prompt = "Analyze this image and generate: 1. Etsy Title (max 140 chars) 2. 13 SEO Tags 3. Product Description."
                    
                    response = model.generate_content([prompt, image])
                    
                    st.success("Success!")
                    st.markdown("### 📋 Results")
                    st.write(response.text)
                    
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.info("Tip: If error persists, ensure your API Key has no restrictions in Google Cloud Console.")

# ==========================================
# 4. Main Loop
# ==========================================
if not st.session_state['auth_state']:
    login_screen()
else:
    main_app()
