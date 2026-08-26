from pathlib import Path
import shutil
from teloce.build import build_project

ROOT = Path(__file__).resolve().parent


def patch_loop_conditions(dist: Path) -> None:
    """Keep v-if conditions scoped correctly when combined with v-for.

    The Studio canvas intentionally uses this common composition. Until the
    compiler runtime ships the upstream fix, patch the generated runtime
    bundle during the Studio build so loop-local conditions are evaluated with
    the loop scope instead of the parent state.
    """
    old = r'''const nested = __renderLoops(body, loopScope); return nested.replace(/{{\s*([^{}]+?)\s*}}/g, (_, expression) => { const result = __evaluate(expression, loopScope); return result == null ? "" : __escapeHtml(String(result)); });'''
    new = r'''const nested = __renderLoops(body, loopScope); return nested.replace(/<if\s+[^>]*?(?:condition|test)="([^"]*)"[^>]*>([\s\S]*?)(?:<else>([\s\S]*?))?<\/if>/g, (_, test, yes, no) => __evaluate(test, loopScope) ? yes : (no || "")).replace(/{{\s*([^{}]+?)\s*}}/g, (_, expression) => { const result = __evaluate(expression, loopScope); return result == null ? "" : __escapeHtml(String(result)); });'''
    for file in dist.rglob("*.js"):
        source = file.read_text(encoding="utf-8")
        updated = source.replace(old, new)
        if updated != source:
            file.write_text(updated, encoding="utf-8")

def build_frontend():
    shutil.rmtree(ROOT / "public", ignore_errors=True)
    result = build_project(ROOT / "editor", options={"dev": False, "source_maps": False})
    public, dist = ROOT / "public", ROOT / "editor" / "dist"
    patch_loop_conditions(dist)
    public.mkdir(parents=True, exist_ok=True)
    for source in (dist / "static", dist / "public"):
        if not source.exists(): continue
        target = public / "static" if source.name == "static" else public
        for item in source.rglob("*"):
            if item.is_file():
                destination = target / item.relative_to(source); destination.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(item, destination)
    for name in ("manifest.webmanifest", "sw.js", "offline.html"):
        source = ROOT / "editor" / "public" / name
        if source.exists(): shutil.copy2(source, public / name)
    return result

if __name__ == "__main__": print(build_frontend())
