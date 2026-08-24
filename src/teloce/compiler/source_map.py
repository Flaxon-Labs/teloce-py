"""
Source map generator.

Generates source maps to map generated JavaScript back to the original source.
"""

from typing import List, Optional, Dict, Any
import json


class SourceMapGenerator:
    """
    Generates source maps for compiled JavaScript.
    """
    
    def __init__(self):
        self.mappings: List[str] = []
        self.sources: List[str] = []
        self.sources_content: List[str] = []
        self.names: List[str] = []
    
    def generate(self, generated_code: str, source_filename: str, source_content: Optional[str] = None) -> Dict[str, Any]:
        """Generate a valid line-level source map.

        The compiler does not currently retain token-to-token mappings, but a
        line-level map is still useful and is materially better than empty
        mappings: every generated line points to the corresponding source
        line (clamped at the final source line).
        """
        lines = generated_code.split('\n')
        source_lines = max(1, (source_content or '').count('\n') + 1)
        mappings = []
        previous_source_line = 0
        for generated_line in range(len(lines)):
            original_line = min(generated_line, source_lines - 1)
            original_delta = original_line - previous_source_line
            previous_source_line = original_line
            mappings.append('AAAA' if original_delta == 0 else self._vlq_segment(original_delta))
        return {
            "version": 3,
            "file": source_filename.replace('.vel', '.js'),
            "sources": [source_filename],
            "sourcesContent": [source_content],
            "names": [],
            "mappings": ';'.join(mappings)
        }

    @staticmethod
    def _vlq_segment(original_line_delta: int) -> str:
        """Encode [generatedColumn, source, originalLine, originalColumn]."""
        values = [0, 0, original_line_delta, 0]
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        encoded = []
        for value in values:
            signed = ((-value) << 1 | 1) if value < 0 else (value << 1)
            while True:
                digit = signed & 31
                signed >>= 5
                if signed:
                    digit |= 32
                encoded.append(alphabet[digit])
                if not signed:
                    break
        return ''.join(encoded)
    
    def to_json(self) -> str:
        """Convert the source map to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the source map to a dictionary."""
        return {
            "version": 3,
            "file": "output.js",
            "sources": self.sources,
            "sourcesContent": self.sources_content,
            "names": self.names,
            "mappings": ';'.join(self.mappings)
        }
