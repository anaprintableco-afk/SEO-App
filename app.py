import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# ==========================================
# 1. UI & Styling (Dark Theme Fix)
# ==========================================
st.set_page_config(page_title="AtlasRank | Etsy SEO", layout="centered")

st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        /* این خط باعث میشه تمام متن‌ها سفید و خوانا بشن */
        h1, h2, h3, p, span, label, div { color: #ffffff !important; }
        
        .login-box {
            background: rgba(255, 255, 255, 0.05);
            padding: 30px; border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
        }
        .stButton>button {
            width: 100%; border-radius: 8px;
            background: linear-gradient(90deg, #FF5A1F 0%, #FF8C00 100%);
            color: white !important; font-weight: bold; border: none; padding: 10px;
        }
        .result-box {
            background-color: #1c2128; padding: 20px; border-radius: 10px;
            border-left: 5px solid #FF5A1F; margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# ==========================================
# 2. Authentication Page
# ==========================================
def auth_screen():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h1 style='color: #FF5A1F !important;'>🚀 AtlasRank</h1>", unsafe_allow_html=True)
        st.write("Etsy SEO Intelligence")
        
        u = st.text_input("Email")
        p = st.text_input("Password", type="password")
        if st.button("Sign In / Enter Dashboard"):
            st.session_state['auth'] = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 3. Main Dashboard
# ==========================================
def main_dashboard():
    st.sidebar.markdown("<h2 style='color: #FF5A1F !important;'>AtlasRank</h2>", unsafe_allow_html=True)
    if st.sidebar.button("Logout"):
        st.session_state['auth'] = False
        st.rerun()

    st.markdown("<h1 style='text-align: center;'>🛠️ SEO Engine</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Upload an image and let Atlas AI write your listing.</p>", unsafe_allow_html=True)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🔑 API Key is missing! Add GEMINI_API_KEY in Render Environment Variables.")
        return
        
    genai.configure(api_key=api_key)

    up = st.file_uploader("Upload Product Photo", type=["jpg", "png", "jpeg"])
    
    if up:
        img = Image.open(up)
        st.image(img, width=350)
        
        if st.button("Analyze & Generate SEO"):
            with st.spinner("Atlas AI is crafting your listing..."):
                try:
                    # تغییر اصلی اینجاست: استفاده از پیشوند models/
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    
                    prompt = "You are an Etsy SEO expert. Analyze this image and provide: 1. Title (max 140 chars). 2. 13 Tags (comma separated). 3. Description."
                    response = model.generate_content([prompt, img])
                    
                    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                    st.markdown("### 📋 Your Listing Data")
                    st.write(response.text)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.balloons()
                    
                except Exception as e:
                    # سیستم پشتیبان در صورت بروز خطا
                    st.warning("🔄 Primary model busy. Trying backup model...")
                    try:
                        backup_model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
                        response = backup_model.generate_content([prompt, img])
                        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                        st.write(response.text)
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.balloons()
                    except Exception as e2:
                        st.error(f"❌ Final Error: {e2}")
                        st.info("Check your API key permissions in Google AI Studio.")

if not st.session_state['auth']:
    auth_screen()
else:
    main_dashboard()
