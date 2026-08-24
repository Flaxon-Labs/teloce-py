"""
Debug package for Teloce.

Provides debugging utilities including error handling, formatting, and suggestions.
"""

from teloce.debug.errors import ErrorHandler, TeloceError, ErrorCode
from teloce.debug.formatter import ErrorFormatter
from teloce.debug.suggestions import SuggestionEngine, Suggestion

__all__ = [
    "ErrorHandler",
    "TeloceError",
    "ErrorCode",
    "ErrorFormatter",
    "SuggestionEngine",
    "Suggestion",
]