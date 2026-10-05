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
