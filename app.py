# app.py
import streamlit as st
from PIL import Image
import os
import seo_engine # متصل کردن به فایل مغز متفکر

# تنظیمات ظاهری سایت روی دامنه جدید
st.set_page_config(
    page_title="AtlasRank | Pro Etsy SEO Engine",
    page_icon="🚀",
    layout="wide"
)

# استایل اختصاصی اطلس‌رنک
st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: white; }
        .stButton>button { 
            background: linear-gradient(90deg, #FF5A1F, #FF8C00); 
            color: white; border-radius: 10px; border: none; font-weight: bold; width: 100%; height: 50px;
        }
        .box-title { color: #FF5A1F; font-size: 1.2em; font-weight: bold; margin-top: 20px; border-bottom: 1px solid #333; padding-bottom: 5px; }
        .stTextArea textarea { background-color: #161b22; color: white; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

def main():
    if 'result_data' not in st.session_state: st.session_state.result_data = None
    
    st.markdown("<h1 style='text-align: center; color: #FF5A1F;'>🌐 ATLASRANK.NET</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>AI-Powered SEO for Smart Etsy Sellers</p>", unsafe_allow_html=True)

    api_key = os.environ.get("GEMINI_API_KEY")

    if not st.session_state.result_data:
        # ستون‌بندی برای فرم ورودی
        col1, col2 = st.columns([1, 1])
        
        with col1:
            p_type = st.radio("Product Type:", ["Art for frame TV", "Printable Wall Art"], horizontal=True)
            up = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
        
        with col2:
            st.info("The system will analyze your image and extract high-performing keywords from your MASTER_API_DATA.csv")

        if up and st.button("Generate Professional SEO"):
            with st.spinner("Analyzing image and mining database..."):
                try:
                    img = Image.open(up)
                    # صدا کردن تابع تولید سئو از فایل seo_engine
                    res = seo_engine.generate_listing(img, p_type, api_key)
                    st.session_state.result_data = res
                    st.session_state.current_img = img
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        # نمایش نتایج نهایی
        res = st.session_state.result_data
        
        col_img, col_main = st.columns([1, 3])
        with col_img:
            st.image(st.session_state.current_img, use_container_width=True)
            if st.button("Start New"):
                st.session_state.result_data = None
                st.rerun()

        with col_main:
            st.markdown("<div class='box-title'>📌 Optimized Title</div>", unsafe_allow_html=True)
            st.code(res.get('Title', ''))

            st.markdown("<div class='box-title'>🏷️ 13 Strategic Tags</div>", unsafe_allow_html=True)
            st.info(" | ".join(res.get('Tags', [])))

            # بخش اتریبیوت‌ها (دقیقاً همانی که می‌خواستی)
            st.markdown("<div class='box-title'>⚙️ Etsy Attributes</div>", unsafe_allow_html=True)
            attr_cols = st.columns(3)
            attrs = res.get('Attributes', {})
            for i, (key, val) in enumerate(attrs.items()):
                with attr_cols[i % 3]:
                    st.text_area(key, value=str(val), height=68)

            st.markdown("<div class='box-title'>📝 Description</div>", unsafe_allow_html=True)
            st.text_area("Description", value=res.get('Description', ''), height=200, label_visibility="collapsed")

if __name__ == "__main__":
    main()
