import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

st.set_page_config(page_title="AtlasRank | AI Dashboard", layout="centered")

st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        h1, h2, h3, p, span, label, div { color: #ffffff !important; }
        .stButton>button {
            width: 100%; border-radius: 8px;
            background: linear-gradient(90deg, #FF5A1F 0%, #FF8C00 100%);
            color: white !important; font-weight: bold; border: none; padding: 10px;
        }
        .result-box { background-color: #1c2128; padding: 20px; border-radius: 10px; border-left: 5px solid #FF5A1F; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown("<h1 style='text-align: center; color: #FF5A1F !important;'>🚀 AtlasRank</h1>", unsafe_allow_html=True)
    if st.button("Enter Dashboard"):
        st.session_state['auth'] = True
        st.rerun()
else:
    st.title("🛠️ SEO Engine & Diagnostic")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🔑 API Key is missing in Render!")
    else:
        genai.configure(api_key=api_key)
        
        # ---------------------------------------------------------
        # بخش هوشمند: پیدا کردن مدل‌هایی که کلید تو اجازه دسترسی دارد
        # ---------------------------------------------------------
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # پیدا کردن بهترین مدل تصویری از لیست مدل‌های مجاز
            best_model = None
            for target in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro-vision']:
                if target in available_models:
                    best_model = target
                    break
            
            if not best_model:
                st.error("❌ Your API Key does NOT have access to any Vision models!")
                st.write("Models your key can see:", available_models)
                st.stop()
                
        except Exception as e:
            st.error(f"Failed to check API Key: {e}")
            st.stop()

        # ---------------------------------------------------------
        # بخش اصلی اپلیکیشن
        # ---------------------------------------------------------
        st.success(f"✅ Atlas AI is connected! Using model: **{best_model}**")
        
        up = st.file_uploader("Upload Product Photo", type=["jpg", "png", "jpeg"])
        
        if up:
            img = Image.open(up)
            st.image(img, width=300)
            
            if st.button("Generate SEO Listing"):
                with st.spinner("Analyzing image..."):
                    try:
                        # استفاده از مدلی که در مرحله قبل تایید شد
                        model = genai.GenerativeModel(best_model)
                        prompt = "You are an Etsy SEO expert. Provide: 1. Title (max 140 chars) 2. 13 Tags (comma separated) 3. Description."
                        
                        response = model.generate_content([prompt, img])
                        
                        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                        st.write(response.text)
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.balloons()
                    except Exception as e:
                        st.error(f"Generation Error: {e}")
