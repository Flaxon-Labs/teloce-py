import json
from pathlib import Path

from backend.services import project_service
from backend.services.generation_service import generate_project


def test_project_model_and_generation_are_portable(tmp_path, monkeypatch):
    monkeypatch.setattr(project_service, "WORKSPACE_ROOT", tmp_path)
    model = project_service.save_project({"name": "Demo Builder"}, "demo")
    result = generate_project(model)
    root = tmp_path / "demo"
    assert result["ok"] is True
    assert (root / "teloce-studio.json").is_file()
    assert (root / "static/js/App.vel").is_file()
    assert (root / "static/js/pages/Home.vel").is_file()
    assert json.loads((root / "teloce-studio.json").read_text()) ["name"] == "Demo Builder"


def test_project_id_rejects_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(project_service, "WORKSPACE_ROOT", tmp_path)
    try:
        project_service.save_project({"name": "Unsafe"}, "../outside")
    except ValueError as error:
        assert "Invalid project id" in str(error)
    else:
        raise AssertionError("path traversal id was accepted")


def test_generation_includes_visual_api_bindings(tmp_path, monkeypatch):
    monkeypatch.setattr(project_service, "WORKSPACE_ROOT", tmp_path)
    model = project_service.save_project({"name": "API Builder", "bindings": [{"name": "Tasks", "method": "GET", "path": "/api/tasks", "response": {"ok": True, "data": []}}]}, "api-demo")
    generate_project(model)
    source = (tmp_path / "api-demo" / "app.py").read_text(encoding="utf-8")
    assert "@app.get('/api/tasks')" in source or '@app.get("/api/tasks")' in source
    assert "generated_api_0" in source
