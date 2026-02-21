# app.py
import streamlit as st
from PIL import Image
import os
import seo_engine

# تنظیمات اصلی صفحه
st.set_page_config(page_title="AtlasRank Pro | Etsy SEO", page_icon="🚀", layout="wide")

# استایل‌های CSS
st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: white; }
        .stButton>button { 
            background: linear-gradient(90deg, #FF5A1F, #FF8C00); 
            color: white; border-radius: 8px; border: none; font-weight: bold; width: 100%; height: 45px;
        }
        .box-title { color: #FF5A1F; font-size: 1.1em; font-weight: bold; margin-top: 15px; border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 10px;}
        .stTextArea textarea { background-color: #161b22; color: white; border: 1px solid #30363d; border-radius: 6px; }
        .stCodeBlock code { background-color: #161b22 !important; color: #44f864 !important; }
    </style>
""", unsafe_allow_html=True)

def main():
    # مدیریت وضعیت‌ها
    if 'data' not in st.session_state: st.session_state.data = None
    if 'is_processing' not in st.session_state: st.session_state.is_processing = False
    
    # هدر سایت
    st.markdown("<h1 style='text-align: center; color: #FF5A1F;'>🌐 ATLASRANK.NET</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Data-Driven SEO Engine for Etsy Sellers</p>", unsafe_allow_html=True)
    st.markdown("---")

    api_key = os.environ.get("GEMINI_API_KEY")

    if not st.session_state.data:
        p_type = st.radio("Choose Product Mode:", ["Art for frame TV", "Printable Wall Art"], horizontal=True)
        up = st.file_uploader("Upload Your Art Image", type=["jpg", "png", "jpeg"])
        
        if up:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                img = Image.open(up)
                st.image(img, use_container_width=True)
            
            # لاجیک دکمه بدون اجازه کلیک تکراری
            if not st.session_state.is_processing:
                if st.button("Generate Professional SEO"):
                    st.session_state.is_processing = True
                    st.rerun()
            else:
                with st.spinner("Mining database and generating SEO..."):
                    try:
                        res = seo_engine.generate_listing_logic(img, p_type, api_key)
                        st.session_state.data = res
                        st.session_state.img = img
                        st.session_state.is_processing = False
                        st.rerun()
                    except Exception as e:
                        st.error("Error connecting to AI. Please try again.")
                        st.session_state.is_processing = False
                        if st.button("Retry"): st.rerun()

    else:
        # نمایش نتایج (UI تمیز)
        res = st.session_state.data
        
        # نمایش عکس کوچک در کنار دکمه ریست
        col_img, col_btn = st.columns([1, 5])
        with col_img:
            st.image(st.session_state.img, use_container_width=True)
        with col_btn:
            if st.button("🔄 Analyze Another Image"):
                st.session_state.data = None
                st.rerun()

        st.success("✅ SEO Generated Successfully!")

        # تایتل
        st.markdown("<div class='box-title'>📌 Optimized Title</div>", unsafe_allow_html=True)
        st.code(res.get('Title', ''))
        
        # تگ‌ها (با فرمت کاما برای کپی با یک کلیک)
        st.markdown("<div class='box-title'>🏷️ 13 Strategic Tags (Click to Copy)</div>", unsafe_allow_html=True)
        all_tags = ", ".join(res.get('Tags', []))
        st.code(all_tags)
        
        # اتریبیوت‌ها
        st.markdown("<div class='box-title'>⚙️ Etsy Attributes</div>", unsafe_allow_html=True)
        attr_cols = st.columns(3)
        for i, (key, val) in enumerate(res.get('Attributes', {}).items()):
            with attr_cols[i % 3]:
                st.text_area(key, value=str(val), height=68)

        # دیسکریپشن
        st.markdown("<div class='box-title'>📝 Description</div>", unsafe_allow_html=True)
        st.text_area("Desc", value=res.get('Description', ''), height=200, label_visibility="collapsed")
        
        # متن‌های جایگزین (Alt Text)
        st.markdown("<div class='box-title'>🖼️ Alt Texts</div>", unsafe_allow_html=True)
        st.text_area("Alt", value="\n".join(res.get('AltTexts', [])), height=120, label_visibility="collapsed")

if __name__ == "__main__":
    main()
