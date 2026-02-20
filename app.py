import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# ==========================================
# 1. UI & Styling (Dark Theme)
# ==========================================
st.set_page_config(page_title="AtlasRank | Etsy SEO", layout="centered")

st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        h1, h2, h3, p, span, label, div { color: #ffffff !important; }
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

if 'auth' not in st.session_state: st.session_state['auth'] = False

# ==========================================
# 2. Authentication
# ==========================================
if not st.session_state['auth']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #FF5A1F !important;'>🚀 AtlasRank</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Next-Gen Etsy SEO Intelligence</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Enter Dashboard"):
            st.session_state['auth'] = True
            st.rerun()
else:
    # ==========================================
    # 3. Main Dashboard (Using Gemini 2.5)
    # ==========================================
    st.sidebar.markdown("<h2 style='color: #FF5A1F !important;'>AtlasRank</h2>", unsafe_allow_html=True)
    st.sidebar.info("Engine: Gemini 2.5 Flash")
    if st.sidebar.button("Logout"):
        st.session_state['auth'] = False
        st.rerun()

    st.title("🛠️ SEO Engine")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🔑 API Key is missing in Render!")
    else:
        genai.configure(api_key=api_key)
        
        up = st.file_uploader("Upload Product Photo", type=["jpg", "png", "jpeg"])
        
        if up:
            img = Image.open(up)
            st.image(img, width=300)
            
            if st.button("Generate SEO Listing"):
                with st.spinner("Atlas AI is analyzing your image using Next-Gen Vision..."):
                    try:
                        # استفاده از مدلی که در اکانتت موجود و قدرتمند است
                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                        
                        prompt = """
                        You are an expert Etsy SEO Optimizer. Analyze this image and provide:
                        1. A highly optimized Title (max 140 chars)
                        2. 13 multi-word Tags (separated by commas)
                        3. A professional, engaging product description.
                        Format it nicely.
                        """
                        
                        response = model.generate_content([prompt, img])
                        
                        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                        st.markdown("### 📋 Your Listing Data")
                        st.write(response.text)
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"Generation Error: {e}")
