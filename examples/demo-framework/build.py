from pathlib import Path

from teloce.build import build_project


if __name__ == "__main__":
    result = build_project(
        Path(__file__).resolve().parent,
        options={"dev": True, "clean": True, "source_maps": True, "shared_runtime": True},
    )
    if result["failed"]:
        raise SystemExit("\n".join(result["errors"]))
    print(f"Compiled {result['compiled']} component(s)")
