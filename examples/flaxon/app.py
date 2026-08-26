"""A real Flaxon + Jinax host for compiled Teloce components."""

import mimetypes
from pathlib import Path
from flaxon import Flaxon
from flaxon.http.response import Response
from flaxon.jinax import Jinax
from teloce.build import build_project

ROOT = Path(__file__).resolve().parent
DIST = (ROOT / "dist").resolve()
app = Flaxon("teloce-flaxon-example", debug=True)
app.use_templates(Jinax(str(ROOT / "templates"), auto_reload=True))


def register_assets() -> None:
    """Register only files inside dist, preventing path traversal."""
    if not DIST.exists():
        return
    for path in DIST.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(DIST).as_posix()
        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"

        async def serve_asset(request, file_path=path, content_type=media_type):
            return Response(file_path.read_bytes(), media_type=content_type)

        app.get(f"/assets/{relative}")(serve_asset)


register_assets()


@app.get("/")
async def home(request):
    return await request.render("index.html", {"title": "Flaxon + Teloce"})


@app.get("/api/health")
async def health():
    return {"ok": True, "service": "teloce-flaxon-example"}


if __name__ == "__main__":
    print("Run `python build.py` before `flaxon run app:app --reload`.")
