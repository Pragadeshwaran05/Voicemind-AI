from flask import Blueprint, render_template, request, jsonify
from services.ai_service import summarize_text
import os
from config import Config

summarizer_bp = Blueprint('summarizer', __name__)

@summarizer_bp.route('/summarizer')
def summarizer_page():
    return render_template('summarizer.html')

@summarizer_bp.route('/api/summarize', methods=['POST'])
def api_summarize():
    text = ""
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            text = file.read().decode('utf-8')
    elif request.json and 'text' in request.json:
        text = request.json['text']
        
    if not text:
         return jsonify({'success': False, 'error': 'Text or file is required'})
    
    result = summarize_text(text)
    result['success'] = True
    return jsonify(result)
