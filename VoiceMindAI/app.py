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
