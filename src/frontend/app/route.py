# app/routes.py

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('dashboard.html')

@main_bp.route('/text-gen')
def textGen():
    return render_template('textGen.html')

@main_bp.route('/stt')
def stt():
    return render_template('stt.html')

@main_bp.route('/tts')
def tts():
    return render_template('tts.html')

@main_bp.route('/all')
def all():
    return render_template('chat.html')

@main_bp.route('/ir')
def ir():
    return render_template('textGen.html')

@main_bp.route('/text-gen/chat')
def chat():
    return render_template('chat.html')