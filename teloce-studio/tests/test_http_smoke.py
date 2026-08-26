from flaxon.testing import TestClient

import app as studio_app
from backend.services import project_service


def test_studio_http_project_generation_flow(tmp_path, monkeypatch):
    monkeypatch.setattr(project_service, "WORKSPACE_ROOT", tmp_path)
    client = TestClient(studio_app.app)
    health = client.get("/api/health")
    assert health.status_code == 200
    created = client.post("/api/projects", json_data={"name": "Smoke App"})
    assert created.status_code == 200
    project = created.json()["project"]
    generated = client.post(f"/api/projects/{project['id']}/generate")
    assert generated.status_code == 200
    assert generated.json()["ok"] is True
    preview = client.get(f"/api/projects/{project['id']}/preview")
    assert preview.status_code == 200
    assert preview.json()["ok"] is True
    preview_page = client.get(f"/api/projects/{project['id']}/preview/page")
    assert preview_page.status_code == 200
    assert "/preview/files/" in preview_page.text
    preview_asset = client.get(f"/api/projects/{project['id']}/preview/files/static/js/App.js")
    assert preview_asset.status_code == 200
    exported = client.get(f"/api/projects/{project['id']}/export")
    assert exported.status_code == 200
    assert exported.headers["content-type"] == "application/zip"
