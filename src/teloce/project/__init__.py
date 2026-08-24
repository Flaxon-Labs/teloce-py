"""
Project package for Teloce.

Handles project discovery, scanning, configuration, and paths.
"""

from teloce.project.scanner import ProjectScanner
from teloce.project.discovery import ProjectDiscovery
from teloce.project.configuration import ProjectConfiguration
from teloce.project.paths import ProjectPaths

__all__ = [
    "ProjectScanner",
    "ProjectDiscovery",
    "ProjectConfiguration",
    "ProjectPaths",
]