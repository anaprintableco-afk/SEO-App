# app.py
import streamlit as st
from PIL import Image
import os
import seo_engine

# تنظیمات اصلی UI
st.set_page_config(page_title="AtlasRank Pro Engine", page_icon="⚙️", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0d1117; color: #c9d1d9; font-family: sans-serif; }
        .box-title { color: #FF5A1F; font-size: 1.1em; font-weight: bold; margin-top: 15px; border-bottom: 1px solid #30363d; padding-bottom: 5px; margin-bottom: 10px;}
        .stButton>button { background: linear-gradient(90deg, #FF5A1F, #FF8C00); color: white; border-radius: 6px; border: none; font-weight: bold; width: 100%; height: 45px; transition: 0.3s;}
        .stButton>button:hover { opacity: 0.8; }
        .stTextArea textarea { background-color: #161b22; color: #58a6ff; border: 1px solid #30363d; border-radius: 6px; font-weight: 500;}
        .stCodeBlock code { background-color: #161b22 !important; color: #3fb950 !important; font-size: 1em; }
    </style>
""", unsafe_allow_html=True)

def main():
    if 'seo_result' not in st.session_state: st.session_state.seo_result = None
    if 'is_running' not in st.session_state: st.session_state.is_running = False

    st.markdown("<h1 style='text-align: center; color: #FF5A1F; margin-bottom: 0;'>🌐 ATLASRANK.NET</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>Advanced Semantic SEO Engine for Etsy</p>", unsafe_allow_html=True)
    
    api_key = os.environ.get("GEMINI_API_KEY")

    if not st.session_state.seo_result:
        # حالت آپلود
        col_type, col_up = st.columns([1, 2])
        with col_type:
            p_type = st.radio("Select Listing Type:", ["Frame TV Art", "Printable Wall Art"])
        with col_up:
            up = st.file_uploader("Drop your artwork here", type=["jpg", "png", "jpeg"])
        
        if up:
            st.image(up, width=250)
            if not st.session_state.is_running:
                if st.button("🚀 Execute SEO Logic"):
                    st.session_state.is_running = True
                    st.rerun()
            else:
                with st.spinner("Mining data, calculating Opportunity Scores, and generating structure..."):
                    try:
                        img = Image.open(up)
                        # ارتباط با مغز متفکر (seo_engine)
                        res = seo_engine.generate_seo_data(img, p_type, api_key)
                        st.session_state.seo_result = res
                        st.session_state.img = img
                        st.session_state.is_running = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Engine Error: {e}")
                        st.session_state.is_running = False
                        if st.button("Retry"): st.rerun()
    else:
        # حالت نمایش نتایج (UI فیکس شده بر اساس 10 فیلد)
        res = st.session_state.seo_result
        
        col_img, col_btn = st.columns([1, 5])
        with col_img:
            st.image(st.session_state.img, use_container_width=True)
        with col_btn:
            if st.button("🔄 Analyze New Artwork"):
                st.session_state.seo_result = None
                st.rerun()

        st.success("✅ SEO Data successfully generated based on CSV mining and Etsy algorithms.")

        # 1. تایتل
        st.markdown("<div class='box-title'>📌 Title (Front-loaded)</div>", unsafe_allow_html=True)
        st.code(res.get('Title', ''))

        # 2. تگ‌ها
        st.markdown("<div class='box-title'>🏷️ 13 Strategic Tags (Comma-Separated)</div>", unsafe_allow_html=True)
        all_tags = ", ".join(res.get('Tags', []))
        st.code(all_tags)

        # 3. اتریبیوت‌ها (دقیقا 7 فیلد فیکس)
        st.markdown("<div class='box-title'>⚙️ Etsy Attributes</div>", unsafe_allow_html=True)
        attr_keys = ["1st Main Color", "2nd Main Color", "Home Style", "Celebration", "Occasion", "Subject", "Room"]
        cols = st.columns(4)
        for i, key in enumerate(attr_keys):
            with cols[i % 4]:
                st.text_area(key, value=res.get(key, "None"), height=68)

        # 4. دیسکریپشن
        st.markdown("<div class='box-title'>📝 Description</div>", unsafe_allow_html=True)
        st.text_area("Desc", value=res.get('Description', ''), height=200, label_visibility="collapsed")

if __name__ == "__main__":
    main()
