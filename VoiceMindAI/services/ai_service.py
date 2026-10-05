import google.generativeai as genai
import json
from config import Config

def init_ai():
    if Config.AI_API_KEY and Config.AI_API_KEY != 'YOUR_API_KEY':
        genai.configure(api_key=Config.AI_API_KEY)
        return True
    return False

def generate_response(prompt, history=[]):
    if not init_ai():
        return "AI is not configured. Please set AI_API_KEY in .env."
    try:
        model = genai.GenerativeModel(Config.AI_MODEL)
        messages = [{'role': 'user' if m['role'] == 'user' else 'model', 'parts': [m['content']]} for m in history]
        messages.append({'role': 'user', 'parts': [prompt]})
        response = model.generate_content(messages)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

def analyze_text(text):
    if not init_ai():
        return {"sentiment": "Neutral", "intent": "Information", "emotion": "Neutral", "keywords": [], "topics": [], "word_count": len(text.split())}
    try:
        model = genai.GenerativeModel(Config.AI_MODEL)
        prompt = f"Analyze the following text and return a JSON object with keys: sentiment (Positive, Neutral, Negative), intent, emotion, keywords (list of strings), topics (list of strings). Text: {text}"
        response = model.generate_content(prompt)
        text_resp = response.text
        # Naive extraction of JSON
        if "```json" in text_resp:
            text_resp = text_resp.split("```json")[1].split("```")[0]
        return json.loads(text_resp)
    except Exception as e:
        return {"sentiment": "Neutral", "intent": "Unknown", "emotion": "Unknown", "keywords": [], "topics": [], "word_count": len(text.split())}

def summarize_text(text):
    if not init_ai():
        return {"summary": "AI not configured.", "key_points": [], "action_items": [], "questions": []}
    try:
        model = genai.GenerativeModel(Config.AI_MODEL)
        prompt = f"Summarize the following text. Return a JSON object with keys: summary (string), key_points (list of strings), action_items (list of strings), questions (list of strings). Text: {text}"
        response = model.generate_content(prompt)
        text_resp = response.text
        if "```json" in text_resp:
            text_resp = text_resp.split("```json")[1].split("```")[0]
        return json.loads(text_resp)
    except Exception as e:
         return {"summary": f"Error: {str(e)}", "key_points": [], "action_items": [], "questions": []}
