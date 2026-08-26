from pathlib import Path
from teloce.build import build_project

if __name__ == "__main__":
    result = build_project(Path(__file__).resolve().parent, options={"dev": True, "source_maps": True})
    print(f"Compiled {result['compiled']} component(s)")
