# app.py
import streamlit as st
from PIL import Image
import os
import seo_engine 

st.set_page_config(page_title="AtlasRank Pro", layout="wide")

# استایل اختصاصی برای باکس‌ها
st.markdown("""
    <style>
        .box-title { color: #FF5A1F; font-weight: bold; margin-top: 15px; border-bottom: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

def main():
    if 'data' not in st.session_state: st.session_state.data = None
    
    st.title("🚀 AtlasRank Pro")
    api_key = os.environ.get("GEMINI_API_KEY")

    if not st.session_state.data:
        p_type = st.radio("Mode:", ["Art for frame TV", "Printable Wall Art"], horizontal=True)
        up = st.file_uploader("Upload Image", type=["jpg", "png"])
        
        if up and st.button("Generate Professional SEO"):
            with st.spinner("Analyzing..."):
                img = Image.open(up)
                st.session_state.data = seo_engine.generate_listing(img, p_type, "", api_key)
                st.session_state.img = img
                st.rerun()
    else:
        res = st.session_state.data
        st.image(st.session_state.img, width=150)
        
        # ۱. نمایش تایتل
        st.markdown("<div class='box-title'>📌 Title</div>", unsafe_allow_html=True)
        st.code(res['Title'])
        
        # ۲. نمایش تگ‌ها
        st.markdown("<div class='box-title'>🏷️ 13 Tags</div>", unsafe_allow_html=True)
        st.info(" | ".join(res['Tags']))
        
        # ۳. نمایش اتریبیوت‌ها (بخش جدید)
        st.markdown("<div class='box-title'>⚙️ Etsy Attributes</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        attrs = res.get('Attributes', {})
        for i, (key, val) in enumerate(attrs.items()):
            with cols[i % 3]:
                display_val = ", ".join(val) if isinstance(val, list) else str(val)
                st.text_area(key, value=display_val, height=68)

        # ۴. نمایش دیسکریپشن
        st.markdown("<div class='box-title'>📝 Description</div>", unsafe_allow_html=True)
        st.write(res['Description'])
        
        if st.button("Start New Analysis"):
            st.session_state.data = None
            st.rerun()

if __name__ == "__main__":
    main()
