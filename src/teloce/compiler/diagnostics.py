"""
Diagnostics and error reporting.

Provides structured error and warning reporting for the compiler.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


class DiagnosticLevel(Enum):
    """Diagnostic severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass
class Diagnostic:
    """A diagnostic message."""
    level: DiagnosticLevel
    message: str
    filename: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    code: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


class Diagnostics:
    """
    Collects and manages diagnostic messages.
    """
    
    def __init__(self):
        self.diagnostics: List[Diagnostic] = []
    
    def add(self, level: DiagnosticLevel, message: str, **kwargs) -> None:
        """
        Add a diagnostic message.
        
        Args:
            level: The severity level
            message: The diagnostic message
            **kwargs: Additional fields (filename, line, column, code, suggestions, notes)
        """
        self.diagnostics.append(Diagnostic(level, message, **kwargs))
    
    def error(self, message: str, **kwargs) -> None:
        """Add an error diagnostic."""
        self.add(DiagnosticLevel.ERROR, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Add a warning diagnostic."""
        self.add(DiagnosticLevel.WARNING, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Add an info diagnostic."""
        self.add(DiagnosticLevel.INFO, message, **kwargs)
    
    def hint(self, message: str, **kwargs) -> None:
        """Add a hint diagnostic."""
        self.add(DiagnosticLevel.HINT, message, **kwargs)
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return any(d.level == DiagnosticLevel.ERROR for d in self.diagnostics)
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return any(d.level == DiagnosticLevel.WARNING for d in self.diagnostics)
    
    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Convert diagnostics to a dictionary."""
        result = {"errors": [], "warnings": [], "info": [], "hints": []}
        
        for d in self.diagnostics:
            entry = {
                "message": d.message,
                "filename": d.filename,
                "line": d.line,
                "column": d.column,
                "code": d.code,
                "suggestions": d.suggestions,
                "notes": d.notes,
            }
            
            if d.level == DiagnosticLevel.ERROR:
                result["errors"].append(entry)
            elif d.level == DiagnosticLevel.WARNING:
                result["warnings"].append(entry)
            elif d.level == DiagnosticLevel.INFO:
                result["info"].append(entry)
            elif d.level == DiagnosticLevel.HINT:
                result["hints"].append(entry)
        
        return result
    
    def __len__(self) -> int:
        return len(self.diagnostics)
    
    def __iter__(self):
        return iter(self.diagnostics)
    
    def __str__(self) -> str:
        lines = []
        for d in self.diagnostics:
            location = ""
            if d.filename:
                location = f"{d.filename}"
                if d.line:
                    location += f":{d.line}"
                    if d.column:
                        location += f":{d.column}"
                location += " "
            
            level_str = d.level.value.upper()
            lines.append(f"[{level_str}] {location}{d.message}")
            
            if d.suggestions:
                lines.append("  Suggestion: " + d.suggestions[0])
            if d.notes:
                for note in d.notes:
                    lines.append(f"  Note: {note}")
        
        return "\n".join(lines)