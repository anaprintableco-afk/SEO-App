import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
import time

# ==========================================
# 1. UI & Styling (دقیقا همان ظاهر قبلی)
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

if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'generated_data' not in st.session_state: st.session_state['generated_data'] = None
if 'current_image' not in st.session_state: st.session_state['current_image'] = None
if 'product_type' not in st.session_state: st.session_state['product_type'] = ""
if 'user_desc' not in st.session_state: st.session_state['user_desc'] = ""

# ==========================================
# 2. Database Uploader Logic
# ==========================================
# این تابع فایل را فقط یک بار در روز در سرور گوگل آپلود می‌کند تا سرعت برنامه بالا بماند
@st.cache_resource(ttl=86400)
def get_or_upload_csv(_api_key):
    genai.configure(api_key=_api_key)
    try:
        if not os.path.exists("MASTER_API_DATA.csv"):
            return None
            
        csv_file = genai.upload_file(path="MASTER_API_DATA.csv", display_name="Master_Etsy_Database")
        while csv_file.state.name == "PROCESSING":
            time.sleep(1)
            csv_file = genai.get_file(csv_file.name)
        return csv_file
    except Exception:
        return None

# ==========================================
# 3. Core SEO Engine (لاجیک جدید و هوشمند)
# ==========================================
def generate_seo_logic(img, p_type, desc, api_key, revision_request=""):
    csv_file = get_or_upload_csv(api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt = f"""
    # IDENTITY & AUTHORITY
    You are the Core SEO Engine of an automated Etsy listing service. 

    # USER INPUTS
    - Product Category: {p_type}
    - Seller's Custom Description: {desc if desc else 'None provided'}
    """
    
    if revision_request:
        prompt += f"\n# REVISION REQUEST\nThe user requested these changes: '{revision_request}'. Apply them carefully.\n"

    prompt += f"""
    # DATABASE MAPPING WORKFLOW (CRITICAL)
    I have attached our entire Master Keywords Database (CSV). You MUST follow this exact thought process for Title and Tags:
    1. IMAGE FIRST: Analyze the visual elements of the image. What is it?
    2. BRAINSTORM: Think of natural describing keywords (e.g., "farmhouse art").
    3. DATABASE SCAN: You MUST scan the attached CSV to find the closest, highest-converting matches for your brainstormed words. 
       - EXAMPLE: If you see a farmhouse style painting, you might think of "farmhouse art". BUT, if you check the CSV and see "farmhouse wall art", you MUST output "farmhouse wall art" instead.
    4. RELEVANCE: ONLY use keywords from the CSV that genuinely match the image. Do not use unrelated words just because they are in the database.

    # ETSY SELLER HANDBOOK RULES:
    1. TITLE: Clear, scannable (under 15 words). NO repetitions. Most important CSV-matched traits first.
    2. TAGS: 13 tags. NO SINGLE-WORD TAGS. Max 20 chars per tag. Use CSV-matched phrases heavily.
    3. DESCRIPTION: First sentence must clearly describe the item naturally.

    # ATTRIBUTES (MUST FILL EVERY SINGLE FIELD)
    - 1st Main Color
    - 2nd Main Color
    - Home Style
    - Subject (Pick up to 3)
    - Room (Pick up to 5)
    - Celebration (or "Not Applicable")
    - Occasion (or "Not Applicable")

    # OUTPUT STRUCTURE (JSON FORMAT REQUIRED)
    Return ONLY a valid JSON object:
    {{
        "Title": "...",
        "Description": "...",
        "AltTexts": ["...", "...", "...", "...", "...", "...", "...", "...", "...", "..."],
        "Attributes": {{
            "1st Main Color": "...", "2nd Main Color": "...", "Home Style": "...",
            "Celebration": "...", "Occasion": "...", "Subject": "...", "Room": "..."
        }},
        "Tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13"]
    }}
    """
    
    # ارسال همزمان پرامپت، عکس و فایل دیتابیس به مغز هوش مصنوعی
    contents = [prompt, img]
    if csv_file:
        contents.append(csv_file)
        
    response = model.generate_content(contents)
    raw_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(raw_text)

# ==========================================
# 4. Main Dashboard (UI قبلی حفظ شد)
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
                st.session_state['current_image'] = img
                st.session_state['product_type'] = p_type
                st.session_state['user_desc'] = u_desc
                
                with st.spinner("Atlas AI is scanning your database for the best keywords..."):
                    try:
                        data = generate_seo_logic(img, p_type, u_desc, api_key)
                        st.session_state['generated_data'] = data
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    else:
        data = st.session_state['generated_data']
        
        if st.session_state['current_image']:
            st.image(st.session_state['current_image'], width=150, caption="Analyzed Image")
            
        st.success("✅ SEO Generated & Database-Optimized!")
        st.markdown("---")
        
        title_val = data.get('Title', '')
        st.markdown(f"<div class='box-title'>📌 Optimized Title</div>", unsafe_allow_html=True)
        st.text_area(f"Length: {len(title_val)} chars", value=title_val, height=68)
        
        st.markdown("<div class='box-title'>🏷️ 13 SEO Tags</div>", unsafe_allow_html=True)
        tags_list = data.get('Tags', [])
        tags_with_counts = [f"{t} ({len(t)})" for t in tags_list]
        st.info(" | ".join(tags_with_counts))
        st.text_area("Copy Tags (Comma separated):", value=", ".join(tags_list), height=68)
        
        st.markdown("<div class='box-title'>⚙️ Item Attributes</div>", unsafe_allow_html=True)
        attr_cols = st.columns(3)
        col_idx = 0
        for key, val in data.get('Attributes', {}).items():
            with attr_cols[col_idx % 3]:
                display_val = ", ".join([str(v) for v in val]) if isinstance(val, list) else str(val)
                st.text_area(key, value=display_val, height=68, key=f"attr_{key}")
            col_idx += 1
            
        st.markdown("<div class='box-title'>🖼️ Alt Texts (10 Options)</div>", unsafe_allow_html=True)
        alts = data.get('AltTexts', [])
        alt_text_str = "\n".join([f"{i+1}. {alt}" for i, alt in enumerate(alts)])
        st.text_area("Select and copy one:", value=alt_text_str, height=250)
            
        st.markdown("<div class='box-title'>📝 Product Description</div>", unsafe_allow_html=True)
        st.text_area("Description:", value=data.get('Description', ''), height=300)

        st.markdown("---")
        
        # بخش Revision و Start Over
        st.markdown("<div class='box-title'>🔄 Revision & New Actions</div>", unsafe_allow_html=True)
        revision_text = st.text_area("Not satisfied? Tell AI what to change (e.g., 'Make it more romantic', 'Change colors to red')", height=68)
        
        col_rev1, col_rev2 = st.columns(2)
        with col_rev1:
            if st.button("✨ Apply Changes & Regenerate"):
                with st.spinner("Applying your revisions and rescanning database..."):
                    try:
                        new_data = generate_seo_logic(
                            st.session_state['current_image'], 
                            st.session_state['product_type'], 
                            st.session_state['user_desc'], 
                            api_key,
                            revision_request=revision_text
                        )
                        st.session_state['generated_data'] = new_data
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
        with col_rev2:
            if st.button("🗑️ Start Over (Upload New Image)"):
                st.session_state['generated_data'] = None
                st.session_state['current_image'] = None
                st.session_state['product_type'] = ""
                st.session_state['user_desc'] = ""
                st.rerun()
