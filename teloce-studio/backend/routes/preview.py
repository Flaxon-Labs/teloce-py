"""Preview and compiler diagnostic routes."""

from flaxon.http.request import Request
from backend.services.project_service import get_project


def register_preview(app):
    @app.get("/api/projects/<project_id>/preview")
    async def preview(request: Request, project_id: str):
        try:
            project = get_project(project_id)
            return {"ok": True, "projectId": project_id, "status": "ready", "message": "Generate the project before starting a preview."}
        except FileNotFoundError:
            return {"ok": False, "error": "Project not found"}
