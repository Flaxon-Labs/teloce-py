import json
from urllib.request import urlopen

from teloce.debug.dashboard import DebuggerDashboard


def get_json(url):
    with urlopen(url, timeout=3) as response:
        return json.loads(response.read().decode("utf-8"))


def test_debugger_dashboard_serves_project_and_diagnostics(tmp_path):
    component_dir = tmp_path / "static" / "js"
    component_dir.mkdir(parents=True)
    (component_dir / "App.vel").write_text(
        "<template><h1>{{ title }}</h1></template>\n"
        "<script>export default { data() { return { title: 'Dashboard' }; } };</script>",
        encoding="utf-8",
    )

    dashboard = DebuggerDashboard(tmp_path, host="127.0.0.1", port=0)
    dashboard.start()
    try:
        with urlopen(dashboard.url, timeout=3) as response:
            assert "Teloce Debugger" in response.read().decode("utf-8")
        health = get_json(f"{dashboard.url}/api/health")
        assert health["ok"] is True
        project = get_json(f"{dashboard.url}/api/project")
        assert project["components"] == ["static/js/App.vel"]
        diagnostics = get_json(f"{dashboard.url}/api/diagnostics")
        assert diagnostics["total"] == 1
        assert diagnostics["passed"] == 1
        assert diagnostics["errors"] == 0
    finally:
        dashboard.close()
