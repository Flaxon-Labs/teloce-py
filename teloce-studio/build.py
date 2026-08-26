from pathlib import Path
import shutil
from teloce.build import build_project

ROOT = Path(__file__).resolve().parent

def build_frontend():
    shutil.rmtree(ROOT / "public", ignore_errors=True)
    result = build_project(ROOT / "editor", options={"dev": False, "source_maps": False})
    public, dist = ROOT / "public", ROOT / "editor" / "dist"
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
