"""
Teloce-Py compiler package.

The compiler transforms .vel Single File Components into JavaScript.
"""

from teloce.compiler.compiler import compile, compile_file, compile_project
from teloce.compiler.lexer import Lexer, Token, TokenType
from teloce.compiler.parser import Parser
from teloce.compiler.transformer import Transformer
from teloce.compiler.optimizer import Optimizer
from teloce.compiler.generator import Generator
from teloce.compiler.source_map import SourceMapGenerator
from teloce.compiler.diagnostics import Diagnostic, DiagnosticLevel, Diagnostics

__all__ = [
    "compile",
    "compile_file",
    "compile_project",
    "Lexer",
    "Token",
    "TokenType",
    "Parser",
    "Transformer",
    "Optimizer",
    "Generator",
    "SourceMapGenerator",
    "Diagnostic",
    "DiagnosticLevel",
    "Diagnostics",
]