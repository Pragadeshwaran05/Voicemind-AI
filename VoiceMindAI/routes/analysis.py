from flask import Blueprint, render_template, request, jsonify
from services.ai_service import analyze_text
from models import db, Analysis

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analysis')
def analysis_page():
    return render_template('analysis.html')

@analysis_bp.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.json
    text = data.get('text')
    if not text:
         return jsonify({'success': False, 'error': 'Text is required'})
    
    result = analyze_text(text)
    
    analysis = Analysis(
        text=text,
        sentiment=result.get('sentiment', 'Neutral'),
        intent=result.get('intent', 'Unknown'),
        emotion=result.get('emotion', 'Neutral'),
        keywords=','.join(result.get('keywords', [])),
        topics=','.join(result.get('topics', [])),
        word_count=len(text.split())
    )
    db.session.add(analysis)
    db.session.commit()
    
    result['success'] = True
    return jsonify(result)
