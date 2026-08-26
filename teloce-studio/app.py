"""Flaxon entry point for the Teloce Studio PWA."""

from pathlib import Path
import mimetypes
import os

from flaxon import Flaxon
from flaxon.http.request import Request
from flaxon.http.response import Response
from flaxon.jinax import Jinax

from backend.routes.assets import register_assets
from backend.routes.bindings import register_bindings
from backend.routes.generation import register_generation
from backend.routes.health import register_health
from backend.routes.preview import register_preview
from backend.routes.projects import register_projects
from backend.routes.pages import register_pages

ROOT = Path(__file__).resolve().parent
app = Flaxon("teloce-studio", debug=os.getenv("FLAXON_DEBUG", "false").lower() == "true")
app.use_templates(Jinax(ROOT / "editor" / "templates", auto_reload=app.debug, strict_undefined=True))


def _file_response(path: Path, media_type: str | None = None):
    resolved = path.resolve()
    if ROOT not in resolved.parents or not resolved.is_file():
        return Response("Not found", status_code=404, media_type="text/plain")
    return Response(resolved.read_bytes(), media_type=media_type or mimetypes.guess_type(resolved.name)[0])


def _register_static_assets():
    media = {".js": "application/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".webmanifest": "application/manifest+json", ".png": "image/png"}
    for path in (ROOT / "public").rglob("*") if (ROOT / "public").exists() else []:
        if path.is_file():
            relative = path.relative_to(ROOT / "public").as_posix()
            app.get(f"/assets/{relative}")(lambda request, path=path: _file_response(path, media.get(path.suffix)))


@app.get("/")
async def home(request):
    return await request.render("index.html", {"title": "Teloce Studio"})


@app.get("/manifest.webmanifest")
async def manifest(request):
    return _file_response(ROOT / "public" / "manifest.webmanifest", "application/manifest+json")


@app.get("/sw.js")
async def service_worker(request):
    return _file_response(ROOT / "public" / "sw.js", "application/javascript")


register_health(app)
register_projects(app)
register_pages(app)
register_generation(app)
register_preview(app)
register_assets(app)
register_bindings(app)
_register_static_assets()


def create_app():
    return app


if __name__ == "__main__":
    print("Teloce Studio: run `flaxon run app:app --reload`")
