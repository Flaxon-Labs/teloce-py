"""Central settings boundary for the Studio host and preview workers."""

from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path(os.getenv("TELOCE_STUDIO_WORKSPACE", ROOT / "workspace")).resolve()
MAX_PROJECT_BYTES = int(os.getenv("TELOCE_STUDIO_MAX_PROJECT_BYTES", "2000000"))
