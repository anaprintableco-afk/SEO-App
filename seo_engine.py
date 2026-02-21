# seo_engine.py
import google.generativeai as genai
import pandas as pd
import json
import constants

def get_targeted_csv_data(subject_keyword):
    # (همان کد قبلی برای فیلتر دیتابیس)
    try:
        df = pd.read_csv("MASTER_API_DATA.csv")
        filtered = df[df['Keyword'].str.contains(subject_keyword, case=False, na=False)]
        if not filtered.empty:
            return filtered.sort_values(by='Avg_Searches', ascending=False).head(50).to_string()
        return df.sort_values(by='Avg_Searches', ascending=False).head(50).to_string()
    except:
        return "Database connection error."

def generate_listing_logic(img, p_type, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # 1. تشخیص سوژه
    vision_res = model.generate_content(["Identify the main subject in 1 word.", img])
    subj_word = vision_res.text.strip()
    
    csv_context = get_targeted_csv_data(subj_word)
    
    # 2. تعریف "فرم توخالی" (این کلید حل مشکل توست)
    empty_form = """
    {
        "Title": "",
        "Description": "",
        "Tags": [],
        "AltTexts": [],
        "Attributes": {
            "1st Main Color": "",
            "2nd Main Color": "",
            "Subject": "",
            "Home Style": "",
            "Room": "",
            "Celebration": "",
            "Occasion": ""
        }
    }
    """
    
    # 3. قوانین پر کردن فرم
    prompt = f"""
    You are an Etsy SEO Machine. Your ONLY job is to fill in the blank JSON form provided below.
    DO NOT change the structure, keys, or format of the JSON. 
    
    Mode: {p_type}
    Subject: {subj_word}
    CSV Data: {csv_context}
    
    # RULES FOR FILLING THE FORM:
    1. "Title": Under 100 characters.
    2. "Tags": Exactly 13 phrases. Max 20 chars per phrase.
    3. "Description": { 'MUST include 16:9 ratio.' if p_type == 'Art for frame TV' else 'Standard description.' }
    4. "AltTexts": Exactly 5 descriptive sentences.
    5. "Attributes": You MUST pick values EXACTLY from these lists:
       - Colors: {constants.ALLOWED_COLORS}
       - Style: {constants.ALLOWED_STYLES}
       - Subject: {constants.ALLOWED_SUBJECTS}
       - Room: {constants.ALLOWED_ROOMS}
       - Celebration: {constants.ALLOWED_CELEBRATIONS}
       - Occasion: {constants.ALLOWED_OCCASIONS}

    # BLANK FORM TO FILL:
    {empty_form}
    """
    
    # 4. قفل کردن خروجی روی JSON خالص (این جلوی توهم هوش مصنوعی را می‌گیرد)
    generation_config = genai.types.GenerationConfig(
        response_mime_type="application/json",
    )
    
    response = model.generate_content(
        [prompt, img],
        generation_config=generation_config # اعمال قفل
    )
    
    return json.loads(response.text)
