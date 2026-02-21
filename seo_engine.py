# seo_engine.py
import google.generativeai as genai
import pandas as pd
import json
import re
import constants

def process_database(dna_keywords, core_subject):
    """معدن‌کاوی دیتابیس با اعمال فیلترهای ریاضی و شاخص فرصت"""
    try:
        df = pd.read_csv("MASTER_API_DATA.csv")
        # تبدیل ستون‌ها به عدد برای محاسبات ریاضی
        df['Avg_Searches'] = pd.to_numeric(df['Avg_Searches'], errors='coerce').fillna(0)
        df['Competition'] = pd.to_numeric(df['Competition'], errors='coerce').fillna(0)

        # پیدا کردن تمام کلمات مرتبط با DNA تصویر
        pattern = '|'.join([re.escape(k.strip()) for k in dna_keywords if k.strip()])
        matched = df[df['Keyword'].str.contains(pattern, case=False, na=False)]

        if matched.empty: return "No data found.", "general art"

        # فیلتر 1: تله اعداد کوچک (سرچ بالای 20 یا استثنای شامل بودن سوژه اصلی)
        cond_min_search = matched['Avg_Searches'] >= 20
        cond_exception = (matched['Avg_Searches'] < 20) & (matched['Keyword'].str.contains(re.escape(core_subject), case=False, na=False))
        filtered = matched[cond_min_search | cond_exception].copy()

        # فیلتر 2: محاسبه شاخص فرصت
        filtered['Opportunity_Score'] = filtered['Avg_Searches'] / (filtered['Competition'] + 1)

        # فیلتر 3: مرتب سازی و انتخاب 50 معدن طلا
        top_50 = filtered.sort_values(by='Opportunity_Score', ascending=False).head(50)
        golden_keyword = top_50.iloc[0]['Keyword'] if not top_50.empty else core_subject
        
        csv_context = top_50.to_string(columns=['Keyword', 'Avg_Searches', 'Opportunity_Score'])
        return csv_context, golden_keyword

    except Exception as e:
        return f"Database Error: {e}", core_subject

def generate_seo_data(img, p_type, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    # فاز 1: استخراج DNA و سوژه اصلی
    vision_prompt = "Describe this art in a comma-separated list of 5 keywords (subject, style, technique, vibe, colors). Then, as the very last word, write the main core subject in 1 word."
    vision_res = model.generate_content([vision_prompt, img]).text.strip().split(',')
    
    core_subject = vision_res[-1].strip() # کلمه آخر سوژه اصلی است
    dna_keywords = [k.strip() for k in vision_res[:-1]]

    # تزریق ماهیت محصول به DNA
    core_product_tags = []
    if p_type == "Frame TV Art":
        core_product_tags = ["Samsung Frame TV Art", "Digital TV Display", "16:9 ratio"]
    else:
        core_product_tags = ["Printable wall art", "Digital download", "Poster"]
    dna_keywords.extend(core_product_tags)

    # فاز 2: شخم زدن دیتابیس با الگوریتم ریاضی
    csv_context, golden_keyword = process_database(dna_keywords, core_subject)

    # فاز 3: قالب فیکس خروجی (Schema)
    json_schema = """
    {
      "Title": "",
      "Description": "",
      "1st Main Color": "",
      "2nd Main Color": "",
      "Home Style": "",
      "Celebration": "",
      "Occasion": "",
      "Subject": "",
      "Room": "",
      "Tags": []
    }
    """

    # فاز 4: پرامپت قوانین سخت‌گیرانه اتسی
    prompt = f"""
    You are an expert Etsy SEO Engine. Fill out the exact JSON schema provided based on these inputs and strict rules.
    
    # CONTEXT
    Product Type: {p_type}
    Golden Keyword (Rank 1): "{golden_keyword}"
    Core Product Tags to prioritize: {core_product_tags}
    Top 50 CSV Data (Sorted by Opportunity Score):
    {csv_context}

    # STRICT RULES (DO NOT FAIL):
    1. **Title**: Under 80 chars. Readable by humans. NO keyword stuffing. NO repeated words. 
       -> FRONT-LOADING: You MUST start the title with the Golden Keyword: "{golden_keyword}".
       -> If Product is Frame TV Art, you MUST include "Samsung Frame TV Art" in the Title.
    2. **Tags**: Exactly 13 tags. Max 20 chars per tag. NO single-word tags.
       -> ANTI-CANNIBALIZATION: Do NOT repeat exact phrases used in Title/Attributes in the Tags.
       -> EXCEPTION BYPASS: You MUST include "{golden_keyword}" and the Core Product Tags in the 13 tags, even if they are in the title. This is the only exception.
    3. **Attributes**: Fill the 7 attribute fields ONLY using exact values from these lists:
       - Colors: {constants.ALLOWED_COLORS}
       - Style: {constants.ALLOWED_STYLES}
       - Subject: {constants.ALLOWED_SUBJECTS}
       - Room: {constants.ALLOWED_ROOMS}
       - Celebration: {constants.ALLOWED_CELEBRATIONS} (Use "None" if not a holiday)
       - Occasion: {constants.ALLOWED_OCCASIONS} (Use "None" if no specific event)
    4. **Description**: Write 2 engaging paragraphs. 
       -> If Frame TV: Mention "16:9 ratio". DO NOT use these words: {constants.FORBIDDEN_TV_WORDS}.

    Return ONLY valid JSON matching this exact structure, nothing else:
    {json_schema}
    """

    # قفل کردن خروجی روی فرمت JSON خالص
    generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
    response = model.generate_content([prompt, img], generation_config=generation_config)
    
    return json.loads(response.text)
