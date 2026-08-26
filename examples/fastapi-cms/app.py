from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

ROOT = Path(__file__).resolve().parent
pages = {
    "home": {"slug": "home", "title": "Welcome", "body": "Edit this page with FastAPI and Teloce."},
    "about": {"slug": "about", "title": "About", "body": "A second page proves the list and editor are real."},
}
app = FastAPI(title="Teloce FastAPI CMS")
STATIC_DIR = ROOT / "dist" / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.get("/api/pages")
async def list_pages():
    return list(pages.values())

@app.put("/api/pages/{slug}")
async def update_page(slug: str, payload: dict):
    if slug not in pages:
        raise HTTPException(404, "Page not found")
    pages[slug].update({"title": str(payload.get("title", "")), "body": str(payload.get("body", ""))})
    return pages[slug]


if __name__ == "__main__":
    import uvicorn
    from teloce.build import build_project

    result = build_project(ROOT, options={"dev": True, "source_maps": True})
    print(f"Compiled {result['compiled']} component(s)")
    uvicorn.run(app, host="127.0.0.1", port=8000)
