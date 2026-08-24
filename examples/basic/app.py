"""A Flask host for the basic Teloce task-board example."""

from pathlib import Path
from flask import Flask, render_template
from teloce.build import build_project


ROOT = Path(__file__).parent


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(ROOT / "dist" / "static"), template_folder=str(ROOT / "templates"))

    @app.get("/")
    def home():
        return render_template("index.html")

    return app


app = create_app()


if __name__ == "__main__":
    result = build_project(ROOT, options={"dev": True, "source_maps": True})
    print(f"Teloce compiled {result['compiled']} component(s)")
    app.run(debug=True, port=5001)
