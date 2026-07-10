import os

files = {
    "backend/app/parser/__init__.py": "",
    "backend/app/parser/models.py": """
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ParseResult(BaseModel):
    files: List[str] = Field(default_factory=list)
    ast: Any = None  # In-memory Tree-sitter object
    symbols: List[Dict[str, Any]] = Field(default_factory=list)
    imports: List[Dict[str, Any]] = Field(default_factory=list)
    routes: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    
    language: str
    parser_version: str
    parse_duration: float
    
    model_config = {"arbitrary_types_allowed": True}
""",
    "backend/app/parser/capabilities.py": """
from typing import Dict, Any

class CapabilityRegistry:
    _capabilities: Dict[str, Dict[str, bool]] = {}

    @classmethod
    def register(cls, language: str, capabilities: Dict[str, bool]):
        cls._capabilities[language] = capabilities

    @classmethod
    def get(cls, language: str) -> Dict[str, bool]:
        return cls._capabilities.get(language, {})
""",
    "backend/app/parser/registry.py": """
from typing import Dict, Type, Any
from app.parser.capabilities import CapabilityRegistry

class ParserRegistry:
    _plugins: Dict[str, Type] = {}

    @classmethod
    def register(cls, language: str, plugin_class: Type, capabilities: Dict[str, bool]):
        cls._plugins[language] = plugin_class
        CapabilityRegistry.register(language, capabilities)

    @classmethod
    def get_plugin(cls, language: str) -> Type | None:
        return cls._plugins.get(language)
    
    @classmethod
    def list_supported_languages(cls) -> list[str]:
        return list(cls._plugins.keys())
""",
    "backend/app/parser/detector.py": """
import os
from typing import Optional

class LanguageDetector:
    EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".cs": "c-sharp",
        ".cpp": "cpp",
        ".c": "c",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php"
    }

    FILENAMES = {
        "Dockerfile": "dockerfile",
        "Makefile": "makefile",
        "Jenkinsfile": "groovy",
        "pom.xml": "xml",
        "package.json": "json"
    }

    SHEBANGS = {
        "python": "python",
        "node": "javascript",
        "bash": "bash",
        "sh": "bash",
        "ruby": "ruby"
    }

    @classmethod
    def detect(cls, filepath: str) -> str:
        filename = os.path.basename(filepath)
        
        # 1. Filename match
        if filename in cls.FILENAMES:
            return cls.FILENAMES[filename]
        
        # 2. Extension match
        _, ext = os.path.splitext(filename)
        if ext.lower() in cls.EXTENSIONS:
            return cls.EXTENSIONS[ext.lower()]
        
        # 3. Shebang match
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line.startswith("#!"):
                    for key, lang in cls.SHEBANGS.items():
                        if key in first_line:
                            return lang
        except Exception:
            pass

        return "unsupported"
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
