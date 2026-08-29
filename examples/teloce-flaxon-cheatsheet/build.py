from pathlib import Path
from teloce.build import build_project

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    result = build_project(ROOT, options={"clean": True, "dev": True, "source_maps": True})
    print(f"Compiled {result['compiled']} .vel components")
