"""Project, path, component, and generated-code validation."""

ALLOWED_TYPES = {"section", "heading", "text", "button", "image", "card", "container"}


def validate_project(model: dict) -> list[dict]:
    issues = []
    if not str(model.get("name", "")).strip(): issues.append({"level": "error", "message": "Project name is required."})
    ids = set()
    for element in model.get("elements", []):
        element_id = element.get("id")
        if not element_id or element_id in ids: issues.append({"level": "error", "message": "Every element needs a unique id."})
        ids.add(element_id)
        if element.get("type") not in ALLOWED_TYPES: issues.append({"level": "error", "message": f"Unsupported element type: {element.get('type')}"})
    return issues
