"""
Template lexer - tokenizes Teloce template source code.
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Tuple


class TokenType(Enum):
    """Token types for template lexer."""
    # HTML
    OPEN_TAG = auto()
    CLOSE_TAG = auto()
    SELF_CLOSE_TAG = auto()
    TEXT = auto()
    COMMENT = auto()
    DOCTYPE = auto()
    
    # Attributes
    ATTRIBUTE_NAME = auto()
    ATTRIBUTE_VALUE = auto()
    EQUALS = auto()
    
    # Teloce directives
    INTERPOLATION_START = auto()  # {{
    INTERPOLATION_END = auto()    # }}
    INTERPOLATION_EXPR = auto()   # expression inside {{ }}
    
    FOR_START = auto()            # <for
    FOR_END = auto()              # </for>
    IF_START = auto()             # <if
    IF_END = auto()               # </if>
    ELSE = auto()                 # <else>
    ELSE_IF = auto()              # <else if>
    
    # Event bindings
    EVENT = auto()                # @click
    EVENT_NAME = auto()           # click
    
    # Property bindings
    BIND = auto()                 # :
    BIND_NAME = auto()            # model, class, style
    
    # Special
    EOF = auto()


@dataclass
class Token:
    """Represents a token."""
    type: TokenType
    value: str
    line: int = 0
    column: int = 0
    
    def __repr__(self) -> str:
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.column})"


class TemplateLexer:
    """
    Lexer for Teloce templates.
    
    Converts template source into tokens.
    """
    
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.errors: List[str] = []
    
    def tokenize(self) -> List[Token]:
        """Tokenize the source string."""
        self.tokens = []
        self.errors = []
        self.position = 0
        self.line = 1
        self.column = 1
        
        while self.position < len(self.source):
            char = self._current_char()
            
            # Skip whitespace (but preserve for text)
            if char.isspace() and not self._is_in_text():
                self._advance()
                continue
            
            # HTML comments
            if char == '<' and self._peek(1) == '!' and self._peek(2) == '-' and self._peek(3) == '-':
                self._tokenize_comment()
                continue
            
            # DOCTYPE
            if char == '<' and self._peek(1) == '!' and self._peek(2).upper() == 'D':
                self._tokenize_doctype()
                continue
            
            # Tags
            if char == '<':
                self._tokenize_tag()
                continue
            
            # Interpolation
            if char == '{' and self._peek(1) == '{':
                self._tokenize_interpolation()
                continue
            
            # Closing braces (handled by interpolation)
            if char == '}' and self._peek(1) == '}':
                self._advance()
                self._advance()
                continue
            
            # Text
            self._tokenize_text()
        
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens
    
    def _tokenize_tag(self):
        """Tokenize an HTML or Teloce tag."""
        start_line = self.line
        start_col = self.column
        
        self._advance()  # Skip '<'
        
        # Check for closing tag
        if self._current_char() == '/':
            self._advance()
            tag_name = self._read_identifier()
            
            # Check for directive closing
            if tag_name == 'for':
                self.tokens.append(Token(TokenType.FOR_END, f"</{tag_name}>", start_line, start_col))
            elif tag_name == 'if':
                self.tokens.append(Token(TokenType.IF_END, f"</{tag_name}>", start_line, start_col))
            elif tag_name == 'else':
                self.tokens.append(Token(TokenType.ELSE, f"</{tag_name}>", start_line, start_col))
            else:
                self.tokens.append(Token(TokenType.CLOSE_TAG, f"</{tag_name}>", start_line, start_col))
            
            self._skip_until('>')
            self._advance()  # Skip '>'
            return
        
        # Read tag name
        tag_name = self._read_identifier()
        
        # Check for directives
        if tag_name == 'for':
            self.tokens.append(Token(TokenType.FOR_START, tag_name, start_line, start_col))
            self._tokenize_attributes()
            self._skip_until('>')
            self._advance()
            return
        elif tag_name == 'if':
            self.tokens.append(Token(TokenType.IF_START, tag_name, start_line, start_col))
            self._tokenize_attributes()
            self._skip_until('>')
            self._advance()
            return
        elif tag_name == 'else':
            self.tokens.append(Token(TokenType.ELSE, tag_name, start_line, start_col))
            self._skip_until('>')
            self._advance()
            return
        elif tag_name == 'else' and self._peek(1) == 'i' and self._peek(2) == 'f':
            # else if
            self.tokens.append(Token(TokenType.ELSE_IF, tag_name, start_line, start_col))
            self._advance()  # skip 'e'
            self._advance()  # skip 'l'
            self._advance()  # skip 's'
            self._advance()  # skip 'e'
            self._advance()  # skip ' '
            self._advance()  # skip 'i'
            self._advance()  # skip 'f'
            self._tokenize_attributes()
            self._skip_until('>')
            self._advance()
            return
        
        # Regular tag
        self.tokens.append(Token(TokenType.OPEN_TAG, tag_name, start_line, start_col))
        self._tokenize_attributes()
        
        # Check for self-closing
        if self._current_char() == '/':
            self.tokens.append(Token(TokenType.SELF_CLOSE_TAG, '/', self.line, self.column))
            self._advance()
        
        self._skip_until('>')
        self._advance()  # Skip '>'
    
    def _tokenize_attributes(self):
        """Tokenize tag attributes."""
        while self.position < len(self.source):
            char = self._current_char()
            
            # Skip whitespace
            if char.isspace():
                self._advance()
                continue
            
            if char == '>' or char == '/':
                break
            
            # Event binding (@click)
            if char == '@':
                self._advance()
                event_name = self._read_identifier()
                self.tokens.append(Token(TokenType.EVENT, f"@{event_name}", self.line, self.column))
                self._tokenize_attribute_value()
                continue
            
            # Property binding (:model)
            if char == ':':
                self._advance()
                bind_name = self._read_identifier()
                self.tokens.append(Token(TokenType.BIND, f":{bind_name}", self.line, self.column))
                self._tokenize_attribute_value()
                continue
            
            # Regular attribute
            attr_name = self._read_identifier()
            self.tokens.append(Token(TokenType.ATTRIBUTE_NAME, attr_name, self.line, self.column))
            
            if self._current_char() == '=':
                self._advance()
                self._tokenize_attribute_value()
    
    def _tokenize_attribute_value(self):
        """Tokenize an attribute value."""
        char = self._current_char()
        
        if char == '"':
            self._advance()
            value = self._read_until('"')
            if self._current_char() == '"':
                self._advance()
            self.tokens.append(Token(TokenType.ATTRIBUTE_VALUE, value, self.line, self.column))
        elif char == "'":
            self._advance()
            value = self._read_until("'")
            if self._current_char() == "'":
                self._advance()
            self.tokens.append(Token(TokenType.ATTRIBUTE_VALUE, value, self.line, self.column))
        else:
            # Unquoted value
            value = self._read_until_whitespace()
            if value:
                self.tokens.append(Token(TokenType.ATTRIBUTE_VALUE, value, self.line, self.column))
    
    def _tokenize_interpolation(self):
        """Tokenize an interpolation {{ expression }}."""
        start_line = self.line
        start_col = self.column
        
        self._advance()  # Skip '{'
        self._advance()  # Skip '{'
        
        self.tokens.append(Token(TokenType.INTERPOLATION_START, '{{', start_line, start_col))
        
        # Read expression
        expression = self._read_until('}}')
        expression = expression.strip()
        
        if expression:
            self.tokens.append(Token(TokenType.INTERPOLATION_EXPR, expression, self.line, self.column))
        
        # Skip closing braces
        if self._current_char() == '}':
            self._advance()
            if self._current_char() == '}':
                self._advance()
        
        self.tokens.append(Token(TokenType.INTERPOLATION_END, '}}', self.line, self.column))
    
    def _tokenize_text(self):
        """Tokenize plain text."""
        start_line = self.line
        start_col = self.column
        text = ""
        
        while self.position < len(self.source):
            char = self._current_char()
            
            # Stop at tag or interpolation
            if char == '<':
                if self._peek(1).isalpha() or self._peek(1) == '/' or self._peek(1) == '!':
                    break
            if char == '{' and self._peek(1) == '{':
                break
            
            text += char
            self._advance()
        
        if text.strip():
            self.tokens.append(Token(TokenType.TEXT, text, start_line, start_col))
    
    def _tokenize_comment(self):
        """Tokenize an HTML comment."""
        start_line = self.line
        start_col = self.column
        
        self._advance()  # Skip '<'
        self._advance()  # Skip '!'
        self._advance()  # Skip '-'
        self._advance()  # Skip '-'
        
        comment = ""
        while self.position < len(self.source):
            char = self._current_char()
            if char == '-' and self._peek(1) == '-' and self._peek(2) == '>':
                self._advance()
                self._advance()
                self._advance()
                break
            comment += char
            self._advance()
        
        self.tokens.append(Token(TokenType.COMMENT, comment, start_line, start_col))
    
    def _tokenize_doctype(self):
        """Tokenize a DOCTYPE declaration."""
        start_line = self.line
        start_col = self.column
        
        doctype = ""
        while self.position < len(self.source):
            char = self._current_char()
            if char == '>':
                doctype += char
                self._advance()
                break
            doctype += char
            self._advance()
        
        self.tokens.append(Token(TokenType.DOCTYPE, doctype, start_line, start_col))
    
    def _read_identifier(self) -> str:
        """Read an identifier."""
        start = self.position
        while self.position < len(self.source):
            char = self._current_char()
            if not (char.isalnum() or char in '-_:'):
                break
            self._advance()
        return self.source[start:self.position]
    
    def _read_until(self, delimiter: str) -> str:
        """Read until a delimiter is found."""
        start = self.position
        while self.position < len(self.source):
            char = self._current_char()
            if char == delimiter[0] and self.source.startswith(delimiter, self.position):
                break
            self._advance()
        return self.source[start:self.position]
    
    def _read_until_whitespace(self) -> str:
        """Read until whitespace is found."""
        start = self.position
        while self.position < len(self.source):
            char = self._current_char()
            if char.isspace() or char == '>' or char == '/':
                break
            self._advance()
        return self.source[start:self.position]
    
    def _skip_until(self, delimiter: str):
        """Skip until a delimiter is found."""
        while self.position < len(self.source):
            char = self._current_char()
            if char == delimiter[0] and self.source.startswith(delimiter, self.position):
                break
            self._advance()
    
    def _current_char(self) -> str:
        """Get the current character."""
        if self.position >= len(self.source):
            return ''
        return self.source[self.position]
    
    def _peek(self, offset: int = 1) -> str:
        """Peek ahead."""
        pos = self.position + offset
        if pos >= len(self.source):
            return ''
        return self.source[pos]
    
    def _advance(self):
        """Advance to the next character."""
        if self.position < len(self.source):
            char = self.source[self.position]
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def _is_in_text(self) -> bool:
        """Check if we're currently parsing text."""
        # Check if we're inside a tag
        if self.position > 0:
            prev = self.source[:self.position]
            last_tag = prev.rfind('<')
            if last_tag != -1:
                after_tag = prev[last_tag:]
                if '>' not in after_tag:
                    return False
        return True
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0