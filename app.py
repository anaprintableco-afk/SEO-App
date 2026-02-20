import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# ==========================================
# 1. حرفه‌ای‌سازی تم و ظاهر (UI/UX)
# ==========================================
st.set_page_config(page_title="AtlasRank | Pro SEO Dashboard", layout="wide")

st.markdown("""
    <style>
        /* پس‌زمینه اصلی و فونت */
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        
        /* استایل کارت لاگین */
        .login-box {
            background: rgba(255, 255, 255, 0.05);
            padding: 40px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            max-width: 500px;
            margin: auto;
        }

        /* دکمه‌های اطلس‌رنک */
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, #FF5A1F 0%, #FF8C00 100%);
            color: white;
            font-weight: bold;
            border: none;
            padding: 12px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255, 90, 31, 0.4);
        }

        /* استایل منوی کناری */
        [data-testid="stSidebar"] {
            background-color: #161b22;
        }
    </style>
""", unsafe_allow_html=True)

# مدیریت وضعیت ورود
if 'auth_state' not in st.session_state:
    st.session_state['auth_state'] = False

# ==========================================
# 2. صفحه ورود و ثبت‌نام (Re-designed)
# ==========================================
def auth_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #FF5A1F;'>🚀 AtlasRank</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; opacity: 0.7;'>Etsy SEO Intelligence Platform</p>", unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Create Account"])
        
        with tab_login:
            email = st.text_input("Email Address", key="l_email")
            password = st.text_input("Password", type="password", key="l_pass")
            if st.button("Sign In"):
                if email and password:
                    st.session_state['auth_state'] = True
                    st.rerun()
                else:
                    st.error("Please enter email and password.")

        with tab_signup:
            st.text_input("Shop Name")
            st.text_input("Full Name")
            reg_email = st.text_input("Email Address", key="r_email")
            reg_pass = st.text_input("Create Password", type="password", key="r_pass")
            if st.button("Get Started - It's Free"):
                if reg_email and reg_pass:
                    st.success("Account created successfully!")
                    st.info("You can now login with your credentials.")
                else:
                    st.warning("Please fill all fields.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 3. پنل اصلی اپلیکیشن
# ==========================================
def main_panel():
    # Sidebar
    st.sidebar.markdown("<h2 style='color: #FF5A1F;'>AtlasRank Panel</h2>", unsafe_allow_html=True)
    st.sidebar.write("Logged in as: User")
    if st.sidebar.button("Logout"):
        st.session_state['auth_state'] = False
        st.rerun()

    st.title("🛠️ SEO Engine")
    st.write("Generate high-converting titles and tags for your listings.")

    # تنظیمات API (استفاده از آخرین نسخه پایدار)
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=400, caption="Preview")
        
        if st.button("Generate Optimized SEO"):
            with st.spinner("Atlas AI is analyzing your product..."):
                try:
                    # تلاش برای فراخوانی مدل 1.5 فلش (تضمینی با پایتون 3.11)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = "Acting as an Etsy SEO expert, analyze this image and provide: 1. A Title (max 140 chars) 2. 13 Tags separated by commas 3. A professional description."
                    
                    response = model.generate_content([prompt, image])
                    
                    st.success("Analysis Complete!")
                    st.markdown("### 📊 SEO Results")
                    st.info(response.text)
                    
                except Exception as e:
                    st.error(f"API Error: {e}")

# کنترل نمایش
if not st.session_state['auth_state']:
    auth_page()
else:
    main_panel()
