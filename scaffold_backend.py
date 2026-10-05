import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created {path}")

base = "VoiceMindAI"

write_file(f"{base}/requirements.txt", """
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
python-dotenv==1.0.0
google-generativeai==0.3.1
""")

write_file(f"{base}/.env.example", """
SECRET_KEY=your_secret_key_here
AI_API_KEY=your_gemini_api_key_here
AI_MODEL=gemini-1.5-flash
DATABASE_URL=sqlite:///voicemind.db
""")

write_file(f"{base}/.env", """
SECRET_KEY=dev_secret_key_12345
AI_API_KEY=YOUR_API_KEY
AI_MODEL=gemini-1.5-flash
DATABASE_URL=sqlite:///voicemind.db
""")

write_file(f"{base}/config.py", """
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///voicemind.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AI_API_KEY = os.environ.get('AI_API_KEY')
    AI_MODEL = os.environ.get('AI_MODEL', 'gemini-1.5-flash')
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB max
""")

write_file(f"{base}/models/__init__.py", """
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="Guest")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), default="New Conversation")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade="all, delete-orphan")

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False) # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    input_type = db.Column(db.String(50), default='TEXT') # 'TEXT' or 'VOICE'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(50))
    intent = db.Column(db.String(100))
    emotion = db.Column(db.String(50))
    keywords = db.Column(db.Text)
    topics = db.Column(db.Text)
    word_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
""")

write_file(f"{base}/services/__init__.py", "")

write_file(f"{base}/services/ai_service.py", """
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
""")

write_file(f"{base}/routes/__init__.py", "")

write_file(f"{base}/routes/main.py", """
from flask import Blueprint, render_template, jsonify
from models import db, Conversation, Message, Analysis

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    total_convs = Conversation.query.count()
    total_msgs = Message.query.count()
    voice_msgs = Message.query.filter_by(input_type='VOICE').count()
    text_msgs = Message.query.filter_by(input_type='TEXT').count()
    recent_convs = Conversation.query.order_by(Conversation.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', 
        total_convs=total_convs, total_msgs=total_msgs,
        voice_msgs=voice_msgs, text_msgs=text_msgs,
        recent_convs=recent_convs)
""")

write_file(f"{base}/routes/chat.py", """
from flask import Blueprint, render_template, request, jsonify
from models import db, Conversation, Message
from services.ai_service import generate_response

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
def chat_page():
    return render_template('chat.html')

@chat_bp.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    conv_id = data.get('conversation_id')
    user_message = data.get('message')
    input_type = data.get('input_type', 'TEXT')

    if not user_message:
        return jsonify({'success': False, 'error': 'Message is required'})

    if not conv_id:
        conv = Conversation(title=user_message[:30] + '...')
        db.session.add(conv)
        db.session.commit()
        conv_id = conv.id
    
    # Save user message
    msg = Message(conversation_id=conv_id, role='user', content=user_message, input_type=input_type)
    db.session.add(msg)
    db.session.commit()

    # Get history
    history = Message.query.filter_by(conversation_id=conv_id).order_by(Message.id).all()
    history_dict = [{'role': m.role, 'content': m.content} for m in history[:-1]]

    # Generate response
    ai_text = generate_response(user_message, history_dict)

    # Save AI message
    ai_msg = Message(conversation_id=conv_id, role='assistant', content=ai_text, input_type='TEXT')
    db.session.add(ai_msg)
    db.session.commit()

    return jsonify({
        'success': True,
        'response': ai_text,
        'conversation_id': conv_id
    })

@chat_bp.route('/api/conversations/<int:conv_id>', methods=['GET', 'DELETE'])
def api_conversation(conv_id):
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    
    if request.method == 'DELETE':
        db.session.delete(conv)
        db.session.commit()
        return jsonify({'success': True})
    
    messages = [{'id': m.id, 'role': m.role, 'content': m.content, 'input_type': m.input_type} for m in conv.messages]
    return jsonify({'success': True, 'id': conv.id, 'title': conv.title, 'messages': messages})
""")

write_file(f"{base}/routes/analysis.py", """
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
""")

write_file(f"{base}/routes/summarizer.py", """
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
""")

write_file(f"{base}/app.py", """
from flask import Flask
from config import Config
from models import db
from routes.main import main_bp
from routes.chat import chat_bp
from routes.analysis import analysis_bp
from routes.summarizer import summarizer_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(summarizer_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
""")
