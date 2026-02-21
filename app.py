import streamlit as st
from PIL import Image
import os
import seo_engine # این فایل را طبق تغییرات دیروز نگه دارید

# 1. تنظیمات پایه صفحه
st.set_page_config(page_title="AtlasRank | Etsy SEO AI Engine", page_icon="🚀", layout="wide")

# 2. مدیریت وضعیت ورود و دیتای برنامه
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'seo_result' not in st.session_state:
    st.session_state.seo_result = None
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'history' not in st.session_state:
    st.session_state.history = []

# 3. تمام استایل‌های ظاهری (ترکیب لندینگ و پنل کاربری)
st.markdown("""
    <style>
        /* استایل‌های کلی */
        .stApp { background-color: #0d1117; color: #c9d1d9; font-family: sans-serif; }
        
        /* استایل‌های لندینگ پیج */
        .hero-text { text-align: center; padding: 60px 0; }
        .hero-title { font-size: 3.8rem; font-weight: 800; color: #FF5A1F; margin-bottom: 10px; line-height: 1.1; }
        .hero-subtitle { font-size: 1.4rem; color: #8b949e; margin-bottom: 40px; }
        .feature-box { 
            background-color: #161b22; padding: 25px; border-radius: 12px; 
            border: 1px solid #30363d; height: 100%; text-align: center; transition: 0.3s;
        }
        .feature-box:hover { border-color: #FF5A1F; transform: translateY(-5px); }
        .pricing-card {
            background: linear-gradient(145deg, #1c2128, #161b22);
            padding: 40px; border-radius: 20px; border: 2px solid #30363d; text-align: center;
        }
        .pricing-card.pro { border-color: #FF5A1F; box-shadow: 0 0 20px rgba(255, 90, 31, 0.1); }
        
        /* استایل‌های پنل کاربری (بدون تغییر نسبت به قبل) */
        .box-title { color: #FF5A1F; font-size: 1.1em; font-weight: bold; margin-top: 15px; border-bottom: 1px solid #30363d; padding-bottom: 5px; margin-bottom: 10px;}
        .stButton>button { background: linear-gradient(90deg, #FF5A1F, #FF8C00); color: white; border-radius: 6px; border: none; font-weight: bold; transition: 0.3s;}
        .stTextArea textarea { background-color: #161b22; color: #58a6ff; border: 1px solid #30363d; border-radius: 6px;}
        .stCodeBlock code { background-color: #161b22 !important; color: #3fb950 !important; font-size: 1em; }
        .stSpinner > div > div { border-color: #FF5A1F transparent transparent transparent !important; }
    </style>
""", unsafe_allow_html=True)

def main():
    api_key = os.environ.get("GEMINI_API_KEY")

    # ---------------------------------------------------------
    # حالت اول: لندینگ پیج (ویترین سایت)
    # ---------------------------------------------------------
    if not st.session_state.logged_in:
        # Header
        col_l, col_r = st.columns([5, 1])
        with col_l: st.markdown("<h2 style='color:#FF5A1F; margin:0;'>AtlasRank</h2>", unsafe_allow_html=True)
        with col_r: 
            if st.button("Login / Signup", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()

        # Hero Section
        st.markdown("""
            <div class='hero-text'>
                <h1 class='hero-title'>Stop Guessing.<br>Master Etsy SEO with AI.</h1>
                <p class='hero-subtitle'>The first data-driven SEO engine designed specifically for Etsy Art Sellers.</p>
            </div>
        """, unsafe_allow_html=True)
        
        _, col_cta, _ = st.columns([2,1.5,2])
        with col_cta:
            if st.button("🚀 Start Free Analysis Now", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()

        st.markdown("<br><br>", unsafe_allow_html=True)

        # Features
        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown("<div class='feature-box'><h3>📊 Data Mining</h3><p>We analyze real CSV search data to find low-competition gems.</p></div>", unsafe_allow_html=True)
        with f2:
            st.markdown("<div class='feature-box'><h3>🧠 AI Vision</h3><p>Gemini 2.0 Flash analyzes your art's DNA, style, and subject.</p></div>", unsafe_allow_html=True)
        with f3:
            st.markdown("<div class='feature-box'><h3>🛡️ Strict SEO</h3><p>Titles & tags following the latest Etsy 2024 handbook rules.</p></div>", unsafe_allow_html=True)

        st.markdown("<br><br><h2 style='text-align:center;'>Pricing Plans</h2>", unsafe_allow_html=True)

        # Pricing
        p1, p2 = st.columns(2)
        with p1:
            st.markdown("<div class='pricing-card'><h3>Free</h3><h2 style='color:#FF5A1F;'>$0</h2><p>3 Analysis per day<br>Standard Support</p></div>", unsafe_allow_html=True)
            if st.button("Join Free", key="join_free", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
        with p2:
            st.markdown("<div class='pricing-card pro'><h3>Pro Artist</h3><h2 style='color:#FF5A1F;'>$9.99<small>/mo</small></h2><p>Unlimited Analysis<br>Advanced Opportunity Scores</p></div>", unsafe_allow_html=True)
            st.link_button("Go Pro (Stripe)", "https://buy.stripe.com/test_link", use_container_width=True)

    # ---------------------------------------------------------
    # حالت دوم: پنل کاربری (دقیقاً همان منطق قبلی شما)
    # ---------------------------------------------------------
    else:
        # نوار کناری برای تاریخچه و خروج (دقیقاً مثل دیروز)
        with st.sidebar:
            st.markdown("<h2 style='color: #FF5A1F; text-align: center;'>AtlasRank</h2>", unsafe_allow_html=True)
            if st.button("Logout 🚪", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 🖼️ Recent Artworks")
            if not st.session_state.history:
                st.info("No history yet.")
            else:
                for item in reversed(st.session_state.history):
                    st.image(item['img'], use_container_width=True)
                    st.caption(item['title'][:40] + "...")
                    st.markdown("---")

        # اگر نتیجه‌ای هنوز تولید نشده، فرم آپلود را نشان بده
        if not st.session_state.seo_result:
            st.markdown("<h2 style='color: #fff;'>Generate New SEO Listing</h2>", unsafe_allow_html=True)
            col_in, col_pre = st.columns([2, 1])
            
            with col_in:
                p_type = st.radio("Listing Type:", ["Frame TV Art", "Printable Wall Art"], horizontal=True)
                up = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
                user_note = st.text_area("Optional Note (Help the AI):", placeholder="e.g. Vintage oil painting style...", height=80)
                
                if up:
                    if not st.session_state.is_running:
                        if st.button("✨ Run SEO Engine"):
                            st.session_state.is_running = True
                            st.rerun()
                    else:
                        with st.spinner(""):
                            try:
                                img = Image.open(up)
                                # فراخوانی مغز سیستم
                                res = seo_engine.generate_seo_data(img, p_type, user_note, api_key)
                                
                                st.session_state.history.append({'img': img, 'title': res.get('Title', 'Untitled')})
                                st.session_state.seo_result = res
                                st.session_state.img = img
                                st.session_state.is_running = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                                st.session_state.is_running = False
            with col_pre:
                if up: st.image(Image.open(up), use_container_width=True, caption="Target Image")

        # اگر نتیجه آماده است، آن را نمایش بده (دقیقاً همان ۱۰ فیلد فیکس)
        else:
            res = st.session_state.seo_result
            st.success("✅ SEO Structure Optimized")
            
            st.markdown("<div class='box-title'>📌 Title</div>", unsafe_allow_html=True)
            st.code(res.get('Title', ''))

            st.markdown("<div class='box-title'>🏷️ 13 Strategic Tags</div>", unsafe_allow_html=True)
            st.code(", ".join(res.get('Tags', [])))

            st.markdown("<div class='box-title'>⚙️ Etsy Attributes</div>", unsafe_allow_html=True)
            attr_keys = ["1st Main Color", "2nd Main Color", "Home Style", "Celebration", "Occasion", "Subject", "Room"]
            cols = st.columns(4)
            for i, key in enumerate(attr_keys):
                with cols[i % 4]:
                    st.text_area(key, value=res.get(key, "None"), height=68, disabled=True)

            st.markdown("<div class='box-title'>📝 Description</div>", unsafe_allow_html=True)
            st.text_area("D", value=res.get('Description', ''), height=200, label_visibility="collapsed")

            st.markdown("---")
            # بخش فیدبک و کنترل
            st.markdown("### Feedback & Actions")
            st.text_area("Any feedback?", placeholder="Accuracy, tone, keywords...", height=70)
            
            c1, c2, c3 = st.columns(3)
            with c1: 
                if st.button("📤 Submit"): st.toast("Saved!")
            with c2:
                if st.button("➕ New Listing"):
                    st.session_state.seo_result = None
                    st.rerun()
            with c3:
                if st.button("🔄 Reset All"):
                    st.session_state.seo_result = None
                    st.session_state.history = []
                    st.rerun()

if __name__ == "__main__":
    main()
