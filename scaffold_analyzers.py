import os

files = {
    "backend/app/parser/plugins/__init__.py": "",
    "backend/app/parser/plugins/base.py": """
from abc import ABC, abstractmethod
from typing import List
from app.parser.models import ParseResult

class ParserPlugin(ABC):
    @classmethod
    @abstractmethod
    def parse_files(cls, filepaths: List[str]) -> ParseResult:
        pass
""",
    "backend/app/parser/analyzers/__init__.py": "",
    "backend/app/parser/analyzers/metadata/__init__.py": "",
    "backend/app/parser/analyzers/metadata/extractor.py": """
import re
from typing import Dict, Any, List

class MetadataExtractor:
    TODO_PATTERN = re.compile(r'(?i)(?:TODO|FIXME|BUG)\\s*[:]\\s*(.*)')
    DEPRECATED_PATTERN = re.compile(r'(?i)@deprecated')
    
    @classmethod
    def extract_from_file(cls, content: str) -> Dict[str, Any]:
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
""",
    "backend/app/parser/analyzers/routes/__init__.py": "",
    "backend/app/parser/analyzers/symbols/__init__.py": "",
    "backend/app/parser/analyzers/imports/__init__.py": "",
    "backend/app/parser/queries/__init__.py": ""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
