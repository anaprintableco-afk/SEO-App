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
        /* مخفی کردن متن لودینگ پیش‌فرض استریم‌لیت در صورت نیاز */
        .stSpinner > div { border-top-color: #FF5A1F !important; }
    </style>
""", unsafe_allow_html=True)

# مدیریت وضعیت‌ها
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'generated_data' not in st.session_state: st.session_state['generated_data'] = None
if 'current_image' not in st.session_state: st.session_state['current_image'] = None
if 'product_type' not in st.session_state: st.session_state['product_type'] = ""
if 'user_desc' not in st.session_state: st.session_state['user_desc'] = ""
if 'is_processing' not in st.session_state: st.session_state['is_processing'] = False

# ==========================================
# 2. Strict Allowed Lists
# ==========================================
ALLOWED_COLORS = ["Beige", "Black", "Blue", "Bronze", "Brown", "Clear", "Copper", "Gold", "Grey", "Green", "Orange", "Pink", "Purple", "Rainbow", "Red", "Rose gold", "Silver", "White", "Yellow"]
ALLOWED_STYLES = ["Art deco", "Art nouveau", "Bohemian & eclectic", "Coastal & tropical", "Contemporary", "Country & farmhouse", "Gothic", "Industrial & utility", "Lodge", "Mid-century", "Minimalist", "Rustic & primitive", "Southwestern", "Victorian"]
ALLOWED_CELEBS = ["Christmas", "Cinco de Mayo", "Dia de los Muertos", "Diwali", "Easter", "Eid", "Father's Day", "Halloween", "Hanukkah", "Holi", "Independence Day", "Kwanzaa", "Lunar New Year", "Mardi Gras", "Mother's Day", "New Year's", "Passover", "Ramadan", "St Patrick's Day", "Thanksgiving", "Valentine's Day", "Veterans Day"]
ALLOWED_OCCASIONS = ["1st birthday", "Anniversary", "Baby shower", "Stag party", "Hen party", "Back to school", "Baptism", "Bar & Bat Mitzvah", "Birthday", "Bridal shower", "Confirmation", "Divorce & breakup", "Engagement", "First Communion", "Graduation", "Grief & mourning", "Housewarming", "LGBTQ pride", "Moving", "Pet loss", "Retirement", "Wedding"]
ALLOWED_SUBJECTS = ["Abstract & geometric", "Animal", "Anime & cartoon", "Architecture & cityscape", "Beach & tropical", "Bollywood", "Comics & manga", "Educational", "Fantasy & Sci Fi", "Fashion", "Flowers", "Food & drink", "Geography & locale", "Horror & gothic", "Humourous saying", "Inspirational saying", "Landscape & scenery", "LGBTQ pride", "Love & friendship", "Military", "Film", "Music", "Nautical", "Nudes", "Patriotic & flags", "People & portrait", "Pet portrait", "Phrase & saying", "Plants & trees", "Religious", "Science & tech", "Sports & fitness", "Stars & celestial", "Steampunk", "Superhero", "Travel & transportation", "TV", "Typography & symbols", "Video game", "Western & cowboy", "Zodiac"]
ALLOWED_ROOMS = ["Bathroom", "Bedroom", "Dorm", "Entryway", "Game room", "Kids", "Kitchen & dining", "Laundry", "Living room", "Nursery", "Office"]

# ==========================================
# 3. Database Uploader
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
    except Exception: return None

# ==========================================
# 4. Core SEO Engine (Gemini 2.5 Flash)
# ==========================================
def generate_seo_logic(img, p_type, desc, api_key, revision_request=""):
    csv_file = get_or_upload_csv(api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    if p_type == "Art for frame TV":
        mode_rules = """
        # MODE 1 — TV (Samsung Frame TV Only)
        DEFINITION: Digital for TV. STRICTLY FORBIDDEN: print, printable, poster, canvas, paper.
        TITLE: Under 100 chars. MUST START with 'Samsung Frame TV Art'.
        DESCRIPTION: Must include: "Digital download for Samsung Frame TV display in 16:9 ratio."
        """
    else:
        mode_rules = """
        # MODE 2 — PRINTABLE (Buyer Prints)
        DEFINITION: Digital download. TITLE: Under 100 chars. Must include 'Printable' or 'Digital Download'.
        """

    base_prompt = f"""
    You are an Expert Etsy SEO Strategist. 
    Analyze the image context and the attached CSV [Keyword, Avg_Searches, Avg_Clicks, Competition].

    # RULES:
    1. DATA MINING: Find keywords in CSV matching image style/subject. Prioritize High Search + Low Competition.
    2. TAGS: 13 tags, NO single-words, max 20 chars.
    3. STYLE: Detect if it's Sketch, Oil, Watercolor, Line Art, etc.
    4. ATTRIBUTES: 
       - Colors: {ALLOWED_COLORS} | Style: {ALLOWED_STYLES}
       - Celeb/Occasion: {ALLOWED_CELEBS}/{ALLOWED_OCCASIONS} (Must Pick)
       - Subject/Room: {ALLOWED_SUBJECTS}/{ALLOWED_ROOMS}

    {mode_rules}

    Return JSON:
    {{
        "Internal_Audit": "Data choices",
        "Final_SEO": {{
            "Title": "Strategic Title",
            "Description": "Sensory Description",
            "AltTexts": ["5 items"],
            "Attributes": {{...}},
            "Tags": ["13 items"]
        }}
    }}
    """
    if revision_request: base_prompt += f"\n# REVISION: {revision_request}"

    contents = [base_prompt, img]
    if csv_file: contents.append(csv_file)
        
    response = model.generate_content(contents)
    raw_text = response.text.replace('```json', '').replace('```', '').strip()
    full_data = json.loads(raw_text)
    return full_data.get("Final_SEO", full_data)

# ==========================================
# 5. Dashboard UI
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
        st.session_state.clear()
        st.rerun()

    st.title("🛠️ AI SEO Optimizer (v2.5)")
    api_key = os.environ.get("GEMINI_API_KEY")

    if not st.session_state['generated_data']:
        p_type = st.radio("Product Type:", ["Art for frame TV", "Printable Wall Art"], horizontal=True)
        u_desc = st.text_area("Product Details:", height=70)
        up = st.file_uploader("Upload Product Image", type=["jpg", "png", "jpeg"])
        
        if up:
            img = Image.open(up)
            st.image(img, width=250)
            
            # منطق دکمه غیرفعال‌شونده
            if not st.session_state['is_processing']:
                if st.button("Analyze & Generate SEO"):
                    st.session_state['is_processing'] = True
                    st.rerun()
            else:
                # لودینگ بدون هیچ نوشته‌ای
                with st.spinner(""):
                    try:
                        data = generate_seo_logic(img, p_type, u_desc, api_key)
                        st.session_state['generated_data'] = data
                        st.session_state['current_image'] = img
                        st.session_state['product_type'] = p_type
                        st.session_state['user_desc'] = u_desc
                        st.session_state['is_processing'] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.session_state['is_processing'] = False
                        if st.button("Try Again"): st.rerun()

    else:
        # نمایش نتایج
        data = st.session_state['generated_data']
        st.image(st.session_state['current_image'], width=150)
        st.success("✅ Analysis Complete!")

        # Title
        st.markdown("<div class='box-title'>📌 Optimized Title</div>", unsafe_allow_html=True)
        st.text_area("T", value=data.get('Title', ''), height=68, label_visibility="collapsed")
        
        # Tags
        st.markdown("<div class='box-title'>🏷️ 13 SEO Tags</div>", unsafe_allow_html=True)
        tags_list = data.get('Tags', [])
        st.info(" | ".join([f"{t} ({len(t)})" for t in tags_list]))
        st.text_area("C", value=", ".join(tags_list), height=68, label_visibility="collapsed")
        
        # Attributes
        st.markdown("<div class='box-title'>⚙️ Attributes</div>", unsafe_allow_html=True)
        attr_cols = st.columns(3)
        for i, (k, v) in enumerate(data.get('Attributes', {}).items()):
            with attr_cols[i % 3]:
                st.text_area(k, value=", ".join(v) if isinstance(v, list) else str(v), height=68)
        
        # Description
        st.markdown("<div class='box-title'>📝 Description</div>", unsafe_allow_html=True)
        st.text_area("D", value=data.get('Description', ''), height=150, label_visibility="collapsed")

        # Alt Text
        st.markdown("<div class='box-title'>🖼️ Alt Texts</div>", unsafe_allow_html=True)
        st.text_area("A", value="\n".join(data.get('AltTexts', [])), height=120, label_visibility="collapsed")

        st.markdown("---")
        if st.button("🗑️ Start New Analysis"):
            st.session_state['generated_data'] = None
            st.rerun()
