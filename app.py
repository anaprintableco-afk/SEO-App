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
    </style>
""", unsafe_allow_html=True)

if 'auth_state' not in st.session_state:
    st.session_state['auth_state'] = False

def login_screen():
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.title("🚀 AtlasRank")
    st.write("Professional Etsy SEO Intelligence")
    tab1, tab2 = st.tabs(["🔑 Log In", "📝 Sign Up"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Access Dashboard"):
            if email and password:
                st.session_state['auth_state'] = True
                st.rerun()
    with tab2:
        st.write("Join the elite Etsy sellers.")
        st.text_input("Full Name")
        st.button("Start Free Trial")
    st.markdown("</div>", unsafe_allow_html=True)

def main_app():
    st.sidebar.title("AtlasRank Panel")
    if st.sidebar.button("Logout"):
        st.session_state['auth_state'] = False
        st.rerun()
    
    st.title("🛠️ SEO Engine")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("API Key is missing in Render Settings!")
        return
        
    genai.configure(api_key=api_key)

    uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=300)
        
        if st.button("Generate Optimized Listing"):
            with st.spinner("Atlas AI is analyzing..."):
                try:
                    # استفاده از مدل 1.5 فلاش که جایگزین مدل‌های قدیمی شده
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = "Acting as an Etsy SEO expert, analyze this image and provide: 1. A Title (max 140 chars) 2. 13 Tags separated by commas 3. A professional description."
                    
                    # متد جدید تولید محتوا
                    response = model.generate_content([prompt, image])
                    
                    st.success("Generation Successful!")
                    st.markdown("### 📋 SEO Data")
                    st.write(response.text)
                    
                except Exception as e:
                    st.error(f"❌ API Error: {e}")

if not st.session_state['auth_state']:
    login_screen()
else:
    main_app()
