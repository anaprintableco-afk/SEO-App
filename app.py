import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import os

# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(page_title="AtlasRank | Etsy SEO Engine", layout="centered")

# ==========================================
# Custom CSS for Noto Font and Minimalist UI
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Display:wght@300;400;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Noto Sans Display', sans-serif !important;
        }
        
        .stTextArea textarea {
            font-size: 16px !important;
            line-height: 1.5 !important;
            border-radius: 8px !important;
        }
        
        h1, h2, h3 {
            font-weight: 600 !important;
            letter-spacing: -0.5px !important;
            color: #1E1E1E;
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            height: 3em;
            background-color: #FF5A1F;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# API Key Configuration (Fixed for Render)
# ==========================================
# اولویت با GEMINI_API_KEY است که در پنل رندر ست کردی
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("🔑 API Key not found! Please add GEMINI_API_KEY to Render Environment Variables.")
    st.stop()

# ==========================================
# User Interface (UI)
# ==========================================
st.title("🚀 AtlasRank SEO Engine")
st.markdown("Automated Etsy Listing Service by **Atlas Creative House**")
st.markdown("---")

product_mode = st.radio(
    "Select Product Mode:",
    ["Printable (Digital Download)", "Frame TV Art (Digital Display)"],
    horizontal=True
)

uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image Preview", width=300)
    
    if st.button("Generate Optimized SEO"):
        with st.spinner("Atlas AI is analyzing image and keywords..."):
            try:
                # Load CSV Data
                df = pd.read_csv('MASTER_API_DATA.csv')
                df['Avg_Searches'] = pd.to_numeric(df['Avg_Searches'], errors='coerce').fillna(0)
                df['Competition'] = pd.to_numeric(df['Competition'], errors='coerce').fillna(1)
                df['Opportunity'] = df['Avg_Searches'] / df['Competition']
                
                top_keywords = df.sort_values(by='Opportunity', ascending=False).head(100)['Keyword'].tolist()
                csv_context = ", ".join(str(x) for x in top_keywords)
                
                if "TV" in product_mode:
                    mode_instruction = '- MODE 1 (TV): Focus on "Digital Display". Prohibited words: print, paper, shipping, canvas, poster.'
                else:
                    mode_instruction = '- MODE 2 (Printable): Focus on "Digital Download". Use multi-word phrases like "printable wall art" or "instant download art". (NEVER use single words like "printable" or "art").'

                prompt = f"""
                You are AtlasRank AI, the core SEO Engine of Atlas Creative House. 
                Your mission: Transform image and keywords into a high-converting Etsy listing.

                # ETSY SELLER HANDBOOK RULES:
                1. TITLE: Clear, scannable, under 15 words. NO repetition. NO subjective words (beautiful, gift for her).
                2. TAGS: Exactly 13 tags. ALL must be multi-word (long-tail). STRICT 20-character limit per tag.
                3. DESCRIPTION: First sentence must be a natural, human-sounding description of the item.

                # MODE-SPECIFIC LOGIC:
                {mode_instruction}

                # TOP OPPORTUNITY KEYWORDS (Use these if they fit the image):
                [{csv_context}]

                # ATTRIBUTE REPOSITORY:
                - COLORS: Beige, Black, Blue, Bronze, Brown, Clear, Copper, Gold, Grey, Green, Orange, Pink, Purple, Rainbow, Red, Rose gold, Silver, White, Yellow
                - HOME STYLE: Art deco, Art nouveau, Bohemian & eclectic, Coastal & tropical, Contemporary, Country & farmhouse, Gothic, Industrial & utility, Lodge, Mid-century, Minimalist, Rustic & primitive, Southwestern, Victorian
                - SUBJECT: Abstract, Animal, Architecture, Astronomy, Botanical, Coastal, Fantasy, Floral, Food & drink, Geometric, Landscape, Minimalist, Nautical, People, Quote & saying, Still life, Transportation
                - ROOMS (Pick 5): Bathroom, Bedroom, Dorm, Entryway, Game room, Kids, Kitchen & dining, Laundry, Living room, Nursery, Office
                - CELEBRATION (Pick 1): Christmas, Easter, Halloween, Mother's Day, Valentine's Day, Thanksgiving, Father's Day, Independence Day
                - OCCASION (Pick 1): Anniversary, Birthday, Graduation, Housewarming, Wedding, Baby Shower, Bridal Shower, Engagement

                # OUTPUT FORMAT (STRICT):
                Title: [Text]
                Description: [Text]
                Alt Texts: [10 sentences]
                1st Main Color: [Value]
                2nd Main Color: [Value]
                Home Style: [Value]
                Celebration: [Value]
                Occasion: [Value]
                Subject: [Values]
                Room: [5 Values]
                Tags: [13 comma-separated phrases]
                """
                
                # Using Stable Model Version
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content([prompt, image])
                raw_text = response.text
                
                # Simple extraction logic
                st.success("SEO Generation Complete!")
                st.markdown("---")
                st.write(raw_text) # نمایش مستقیم خروجی برای اطمینان از عملکرد

            except Exception as e:
                st.error(f"An error occurred: {e}")
