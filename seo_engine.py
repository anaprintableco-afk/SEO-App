# seo_engine.py
import google.generativeai as genai
import pandas as pd
import json
import constants # وارد کردن لیست‌های رسمی از فایل قبلی

def get_targeted_data(subject_query):
    """فیلتر کردن هوشمند دیتابیس برای پیدا کردن بهترین کلمات کلیدی"""
    try:
        df = pd.read_csv("MASTER_API_DATA.csv")
        filtered = df[df['Keyword'].str.contains(subject_query, case=False, na=False)]
        if not filtered.empty:
            return filtered.sort_values(by='Avg_Searches', ascending=False).head(50).to_string()
        return df.sort_values(by='Avg_Searches', ascending=False).head(50).to_string()
    except:
        return "Database not available."

def generate_listing(img, p_type, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # 1. تشخیص سوژه برای سرچ در دیتابیس
    vision_res = model.generate_content(["What is the main subject of this art? (1 word)", img])
    subject = vision_res.text.strip()
    
    # 2. گرفتن دیتا از CSV
    csv_context = get_targeted_data(subject)
    
    # 3. پرامپت نهایی برای تولید تمام بخش‌ها
    prompt = f"""
    You are an Etsy SEO Master. Mode: {p_type}
    Use this CSV data for keywords: {csv_context}
    
    # STRICT RULES FOR ATTRIBUTES:
    - Pick '1st Main Color' & '2nd Main Color' ONLY from: {constants.ALLOWED_COLORS}
    - Pick 'Subject' ONLY from: {constants.ALLOWED_SUBJECTS}
    - Pick 'Room' ONLY from: {constants.ALLOWED_ROOMS}
    - Pick 'Home Style' ONLY from: {constants.ALLOWED_STYLES}
    
    # TV MODE RULES:
    {'Forbidden: print, printable, canvas, paper.' if p_type == "Art for frame TV" else ''}
    
    Return ONLY JSON:
    {{
        "Title": "...",
        "Description": "...",
        "Tags": ["...13 tags..."],
        "Attributes": {{
            "1st Main Color": "...",
            "2nd Main Color": "...",
            "Subject": "...",
            "Room": "...",
            "Home Style": "..."
        }}
    }}
    """
    
    response = model.generate_content([prompt, img])
    # استخراج و تمیز کردن JSON
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)
