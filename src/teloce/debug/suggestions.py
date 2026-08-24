"""
Suggestion engine - provides suggestions for fixing errors.

Generates helpful suggestions for common errors.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from teloce.debug.errors import TeloceError, ErrorCode


@dataclass
class Suggestion:
    """A suggestion for fixing an error."""
    text: str
    code: Optional[str] = None
    priority: int = 0
    explanation: Optional[str] = None
    docs_url: Optional[str] = None


class SuggestionEngine:
    """
    Suggestion engine for errors.
    
    Generates helpful suggestions for fixing errors.
    """
    
    def __init__(self):
        self.suggestions: Dict[ErrorCode, List[Suggestion]] = {}
        self._register_suggestions()
    
    def _register_suggestions(self) -> None:
        """Register all built-in suggestions."""
        # Missing template
        self.suggestions[ErrorCode.MISSING_TEMPLATE] = [
            Suggestion(
                text="Add a <template> section to your .vel file",
                code="<template>\n  <div>Hello World</div>\n</template>",
                priority=10,
                explanation="Every .vel file must have a <template> section",
                docs_url="/docs/sfc#template"
            )
        ]
        
        # Missing script
        self.suggestions[ErrorCode.MISSING_SCRIPT] = [
            Suggestion(
                text="Add a <script> section to your .vel file",
                code="<script>\nexport default {\n  data() {\n    return {}\n  }\n}\n</script>",
                priority=9,
                explanation="Add a <script> section with a default export",
                docs_url="/docs/sfc#script"
            )
        ]
        
        # Invalid directive
        self.suggestions[ErrorCode.INVALID_DIRECTIVE] = [
            Suggestion(
                text="Check the directive syntax",
                code="@click=\"handler\"",
                priority=8,
                explanation="Directives should start with @ for events or : for bindings",
                docs_url="/docs/directives"
            ),
            Suggestion(
                text="Make sure the directive is registered",
                priority=7,
                explanation="Custom directives must be registered before use",
                docs_url="/docs/plugins/directives"
            )
        ]
        
        # Invalid expression
        self.suggestions[ErrorCode.INVALID_EXPRESSION] = [
            Suggestion(
                text="Check your JavaScript syntax",
                code="count + 1",
                priority=10,
                explanation="Expressions must be valid JavaScript",
                docs_url="/docs/expressions"
            ),
            Suggestion(
                text="Make sure variables are defined",
                priority=9,
                explanation="Variables used in expressions must be defined in data or computed",
                docs_url="/docs/reactivity"
            )
        ]
        
        # Unclosed tag
        self.suggestions[ErrorCode.UNCLOSED_TAG] = [
            Suggestion(
                text="Add a closing tag",
                code="</div>",
                priority=10,
                explanation="Every opening tag must have a corresponding closing tag",
                docs_url="/docs/templates"
            )
        ]
        
        # Component not found
        self.suggestions[ErrorCode.COMPONENT_NOT_FOUND] = [
            Suggestion(
                text="Import the component",
                code="import MyComponent from './components/MyComponent.vel'",
                priority=10,
                explanation="Components must be imported before use",
                docs_url="/docs/components"
            ),
            Suggestion(
                text="Register the component",
                code="components: { MyComponent }",
                priority=9,
                explanation="Components must be registered in the components option",
                docs_url="/docs/components#registration"
            )
        ]
        
        # Invalid event
        self.suggestions[ErrorCode.INVALID_EVENT] = [
            Suggestion(
                text="Use a valid event name",
                code="@click, @submit, @input, @change, @keyup, @focus, @blur",
                priority=10,
                explanation="Only supported events can be used",
                docs_url="/docs/events"
            )
        ]
        
        # Invalid binding
        self.suggestions[ErrorCode.INVALID_BINDING] = [
            Suggestion(
                text="Use a valid binding name",
                code=":model, :class, :style, :show, :hide",
                priority=10,
                explanation="Only supported bindings can be used",
                docs_url="/docs/bindings"
            )
        ]
        
        # Invalid for
        self.suggestions[ErrorCode.INVALID_FOR] = [
            Suggestion(
                text="Use the correct for syntax",
                code="<for item in items key=\"id\">",
                priority=10,
                explanation="For loops must have item and collection",
                docs_url="/docs/loops"
            )
        ]
        
        # Invalid if
        self.suggestions[ErrorCode.INVALID_IF] = [
            Suggestion(
                text="Use the correct if syntax",
                code="<if condition=\"isLoggedIn\">",
                priority=10,
                explanation="If statements must have a condition",
                docs_url="/docs/conditions"
            )
        ]
    
    def get_suggestions(self, error: TeloceError) -> List[Suggestion]:
        """
        Get suggestions for an error.
        
        Args:
            error: The error to get suggestions for.
            
        Returns:
            A list of suggestions.
        """
        return self.suggestions.get(error.code, [])
    
    def get_best_suggestion(self, error: TeloceError) -> Optional[Suggestion]:
        """
        Get the best suggestion for an error.
        
        Args:
            error: The error to get a suggestion for.
            
        Returns:
            The best suggestion or None.
        """
        suggestions = self.get_suggestions(error)
        if not suggestions:
            return None
        
        # Return the suggestion with the highest priority
        return max(suggestions, key=lambda s: s.priority)
    
    def add_suggestion(self, error_code: ErrorCode, suggestion: Suggestion) -> None:
        """
        Add a custom suggestion.
        
        Args:
            error_code: The error code.
            suggestion: The suggestion to add.
        """
        if error_code not in self.suggestions:
            self.suggestions[error_code] = []
        self.suggestions[error_code].append(suggestion)
    
    def format_suggestions(self, error: TeloceError) -> str:
        """
        Format suggestions for an error.
        
        Args:
            error: The error to format suggestions for.
            
        Returns:
            A formatted string of suggestions.
        """
        suggestions = self.get_suggestions(error)
        if not suggestions:
            return ""
        
        lines = []
        lines.append("💡 Suggestions:")
        
        for i, suggestion in enumerate(suggestions, 1):
            lines.append(f"  {i}. {suggestion.text}")
            if suggestion.code:
                lines.append(f"     {suggestion.code}")
            if suggestion.explanation:
                lines.append(f"     → {suggestion.explanation}")
        
        return '\n'.join(lines)