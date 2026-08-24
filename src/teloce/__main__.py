"""
Teloce-Py command-line entry point.

Usage:
    python -m teloce [command] [options]
"""

import sys

from teloce.cli.main import main

if __name__ == "__main__":
    sys.exit(main())