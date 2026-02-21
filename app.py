# app.py
import streamlit as st
from PIL import Image
import os
import seo_engine

st.set_page_config(page_title="AtlasRank Pro", page_icon="⚡", layout="wide")

# استایل‌های تمیز و مدرن
st.markdown("""
    <style>
        .stApp { background-color: #0d1117; color: #c9d1d9; font-family: sans-serif; }
        .box-title { color: #FF5A1F; font-size: 1.1em; font-weight: bold; margin-top: 15px; border-bottom: 1px solid #30363d; padding-bottom: 5px; margin-bottom: 10px;}
        .stButton>button { background: linear-gradient(90deg, #FF5A1F, #FF8C00); color: white; border-radius: 6px; border: none; font-weight: bold; width: 100%; height: 45px; transition: 0.3s;}
        .stButton>button:hover { opacity: 0.8; }
        .stTextArea textarea { background-color: #161b22; color: #58a6ff; border: 1px solid #30363d; border-radius: 6px;}
        .stCodeBlock code { background-color: #161b22 !important; color: #3fb950 !important; font-size: 1em; }
        /* مخفی کردن متن لودینگ دیفالت استریم‌لیت در صورت وجود */
        .stSpinner > div > div { border-color: #FF5A1F transparent transparent transparent !important; }
    </style>
""", unsafe_allow_html=True)

def main():
    # مدیریت تاریخچه عکس‌ها (برای لیست سمت چپ)
    if 'history' not in st.session_state: st.session_state.history = []
    if 'seo_result' not in st.session_state: st.session_state.seo_result = None
    if 'is_running' not in st.session_state: st.session_state.is_running = False

    api_key = os.environ.get("GEMINI_API_KEY")

    # ----- نوار کناری (Sidebar) شبیه داشبوردهای حرفه‌ای -----
    with st.sidebar:
        st.markdown("<h2 style='color: #FF5A1F; text-align: center;'>AtlasRank</h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 🖼️ Recent Artworks")
        
        if not st.session_state.history:
            st.info("No history yet.")
        else:
            # نمایش عکس‌های قبلی از آخر به اول
            for item in reversed(st.session_state.history):
                st.image(item['img'], use_container_width=True)
                st.caption(item['title'][:40] + "...")
                st.markdown("---")

    # ----- محیط اصلی (Main Area) -----
    if not st.session_state.seo_result:
        st.markdown("<h2 style='color: #fff;'>Start New AI SEO Listing</h2>", unsafe_allow_html=True)
        
        col_input, col_img = st.columns([2, 1])
        
        with col_input:
            p_type = st.radio("Select Listing Type:", ["Frame TV Art", "Printable Wall Art"], horizontal=True)
            up = st.file_uploader("Upload your artwork here (JPG/PNG)", type=["jpg", "png", "jpeg"])
            
            # باکس جدید: توضیح اختیاری کاربر
            user_note = st.text_area("Optional: Add a hint for the AI (e.g., 'This is a vintage oil painting of a horse')", height=80)
            
            if up:
                if not st.session_state.is_running:
                    if st.button("✨ Generate SEO Listing"):
                        st.session_state.is_running = True
                        st.rerun()
                else:
                    # لودینگ بدون هیچ متنی
                    with st.spinner(""):
                        try:
                            img = Image.open(up)
                            res = seo_engine.generate_seo_data(img, p_type, user_note, api_key)
                            
                            # ذخیره در تاریخچه سایدبار
                            st.session_state.history.append({
                                'img': img,
                                'title': res.get('Title', 'Untitled')
                            })
                            
                            st.session_state.seo_result = res
                            st.session_state.img = img
                            st.session_state.is_running = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Engine Error: {e}")
                            st.session_state.is_running = False
                            if st.button("Retry"): st.rerun()
                            
        with col_img:
            if up:
                st.image(Image.open(up), use_container_width=True, caption="Ready for analysis")

    else:
        # ----- حالت نمایش نتایج -----
        res = st.session_state.seo_result
        st.success("✅ Listing Generated Successfully")

        st.markdown("<div class='box-title'>📌 Title</div>", unsafe_allow_html=True)
        st.code(res.get('Title', ''))

        st.markdown("<div class='box-title'>🏷️ 13 Tags</div>", unsafe_allow_html=True)
        st.code(", ".join(res.get('Tags', [])))

        st.markdown("<div class='box-title'>⚙️ Attributes</div>", unsafe_allow_html=True)
        attr_keys = ["1st Main Color", "2nd Main Color", "Home Style", "Celebration", "Occasion", "Subject", "Room"]
        cols = st.columns(4)
        for i, key in enumerate(attr_keys):
            with cols[i % 4]:
                st.text_area(key, value=res.get(key, "None"), height=68, disabled=True)

        st.markdown("<div class='box-title'>📝 Description</div>", unsafe_allow_html=True)
        st.text_area("Desc", value=res.get('Description', ''), height=200, label_visibility="collapsed")

        st.markdown("---")
        
        # ----- بخش پایانی: فیدبک و دکمه‌های اکشن -----
        st.markdown("### 💬 Provide Feedback")
        feedback = st.text_area("How accurate was this result?", placeholder="Type your feedback here...", height=68)
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("📤 Submit Feedback"):
                st.toast("Feedback submitted! Thank you.")
        with col_btn2:
            if st.button("➕ Start with New Product"):
                st.session_state.seo_result = None
                st.rerun()
        with col_btn3:
            if st.button("🔄 Restart App (Clear All)"):
                st.session_state.seo_result = None
                st.session_state.history = []
                st.rerun()

if __name__ == "__main__":
    main()
