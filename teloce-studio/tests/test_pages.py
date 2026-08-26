from flaxon.testing import TestClient

import app as studio_app
from backend.services import project_service


def test_pages_are_real_project_resources(tmp_path, monkeypatch):
    monkeypatch.setattr(project_service, "WORKSPACE_ROOT", tmp_path)
    client = TestClient(studio_app.app)
    project = client.post("/api/projects", json_data={"name": "Pages"}).json()["project"]
    project_id = project["id"]
    added = client.post(f"/api/projects/{project_id}/pages", json_data={"name": "About", "path": "/about"})
    assert added.json()["ok"] is True
    assert len(added.json()["project"]["pages"]) == 2
    generated = client.post(f"/api/projects/{project_id}/generate").json()
    assert generated["ok"] is True
    assert any(path.lower().endswith("about.vel") for path in generated["files"])
    page_id = added.json()["page"]["id"]
    assert client.delete(f"/api/projects/{project_id}/pages/{page_id}").json()["ok"] is True
