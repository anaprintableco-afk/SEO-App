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
        .result-box { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state['auth'] = False

# ==========================================
# 2. CSV Loader
# ==========================================
def load_csv_keywords():
    try:
        df = pd.read_csv("MASTER_API_DATA.csv")
        # فرض میکنیم اسم ستون Keyword است
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
        st.rerun()

    st.title("🛠️ AI SEO Optimizer")
    st.info("Upload image -> Process with CSV -> Validate Etsy Rules.")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    
    up = st.file_uploader("Upload Product Photo", type=["jpg", "png", "jpeg"])
    
    if up:
        img = Image.open(up)
        st.image(img, width=300)
        
        if st.button("Generate Optimized Listing"):
            with st.spinner("Applying strict Etsy Handbook rules..."):
                try:
                    csv_data = load_csv_keywords()
                    model = genai.GenerativeModel('models/gemini-2.5-flash')
                    
                    # پرامپت طلایی شما + خروجی جیسون
                    prompt = f"""
                    # IDENTITY & AUTHORITY
                    You are the Core SEO Engine of an automated Etsy listing service. Your primary mission is to transform user inputs into high-converting, SEO-optimized listings.

                    # ETSY SELLER HANDBOOK RULES (UPDATED CRITICAL GUIDELINES):
                    1. TITLE NEW GUIDELINES: 
                       - Write clear, scannable titles (preferably under 15 words).
                       - NEVER repeat words or phrases in the title. State what the item is EXACTLY ONCE.
                       - REMOVE all subjective words (e.g., "beautiful", "perfect") and gifting phrases (e.g., "gift for him").
                       - Put the most important traits (color, material, style) at the very beginning.
                    2. TAGGING RULES:
                       - NO SINGLE-WORD TAGS. All 13 tags MUST be multi-word long-tail phrases.
                       - STRICT 20-CHARACTER LIMIT: You MUST count characters. Tags cannot exceed 20 characters.
                       - DIVERSIFY: Do not repeat the same root word (e.g., if you use "octopus print", do not use "octopus art").
                    3. DESCRIPTION RULES:
                       - The first sentence MUST clearly describe the item using a natural, human-sounding voice. NEVER just copy/paste the title into the first line.

                    # OPERATIONAL PROTOCOL
                    1. CSV ANALYSIS: Analyze the provided CSV Opportunity Score below. Prioritize these high-opportunity keywords BUT ensure they fit the 20-character limit and are NOT single words.
                    2. IMAGE RECOGNITION: Strictly describe only what is visible in the uploaded image.

                    # CSV DATA (Opportunity Keywords):
                    [{csv_data}]

                    # ATTRIBUTE REPOSITORY (STRICT USE ONLY)
                    - COLORS: Beige, Black, Blue, Bronze, Brown, Clear, Copper, Gold, Grey, Green, Orange, Pink, Purple, Rainbow, Red, Rose gold, Silver, White, Yellow
                    - HOME STYLE: Art deco, Art nouveau, Bohemian & eclectic, Coastal & tropical, Contemporary, Country & farmhouse, Gothic, Industrial & utility, Lodge, Mid-century, Minimalist, Rustic & primitive, Southwestern, Victorian
                    - SUBJECT: Abstract, Animal, Architecture, Astronomy, Botanical, Coastal, Fantasy, Floral, Food & drink, Geometric, Landscape, Minimalist, Nautical, People, Quote & saying, Still life, Transportation
                    - ROOMS (Pick 5): Bathroom, Bedroom, Dorm, Entryway, Game room, Kids, Kitchen & dining, Laundry, Living room, Nursery, Office

                    # OUTPUT STRUCTURE (JSON FORMAT REQUIRED)
                    Return the output ONLY as a valid JSON object. No markdown, no extra text. Use these exact keys:
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

                    # QUALITY CONTROL LOCKS
                    - No emojis, no conversational fillers.
                    - Titles < 100 characters, no word repetition.
                    """
                    
                    response = model.generate_content([prompt, img])
                    
                    # تمیز کردن خروجی برای خواندن جیسون
                    raw_text = response.text.replace('```json', '').replace('```', '').strip()
                    data = json.loads(raw_text)
                    
                    st.success("✅ SEO Generated Successfully!")
                    
                    # ==========================================
                    # نمایش در باکس‌های مجزا
                    # ==========================================
                    st.markdown("<div class='box-title'>📌 Optimized Title</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='result-box'>{data.get('Title', '')}</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div class='box-title'>🏷️ 13 SEO Tags</div>", unsafe_allow_html=True)
                    tags = data.get('Tags', [])
                    st.markdown(f"<div class='result-box'>{', '.join(tags)}</div>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("<div class='box-title'>⚙️ Item Attributes</div>", unsafe_allow_html=True)
                        st.json(data.get('Attributes', {}))
                    with col2:
                        st.markdown("<div class='box-title'>🖼️ Alt Texts (10 lines)</div>", unsafe_allow_html=True)
                        alts = data.get('AltTexts', [])
                        for i, alt in enumerate(alts, 1):
                            st.write(f"{i}. {alt}")
                            
                    st.markdown("<div class='box-title'>📝 Product Description</div>", unsafe_allow_html=True)
                    st.text_area("", value=data.get('Description', ''), height=200, label_visibility="collapsed")
                    
                    st.balloons()
                    
                except json.JSONDecodeError:
                    st.error("JSON Error: The AI format was incorrect. Raw output:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")
