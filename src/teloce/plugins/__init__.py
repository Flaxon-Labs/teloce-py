"""
Plugins package for Teloce.

Provides plugin system for extending Teloce.
"""

from teloce.plugins.api import PluginAPI, Plugin
from teloce.plugins.registry import PluginRegistry
from teloce.plugins.directives import DirectivePlugin
from teloce.plugins.filters import FilterPlugin
from teloce.plugins.hooks import HookPlugin, Hook

__all__ = [
    "PluginAPI",
    "Plugin",
    "PluginRegistry",
    "DirectivePlugin",
    "FilterPlugin",
    "HookPlugin",
    "Hook",
]