"""
Template parser for .vel components.

Parses the <template> section of a .vel file.
"""

from typing import List, Optional

from teloce.compiler.lexer import Lexer
from teloce.compiler.parser import Parser
from teloce.ast.nodes import ASTNode


class TemplateParser:
    """
    Parses the template section of a .vel component.
    """
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def parse(self, source: str, filename: str = "<input>") -> List[ASTNode]:
        """
        Parse the template section into an AST.
        
        Args:
            source: The template source code
            filename: The source filename
            
        Returns:
            A list of AST nodes.
        """
        self.errors = []
        self.warnings = []
        
        if not source or not source.strip():
            self.warnings.append(f"Empty template in {filename}")
            return []
        
        try:
            # Lex the template
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            if lexer.has_errors:
                self.errors.extend(lexer.errors)
                return []
            
            # Parse the tokens
            parser = Parser(tokens)
            ast = parser.parse()
            
            if parser.has_errors:
                self.errors.extend(parser.errors)
                return []
            
            return ast
            
        except Exception as e:
            self.errors.append(f"Error parsing template in {filename}: {str(e)}")
            return []
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
