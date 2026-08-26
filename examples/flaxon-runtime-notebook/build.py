from importlib.resources import files
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def copy_runtime() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    source = files("teloce.runtime").joinpath("standalone.js")
    destination = DIST / "teloce-standalone.js"
    with source.open("rb") as input_file, destination.open("wb") as output_file:
        shutil.copyfileobj(input_file, output_file)


if __name__ == "__main__":
    copy_runtime()
    print(f"Copied Teloce runtime to {DIST / 'teloce-standalone.js'}")
