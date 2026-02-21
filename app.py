import streamlit as st
import os
from streamlit_google_auth import Authenticate
from PIL import Image
import seo_engine # مطمئن شو این فایل کنار app.py هست

# --- ۱. اطلاعات گوگل (پر شده طبق پیام شما) ---
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

# --- ۲. تنظیمات پایه صفحه ---
st.set_page_config(page_title="AtlasRank | Etsy SEO AI", page_icon="🚀", layout="wide")

# تنظیمات احراز هویت - مخصوص دامین تو
authenticator = Authenticate(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="https://atlasrank.net", # آدرس دقیق دامین تو
    cookie_name='atlas_rank_user_cookie',
    cookie_key='atlas_rank_secure_key', 
    cookie_expiry_days=30
)

# بررسی وضعیت لاگین
authenticator.check_authenticity()

# --- ۳. مدیریت دیتای برنامه (Session States) ---
if 'seo_result' not in st.session_state: st.session_state.seo_result = None
if 'is_running' not in st.session_state: st.session_state.is_running = False
if 'history' not in st.session_state: st.session_state.history = []

# --- ۴. استایل‌های ظاهری (لندینگ و پنل) ---
st.markdown("""
    <style>
        .stApp { background-color: #0d1117; color: #c9d1d9; }
        .logo-text { font-weight: 800; font-size: 28px; color: #ffffff; display: flex; align-items: center; gap: 10px; margin-bottom: 20px;}
        .logo-icon { background: #FF5A1F; color: white; padding: 5px 12px; border-radius: 8px; }
        .box-title { color: #FF5A1F; font-size: 1.1em; font-weight: bold; margin-top: 15px; border-bottom: 1px solid #30363d; padding-bottom: 5px;}
        .stButton>button { background: linear-gradient(90deg, #FF5A1F, #FF8C00); color: white; border: none; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# منطق اصلی نمایش
# ---------------------------------------------------------

# الف) اگر کاربر هنوز وارد نشده (لندینگ پیج)
if not st.session_state.get('connected'):
    st.markdown('<div class="logo-text"><span class="logo-icon">A</span> AtlasRank</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='text-align:center; padding:60px 0;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:3.5rem; color:#FF5A1F;'>Scale Your Etsy Shop with AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.4rem; color:#8b949e;'>Stop guessing keywords. Start using data-backed SEO.</p>", unsafe_allow_html=True)
    
    _, col_login, _ = st.columns([1.5, 1, 1.5])
    with col_login:
        st.markdown("<br>", unsafe_allow_html=True)
        # دکمه لاگین گوگل
        .login()
    st.markdown("</div>", unsafe_allow_html=True)

# ب) اگر لاگین موفق بود (محیط برنامه)
else:
    user_info = st.session_state.get('user_info')
    api_key = os.environ.get("GEMINI_API_KEY")

    # هدر و دکمه خروج در سایدبار
    with st.sidebar:
        st.markdown('<div class="logo-text"><span class="logo-icon">A</span> AtlasRank</div>', unsafe_allow_html=True)
        st.write(f"Welcome, **{user_info.get('given_name')}** 👋")
        st.image(user_info.get('picture'), width=70)
        st.markdown("---")
        if st.button("Logout 🚪", use_container_width=True):
            .logout()
            st.rerun()
        
        st.markdown("### 🖼️ Recent Artworks")
        if st.session_state.history:
            for item in reversed(st.session_state.history):
                st.image(item['img'], use_container_width=True)
                st.caption(item['title'][:30] + "...")
                st.markdown("---")

    # --- بدنه اصلی برنامه (دقیقا کدهای قبلی) ---
    if not st.session_state.seo_result:
        st.markdown("## Generate New SEO Listing")
        col_in, col_pre = st.columns([2, 1])
        
        with col_in:
            p_type = st.radio("Listing Type:", ["Frame TV Art", "Printable Wall Art"], horizontal=True)
            up = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
            user_note = st.text_area("Optional Note:", placeholder="e.g. Vintage style...", height=80)
            
            if up:
                if not st.session_state.is_running:
                    if st.button("✨ Run SEO Engine"):
                        st.session_state.is_running = True
                        st.rerun()
                else:
                    with st.spinner("Analyzing your art..."):
                        img = Image.open(up)
                        res = seo_engine.generate_seo_data(img, p_type, user_note, api_key)
                        st.session_state.history.append({'img': img, 'title': res.get('Title', 'Untitled')})
                        st.session_state.seo_result = res
                        st.session_state.is_running = False
                        st.rerun()
        with col_pre:
            if up: st.image(Image.open(up), use_container_width=True, caption="Preview")

    else:
        # نمایش خروجی ۱۰ فیلد فیکس
        res = st.session_state.seo_result
        st.success("✅ SEO Optimized!")
        
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
        st.text_area("D", value=res.get('Description', ''), height=200, label_visibility="collapsed")

        if st.button("➕ New Analysis"):
            st.session_state.seo_result = None
            st.rerun()
