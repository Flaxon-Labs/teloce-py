from pathlib import Path
from flask import Flask, jsonify, render_template, request

PROJECT_ROOT = Path(__file__).resolve().parent
messages = [
    {"id": 1, "author": "system", "body": "Welcome to the Flask chat demo."},
]

app = Flask(__name__, static_folder=str(PROJECT_ROOT / "dist" / "static"), template_folder=str(PROJECT_ROOT / "templates"))

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/messages")
def list_messages():
    return jsonify(messages)

@app.post("/api/messages")
def create_message():
    payload = request.get_json(silent=True) or {}
    body = str(payload.get("body", "")).strip()
    if not body or len(body) > 500:
        return jsonify({"error": "Message must contain 1-500 characters."}), 400
    message = {"id": messages[-1]["id"] + 1, "author": "you", "body": body}
    messages.append(message)
    return jsonify(message), 201

if __name__ == "__main__":
    from build import build_project
    build_project(PROJECT_ROOT, options={"dev": True, "source_maps": True})
    app.run(debug=True, port=5000)
