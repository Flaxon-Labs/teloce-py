"""Preview and compiler diagnostic routes."""

from flaxon.http.request import Request
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
