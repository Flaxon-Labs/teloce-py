"""
Template package for parsing Teloce templates.

Provides lexer, parser, and AST nodes for template processing.
"""

from teloce.template.lexer import TemplateLexer, Token, TokenType
from teloce.template.parser import TemplateParser
from teloce.template.expressions import ExpressionParser
from teloce.template.interpolation import InterpolationParser
from teloce.template.directives import DirectiveParser
from teloce.template.loops import LoopParser
from teloce.template.conditions import ConditionParser
from teloce.template.slots import SlotParser
from teloce.template.components import ComponentParser

__all__ = [
    "TemplateLexer",
    "Token",
    "TokenType",
    "TemplateParser",
    "ExpressionParser",
    "InterpolationParser",
    "DirectiveParser",
    "LoopParser",
    "ConditionParser",
    "SlotParser",
    "ComponentParser",
]