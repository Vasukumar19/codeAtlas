import re
from typing import Any


class MetadataExtractor:
    TODO_PATTERN = re.compile(r'(?i)(?:TODO|FIXME|BUG)\s*[:]\s*(.*)')
    DEPRECATED_PATTERN = re.compile(r'(?i)@deprecated')
    
    @classmethod
    def extract_from_file(cls, content: str) -> dict[str, Any]:
        lines = content.splitlines()
        loc = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        
        # Extremely basic heuristics since we aren't walking AST for these in Python without full trees
        # In a real AST-based analyzer, we'd count functions and classes.
        # This is a fallback string-based metadata pass.
        
        todos = []
        deprecations = 0
        for i, line in enumerate(lines):
            match = cls.TODO_PATTERN.search(line)
            if match:
                todos.append({"line": i + 1, "text": match.group(1).strip()})
            if cls.DEPRECATED_PATTERN.search(line):
                deprecations += 1
                
        return {
            "loc": loc,
            "blank_lines": blank_lines,
            "todos": todos,
            "deprecated_annotations": deprecations
        }
