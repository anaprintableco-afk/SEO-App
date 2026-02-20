import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import json
import os

# ==========================================
# تنظیمات اصلی سایت
# ==========================================
st.set_page_config(page_title="Etsy SEO Pro AI", page_icon="📈", layout="centered")

LINK_TO_BUY = "https://your-gumroad-link.com"
PREMIUM_UPGRADE_CODE = "PRO-ETSY-500"

# خواندن کلید API به صورت مخفی از گاوصندوق Streamlit
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ==========================================
# سیستم دیتابیس کاربران
# ==========================================
DB_FILE = 'users.json'

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_users(users_dict):
    with open(DB_FILE, 'w') as f:
        json.dump(users_dict, f)

users_db = load_users()

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# ==========================================
# بخش ثبت‌نام و ورود
# ==========================================
if st.session_state.current_user is None:
    st.title("📈 ورود به پلتفرم هوش مصنوعی اتسی")
    st.markdown("برای تست ابزار، ثبت‌نام کنید و **۳ اعتبار رایگان** بگیرید.")
    
    tab1, tab2 = st.tabs(["ثبت‌نام جدید", "ورود"])
    
    with tab1:
        st.subheader("ساخت حساب کاربری")
        new_email = st.text_input("ایمیل شما:", key="reg_email").strip().lower()
        new_password = st.text_input("رمز عبور:", type="password", key="reg_pass")
        if st.button("ثبت‌نام و دریافت اعتبار رایگان"):
            if new_email in users_db:
                st.error("این ایمیل قبلاً ثبت شده است! لطفاً وارد شوید.")
            elif new_email and new_password:
                users_db[new_email] = {
                    "password": new_password,
                    "credits": 3,
                    "tier": "Free"
                }
                save_users(users_db)
                st.success("ثبت‌نام موفقیت‌آمیز بود! از تب ورود، وارد شوید.")
            else:
                st.warning("لطفاً ایمیل و رمز عبور را وارد کنید.")

    with tab2:
        st.subheader("ورود به حساب")
        login_email = st.text_input("ایمیل:", key="log_email").strip().lower()
        login_password = st.text_input("رمز عبور:", type="password", key="log_pass")
        if st.button("ورود"):
            if login_email in users_db and users_db[login_email]["password"] == login_password:
                st.session_state.current_user = login_email
                st.rerun()
            else:
                st.error("ایمیل یا رمز عبور اشتباه است.")
    
    st.stop()

# ==========================================
# بخش داشبورد کاربر
# ==========================================
current_email = st.session_state.current_user
user_data = users_db[current_email]

col1, col2 = st.columns([8, 2])
with col1:
    st.title("🚀 داشبورد سئو اتسی شما")
with col2:
    if st.button("خروج"):
        st.session_state.current_user = None
        st.rerun()

st.write(f"👤 کاربر: `{current_email}` | 🌟 پلن: `{user_data.get('tier', 'Free')}`")

if user_data['credits'] > 0:
    st.info(f"🪙 اعتبارهای باقیمانده شما: **{user_data['credits']}** درخواست")
else:
    st.error("🛑 اعتبار شما به پایان رسیده است.")

with st.expander("💎 شارژ حساب / ارتقا به پلن حرفه‌ای"):
    st.markdown(f"برای خرید پکیج ۵۰۰ اعتباری روی لینک زیر کلیک کنید:")
    st.markdown(f"[💳 خرید پکیج اعتباری]({LINK_TO_BUY})")
    upgrade_code = st.text_input("کد شارژ (پس از خرید دریافت می‌کنید):")
    if st.button("اعمال کد شارژ"):
        if upgrade_code == PREMIUM_UPGRADE_CODE:
            users_db[current_email]["credits"] += 500
            users_db[current_email]["tier"] = "Premium"
            save_users(users_db)
            st.success("تبریک! ۵۰۰ اعتبار جدید به حساب شما اضافه شد.")
            st.rerun()
        else:
            st.error("کد وارد شده نامعتبر است.")

if user_data["credits"] <= 0:
    st.stop()

# ==========================================
# پردازش با هوش مصنوعی
# ==========================================
st.markdown("---")
st.subheader("🖼️ آپلود محصول و تولید تگ")

uploaded_file = st.file_uploader("عکس محصول خود را آپلود کنید", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="عکس محصول شما", use_container_width=True)
    
    if st.button("✨ پردازش هوشمند (کسر ۱ اعتبار)"):
        with st.spinner("در حال تحلیل و تطبیق با دیتابیس..."):
            try:
                df = pd.read_csv('MASTER_API_DATA.csv')
                df['Avg_Searches'] = pd.to_numeric(df['Avg_Searches'], errors='coerce').fillna(0)
                df['Competition'] = pd.to_numeric(df['Competition'], errors='coerce').fillna(1)
                df['Opportunity'] = df['Avg_Searches'] / df['Competition']
                
                top_keywords = df.sort_values(by='Opportunity', ascending=False).head(300)['Keyword'].tolist()
                csv_context = ", ".join(str(x) for x in top_keywords)
                
                prompt = f"""
                # ROLE: Etsy SEO Strategist & Optimizer (Digital Products)

                # CORE KNOWLEDGE BASES:
                1. INTERNAL: Your pre-trained knowledge of global search trends.
                2. COMPLIANCE: Strictly adhere to the Etsy Seller Handbook rules.
                3. DATA-DRIVEN: Use this list of high-opportunity keywords: [{csv_context}]

                # PROCESSING PIPELINE:
                1. CREATIVE GENERATION: Analyze the image and generate high-intent Title and 13 Tags.
                2. HANDBOOK VERIFICATION: Title < 100 chars, Tags < 20 chars, No keyword stuffing.
                3. CSV CROSS-OPTIMIZATION: Compare generated tags with the CSV list. REPLACE generic tags with highly relevant CSV tags that have better Opportunity Ratios. Target a mix of 70% CSV data / 30% image-specific tags.
                4. FINAL AUDIT: Ensure 13 unique tags and no prohibited words.

                # OUTPUT FORMAT:
                Title: [Title]
                Description: [Description]
                Alt Texts: [10 Alt Texts]
                Tags: [13 Tags]
                """
                
                # رفع ارور نام مدل با اضافه کردن latest
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content([prompt, image])
                
                st.success("✅ سئو با موفقیت انجام شد!")
                st.text_area("کپی کنید:", value=response.text, height=400)
                
                users_db[current_email]["credits"] -= 1
                save_users(users_db)
                st.info(f"🪙 یک اعتبار مصرف شد. اعتبارهای باقیمانده شما: {users_db[current_email]['credits']}")
                
            except Exception as e:
                st.error(f"خطایی رخ داد: {e}")

