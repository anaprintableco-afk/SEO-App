import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image

# ==========================================
# تنظیمات اصلی سایت
# ==========================================
st.set_page_config(page_title="Etsy Core SEO Engine", page_icon="⚙️", layout="centered")

# خواندن کلید API از گاوصندوق
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("خطا در خواندن کلید API. لطفاً بخش Secrets را بررسی کنید.")
    st.stop()

# ==========================================
# رابط کاربری (UI)
# ==========================================
st.title("⚙️ Etsy Core SEO Engine")
st.markdown("عکس محصول را آپلود کنید، نوع آن را مشخص کنید و سئوی طبقه‌بندی شده تحویل بگیرید.")

# فیلد انتخاب نوع محصول (Mode)
product_mode = st.radio(
    "📺 نوع محصول (Mode) را انتخاب کنید:",
    ["Printable (دیجیتال دانلود - مناسب برای چاپ)", "Frame TV Art (مخصوص نمایشگر تلویزیون)"],
    horizontal=True
)

st.markdown("---")

# آپلود عکس
uploaded_file = st.file_uploader("🖼️ آپلود عکس محصول", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="عکس محصول شما", use_container_width=True)
    
    if st.button("🚀 پردازش و تولید سئو"):
        with st.spinner("در حال تحلیل عکس، اعمال قوانین سخت‌گیرانه اتسی و تطبیق با CSV..."):
            try:
                # خواندن کلمات کلیدی از فایل CSV
                df = pd.read_csv('MASTER_API_DATA.csv')
                df['Avg_Searches'] = pd.to_numeric(df['Avg_Searches'], errors='coerce').fillna(0)
                df['Competition'] = pd.to_numeric(df['Competition'], errors='coerce').fillna(1)
                df['Opportunity'] = df['Avg_Searches'] / df['Competition']
                
                # استخراج ۱۰۰ کلمه برتر برای پرامپت
                top_keywords = df.sort_values(by='Opportunity', ascending=False).head(100)['Keyword'].tolist()
                csv_context = ", ".join(str(x) for x in top_keywords)
                
                # تعیین منطق بر اساس Mode انتخاب شده
                if "TV" in product_mode:
                    mode_instruction = '- MODE 1 (TV): Focus on "Digital Display". Prohibited words: print, paper, shipping, canvas, poster.'
                else:
                    mode_instruction = '- MODE 2 (Printable): Focus on "Digital Download". Use multi-word phrases like "printable wall art" or "instant download art". (NEVER use single words like "printable" or "art").'

                # پرامپت دقیق، خشن و منطبق بر هندبوک اتسی
                prompt = f"""
                # IDENTITY & AUTHORITY
                You are the Core SEO Engine of an automated Etsy listing service. Your primary mission is to transform user inputs into high-converting, SEO-optimized listings.

                # ETSY SELLER HANDBOOK RULES (CRITICAL - YOU MUST OBEY):
                1. NO SINGLE-WORD TAGS: NEVER use a single word as a tag (e.g., "printable", "art", "vintage"). ALL 13 tags MUST be multi-word phrases (e.g., "printable wall art", "vintage flower decor").
                2. STRICT 20-CHARACTER LIMIT: You MUST physically count the characters of EVERY tag. A tag cannot exceed 20 characters (including spaces). 
                   - Example BAD: "mid century modern art" (22 chars)
                   - Example GOOD: "mid century art" (15 chars)
                3. NO REPETITION STUFFING: Do not repeat the same root word in every tag. Mix your vocabulary.

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
                - SECTIONS: Tapestry | Rug, Fall | Halloween | Dark, Floral | Nursery| Animal, Winter | Christmas, Frame TV Art, Spring | Easter | Valen, Portrait | People, Summer | Coastal, Kitchen, Abstract, Architecture | Cityscape, Christian

                # OUTPUT STRUCTURE (COPY-PASTE READY)
                Return the output in this EXACT format. Use these exact headers so the system can parse them:
                Title: [Text]
                Description: [Text]
                Alt Texts: [10 descriptive sentences separated by lines]
                1st Main Color: [Value]
                2nd Main Color: [Value]
                Home Style: [Value]
                Celebration: [Value or Blank]
                Occasion: [Value or Blank]
                Subject: [Up to 3 Values]
                Room: [5 Values]
                Tags: [13 comma-separated phrases, NO single words, ALL under 20 chars]
                Section: [Value]

                # QUALITY CONTROL LOCKS
                - No emojis, no conversational fillers.
                - Titles < 100 characters.
                - Descriptions < 400 characters.
                """
                
                # پردازش با مدل پرسرعت فلش
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content([prompt, image])
                raw_text = response.text
                
                st.success("✅ استخراج سئو با موفقیت انجام شد!")
                st.markdown("---")
                
                # ==========================================
                # پردازش‌گر متن: جدا کردن بخش‌ها برای نمایش در باکس‌های مجزا
                # ==========================================
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

                # استخراج اطلاعات بر اساس هدرهای مشخص شده در پرامپت
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
                tags = extract_section(raw_text, "Tags:", "Section:")
                section = extract_section(raw_text, "Section:", None)

                # ==========================================
                # نمایش خروجی‌ها در باکس‌های اختصاصی با قابلیت کپی
                # ==========================================
                
                st.subheader("📝 تایتل (Title)")
                st.code(title, language="text")
                
                st.subheader("🏷️ تگ‌ها (13 Tags)")
                st.code(tags, language="text")
                
                st.subheader("📄 توضیحات محصول (Description)")
                st.code(description, language="text")
                
                st.subheader("🖼️ متن‌های جایگزین (Alt Texts)")
                st.code(alt_texts, language="text")
                
                st.subheader("⚙️ ویژگی‌ها و دسته‌بندی‌ها (Attributes)")
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
                    st.text_input("Section", value=section)

                with st.expander("👀 مشاهده متن خام تولید شده توسط هوش مصنوعی"):
                    st.text_area("", value=raw_text, height=300)

            except Exception as e:
                st.error(f"❌ خطایی رخ داد: {e}")
