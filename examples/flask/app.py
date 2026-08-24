"""A real Flask host for the compiled Teloce frontend."""

from pathlib import Path
from flask import Flask, jsonify, render_template
from teloce.build import build_project

PROJECT_ROOT = Path(__file__).parent


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(PROJECT_ROOT / "dist" / "static"), template_folder=str(PROJECT_ROOT / "templates"))

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True, "service": "teloce-flask-example"})

    return app


app = create_app()

if __name__ == "__main__":
    result = build_project(PROJECT_ROOT, options={"dev": True, "source_maps": True})
    print(f"Teloce compiled {result['compiled']} component(s)")
    app.run(debug=True, port=5000)
