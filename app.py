import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# ==========================================
# 1. UI & Styling (eRank Dark Theme)
# ==========================================
st.set_page_config(page_title="AtlasRank | Etsy SEO Engine", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        .login-box {
            background: rgba(255, 255, 255, 0.05);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            background: linear-gradient(90deg, #FF5A1F 0%, #FF8C00 100%);
            color: white; font-weight: bold; border: none; padding: 10px;
        }
        .result-box {
            background-color: #1c2128;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #FF5A1F;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Auth State
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# ==========================================
# 2. Authentication Pages
# ==========================================
def auth_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h1 style='color: #FF5A1F;'>AtlasRank</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            u = st.text_input("Email")
            p = st.text_input("Password", type="password")
            if st.button("Sign In"):
                if u and p:
                    st.session_state['auth'] = True
                    st.rerun()
        
        with tab2:
            st.text_input("Full Name")
            st.text_input("Shop Name (Optional)")
            st.text_input("Email Address")
            st.text_input("Create Password", type="password")
            if st.button("Create My Free Account"):
                st.success("Account created! Now go to Login tab.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 3. Main Dashboard (SaaS Panel)
# ==========================================
def main_dashboard():
    st.sidebar.markdown("<h2 style='color: #FF5A1F;'>AtlasRank</h2>", unsafe_allow_html=True)
    st.sidebar.info("Plan: Free Trial")
    if st.sidebar.button("Logout"):
        st.session_state['auth'] = False
        st.rerun()

    st.title("🚀 Etsy SEO Generator")
    st.write("Upload an image and let Atlas AI write your listing.")

    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    up = st.file_uploader("Upload Product Photo", type=["jpg", "png", "jpeg"])
    
    if up:
        img = Image.open(up)
        st.image(img, width=350)
        
        if st.button("Analyze & Generate SEO"):
            with st.spinner("Atlas AI is crafting your listing..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = """
                    You are an Etsy SEO expert. Analyze this image and provide:
                    1. Title: A high-converting title (max 140 chars).
                    2. Tags: 13 multi-word tags separated by commas.
                    3. Description: A professional product description.
                    Use clear headings.
                    """
                    response = model.generate_content([prompt, img])
                    output = response.text

                    st.markdown("### 📋 Your Listing Data")
                    
                    # نمایش خروجی در باکس‌های شیک
                    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                    st.write(output)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")

# Logic Flow
if not st.session_state['auth']:
    auth_screen()
else:
    main_dashboard()
