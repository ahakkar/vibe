# app/routes.py

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('dashboard.html')

@main_bp.route('/text-gen')
def textGen():
    return render_template('textGen.html')

@main_bp.route('/text-gen/chat')
def chat():
    return render_template('chat.html')