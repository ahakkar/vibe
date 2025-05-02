from flask import Blueprint, render_template, request, jsonify

text_gen_bp = Blueprint("chat", __name__)


@text_gen_bp.route("/chat")
def chat_page():
    return render_template("chat.html")


@text_gen_bp.route("/receive", methods=["POST"])
def receive_message():
    data = request.json
    message = data["message"]
    response = "This is a placeholder response."
    return jsonify({"message": message})


@text_gen_bp.route("/send", methods=["POST"])
def send_message():
    data = request.json
    message = data["message"]
    return jsonify({"status": "success", "message": message})
