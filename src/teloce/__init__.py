"""
Teloce-Py - A Python compiler for Teloce .vel Single File Components

Teloce-Py transforms .vel files into self-contained vanilla JavaScript
without requiring Node.js, npm, or a CDN.
"""

from teloce.version import __version__

__all__ = [
    "__version__",
    "compile",
    "compile_file",
    "compile_project",
]

from teloce.compiler.compiler import compile, compile_file, compile_project
from teloce.ssr import render_ssr, to_jinax_template

__all__ = [
    "__version__",
    "compile",
    "compile_file",
    "compile_project",
    "render_ssr",
    "to_jinax_template",
]
