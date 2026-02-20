import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import os

# ==========================================
# 1. Page Config & Brand Style
# ==========================================
st.set_page_config(page_title="AtlasRank | Etsy SEO", layout="centered")

st.markdown("""
    <style>
        .stApp { background-color: #ffffff; }
        .stButton>button { width: 100%; border-radius: 8px; background-color: #FF5A1F; color: white; font-weight: bold; height: 3em; border: none; }
        .login-card { padding: 30px; border-radius: 15px; border: 1px solid #eee; background-color: #f9f9f9; text-align: center; }
        h1 { color: #002d72; font-family: 'Noto Sans Display', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Simple Auth Logic (SaaS Style)
# ==========================================
if 'auth_state' not in st.session_state:
    st.session_state['auth_state'] = False

def login_screen():
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.title("🚀 AtlasRank")
    st.write("Professional Etsy SEO Intelligence")
    
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        user = st.text_input("Email", placeholder="your@email.com")
        passw = st.text_input("Password", type="password")
        if st.button("Log In"):
            if user and passw: # اینجا فعلا هر یوزری را قبول می‌کند برای تست
                st.session_state['auth_state'] = True
                st.rerun()
    
    with tab2:
        st.write("Join the elite Etsy sellers.")
        st.text_input("Full Name")
        st.text_input("Work Email")
        st.button("Start Free Trial")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 3. Main SEO Engine (The App)
# ==========================================
def main_app():
    # Sidebar for logout and info
    st.sidebar.image("https://via.placeholder.com/150x50?text=AtlasRank", use_container_width=True)
    if st.sidebar.button("Logout"):
        st.session_state['auth_state'] = False
        st.rerun()
    
    st.title("🛠️ SEO Listing Generator")
    st.write("Upload an image to generate data-driven Etsy SEO.")

    # API Configuration
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("API Key missing in Render!")
        return
    genai.configure(api_key=api_key)

    uploaded_file = st.file_uploader("Choose product image...", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=300)
        
        if st.button("Generate Optimization"):
            with st.spinner("AI is analyzing (using Gemini 1.5 Flash)..."):
                try:
                    # استفاده از نام مدل بدون پیشوند برای سازگاری بیشتر
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = "Analyze this image and provide: 1. A catchy Etsy Title. 2. 13 Tags. 3. A short description."
                    
                    response = model.generate_content([prompt, image])
                    
                    st.success("Analysis Complete!")
                    st.markdown("### 📋 SEO Results")
                    st.write(response.text)
                    
                except Exception as e:
                    # راه حل جایگزین اگر باز هم 404 داد
                    st.error(f"Primary model error: {e}")
                    st.info("Trying legacy model connection...")
                    try:
                        legacy_model = genai.GenerativeModel('models/gemini-1.5-flash')
                        response = legacy_model.generate_content([prompt, image])
                        st.write(response.text)
                    except Exception as e2:
                        st.error(f"Final Error: {e2}")

# ==========================================
# 4. Execution Flow
# ==========================================
if not st.session_state['auth_state']:
    login_screen()
else:
    main_app()
