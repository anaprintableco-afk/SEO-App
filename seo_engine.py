# seo_engine.py
import google.generativeai as genai
import pandas as pd
import json
import constants

def generate_listing(img, p_type, user_desc, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # تشخیص سوژه برای فیلتر دیتابیس
    vision_res = model.generate_content(["Identify this art subject in 1 word", img])
    subject_query = vision_res.text.strip()
    
    # فیلتر کردن دیتابیس (ساده شده برای تست)
    csv_context = "Use relevant high-search keywords from database." 

    prompt = f"""
    You are an Etsy SEO Master.
    Mode: {p_type} | Subject: {subject_query}
    
    # RULES:
    1. Attributes: Choose ONLY from: 
       Colors: {constants.ALLOWED_COLORS}, Subjects: {constants.ALLOWED_SUBJECTS}, 
       Rooms: {constants.ALLOWED_ROOMS}, Styles: {constants.ALLOWED_STYLES}.
    2. Tags: 13 phrases.
    3. TV Mode Rules: {constants.FORBIDDEN_TV_WORDS} are forbidden. Mention 16:9 ratio.

    Return JSON strictly:
    {{
        "Title": "...",
        "Description": "...",
        "Tags": [],
        "AltTexts": [],
        "Attributes": {{
            "1st Main Color": "...",
            "2nd Main Color": "...",
            "Home Style": "...",
            "Subject": ["..."],
            "Room": ["..."],
            "Celebration": "...",
            "Occasion": "..."
        }}
    }}
    """
    response = model.generate_content([prompt, img])
    return json.loads(response.text.replace('```json', '').replace('```', '').strip())
