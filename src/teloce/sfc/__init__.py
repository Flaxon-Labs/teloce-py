"""
SFC (Single File Component) package.

Parses .vel files into component structures.
"""

from teloce.sfc.parser import SFCParser, parse_sfc, parse_sfc_result
from teloce.sfc.component import Component, ComponentScript, ComponentStyle
from teloce.sfc.sections import SFCSections
from teloce.sfc.script import ScriptParser
from teloce.sfc.template import TemplateParser
from teloce.sfc.style import StyleParser

__all__ = [
    "SFCParser",
    "parse_sfc",
    "parse_sfc_result",
    "Component",
    "ComponentScript",
    "ComponentStyle",
    "SFCSections",
    "ScriptParser",
    "TemplateParser",
    "StyleParser",
]
