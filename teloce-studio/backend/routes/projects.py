"""Project lifecycle routes: create, open, save, export, and delete."""

from flaxon.http.request import Request
from backend.services.project_service import get_project, list_projects, save_project


def register_projects(app):
    @app.get("/api/projects")
    async def projects(request):
        return {"ok": True, "projects": list_projects()}

    @app.post("/api/projects")
    async def create_project(request: Request):
        try:
            data = await request.json()
            return {"ok": True, "project": save_project(data or {})}
        except (ValueError, TypeError) as error:
            return {"ok": False, "error": str(error)}

    @app.get("/api/projects/<project_id>")
    async def project(request: Request, project_id: str):
        try:
            return {"ok": True, "project": get_project(project_id)}
        except FileNotFoundError:
            return {"ok": False, "error": "Project not found"}

    @app.put("/api/projects/<project_id>")
    async def update_project(request: Request, project_id: str):
        try:
            data = await request.json()
            return {"ok": True, "project": save_project(data or {}, project_id)}
        except (ValueError, TypeError) as error:
            return {"ok": False, "error": str(error)}
