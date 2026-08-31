"""Runnable Flask host for the MiniVel demo component framework."""

from pathlib import Path

from flask import Flask, render_template
from teloce.build import build_project


ROOT = Path(__file__).resolve().parent

app = Flask(
    __name__,
    static_folder=str(ROOT / "dist" / "static"),
    static_url_path="/static",
    template_folder=str(ROOT / "templates"),
)


@app.get("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    result = build_project(
        ROOT,
        options={"dev": True, "clean": True, "source_maps": True, "shared_runtime": True},
    )
    if result["failed"]:
        raise SystemExit("\n".join(result["errors"]))
    print(f"Teloce compiled {result['compiled']} component(s)")
  
    app.run(debug=True, port=5002, use_reloader=True)
