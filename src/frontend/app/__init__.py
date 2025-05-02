from flask import Flask
from flask_cors import CORS  # ← ADD THIS
from src.frontend.app.route import main_bp


def create_app():
    app = Flask(__name__)
    CORS(app)  # ← ADD THIS HERE to enable CORS globally
    app.register_blueprint(main_bp)
    return app
