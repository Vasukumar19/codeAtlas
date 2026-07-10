import os

files = {
    "backend/app/parser/plugins/python_plugin.py": """
import time
import tree_sitter_python as ts_python
from tree_sitter import Language, Parser
from typing import List
from app.parser.plugins.base import ParserPlugin
from app.parser.models import ParseResult
from app.parser.analyzers.metadata.extractor import MetadataExtractor

class PythonPlugin(ParserPlugin):
    LANGUAGE = Language(ts_python.language())

    @classmethod
    def parse_files(cls, filepaths: List[str]) -> ParseResult:
        start_time = time.time()
        parser = Parser(cls.LANGUAGE)
        
        ast_nodes = {}
        metadata = {"total_loc": 0, "total_todos": 0}
        
        for filepath in filepaths:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = parser.parse(bytes(content, "utf8"))
                ast_nodes[filepath] = tree
                
                meta = MetadataExtractor.extract_from_file(content)
                metadata["total_loc"] += meta["loc"]
                metadata["total_todos"] += len(meta["todos"])
            except Exception:
                pass
                
        duration = time.time() - start_time
        return ParseResult(
            files=filepaths,
            ast=ast_nodes,
            language="python",
            parser_version="tree-sitter-python",
            parse_duration=duration,
            metadata=metadata
        )
""",
    "backend/app/parser/plugins/javascript_plugin.py": """
import time
import tree_sitter_javascript as ts_javascript
from tree_sitter import Language, Parser
from typing import List
from app.parser.plugins.base import ParserPlugin
from app.parser.models import ParseResult
from app.parser.analyzers.metadata.extractor import MetadataExtractor

class JavaScriptPlugin(ParserPlugin):
    LANGUAGE = Language(ts_javascript.language())

    @classmethod
    def parse_files(cls, filepaths: List[str]) -> ParseResult:
        start_time = time.time()
        parser = Parser(cls.LANGUAGE)
        
        ast_nodes = {}
        metadata = {"total_loc": 0, "total_todos": 0}
        
        for filepath in filepaths:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = parser.parse(bytes(content, "utf8"))
                ast_nodes[filepath] = tree
                meta = MetadataExtractor.extract_from_file(content)
                metadata["total_loc"] += meta["loc"]
                metadata["total_todos"] += len(meta["todos"])
            except Exception:
                pass
                
        return ParseResult(
            files=filepaths,
            ast=ast_nodes,
            language="javascript",
            parser_version="tree-sitter-javascript",
            parse_duration=time.time() - start_time,
            metadata=metadata
        )
""",
    "backend/app/parser/plugins/typescript_plugin.py": """
import time
import tree_sitter_typescript as ts_typescript
from tree_sitter import Language, Parser
from typing import List
from app.parser.plugins.base import ParserPlugin
from app.parser.models import ParseResult
from app.parser.analyzers.metadata.extractor import MetadataExtractor

class TypeScriptPlugin(ParserPlugin):
    LANGUAGE = Language(ts_typescript.language_typescript())

    @classmethod
    def parse_files(cls, filepaths: List[str]) -> ParseResult:
        start_time = time.time()
        parser = Parser(cls.LANGUAGE)
        
        ast_nodes = {}
        metadata = {"total_loc": 0, "total_todos": 0}
        
        for filepath in filepaths:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = parser.parse(bytes(content, "utf8"))
                ast_nodes[filepath] = tree
                meta = MetadataExtractor.extract_from_file(content)
                metadata["total_loc"] += meta["loc"]
                metadata["total_todos"] += len(meta["todos"])
            except Exception:
                pass
                
        return ParseResult(
            files=filepaths,
            ast=ast_nodes,
            language="typescript",
            parser_version="tree-sitter-typescript",
            parse_duration=time.time() - start_time,
            metadata=metadata
        )
""",
    "backend/app/parser/plugins/java_plugin.py": """
import time
import tree_sitter_java as ts_java
from tree_sitter import Language, Parser
from typing import List
from app.parser.plugins.base import ParserPlugin
from app.parser.models import ParseResult
from app.parser.analyzers.metadata.extractor import MetadataExtractor

class JavaPlugin(ParserPlugin):
    LANGUAGE = Language(ts_java.language())

    @classmethod
    def parse_files(cls, filepaths: List[str]) -> ParseResult:
        start_time = time.time()
        parser = Parser(cls.LANGUAGE)
        
        ast_nodes = {}
        metadata = {"total_loc": 0, "total_todos": 0}
        
        for filepath in filepaths:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = parser.parse(bytes(content, "utf8"))
                ast_nodes[filepath] = tree
                meta = MetadataExtractor.extract_from_file(content)
                metadata["total_loc"] += meta["loc"]
                metadata["total_todos"] += len(meta["todos"])
            except Exception:
                pass
                
        return ParseResult(
            files=filepaths,
            ast=ast_nodes,
            language="java",
            parser_version="tree-sitter-java",
            parse_duration=time.time() - start_time,
            metadata=metadata
        )
""",
    "backend/app/parser/plugins/go_plugin.py": """
import time
import tree_sitter_go as ts_go
from tree_sitter import Language, Parser
from typing import List
from app.parser.plugins.base import ParserPlugin
from app.parser.models import ParseResult
from app.parser.analyzers.metadata.extractor import MetadataExtractor

class GoPlugin(ParserPlugin):
    LANGUAGE = Language(ts_go.language())

    @classmethod
    def parse_files(cls, filepaths: List[str]) -> ParseResult:
        start_time = time.time()
        parser = Parser(cls.LANGUAGE)
        
        ast_nodes = {}
        metadata = {"total_loc": 0, "total_todos": 0}
        
        for filepath in filepaths:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = parser.parse(bytes(content, "utf8"))
                ast_nodes[filepath] = tree
                meta = MetadataExtractor.extract_from_file(content)
                metadata["total_loc"] += meta["loc"]
                metadata["total_todos"] += len(meta["todos"])
            except Exception:
                pass
                
        return ParseResult(
            files=filepaths,
            ast=ast_nodes,
            language="go",
            parser_version="tree-sitter-go",
            parse_duration=time.time() - start_time,
            metadata=metadata
        )
""",
    "backend/app/parser/plugins/csharp_plugin.py": """
import time
import tree_sitter_c_sharp as ts_c_sharp
from tree_sitter import Language, Parser
from typing import List
from app.parser.plugins.base import ParserPlugin
from app.parser.models import ParseResult
from app.parser.analyzers.metadata.extractor import MetadataExtractor

class CSharpPlugin(ParserPlugin):
    LANGUAGE = Language(ts_c_sharp.language())

    @classmethod
    def parse_files(cls, filepaths: List[str]) -> ParseResult:
        start_time = time.time()
        parser = Parser(cls.LANGUAGE)
        
        ast_nodes = {}
        metadata = {"total_loc": 0, "total_todos": 0}
        
        for filepath in filepaths:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = parser.parse(bytes(content, "utf8"))
                ast_nodes[filepath] = tree
                meta = MetadataExtractor.extract_from_file(content)
                metadata["total_loc"] += meta["loc"]
                metadata["total_todos"] += len(meta["todos"])
            except Exception:
                pass
                
        return ParseResult(
            files=filepaths,
            ast=ast_nodes,
            language="c-sharp",
            parser_version="tree-sitter-c-sharp",
            parse_duration=time.time() - start_time,
            metadata=metadata
        )
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
