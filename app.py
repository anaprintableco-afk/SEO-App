import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
import pandas as pd

# ==========================================
# 1. UI & Styling
# ==========================================
st.set_page_config(page_title="AtlasRank | Pro SEO", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        h1, h2, h3, p, span, label, div { color: #ffffff !important; }
        .stButton>button {
            width: 100%; border-radius: 8px;
            background: linear-gradient(90deg, #FF5A1F 0%, #FF8C00 100%);
            color: white !important; font-weight: bold; border: none; padding: 10px;
        }
        .stButton>button:hover { transform: scale(1.02); }
        .box-title { color: #FF5A1F !important; font-size: 1.2em; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
        .stTextArea textarea {
            background-color: #161b22 !important; color: #ffffff !important;
            border: 1px solid #30363d !important; border-radius: 8px !important;
        }
    </style>
""", unsafe_allow_html=True)

# مقداردهی اولیه متغیرهای سشن برای کنترل مراحل
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'generated_data' not in st.session_state: st.session_state['generated_data'] = None
if 'current_image' not in st.session_state: st.session_state['current_image'] = None
if 'product_type' not in st.session_state: st.session_state['product_type'] = ""
if 'user_desc' not in st.session_state: st.session_state['user_desc'] = ""

# ==========================================
# 2. Functions
# ==========================================
def load_csv_keywords():
    try:
        df = pd.read_csv("MASTER_API_DATA.csv")
        keywords = df['Keyword'].head(50).tolist()
        return ", ".join(str(k) for k in keywords)
    except Exception:
        return ""

def generate_seo_logic(img, p_type, desc, revision_request=""):
    csv_data = load_csv_keywords()
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt = f"""
    # IDENTITY & AUTHORITY
    You are the Core SEO Engine of an automated Etsy listing service. 

    # USER INPUTS
    - Product Category: {p_type}
    - Seller's Custom Description: {desc if desc else 'None provided'}
    """
    
    # اگر کاربر درخواست ویرایش داده بود، به پرامپت اضافه می‌شود
    if revision_request:
        prompt += f"\n# REVISION REQUEST (CRITICAL)\nThe user requested the following changes to the previous output: '{revision_request}'. Apply these changes while maintaining all previous Etsy rules.\n"

    prompt += f"""
    # ETSY SELLER HANDBOOK RULES:
    1. TITLE: Clear, scannable (under 15 words). NO repetitions. NO subjective words.
    2. TAGS: 13 tags. NO SINGLE-WORD TAGS. Max 20 chars per tag.
    3. DESCRIPTION: First sentence must clearly describe the item naturally.

    # ATTRIBUTES (CRITICAL RULE - MUST FILL EVERY SINGLE FIELD)
    - 1st Main Color
    - 2nd Main Color
    - Home Style
    - Subject (Pick up to 3)
    - Room (Pick up to 5)
    - Celebration (or "Not Applicable")
    - Occasion (or "Not Applicable")

    # CSV DATA:
    [{csv_data}]

    # OUTPUT STRUCTURE (JSON FORMAT REQUIRED)
    Return ONLY a valid JSON object:
    {{
        "Title": "...",
        "Description": "...",
        "AltTexts": ["...", "...", "...", "...", "...", "...", "...", "...", "...", "..."],
        "Attributes": {{
            "1st Main Color": "...",
            "2nd Main Color": "...",
            "Home Style": "...",
            "Celebration": "...",
            "Occasion": "...",
            "Subject": "...",
            "Room": "..."
        }},
        "Tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13"]
    }}
    """
    response = model.generate_content([prompt, img])
    raw_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(raw_text)

# ==========================================
# 3. Main Logic
# ==========================================
if not st.session_state['auth']:
    st.markdown("<br><br><h1 style='text-align: center; color: #FF5A1F !important;'>🚀 AtlasRank</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Enter Dashboard"):
            st.session_state['auth'] = True
            st.rerun()
else:
    st.sidebar.markdown("<h2>AtlasRank Pro</h2>", unsafe_allow_html=True)
    if st.sidebar.button("Logout"):
        st.session_state['auth'] = False
        st.session_state['generated_data'] = None
        st.session_state['current_image'] = None
        st.rerun()

    st.title("🛠️ AI SEO Optimizer")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🔑 API Key is missing!")
        st.stop()
    genai.configure(api_key=api_key)

    # -------------------------------------------------------------------
    # مرحله ۱: آپلود و تنظیمات (فقط وقتی نشان داده می‌شود که دیتایی تولید نشده باشد)
    # -------------------------------------------------------------------
    if not st.session_state['generated_data']:
        st.markdown("<div class='box-title'>1. Select Product Type</div>", unsafe_allow_html=True)
        p_type = st.radio("Product Type:", ["Art for frame TV", "Printable Wall Art"], horizontal=True, label_visibility="collapsed")
        
        st.markdown("<div class='box-title'>2. Describe Your Product (Optional)</div>", unsafe_allow_html=True)
        u_desc = st.text_area("Write anything about your product in any language...", height=80)
        
        st.markdown("<div class='box-title'>3. Upload Image</div>", unsafe_allow_html=True)
        up = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        
        if up:
            img = Image.open(up)
            st.image(img, width=250)
            
            if st.button("Analyze & Generate SEO"):
                # ذخیره مقادیر در سشن برای استفاده در آینده
                st.session_state['current_image'] = img
                st.session_state['product_type'] = p_type
                st.session_state['user_desc'] = u_desc
                
                with st.spinner("Atlas AI is crafting your masterpiece..."):
                    try:
                        data = generate_seo_logic(img, p_type, u_desc)
                        st.session_state['generated_data'] = data
                        st.rerun() # رفرش صفحه برای محو کردن بخش آپلود و نمایش نتایج
                    except Exception as e:
                        st.error(f"Error: {e}")

    # -------------------------------------------------------------------
    # مرحله ۲: نمایش نتایج، ویرایش و شروع مجدد (فقط وقتی دیتا موجود است)
    # -------------------------------------------------------------------
    else:
        data = st.session_state['generated_data']
        
        # نمایش عکس کوچک شده برای یادآوری
        if st.session_state['current_image']:
            st.image(st.session_state['current_image'], width=150, caption="Analyzed Image")
            
        st.success("✅ SEO Generated Successfully!")
        st.markdown("---")
        
        # 1. تایتل
        title_val = data.get('Title', '')
        st.markdown(f"<div class='box-title'>📌 Optimized Title</div>", unsafe_allow_html=True)
        st.text_area(f"Length: {len(title_val)} chars", value=title_val, height=68)
        
        # 2. تگ‌ها
        st.markdown("<div class='box-title'>🏷️ 13 SEO Tags</div>", unsafe_allow_html=True)
        tags_list = data.get('Tags', [])
        tags_with_counts = [f"{t} ({len(t)})" for t in tags_list]
        st.info(" | ".join(tags_with_counts))
        st.text_area("Copy Tags (Comma separated):", value=", ".join(tags_list), height=68)
        
        # 3. اتریبیوت‌ها (حل مشکل لیست‌ها و داینامیک شدن باکس‌ها)
        st.markdown("<div class='box-title'>⚙️ Item Attributes</div>", unsafe_allow_html=True)
        attr_cols = st.columns(3)
        col_idx = 0
        for key, val in data.get('Attributes', {}).items():
            with attr_cols[col_idx % 3]:
                # اگر ولیو یک لیست بود، آن را با کاما به هم می‌چسبانیم (حل مشکل سابجکت و اتاق‌ها)
                display_val = ", ".join([str(v) for v in val]) if isinstance(val, list) else str(val)
                # استفاده از text_area به جای text_input برای اینکه داینامیک شود و جا باز کند
                st.text_area(key, value=display_val, height=68, key=f"attr_{key}")
            col_idx += 1
            
        # 4. Alt Texts
        st.markdown("<div class='box-title'>🖼️ Alt Texts (10 Options)</div>", unsafe_allow_html=True)
        alts = data.get('AltTexts', [])
        alt_text_str = "\n".join([f"{i+1}. {alt}" for i, alt in enumerate(alts)])
        st.text_area("Select and copy one:", value=alt_text_str, height=250)
            
        # 5. توضیحات
        st.markdown("<div class='box-title'>📝 Product Description</div>", unsafe_allow_html=True)
        st.text_area("Description:", value=data.get('Description', ''), height=300)

        st.markdown("---")
        
        # -------------------------------------------------------------------
        # بخش درخواست تغییرات و دکمه‌های کنترل
        # -------------------------------------------------------------------
        st.markdown("<div class='box-title'>🔄 Revision & New Actions</div>", unsafe_allow_html=True)
        revision_text = st.text_area("Not satisfied? Tell AI what to change (e.g., 'Make it more romantic', 'Change colors to red')", height=68)
        
        col_rev1, col_rev2 = st.columns(2)
        with col_rev1:
            if st.button("✨ Apply Changes & Regenerate"):
                with st.spinner("Applying your revisions..."):
                    try:
                        # ارسال مجدد به هوش مصنوعی همراه با درخواست تغییرات کاربر
                        new_data = generate_seo_logic(
                            st.session_state['current_image'], 
                            st.session_state['product_type'], 
                            st.session_state['user_desc'], 
                            revision_request=revision_text
                        )
                        st.session_state['generated_data'] = new_data
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
        with col_rev2:
            if st.button("🗑️ Start Over (Upload New Image)"):
                # پاک کردن اطلاعات قبلی برای آپلود عکس جدید
                st.session_state['generated_data'] = None
                st.session_state['current_image'] = None
                st.session_state['product_type'] = ""
                st.session_state['user_desc'] = ""
                st.rerun()
