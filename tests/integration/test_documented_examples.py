from pathlib import Path

import pytest

from teloce.compiler import compile_file


ROOT = Path(__file__).parents[2]
EXAMPLES = {
    "flask-chat": "Flask",
    "fastapi-cms": "FastAPI",
    "django-scanner": "Django",
    "flaxon-network": "Flaxon",
}


@pytest.mark.parametrize("name", EXAMPLES)
def test_real_world_example_has_server_shell_and_compilable_component(name):
    example = ROOT / "examples" / name
    assert (example / "README.md").exists()
    assert (example / "requirements.txt").exists()
    assert list(example.rglob("*.py"))
    components = list((example / "static" / "js").rglob("*.vel"))
    assert components, f"{name} must contain a .vel component"
    for component in components:
        result = compile_file(component)
        assert result["success"], result["diagnostics"]
        assert result["code"]
        assert "Teloce" in result["code"] or "teloce" in result["code"]


def test_readme_links_to_all_real_world_examples():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name in EXAMPLES:
        assert f"examples/{name}" in readme


def test_every_documentation_page_has_content_and_python_app_workflow():
    pages = list((ROOT / "docs").glob("*.md"))
    assert pages
    assert all(page.read_text(encoding="utf-8").strip() for page in pages)
    getting_started = (ROOT / "docs" / "getting-started.md").read_text(encoding="utf-8")
    assert "python app.py" in getting_started
    assert "App.vel" in getting_started
