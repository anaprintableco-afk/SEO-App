import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
import time

# ==========================================
# 1. UI & Styling
# ==========================================
st.set_page_config(page_title="AtlasRank | Pro SEO Engine", layout="wide")

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
# 2. Strict Allowed Lists (The Master Database)
# ==========================================
ALLOWED_COLORS = ["Beige", "Black", "Blue", "Bronze", "Brown", "Clear", "Copper", "Gold", "Grey", "Green", "Orange", "Pink", "Purple", "Rainbow", "Red", "Rose gold", "Silver", "White", "Yellow"]
ALLOWED_STYLES = ["Art deco", "Art nouveau", "Bohemian & eclectic", "Coastal & tropical", "Contemporary", "Country & farmhouse", "Gothic", "Industrial & utility", "Lodge", "Mid-century", "Minimalist", "Rustic & primitive", "Southwestern", "Victorian"]
ALLOWED_CELEBS = ["Christmas", "Cinco de Mayo", "Dia de los Muertos", "Diwali", "Easter", "Eid", "Father's Day", "Halloween", "Hanukkah", "Holi", "Independence Day", "Kwanzaa", "Lunar New Year", "Mardi Gras", "Mother's Day", "New Year's", "Passover", "Ramadan", "St Patrick's Day", "Thanksgiving", "Valentine's Day", "Veterans Day"]
ALLOWED_OCCASIONS = ["1st birthday", "Anniversary", "Baby shower", "Stag party", "Hen party", "Back to school", "Baptism", "Bar & Bat Mitzvah", "Birthday", "Bridal shower", "Confirmation", "Divorce & breakup", "Engagement", "First Communion", "Graduation", "Grief & mourning", "Housewarming", "LGBTQ pride", "Moving", "Pet loss", "Retirement", "Wedding"]
ALLOWED_SUBJECTS = [
    "Abstract & geometric", "Animal", "Anime & cartoon", "Architecture & cityscape", 
    "Beach & tropical", "Bollywood", "Comics & manga", "Educational", "Fantasy & Sci Fi", 
    "Fashion", "Flowers", "Food & drink", "Geography & locale", "Horror & gothic", 
    "Humourous saying", "Inspirational saying", "Landscape & scenery", "LGBTQ pride", 
    "Love & friendship", "Military", "Film", "Music", "Nautical", "Nudes", 
    "Patriotic & flags", "People & portrait", "Pet portrait", "Phrase & saying", 
    "Plants & trees", "Religious", "Science & tech", "Sports & fitness", 
    "Stars & celestial", "Steampunk", "Superhero", "Travel & transportation", 
    "TV", "Typography & symbols", "Video game", "Western & cowboy", "Zodiac"
]
ALLOWED_ROOMS = ["Bathroom", "Bedroom", "Dorm", "Entryway", "Game room", "Kids", "Kitchen & dining", "Laundry", "Living room", "Nursery", "Office"]

# ==========================================
# 3. Database Uploader Logic
# ==========================================
@st.cache_resource(ttl=86400)
def get_or_upload_csv(_api_key):
    genai.configure(api_key=_api_key)
    try:
        if not os.path.exists("MASTER_API_DATA.csv"): return None
        csv_file = genai.upload_file(path="MASTER_API_DATA.csv", display_name="Master_Etsy_Database")
        while csv_file.state.name == "PROCESSING":
            time.sleep(1)
            csv_file = genai.get_file(csv_file.name)
        return csv_file
    except Exception:
        return None

# ==========================================
# 4. Core SEO Engine (One-Shot Self-Correction)
# ==========================================
def generate_seo_logic(img, p_type, desc, api_key, revision_request=""):
    csv_file = get_or_upload_csv(api_key)
    # تغییر مدل به نسخه لایت برای دور زدن محدودیت سقف صفر     model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
    
    if p_type == "Art for frame TV":
        mode_rules = """
        # MODE 1 — TV (Samsung Frame TV Only)
        PRODUCT DEFINITION: Digital download specifically for Samsung Frame TV display only. Do NOT mention printing, physical items, frames, posters, canvas, print sizes, or delivery.
        
        TITLE RULES (TV):
        - Under 100 characters total.
        - Buyer phrase first, then item type, then 2-3 objective descriptors.
        - Under 20 words (prefer under 15).
        - Avoid subjective words (perfect, beautiful, stunning).
        - No repeated words.
        - Every word MUST start with a capital letter (Title Case).
        - FORBIDDEN WORDS: "print", "printable", "poster", "canvas", "wall decor".
        
        DESCRIPTION RULES (TV):
        - Under 400 characters. Emotional but clear. No sales language.
        - Describe subject, colors, mood, atmosphere, visible details.
        - MUST include exactly this sentence once: "Digital download for Samsung Frame TV display in 16:9 ratio."
        - No shipping. No printing. No guarantees.
        """
    else:
        mode_rules = """
        # MODE 2 — PRINTABLE (Buyer Prints)
        PRODUCT DEFINITION: Digital download / printable only. Do NOT mention physical shipping, printed items, frames, posters, canvas, or delivery.
        
        TITLE RULES (PRINTABLE):
        - Under 100 characters total.
        - MUST include exactly ONE of these phrases (choose only one): printable OR digital download OR instant download.
        - Buyer phrase first, then item type, then 2-3 objective descriptors.
        - Under 20 words (prefer under 15).
        - Avoid subjective words (perfect, beautiful, stunning).
        - No repeated words.
        - Every word MUST start with a capital letter (Title Case).
        
        DESCRIPTION RULES (PRINTABLE):
        - Under 400 characters. Emotional but clear. No sales language.
        - Describe subject, colors, mood, atmosphere, visible details.
        - No shipping. No guarantees.
        """

    base_prompt = f"""
    You are the Core SEO Engine.

    # USER INPUTS
    - Product Category: {p_type}
    - Custom Description: {desc if desc else 'None provided'}
    
    {mode_rules}

    # 📸 IMAGE CONTEXT EXTRACTION:
    - **ARTISTIC MEDIUM & STYLE:** Identify the exact medium (watercolor, line ink drawing, sketch, digital, etc.). Include all visible techniques.
    - **SEASON & LOCATION:** Identify any visible season, holiday, or location.

    # TAGGING RULES:
    - Exactly 13 tags. NO SINGLE-WORD TAGS. Max 20 chars per tag.
    - Scan the attached CSV file and prioritize exact matches for your tags.

    # STRICT ATTRIBUTES PROTOCOL (YOU MUST PICK FROM THESE EXACT LISTS ONLY)
    - 1st Main Color & 2nd Main Color: {ALLOWED_COLORS}
    - Home Style: {ALLOWED_STYLES}
    - Celebration: {ALLOWED_CELEBS}
    - Occasion: {ALLOWED_OCCASIONS}
    - Subject (Up to 3): {ALLOWED_SUBJECTS}
    - Room (Exactly 5): {ALLOWED_ROOMS}

    # OUTPUT STRUCTURE (CHAIN OF THOUGHT JSON)
    You MUST output ONLY a valid JSON object. 
    To ensure accuracy, you must first do an "Internal_Audit" before generating the "Final_SEO".
    Follow this EXACT structure:
    {{
        "Internal_Audit": {{
            "Step_1_Brainstorm": "Brainstorm tags and title based on image and CSV.",
            "Step_2_Forbidden_Check": "Did I use any forbidden words like 'print' for TV Mode? If yes, remove them.",
            "Step_3_Attribute_Check": "Are all selected attributes EXACTLY matching the provided allowed lists?"
        }},
        "Final_SEO": {{
            "Title": "...",
            "Description": "...",
            "AltTexts": ["...", "...", "...", "...", "..."],
            "Attributes": {{
                "1st Main Color": "...", "2nd Main Color": "...", "Home Style": "...",
                "Celebration": "...", "Occasion": "...", "Subject": ["..."], "Room": ["..."]
            }},
            "Tags": ["..."]
        }}
    }}
    """
    
    if revision_request:
        base_prompt += f"\n# REVISION REQUEST: {revision_request}\n"

    contents = [base_prompt, img]
    if csv_file: contents.append(csv_file)
        
    response = model.generate_content(contents)
    raw_text = response.text.replace('```json', '').replace('```', '').strip()
    
    try:
        full_data = json.loads(raw_text)
        # فقط بخش نهایی سئو را برمی‌گردانیم تا در ظاهر سایت نمایش داده شود
        return full_data.get("Final_SEO", full_data)
    except Exception as e:
        raise Exception("Failed to parse AI output. AI format was incorrect.")

# ==========================================
# 5. Main Dashboard
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
    if not api_key: st.stop()
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
                with st.spinner("Atlas AI is generating and performing internal audit..."):
                    try:
                        st.session_state['generated_data'] = generate_seo_logic(img, p_type, u_desc, api_key)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    else:
        data = st.session_state['generated_data']
        if st.session_state['current_image']: st.image(st.session_state['current_image'], width=150)
            
        st.success("✅ SEO Generated & Audited Successfully!")
        st.markdown("---")
        
        title_val = data.get('Title', '')
        st.markdown(f"<div class='box-title'>📌 Optimized Title</div>", unsafe_allow_html=True)
        st.text_area(f"Length: {len(title_val)} chars (Limit: 100)", value=title_val, height=68)
        
        st.markdown("<div class='box-title'>🏷️ 13 SEO Tags</div>", unsafe_allow_html=True)
        tags_list = data.get('Tags', [])
        tags_with_counts = [f"{t} ({len(t)})" for t in tags_list]
        st.info(" | ".join(tags_with_counts))
        st.text_area("Copy Tags:", value=", ".join(tags_list), height=68)
        
        st.markdown("<div class='box-title'>⚙️ Item Attributes</div>", unsafe_allow_html=True)
        attr_cols = st.columns(3)
        col_idx = 0
        for key, val in data.get('Attributes', {}).items():
            with attr_cols[col_idx % 3]:
                display_val = ", ".join([str(v) for v in val]) if isinstance(val, list) else str(val)
                st.text_area(key, value=display_val, height=68)
            col_idx += 1
            
        st.markdown("<div class='box-title'>📝 Product Description</div>", unsafe_allow_html=True)
        desc_val = data.get('Description', '')
        st.text_area(f"Length: {len(desc_val)} chars (Limit: 400)", value=desc_val, height=200)

        st.markdown("<div class='box-title'>🖼️ Alt Texts (5 Options)</div>", unsafe_allow_html=True)
        alts = data.get('AltTexts', [])
        st.text_area("Select one:", value="\n".join([f"{i+1}. {alt}" for i, alt in enumerate(alts)]), height=150)

        st.markdown("---")
        st.markdown("<div class='box-title'>🔄 Revision & Actions</div>", unsafe_allow_html=True)
        rev_text = st.text_area("Request changes...", height=68)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✨ Apply Changes"):
                with st.spinner("Applying revisions..."):
                    try:
                        st.session_state['generated_data'] = generate_seo_logic(st.session_state['current_image'], st.session_state['product_type'], st.session_state['user_desc'], api_key, rev_text)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        with c2:
            if st.button("🗑️ Start Over"):
                st.session_state['generated_data'] = None
                st.session_state['current_image'] = None
                st.rerun()
