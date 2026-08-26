"""Preview and compiler diagnostic routes."""

from flaxon.http.request import Request
from flaxon.http.response import Response
import mimetypes
from backend.services.project_service import get_project
from backend.services.project_service import _project_dir
from backend.services.validation_service import validate_project
from teloce.build import build_project


def register_preview(app):
    @app.get("/api/projects/<project_id>/preview")
    async def preview(request: Request, project_id: str):
        try:
            project = get_project(project_id)
            issues = validate_project(project)
            if issues: return {"ok": False, "status": "invalid", "issues": issues}
            from backend.services.generation_service import generate_project
            generate_project(project)
            result = build_project(_project_dir(project_id), options={"dev": False, "source_maps": False})
            return {"ok": not result.get("failed"), "projectId": project_id, "status": "ready" if not result.get("failed") else "failed", "diagnostics": result.get("errors", [])}
        except FileNotFoundError:
            return {"ok": False, "error": "Project not found"}

    @app.get("/api/projects/<project_id>/preview/page")
    async def preview_page(request: Request, project_id: str):
        try:
            project = get_project(project_id)
            issues = validate_project(project)
            if issues: return Response("Preview validation failed", status_code=422, media_type="text/plain")
            from backend.services.generation_service import generate_project
            generate_project(project)
            result = build_project(_project_dir(project_id), options={"dev": False, "source_maps": False})
            if result.get("failed"): return Response("Preview compilation failed", status_code=422, media_type="text/plain")
            template = (_project_dir(project_id) / "templates" / "index.html").read_text(encoding="utf-8")
            base = f"/api/projects/{project_id}/preview/files/"
            return Response(template.replace("/assets/", base), media_type="text/html; charset=utf-8")
        except FileNotFoundError:
            return Response("Project not found", status_code=404, media_type="text/plain")

    @app.get("/api/projects/<project_id>/preview/files/<path:file_path>")
    async def preview_file(request: Request, project_id: str, file_path: str):
        try:
            project = get_project(project_id)
            from backend.services.generation_service import generate_project
            generate_project(project)
            result = build_project(_project_dir(project_id), options={"dev": False, "source_maps": False})
            if result.get("failed"): return Response("Preview compilation failed", status_code=422, media_type="text/plain")
            root = (_project_dir(project_id) / "dist").resolve()
            target = (root / file_path).resolve()
            if root not in target.parents or not target.is_file(): return Response("Not found", status_code=404, media_type="text/plain")
            return Response(target.read_bytes(), media_type=mimetypes.guess_type(target.name)[0] or "application/octet-stream")
        except FileNotFoundError:
            return Response("Project not found", status_code=404, media_type="text/plain")
