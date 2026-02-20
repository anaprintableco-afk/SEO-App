import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import os

# ==========================================
# 1. Page Configuration & UI
# ==========================================
st.set_page_config(page_title="AtlasRank | Etsy SEO Engine", layout="centered")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Display:wght@300;400;600&display=swap');
        html, body, [class*="css"] { font-family: 'Noto Sans Display', sans-serif !important; }
        .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #FF5A1F; color: white; font-weight: 600; border: none; }
        .stButton>button:hover { background-color: #e44d18; color: white; }
        .stTextArea textarea { font-size: 15px !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. API Key Configuration
# ==========================================
api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("🔑 API Key not found! Please add GEMINI_API_KEY to Render Environment Variables.")
    st.stop()

# ==========================================
# 3. Core Logic
# ==========================================
st.title("🚀 AtlasRank SEO Engine")
st.markdown("Automated Etsy Listing Service by **Atlas Creative House**")

product_mode = st.radio("Select Mode:", ["Printable (Digital Download)", "Frame TV Art (Digital Display)"], horizontal=True)

uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", width=350)
    
    if st.button("Generate Optimized SEO Data"):
        with st.spinner("Atlas AI is analyzing and generating..."):
            try:
                # خواندن دیتای کلمات کلیدی (در صورت وجود)
                csv_context = ""
                if os.path.exists('MASTER_API_DATA.csv'):
                    df = pd.read_csv('MASTER_API_DATA.csv')
                    top_keywords = df.head(50)['Keyword'].tolist()
                    csv_context = ", ".join(str(x) for x in top_keywords)

                # پرامپت دقیق برای استخراج راحت‌تر
                prompt = f"""
                You are AtlasRank AI. Create a high-converting Etsy listing.
                Mode: {product_mode}
                Keywords to use: {csv_context}
                
                Please provide the output EXACTLY in this format:
                [TITLE_START] Write the title here [TITLE_END]
                [TAGS_START] Write 13 multi-word tags here separated by comma [TAGS_END]
                [DESC_START] Write the professional description here [DESC_END]
                """
                
                # استفاده از نام کامل مدل برای رفع خطای 404
                model = genai.GenerativeModel('models/gemini-1.5-flash')
                response = model.generate_content([prompt, image])
                res_text = response.text

                # تابع کمکی برای جدا کردن بخش‌ها
                def get_content(text, start_tag, end_tag):
                    try:
                        return text.split(start_tag)[1].split(end_tag)[0].strip()
                    except:
                        return "Content not found."

                title_final = get_content(res_text, "[TITLE_START]", "[TITLE_END]")
                tags_final = get_content(res_text, "[TAGS_START]", "[TAGS_END]")
                desc_final = get_content(res_text, "[DESC_START]", "[DESC_END]")

                # نمایش در باکس‌های جداگانه
                st.success("SEO Generation Successful!")
                
                st.subheader("📌 Optimized Title")
                st.text_area("Copy Title:", value=title_final, height=70, key="title_box")
                
                st.subheader("🏷️ 13 SEO Tags")
                st.text_area("Copy Tags:", value=tags_final, height=100, key="tags_box")
                
                st.subheader("📝 Product Description")
                st.text_area("Copy Description:", value=desc_final, height=250, key="desc_box")

            except Exception as e:
                st.error(f"❌ Error during generation: {e}")
                # اگر خطای مدل داد، متن خام را نشان بده تا بفهمیم مشکل چیست
                if 'res_text' in locals():
                    st.write("Raw Output for debugging:", res_text)

st.markdown("---")
st.caption("© 2026 AtlasRank.io | Atlas Creative House Canada")
