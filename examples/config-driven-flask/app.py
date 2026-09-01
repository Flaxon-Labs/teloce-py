"""Flask host that delegates the component build to teloce.config.json."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from flask import Flask, render_template


ROOT = Path(__file__).resolve().parent


def build_assets() -> None:
    """Run the configured Teloce project build before serving browser assets."""
    completed = subprocess.run(
        [sys.executable, "-m", "teloce", "build"],
        cwd=ROOT,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError("Teloce build failed; fix the reported diagnostics before starting Flask.")


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=str(ROOT / "public-assets" / "client"),
        static_url_path="/static",
        template_folder=str(ROOT / "templates"),
    )

    @app.get("/")
    def home():
        return render_template("index.html")

    return app


app = create_app()


if __name__ == "__main__":
    build_assets()
    app.run(debug=True, port=5002)
