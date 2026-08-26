"""Project model persistence and migration service."""

from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from config.settings import WORKSPACE_ROOT
from backend.security.workspace_policy import contained, safe_project_id

DEFAULT_MODEL = {
    "schemaVersion": 1,
    "name": "My Flaxon App",
    "pages": [{"id": "home", "name": "Home", "path": "/", "file": "static/js/pages/Home.vel"}],
    "components": [],
    "routes": [],
    "bindings": [],
    "theme": {"primary": "#6c63ff", "background": "#0b1020"},
    "elements": [
        {"id": "hero", "type": "section", "label": "Hero section", "text": "Build with Teloce and Flaxon", "children": ["hero-title", "hero-copy", "hero-button"]},
        {"id": "hero-title", "parentId": "hero", "type": "heading", "label": "Heading", "text": "My Flaxon App"},
        {"id": "hero-copy", "parentId": "hero", "type": "text", "label": "Paragraph", "text": "A real editable application generated from a visual project model."},
        {"id": "hero-button", "parentId": "hero", "type": "button", "label": "Button", "text": "Get started"},
    ],
}


def _project_dir(project_id: str) -> Path:
    return contained(WORKSPACE_ROOT, WORKSPACE_ROOT / safe_project_id(project_id))


def model_path(project_id: str) -> Path:
    return _project_dir(project_id) / "teloce-studio.json"


def list_projects() -> list[dict]:
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    projects = []
    for path in sorted(WORKSPACE_ROOT.iterdir()):
        target = path / "teloce-studio.json"
        if path.is_dir() and target.is_file():
            try:
                model = json.loads(target.read_text(encoding="utf-8"))
                projects.append({"id": path.name, "name": model.get("name", path.name), "updatedAt": model.get("updatedAt")})
            except (OSError, ValueError, json.JSONDecodeError):
                continue
    return projects


def get_project(project_id: str) -> dict:
    path = model_path(project_id)
    if not path.is_file():
        raise FileNotFoundError(project_id)
    model = json.loads(path.read_text(encoding="utf-8"))
    model.setdefault("elements", [])
    model.setdefault("theme", {"primary": "#6c63ff", "background": "#0b1020"})
    model.setdefault("bindings", [])
    return model


def save_project(model: dict, project_id: str | None = None) -> dict:
    project_id = safe_project_id(project_id or model.get("id") or uuid4().hex[:12])
    model = {**DEFAULT_MODEL, **model, "id": project_id, "updatedAt": datetime.now(timezone.utc).isoformat()}
    if not isinstance(model.get("elements"), list):
        raise ValueError("elements must be a list")
    if not isinstance(model.get("bindings", []), list):
        raise ValueError("bindings must be a list")
    if len(json.dumps(model)) > 2_000_000:
        raise ValueError("Project model is too large")
    target = _project_dir(project_id)
    target.mkdir(parents=True, exist_ok=True)
    model_path(project_id).write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
    return model
