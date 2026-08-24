"""
CLI package for Teloce.

Provides command-line interface for Teloce.
"""

from teloce.cli.main import main
from teloce.cli.dev import dev_command
from teloce.cli.build import build_command
from teloce.cli.watch import watch_command
from teloce.cli.debug import debug_command
from teloce.cli.doctor import doctor_command
from teloce.cli.lint import lint_command
from teloce.cli.create import create_command

__all__ = [
    "main",
    "dev_command",
    "build_command",
    "watch_command",
    "debug_command",
    "doctor_command",
    "lint_command",
    "create_command",
]