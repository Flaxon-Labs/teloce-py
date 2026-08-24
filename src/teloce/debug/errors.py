"""
Error handling for Teloce.

Provides error types, error codes, and error handling utilities.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict
import traceback


class ErrorCode(Enum):
    """Error codes for Teloce errors."""
    # Compiler errors
    COMPILER_ERROR = auto()
    LEXER_ERROR = auto()
    PARSER_ERROR = auto()
    AST_ERROR = auto()
    TRANSFORMER_ERROR = auto()
    OPTIMIZER_ERROR = auto()
    GENERATOR_ERROR = auto()
    
    # SFC errors
    SFC_PARSE_ERROR = auto()
    MISSING_TEMPLATE = auto()
    MISSING_SCRIPT = auto()
    MISSING_STYLE = auto()
    INVALID_SECTION = auto()
    
    # Template errors
    TEMPLATE_PARSE_ERROR = auto()
    INVALID_DIRECTIVE = auto()
    INVALID_EXPRESSION = auto()
    UNCLOSED_TAG = auto()
    UNCLOSED_INTERPOLATION = auto()
    
    # Directive errors
    INVALID_EVENT = auto()
    INVALID_BINDING = auto()
    INVALID_MODEL = auto()
    INVALID_FOR = auto()
    INVALID_IF = auto()
    
    # Component errors
    COMPONENT_NOT_FOUND = auto()
    COMPONENT_CYCLE = auto()
    COMPONENT_IMPORT_ERROR = auto()
    
    # Build errors
    BUILD_ERROR = auto()
    FILE_NOT_FOUND = auto()
    FILE_READ_ERROR = auto()
    FILE_WRITE_ERROR = auto()
    
    # Runtime errors
    RUNTIME_ERROR = auto()
    REACTIVITY_ERROR = auto()
    DOM_ERROR = auto()
    
    # Plugin errors
    PLUGIN_ERROR = auto()
    PLUGIN_NOT_FOUND = auto()
    PLUGIN_VERSION_MISMATCH = auto()


@dataclass
class TeloceError(Exception):
    """
    Base exception for Teloce errors.
    
    Attributes:
        code: The error code
        message: The error message
        file: The file where the error occurred
        line: The line number
        column: The column number
        details: Additional error details
    """
    code: ErrorCode
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    _stack: Optional[str] = None
    
    def __str__(self) -> str:
        """Get the string representation of the error."""
        location = ""
        if self.file:
            location = f"{self.file}"
            if self.line:
                location += f":{self.line}"
                if self.column:
                    location += f":{self.column}"
            location += " "
        
        return f"[{self.code.name}] {location}{self.message}"
    
    def get_stack(self) -> str:
        """Get the stack trace."""
        if self._stack is None:
            self._stack = traceback.format_exc()
        return self._stack
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code.name,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "details": self.details,
        }


class ErrorHandler:
    """
    Handles errors and exceptions in Teloce.
    
    Provides error logging, formatting, and recovery.
    """
    
    def __init__(self):
        self.errors: List[TeloceError] = []
        self.warnings: List[TeloceError] = []
    
    def add_error(self, code: ErrorCode, message: str, 
                  file: Optional[str] = None,
                  line: Optional[int] = None,
                  column: Optional[int] = None,
                  details: Optional[Dict[str, Any]] = None) -> TeloceError:
        """Add an error."""
        error = TeloceError(
            code=code,
            message=message,
            file=file,
            line=line,
            column=column,
            details=details
        )
        self.errors.append(error)
        return error
    
    def add_warning(self, code: ErrorCode, message: str,
                    file: Optional[str] = None,
                    line: Optional[int] = None,
                    column: Optional[int] = None,
                    details: Optional[Dict[str, Any]] = None) -> TeloceError:
        """Add a warning."""
        warning = TeloceError(
            code=code,
            message=message,
            file=file,
            line=line,
            column=column,
            details=details
        )
        self.warnings.append(warning)
        return warning
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def get_errors(self) -> List[TeloceError]:
        """Get all errors."""
        return self.errors.copy()
    
    def get_warnings(self) -> List[TeloceError]:
        """Get all warnings."""
        return self.warnings.copy()
    
    def clear(self) -> None:
        """Clear all errors and warnings."""
        self.errors.clear()
        self.warnings.clear()
    
    def get_summary(self) -> Dict[str, int]:
        """Get a summary of errors and warnings."""
        return {
            "errors": len(self.errors),
            "warnings": len(self.warnings),
        }
    
    def raise_if_errors(self) -> None:
        """Raise an exception if there are errors."""
        if self.errors:
            raise self.errors[0]