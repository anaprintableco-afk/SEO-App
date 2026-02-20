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
        .box-title { color: #FF5A1F !important; font-size: 1.2em; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
        .stTextArea textarea, .stTextInput input {
            background-color: #161b22 !important; color: #ffffff !important;
            border: 1px solid #30363d !important; border-radius: 8px !important;
        }
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'generated_data' not in st.session_state: st.session_state['generated_data'] = None

# ==========================================
# 2. CSV Loader
# ==========================================
def load_csv_keywords():
    try:
        df = pd.read_csv("MASTER_API_DATA.csv")
        keywords = df['Keyword'].head(50).tolist()
        return ", ".join(str(k) for k in keywords)
    except Exception:
        return ""

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
        st.rerun()

    st.title("🛠️ AI SEO Optimizer")
    
    st.markdown("<div class='box-title'>1. Select Product Type</div>", unsafe_allow_html=True)
    product_type = st.radio("Product Type:", ["Art for frame TV", "Printable Wall Art"], horizontal=True, label_visibility="collapsed")
    
    st.markdown("<div class='box-title'>2. Describe Your Product (Optional)</div>", unsafe_allow_html=True)
    user_desc = st.text_area("Write anything about your product in any language...", height=80)
    
    st.markdown("<div class='box-title'>3. Upload Image</div>", unsafe_allow_html=True)
    up = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    
    if up:
        img = Image.open(up)
        st.image(img, width=250)
        
        if st.button("Analyze & Generate SEO"):
            with st.spinner("Atlas AI is crafting your masterpiece..."):
                try:
                    csv_data = load_csv_keywords()
                    model = genai.GenerativeModel('models/gemini-2.5-flash')
                    
                    # پرامپت با دستورات سخت‌گیرانه برای فورس کردن اتریبیوت‌ها
                    prompt = f"""
                    # IDENTITY & AUTHORITY
                    You are the Core SEO Engine of an automated Etsy listing service. 

                    # USER INPUTS
                    - Product Category: {product_type}
                    - Seller's Custom Description: {user_desc if user_desc else 'None provided'}
                    
                    # ETSY SELLER HANDBOOK RULES:
                    1. TITLE: Clear, scannable (under 15 words). NO repetitions. NO subjective words. Most important traits first.
                    2. TAGS: 13 tags. NO SINGLE-WORD TAGS. Max 20 chars per tag. Do not repeat root words.
                    3. DESCRIPTION: First sentence must clearly describe the item naturally.

                    # ATTRIBUTES (CRITICAL RULE - YOU MUST FILL EVERY SINGLE FIELD)
                    You are FORCED to provide a value for EVERY attribute below. DO NOT leave any blank. If an exact match is hard, pick the closest logical option.
                    - 1st Main Color: Pick 1 from [Beige, Black, Blue, Bronze, Brown, Clear, Copper, Gold, Grey, Green, Orange, Pink, Purple, Rainbow, Red, Rose gold, Silver, White, Yellow]
                    - 2nd Main Color: Pick 1 from the colors list (must be different from 1st).
                    - Home Style: Pick 1 from [Art deco, Art nouveau, Bohemian, Coastal, Contemporary, Farmhouse, Gothic, Industrial, Lodge, Mid-century, Minimalist, Rustic, Southwestern, Victorian]
                    - Subject: Pick up to 3 from [Abstract, Animal, Architecture, Astronomy, Botanical, Coastal, Fantasy, Floral, Geometric, Landscape, Minimalist, Nautical, People, Quote, Still life]
                    - Room: Pick up to 5 from [Bathroom, Bedroom, Dorm, Entryway, Game room, Kids, Kitchen, Laundry, Living room, Nursery, Office]
                    - Celebration: Pick the most relevant celebration (e.g., Christmas, Halloween) OR write "Not Applicable".
                    - Occasion: Pick the most relevant occasion (e.g., Birthday, Housewarming) OR write "Not Applicable".

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
                    
                    st.session_state['generated_data'] = json.loads(raw_text)
                    st.success("✅ SEO Generated Successfully!")
                    
                except Exception as e:
                    st.error(f"Error: {e}")

    # -----------------------------------------
    # نمایش نتایج 
    # -----------------------------------------
    if st.session_state['generated_data']:
        data = st.session_state['generated_data']
        st.markdown("---")
        
        # 1. Title
        title_val = data.get('Title', '')
        st.markdown(f"<div class='box-title'>📌 Optimized Title</div>", unsafe_allow_html=True)
        st.text_area(f"Length: {len(title_val)} chars (Editable)", value=title_val, height=68)
        
        # 2. Tags
        st.markdown("<div class='box-title'>🏷️ 13 SEO Tags</div>", unsafe_allow_html=True)
        tags_list = data.get('Tags', [])
        tags_with_counts = [f"{t} ({len(t)})" for t in tags_list]
        st.info(" | ".join(tags_with_counts))
        st.text_area("Copy Tags (Comma separated):", value=", ".join(tags_list), height=68)
        
        # 3. Attributes (Forced)
        st.markdown("<div class='box-title'>⚙️ Item Attributes</div>", unsafe_allow_html=True)
        attr_cols = st.columns(3)
        col_idx = 0
        for key, val in data.get('Attributes', {}).items():
            with attr_cols[col_idx % 3]:
                st.text_input(key, value=val)
            col_idx += 1
            
        # 4. Alt Texts
        st.markdown("<div class='box-title'>🖼️ Alt Texts (10 Options)</div>", unsafe_allow_html=True)
        alts = data.get('AltTexts', [])
        alt_text_str = "\n".join([f"{i+1}. {alt}" for i, alt in enumerate(alts)])
        st.text_area("Select and copy one:", value=alt_text_str, height=250)
            
        # 5. Description
        st.markdown("<div class='box-title'>📝 Product Description</div>", unsafe_allow_html=True)
        st.text_area("Editable Description:", value=data.get('Description', ''), height=300)
