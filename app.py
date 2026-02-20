import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image

# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(page_title="Etsy Core SEO Engine", layout="centered")

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
        }
    </style>
""", unsafe_allow_html=True)

# API Key Configuration
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Error loading API Key. Please check your Secrets configuration.")
    st.stop()

# ==========================================
# User Interface (UI)
# ==========================================
st.title("Etsy Core SEO Engine")
st.markdown("Upload your product image, select the specific mode, and generate highly optimized, data-driven SEO listings.")

product_mode = st.radio(
    "Select Product Mode:",
    ["Printable (Digital Download)", "Frame TV Art (Digital Display)"],
    horizontal=True
)

st.markdown("---")

uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image Preview", width=300)
    
    if st.button("Generate SEO Data"):
        with st.spinner("Loading..."):
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
                # IDENTITY & AUTHORITY
                You are the Core SEO Engine of an automated Etsy listing service. Your primary mission is to transform user inputs into high-converting, SEO-optimized listings.

                # ETSY SELLER HANDBOOK RULES (CRITICAL - YOU MUST OBEY):
                1. NO SINGLE-WORD TAGS: NEVER use a single word as a tag. ALL 13 tags MUST be multi-word phrases.
                2. STRICT 20-CHARACTER LIMIT: You MUST physically count the characters of EVERY tag. A tag cannot exceed 20 characters (including spaces). 
                3. NO REPETITION STUFFING: Do not repeat the same root word in every tag. Mix your vocabulary.
                4. ALT TEXTS FORMAT: You must provide exactly 10 alt texts, numbered strictly from 1 to 10.

                # OPERATIONAL PROTOCOL
                1. CSV ANALYSIS: Analyze the provided CSV Opportunity Score below. Prioritize these high-opportunity keywords BUT ensure they fit the 20-character limit and are NOT single words.
                2. IMAGE RECOGNITION: Strictly describe only what is visible in the uploaded image.

                # MODE-SPECIFIC LOGIC
                {mode_instruction}

                # CSV DATA (Opportunity Keywords):
                [{csv_context}]

                # ATTRIBUTE REPOSITORY (STRICT USE ONLY)
                - COLORS: Beige, Black, Blue, Bronze, Brown, Clear, Copper, Gold, Grey, Green, Orange, Pink, Purple, Rainbow, Red, Rose gold, Silver, White, Yellow
                - HOME STYLE: Art deco, Art nouveau, Bohemian & eclectic, Coastal & tropical, Contemporary, Country & farmhouse, Gothic, Industrial & utility, Lodge, Mid-century, Minimalist, Rustic & primitive, Southwestern, Victorian
                - SUBJECT: Abstract, Animal, Architecture, Astronomy, Botanical, Coastal, Fantasy, Floral, Food & drink, Geometric, Landscape, Minimalist, Nautical, People, Quote & saying, Still life, Transportation
                - ROOMS (Pick 5): Bathroom, Bedroom, Dorm, Entryway, Game room, Kids, Kitchen & dining, Laundry, Living room, Nursery, Office

                # OUTPUT STRUCTURE (COPY-PASTE READY)
                Return the output in this EXACT format. Use these exact headers so the system can parse them:
                Title: [Text]
                Description: [Text]
                Alt Texts:
                1. [Sentence]
                2. [Sentence]
                ...
                10. [Sentence]
                1st Main Color: [Value]
                2nd Main Color: [Value]
                Home Style: [Value]
                Celebration: [Value or Blank]
                Occasion: [Value or Blank]
                Subject: [Up to 3 Values]
                Room: [5 Values]
                Tags: [13 comma-separated phrases, NO single words, ALL under 20 chars]

                # QUALITY CONTROL LOCKS
                - No emojis, no conversational fillers.
                - Titles < 100 characters.
                - Descriptions < 400 characters.
                """
                
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content([prompt, image])
                raw_text = response.text
                
                def extract_section(text, current_header, next_header):
                    try:
                        start = text.index(current_header) + len(current_header)
                        if next_header:
                            end = text.index(next_header, start)
                            return text[start:end].strip()
                        else:
                            return text[start:].strip()
                    except ValueError:
                        return ""

                # Extracting initial data
                title = extract_section(raw_text, "Title:", "Description:")
                description = extract_section(raw_text, "Description:", "Alt Texts:")
                alt_texts = extract_section(raw_text, "Alt Texts:", "1st Main Color:")
                
                c1 = extract_section(raw_text, "1st Main Color:", "2nd Main Color:")
                c2 = extract_section(raw_text, "2nd Main Color:", "Home Style:")
                h_style = extract_section(raw_text, "Home Style:", "Celebration:")
                cel = extract_section(raw_text, "Celebration:", "Occasion:")
                occ = extract_section(raw_text, "Occasion:", "Subject:")
                subj = extract_section(raw_text, "Subject:", "Room:")
                room = extract_section(raw_text, "Room:", "Tags:")
                raw_tags = extract_section(raw_text, "Tags:", None)

                # ==========================================
                # SAFETY NET: PYTHON POST-PROCESSING (QUALITY CONTROL)
                # ==========================================
                
                # 1. Title Safety Check (<100 chars)
                if len(title) > 100:
                    title = title[:100].rsplit(' ', 1)[0] # Cuts at the last full word before 100 chars

                # 2. Tags Safety Check (Max 13 tags, Max 20 chars each)
                cleaned_tags_list = []
                raw_tags = raw_tags.replace('\n', '').replace('[', '').replace(']', '')
                parsed_tags = [t.strip() for t in raw_tags.split(',') if t.strip()]
                
                for t in parsed_tags:
                    if len(t) > 20:
                        # Try to keep words that fit under 20 chars
                        words = t.split()
                        fixed_tag = ""
                        for w in words:
                            if len(fixed_tag) + len(w) + (1 if fixed_tag else 0) <= 20:
                                fixed_tag += (" " + w if fixed_tag else w)
                        fixed_tag = fixed_tag.strip()
                        if not fixed_tag: # If a single word is somehow > 20 chars
                            fixed_tag = t[:20]
                        cleaned_tags_list.append(fixed_tag)
                    else:
                        cleaned_tags_list.append(t)
                
                # Enforce exactly 13 tags limit
                cleaned_tags_list = cleaned_tags_list[:13]
                final_tags = ", ".join(cleaned_tags_list)

                # ==========================================
                # Display Results in Large Text Areas
                # ==========================================
                st.success("SEO Data Extracted & Validated Successfully.")
                st.markdown("---")
                
                st.subheader(f"Title ({len(title)} chars)")
                st.text_area("Copy Title:", value=title, height=100, label_visibility="collapsed")
                
                st.subheader(f"Tags ({len(cleaned_tags_list)} Items - All under 20 chars)")
                st.text_area("Copy Tags:", value=final_tags, height=120, label_visibility="collapsed")
                
                st.subheader("Description")
                st.text_area("Copy Description:", value=description, height=300, label_visibility="collapsed")
                
                st.subheader("Alt Texts (1-10)")
                st.text_area("Copy Alt Texts:", value=alt_texts, height=250, label_visibility="collapsed")
                
                st.subheader("Attributes")
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("1st Main Color", value=c1)
                    st.text_input("Home Style", value=h_style)
                    st.text_input("Occasion", value=occ)
                    st.text_input("Room", value=room)
                with col2:
                    st.text_input("2nd Main Color", value=c2)
                    st.text_input("Celebration", value=cel)
                    st.text_input("Subject", value=subj)

            except Exception as e:
                st.error(f"An error occurred: {e}")
