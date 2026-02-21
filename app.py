import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd # برای مدیریت بهتر دیتابیس
import os, json, time

# ==========================================
# 1. SETUP & THEME
# ==========================================
st.set_page_config(page_title="AtlasRank Pro", layout="centered")

st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: white; }
        .stButton>button { 
            background: linear-gradient(90deg, #FF5A1F, #FF8C00); 
            color: white; border-radius: 20px; border: none; padding: 12px 30px;
            font-weight: bold; width: 100%;
        }
        .stTextArea textarea { background-color: #161b22; color: white; border: 1px solid #30363d; }
        h1 { color: #FF5A1F; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SMART DATA FILTERING (لاجیک جدید)
# ==========================================
def get_best_keywords(csv_path, search_term, top_n=30):
    """پیدا کردن بهترین کلمات از دیتابیس قبل از ارسال به هوش مصنوعی"""
    try:
        df = pd.read_csv(csv_path)
        # فیلتر کردن کلماتی که شامل سوژه هستند
        filtered = df[df['Keyword'].str.contains(search_term, case=False, na=False)]
        # امتیازدهی: جستجوی بالا، رقابت پایین (فرض بر وجود ستون‌ها)
        filtered['Score'] = filtered['Avg_Searches'] / (filtered['Competition'] + 1)
        return filtered.sort_values('Score', ascending=False).head(top_n)['Keyword'].tolist()
    except:
        return []

# ==========================================
# 3. CORE ENGINE (GEMINI 2.5 FLASH)
# ==========================================
def generate_seo_pro(img, p_type, user_desc, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # فاز اول: درک عمیق تصویر (بدون محدودیت سئو)
    vision_prompt = "Describe this art in 5 keywords: subject, style, main color, mood, era."
    vision_res = model.generate_content([vision_prompt, img])
    tags_found = vision_res.text.split(',')

    # فاز دوم: استخراج کلمات طلایی از CSV بر اساس درک تصویر
    # (در اینجا ما از کلمات پیدا شده در عکس برای جستجو در CSV استفاده می‌کنیم)
    csv_keywords = []
    for t in tags_found[:2]: # برای سرعت، روی دو تم اصلی زوم میکنیم
        csv_keywords.extend(get_best_keywords("MASTER_API_DATA.csv", t.strip()))
    
    # فاز سوم: ساخت سئو نهایی با دیتای واقعی
    final_prompt = f"""
    You are an Etsy SEO Master.
    Product: {p_type}
    Visual Context: {vision_res.text}
    Data-Back Keywords (from CSV): {csv_keywords}
    
    # OBJECTIVE:
    Create a high-converting Etsy listing.
    
    # CONSTRAINTS:
    - MODE: {'Samsung Frame TV (16:9 ratio, no prints/physical)' if p_type == 'Art for frame TV' else 'Printable Wall Art'}
    - TITLE: Strategic, under 100 chars, Title Case.
    - TAGS: 13 tags, max 20 chars, use the CSV keywords heavily.
    - DESCRIPTION: Under 400 chars, emotional and descriptive.
    
    Output JSON ONLY:
    {{
        "Title": "...",
        "Tags": ["...", "..."],
        "Description": "...",
        "Attributes": {{"Color": "...", "Style": "...", "Subject": "...", "Room": "...", "Occasion": "...", "Celebration": "..."}}
    }}
    """
    
    response = model.generate_content([final_prompt, img])
    return json.loads(response.text.replace('```json', '').replace('```', '').strip())

# ==========================================
# 4. MAIN APP INTERFACE
# ==========================================
st.title("🚀 AtlasRank Pro")

if 'auth' not in st.session_state:
    if st.button("Start SEO Journey"):
        st.session_state['auth'] = True
        st.rerun()

else:
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not st.session_state.get('generated'):
        p_type = st.radio("Choose Mode:", ["Art for frame TV", "Printable Wall Art"], horizontal=True)
        u_desc = st.text_area("Anything special about this art?", placeholder="e.g. It's for a modern nursery...")
        uploaded_file = st.file_uploader("Upload Art Image", type=["jpg", "png", "jpeg"])

        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, use_container_width=True)

            # دکمه با منطق لودینگ و غیرفعال‌سازی
            if st.button("Generate Professional SEO", disabled=st.session_state.get('loading', False)):
                st.session_state['loading'] = True
                st.rerun()

            if st.session_state.get('loading'):
                with st.spinner(""): # لودینگ بدون متن
                    try:
                        result = generate_seo_pro(img, p_type, u_desc, api_key)
                        st.session_state['data'] = result
                        st.session_state['generated'] = True
                        st.session_state['loading'] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Something went wrong. Please try again.")
                        st.session_state['loading'] = False

    else:
        # نمایش نتایج نهایی
        data = st.session_state['data']
        st.success("✨ Your Optimized SEO is Ready!")
        
        st.subheader("📌 Title")
        st.code(data['Title'])
        
        st.subheader("🏷️ 13 SEO Tags")
        st.write(" | ".join(data['Tags']))
        
        st.subheader("📝 Description")
        st.info(data['Description'])
        
        if st.button("Analyze Another Image"):
            st.session_state['generated'] = False
            st.session_state['data'] = None
            st.rerun()
