"""
Error formatter - formats errors for human-readable output.

Provides colorful, formatted error messages for the CLI.
"""

from typing import Optional, List, Dict, Any
import sys

from teloce.debug.errors import TeloceError, ErrorCode


class ErrorFormatter:
    """
    Formats errors for human-readable output.
    
    Provides colorful error messages with context.
    """
    
    def __init__(self, color: bool = True):
        self.color = color and self._supports_color()
        
        # Colors
        self.RED = '\033[91m' if self.color else ''
        self.GREEN = '\033[92m' if self.color else ''
        self.YELLOW = '\033[93m' if self.color else ''
        self.BLUE = '\033[94m' if self.color else ''
        self.MAGENTA = '\033[95m' if self.color else ''
        self.CYAN = '\033[96m' if self.color else ''
        self.WHITE = '\033[97m' if self.color else ''
        self.BOLD = '\033[1m' if self.color else ''
        self.UNDERLINE = '\033[4m' if self.color else ''
        self.RESET = '\033[0m' if self.color else ''
    
    def _as_error(self, error: Any) -> TeloceError:
        """Normalize compiler dictionaries and exception objects."""
        if isinstance(error, TeloceError):
            return error
        if isinstance(error, dict):
            code = error.get("code", ErrorCode.COMPILER_ERROR)
            if isinstance(code, str):
                code = ErrorCode.__members__.get(code, ErrorCode.COMPILER_ERROR)
            return TeloceError(code=code, message=str(error.get("message", error)),
                               file=error.get("file"), line=error.get("line"),
                               column=error.get("column"), details=error.get("details"))
        return TeloceError(ErrorCode.COMPILER_ERROR, str(error))

    def format_error(self, error: TeloceError) -> str:
        """
        Format a single error.
        
        Args:
            error: The error to format.
            
        Returns:
            A formatted error message.
        """
        lines = []
        
        # Header
        lines.append(f"{self.RED}{self.BOLD}Error{self.RESET}")
        lines.append("=" * 40)
        
        # Code and message
        lines.append(f"{self.BOLD}Code:{self.RESET} {error.code.name}")
        lines.append(f"{self.BOLD}Message:{self.RESET} {error.message}")
        
        # Location
        if error.file:
            location = error.file
            if error.line:
                location += f":{error.line}"
                if error.column:
                    location += f":{error.column}"
            lines.append(f"{self.BOLD}Location:{self.RESET} {location}")
        
        # Details
        if error.details:
            lines.append(f"{self.BOLD}Details:{self.RESET}")
            for key, value in error.details.items():
                lines.append(f"  {key}: {value}")
        
        # Stack trace
        if error._stack:
            lines.append(f"{self.BOLD}Stack:{self.RESET}")
            for line in error._stack.strip().split('\n'):
                lines.append(f"  {line}")
        
        return '\n'.join(lines)
    
    def format_multiple(self, errors: List[TeloceError], 
                        title: str = "Errors") -> str:
        """
        Format multiple errors.
        
        Args:
            errors: The list of errors.
            title: The title for the error list.
            
        Returns:
            A formatted error message.
        """
        if not errors:
            return ""
        
        lines = []
        lines.append(f"{self.RED}{self.BOLD}{title}{self.RESET}")
        lines.append("=" * 40)
        
        for i, raw_error in enumerate(errors, 1):
            error = self._as_error(raw_error)
            lines.append(f"{self.BOLD}{i}.{self.RESET} {error.message}")
            if error.file:
                location = error.file
                if error.line:
                    location += f":{error.line}"
                lines.append(f"   {self.BLUE}→{self.RESET} {location}")
        
        return '\n'.join(lines)
    
    def format_diagnostics(self, errors: List[TeloceError],
                           warnings: List[TeloceError]) -> str:
        """
        Format diagnostics with both errors and warnings.
        
        Args:
            errors: The list of errors.
            warnings: The list of warnings.
            
        Returns:
            A formatted diagnostic message.
        """
        lines = []
        
        if errors:
            lines.append(self.format_multiple(errors, "Errors"))
            lines.append("")
        
        if warnings:
            lines.append(self.format_multiple(warnings, "Warnings"))
            lines.append("")
        
        if not errors and not warnings:
            lines.append(f"{self.GREEN}✅ No issues found{self.RESET}")
        else:
            lines.append(f"{self.YELLOW}⚠️  {len(errors)} errors, {len(warnings)} warnings{self.RESET}")
        
        return '\n'.join(lines)
    
    def format_compiler_output(self, result: Dict[str, Any]) -> str:
        """
        Format compiler output.
        
        Args:
            result: The compiler result dictionary.
            
        Returns:
            A formatted compiler output.
        """
        lines = []
        
        if result.get('success'):
            lines.append(f"{self.GREEN}✅ Compilation successful{self.RESET}")
            stats = result.get('stats', {})
            lines.append(f"  {self.BOLD}Files:{self.RESET} {stats.get('files', 0)}")
            lines.append(f"  {self.BOLD}Time:{self.RESET} {stats.get('time', 0):.2f}ms")
        else:
            lines.append(f"{self.RED}❌ Compilation failed{self.RESET}")
        
        diagnostics = result.get('diagnostics', {})
        if diagnostics.get('errors'):
            lines.append("")
            lines.append(self.format_multiple(diagnostics['errors'], "Errors"))
        
        if diagnostics.get('warnings'):
            lines.append("")
            lines.append(self.format_multiple(diagnostics['warnings'], "Warnings"))
        
        return '\n'.join(lines)
    
    def _supports_color(self) -> bool:
        """Check if the terminal supports color."""
        if hasattr(sys.stdout, 'isatty'):
            return sys.stdout.isatty()
        return False
