# seo_engine.py
import google.generativeai as genai
import pandas as pd
import json
import constants

def get_targeted_csv_data(subject_keyword):
    """فیلتر کردن هوشمند دیتابیس برای کلمات مرتبط با سوژه"""
    try:
        df = pd.read_csv("MASTER_API_DATA.csv")
        filtered = df[df['Keyword'].str.contains(subject_keyword, case=False, na=False)]
        if not filtered.empty:
            return filtered.sort_values(by='Avg_Searches', ascending=False).head(50).to_string()
        return df.sort_values(by='Avg_Searches', ascending=False).head(50).to_string()
    except:
        return "Database connection error or file not found."

def generate_listing_logic(img, p_type, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # 1. تشخیص سوژه برای جستجو در دیتابیس
    vision_res = model.generate_content(["What is the main subject of this art? (Output only 1 word)", img])
    subj_word = vision_res.text.strip()
    
    # 2. استخراج کلمات کلیدی طلایی
    csv_context = get_targeted_csv_data(subj_word)
    
    # 3. تولید سئو با قوانین سفت و سخت
    prompt = f"""
    You are an expert Etsy SEO Master for AtlasRank.net. 
    Mode: {p_type} | Detected Subject: {subj_word}
    
    # DATA CONTEXT (From CSV):
    {csv_context}
    
    # STRICT RULES:
    1. TAGS: Exactly 13 tags. EVERY tag MUST be under 20 characters. No single words.
    2. ATTRIBUTES: You MUST fill all attributes below using ONLY these allowed lists:
       - Colors: {constants.ALLOWED_COLORS}
       - Style: {constants.ALLOWED_STYLES}
       - Subject: {constants.ALLOWED_SUBJECTS}
       - Room: {constants.ALLOWED_ROOMS}
       - Celebration: {constants.ALLOWED_CELEBRATIONS}
       - Occasion: {constants.ALLOWED_OCCASIONS}
    3. TV MODE: {'STRICTLY FORBIDDEN to use these words: ' + str(constants.FORBIDDEN_TV_WORDS) + '. You MUST mention 16:9 ratio.' if p_type == 'Art for frame TV' else ''}

    Return ONLY a valid JSON object matching this structure:
    {{
        "Title": "...",
        "Description": "...",
        "Tags": ["...", "..."],
        "AltTexts": ["...", "...", "...", "...", "..."],
        "Attributes": {{
            "1st Main Color": "...",
            "2nd Main Color": "...",
            "Subject": "...",
            "Home Style": "...",
            "Room": "...",
            "Celebration": "...",
            "Occasion": "..."
        }}
    }}
    """
    
    response = model.generate_content([prompt, img])
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)
