"""Visual API binding routes used by the Studio data panel."""

import re
from uuid import uuid4

from flaxon.http.request import Request

from backend.services.project_service import get_project, save_project

METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def _validate(binding: dict) -> dict:
    method = str(binding.get("method", "GET")).upper()
    path = str(binding.get("path", "")).strip()
    if method not in METHODS:
        raise ValueError("Unsupported HTTP method")
    if not path.startswith("/") or "{" in path or "}" in path or len(path) > 120:
        raise ValueError("Binding path must be a short absolute path without template expressions")
    if not re.fullmatch(r"/[A-Za-z0-9_./-]*", path):
        raise ValueError("Binding path contains unsupported characters")
    return {"id": str(binding.get("id") or uuid4().hex[:10]), "name": str(binding.get("name") or "API binding"), "method": method, "path": path, "response": binding.get("response", {"ok": True, "data": []})}


def register_bindings(app):
    @app.get("/api/projects/<project_id>/bindings")
    async def bindings(request: Request, project_id: str):
        try: return {"ok": True, "bindings": get_project(project_id).get("bindings", [])}
        except FileNotFoundError: return {"ok": False, "error": "Project not found"}

    @app.post("/api/projects/<project_id>/bindings")
    async def add_binding(request: Request, project_id: str):
        try:
            model = get_project(project_id); binding = _validate(await request.json()); model["bindings"] = model.get("bindings", []) + [binding]; return {"ok": True, "binding": binding, "project": save_project(model, project_id)}
        except FileNotFoundError: return {"ok": False, "error": "Project not found"}
        except (TypeError, ValueError) as error: return {"ok": False, "error": str(error)}

    @app.delete("/api/projects/<project_id>/bindings/<binding_id>")
    async def remove_binding(request: Request, project_id: str, binding_id: str):
        try:
            model = get_project(project_id); before = len(model.get("bindings", [])); model["bindings"] = [item for item in model.get("bindings", []) if item.get("id") != binding_id]
            if len(model["bindings"]) == before: return {"ok": False, "error": "Binding not found"}
            return {"ok": True, "project": save_project(model, project_id)}
        except FileNotFoundError: return {"ok": False, "error": "Project not found"}
