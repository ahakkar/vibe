from flask import Flask
from app.route import main_bp
from app.text_gen_page import text_gen_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_bp)
    app.register_blueprint(text_gen_bp)
    return app
