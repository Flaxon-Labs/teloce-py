"""Page management endpoints for the visual project model."""

import re
from uuid import uuid4

from flaxon.http.request import Request

from backend.services.project_service import get_project, save_project


def _page(data: dict) -> dict:
    name = str(data.get("name") or "New page").strip()[:80]
    slug = str(data.get("path") or "/" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")).strip()
    if not slug.startswith("/") or not re.fullmatch(r"/[a-z0-9/_-]*", slug):
        raise ValueError("Page path must start with / and contain only lowercase URL characters")
    page_id = str(data.get("id") or uuid4().hex[:10])
    file_stem = slug.strip("/").split("/")[-1] or "Home"
    return {"id": page_id, "name": name or "New page", "path": slug or "/", "file": "static/js/pages/" + file_stem.title().replace("-", "") + ".vel"}


def register_pages(app):
    @app.get("/api/projects/<project_id>/pages")
    async def pages(request: Request, project_id: str):
        try:
            return {"ok": True, "pages": get_project(project_id).get("pages", [])}
        except FileNotFoundError:
            return {"ok": False, "error": "Project not found"}

    @app.post("/api/projects/<project_id>/pages")
    async def add_page(request: Request, project_id: str):
        try:
            model = get_project(project_id)
            page = _page(await request.json())
            pages = model.get("pages", [])
            if any(item.get("path") == page["path"] for item in pages):
                raise ValueError("A page with this path already exists")
            model["pages"] = pages + [page]
            return {"ok": True, "page": page, "project": save_project(model, project_id)}
        except FileNotFoundError:
            return {"ok": False, "error": "Project not found"}
        except (TypeError, ValueError) as error:
            return {"ok": False, "error": str(error)}

    @app.delete("/api/projects/<project_id>/pages/<page_id>")
    async def remove_page(request: Request, project_id: str, page_id: str):
        try:
            model = get_project(project_id)
            pages = model.get("pages", [])
            if len(pages) <= 1:
                return {"ok": False, "error": "A project must keep one page"}
            model["pages"] = [item for item in pages if item.get("id") != page_id]
            if len(model["pages"]) == len(pages):
                return {"ok": False, "error": "Page not found"}
            return {"ok": True, "project": save_project(model, project_id)}
        except FileNotFoundError:
            return {"ok": False, "error": "Project not found"}
