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
# 4. Core SEO Engine (With Validation Loop)
# ==========================================
def generate_seo_logic(img, p_type, desc, api_key, revision_request=""):
    csv_file = get_or_upload_csv(api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
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

    # 📸 IMAGE CONTEXT EXTRACTION (CRITICAL):
    - **ARTISTIC MEDIUM & STYLE:** Carefully examine the image to identify its EXACT artistic medium and style (whatever it may be: watercolor, oil painting, pencil sketch, line ink drawing, digital illustration, photography, vintage etching, etc.). You MUST explicitly include the accurately identified medium/style in your tags and description. If it uses multiple techniques, mention all of them. Do not use generic terms if a specific technique is visible.
    - **SEASON & LOCATION:** Identify any visible season, holiday, or location and include them.

    # TAGGING RULES (CRITICAL):
    - Exactly 13 tags. NO SINGLE-WORD TAGS. Max 20 chars per tag.
    - If seasonal/holiday elements are VISIBLE in the image, include them heavily.
    - Scan the attached CSV file and prioritize exact matches for your tags.

    # STRICT ATTRIBUTES PROTOCOL (YOU MUST PICK FROM THESE EXACT LISTS ONLY)
    You are FORCED to select attributes. "Not Applicable" or blank is FORBIDDEN. Guess the closest match if unsure.
    - 1st Main Color: Choose exactly 1 from {ALLOWED_COLORS}
    - 2nd Main Color: Choose exactly 1 from {ALLOWED_COLORS}
    - Home Style: Choose exactly 1 from {ALLOWED_STYLES}
    - Celebration: Choose exactly 1 from {ALLOWED_CELEBS}. YOU MUST PICK ONE.
    - Occasion: Choose exactly 1 from {ALLOWED_OCCASIONS}. YOU MUST PICK ONE.
    - Subject: Choose up to 3 ONLY from {ALLOWED_SUBJECTS}
    - Room: Choose exactly 5 ONLY from {ALLOWED_ROOMS}

    # OUTPUT STRUCTURE (JSON)
    Return ONLY a valid JSON object with exactly 5 AltTexts:
    {{
        "Title": "...",
        "Description": "...",
        "AltTexts": ["...", "...", "...", "...", "..."],
        "Attributes": {{
            "1st Main Color": "...", "2nd Main Color": "...", "Home Style": "...",
            "Celebration": "...", "Occasion": "...", "Subject": ["..."], "Room": ["..."]
        }},
        "Tags": ["..."]
    }}
    """
    
    if revision_request:
        base_prompt += f"\n# REVISION REQUEST: {revision_request}\n"

    max_retries = 3
    current_prompt = base_prompt
    
    for attempt in range(max_retries):
        contents = [current_prompt, img]
        if csv_file: contents.append(csv_file)
            
        response = model.generate_content(contents)
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(raw_text)
        
        errors = []
        attrs = data.get("Attributes", {})
        
        if attrs.get("1st Main Color") not in ALLOWED_COLORS: errors.append(f"1st Main Color '{attrs.get('1st Main Color')}' is not in list.")
        if attrs.get("2nd Main Color") not in ALLOWED_COLORS: errors.append(f"2nd Main Color '{attrs.get('2nd Main Color')}' is not in list.")
        if attrs.get("Home Style") not in ALLOWED_STYLES: errors.append(f"Home Style '{attrs.get('Home Style')}' is not in list.")
        if attrs.get("Celebration") not in ALLOWED_CELEBS: errors.append(f"Celebration '{attrs.get('Celebration')}' is not in list. You MUST pick one.")
        if attrs.get("Occasion") not in ALLOWED_OCCASIONS: errors.append(f"Occasion '{attrs.get('Occasion')}' is not in list. You MUST pick one.")
        
        subjs = attrs.get("Subject", [])
        if isinstance(subjs, str): subjs = [subjs]
        for s in subjs:
            if s not in ALLOWED_SUBJECTS: errors.append(f"Subject '{s}' is not allowed.")
            
        rooms = attrs.get("Room", [])
        if isinstance(rooms, str): rooms = [rooms]
        for r in rooms:
            if r not in ALLOWED_ROOMS: errors.append(f"Room '{r}' is not allowed.")

        if not errors:
            return data
            
        st.toast(f"Checking AI compliance (Attempt {attempt+1})... Correcting attributes.")
        current_prompt = base_prompt + "\n\nCRITICAL ERROR IN PREVIOUS ATTEMPT:\nYou used invalid attributes. Fix these errors immediately by strictly choosing from the provided lists:\n" + "\n".join(errors)

    return data

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
                with st.spinner("Atlas AI is generating and validating Etsy rules..."):
                    try:
                        st.session_state['generated_data'] = generate_seo_logic(img, p_type, u_desc, api_key)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    else:
        data = st.session_state['generated_data']
        if st.session_state['current_image']: st.image(st.session_state['current_image'], width=150)
            
        st.success("✅ SEO Generated & Validated!")
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
                    st.session_state['generated_data'] = generate_seo_logic(st.session_state['current_image'], st.session_state['product_type'], st.session_state['user_desc'], api_key, rev_text)
                    st.rerun()
        with c2:
            if st.button("🗑️ Start Over"):
                st.session_state['generated_data'] = None
                st.session_state['current_image'] = None
                st.rerun()
