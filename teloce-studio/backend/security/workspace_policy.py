"""Path traversal, allowed-file, and workspace isolation policy."""

from pathlib import Path

ALLOWED_SOURCE_SUFFIXES = {".vel", ".css", ".py", ".json", ".html", ".md"}


def safe_project_id(value: str) -> str:
    cleaned = "".join(character for character in str(value) if character.isalnum() or character in "-_")
    if not cleaned or cleaned != str(value) or len(cleaned) > 64:
        raise ValueError("Invalid project id")
    return cleaned


def contained(root: Path, candidate: Path) -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    if root != candidate and root not in candidate.parents:
        raise ValueError("Path escapes the Studio workspace")
    return candidate


def allowed_source(path: Path) -> bool:
    return path.suffix.lower() in ALLOWED_SOURCE_SUFFIXES
