"""Bundled browser runtime assets for generated Teloce components."""

from pathlib import Path

RUNTIME_DIR = Path(__file__).parent
STANDALONE_RUNTIME = RUNTIME_DIR / "standalone.js"

__all__ = ["RUNTIME_DIR", "STANDALONE_RUNTIME"]
