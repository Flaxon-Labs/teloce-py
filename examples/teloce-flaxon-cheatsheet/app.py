import mimetypes
from pathlib import Path

from flaxon import Flaxon
from flaxon.http.response import Response
from flaxon.jinax import Jinax

from teloce.build import build_project

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

# The build is explicit and deterministic. A server never starts against stale
# frontend output, which is especially useful on serverless deployments.
if not (DIST / "static/js/App.js").exists():
    build_project(ROOT, options={"clean": True, "dev": True, "source_maps": True})

app = Flaxon("teloce-flaxon-cheatsheet", debug=False)
app.use_templates(Jinax(str(ROOT / "templates"), auto_reload=False))


def register_assets():
    for path in DIST.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(DIST).as_posix()
        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"

        async def asset(request, file_path=path, content_type=media_type):
            return Response(file_path.read_bytes(), media_type=content_type)

        app.get(f"/assets/{relative}")(asset)


register_assets()


@app.get("/")
async def home(request):
    return await request.render("index.html", {"title": "Teloce Cheatsheet"})


@app.get("/api/health")
async def health():
    return {"ok": True, "service": "teloce-flaxon-cheatsheet", "components": 40}


if __name__ == "__main__":
    print("Run: python -m flaxon run app:app --reload")
