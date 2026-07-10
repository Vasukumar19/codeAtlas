import os

files = {
    "backend/tests/parser/__init__.py": "",
    "backend/tests/parser/test_detector.py": """
from app.parser.detector import LanguageDetector

def test_language_detector_extension():
    assert LanguageDetector.detect("main.py") == "python"
    assert LanguageDetector.detect("app.js") == "javascript"
    assert LanguageDetector.detect("main.go") == "go"
    assert LanguageDetector.detect("Program.cs") == "c-sharp"
    assert LanguageDetector.detect("unknown.xyz") == "unsupported"

def test_language_detector_filename():
    assert LanguageDetector.detect("Dockerfile") == "dockerfile"
    assert LanguageDetector.detect("Makefile") == "makefile"
    assert LanguageDetector.detect("package.json") == "json"
""",
    "backend/tests/parser/test_registry.py": """
from app.parser.registry import ParserRegistry
from app.parser.capabilities import CapabilityRegistry
from app.parser import initialize_registry

def test_registry_initialization():
    initialize_registry()
    assert "python" in ParserRegistry.list_supported_languages()
    
    python_plugin = ParserRegistry.get_plugin("python")
    assert python_plugin is not None
    
    caps = CapabilityRegistry.get("python")
    assert caps.get("ast") is True
""",
    "backend/tests/parser/test_python_plugin.py": """
import tempfile
import os
from app.parser.plugins.python_plugin import PythonPlugin

def test_python_plugin_parse():
    content = \"\"\"
def hello_world():
    # TODO: Implement this
    pass
\"\"\"
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test.py")
        with open(filepath, "w") as f:
            f.write(content)
            
        result = PythonPlugin.parse_files([filepath])
        
        assert len(result.files) == 1
        assert result.language == "python"
        assert result.metadata["total_loc"] == 4
        assert result.metadata["total_todos"] == 1
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
