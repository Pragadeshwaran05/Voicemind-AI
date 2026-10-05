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
