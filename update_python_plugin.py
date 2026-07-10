import os

files = {
    "backend/app/parser/plugins/python_plugin.py": """
import time
import os
from pathlib import Path
import tree_sitter_python as ts_python
from tree_sitter import Language, Parser, Query, QueryCursor
from typing import List
from app.parser.plugins.base import ParserPlugin
from app.parser.models import ParseResult
from app.parser.analyzers.metadata.extractor import MetadataExtractor

class PythonPlugin(ParserPlugin):
    LANGUAGE = Language(ts_python.language())

    @classmethod
    def load_query(cls, name: str):
        query_path = Path(__file__).parent.parent / "queries" / "python" / f"{name}.scm"
        if query_path.exists():
            return Query(cls.LANGUAGE, query_path.read_text("utf-8"))
        return None

    @classmethod
    def parse_files(cls, filepaths: List[str]) -> ParseResult:
        start_time = time.time()
        parser = Parser(cls.LANGUAGE)
        
        ast_nodes = {}
        metadata = {"total_loc": 0, "total_todos": 0}
        
        symbols_extracted = []
        imports_extracted = []
        routes_extracted = []
        
        q_symbols = cls.load_query("symbols")
        q_imports = cls.load_query("imports")
        q_routes = cls.load_query("routes")
        
        for filepath in filepaths:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                content_bytes = bytes(content, "utf8")
                tree = parser.parse(content_bytes)
                ast_nodes[filepath] = tree
                
                # Extract Symbols
                if q_symbols:
                    cursor = QueryCursor(q_symbols)
                    for _, match in cursor.matches(tree.root_node):
                        for cap_name, nodes in match.items():
                            for node in nodes:
                                if cap_name in ["symbol.function.name", "symbol.class.name"]:
                                    text = content_bytes[node.start_byte:node.end_byte].decode("utf8")
                                    symbols_extracted.append({"file": filepath, "name": text, "type": cap_name})
                                    
                # Extract Imports
                if q_imports:
                    cursor = QueryCursor(q_imports)
                    for _, match in cursor.matches(tree.root_node):
                        for cap_name, nodes in match.items():
                            for node in nodes:
                                text = content_bytes[node.start_byte:node.end_byte].decode("utf8")
                                imports_extracted.append({"file": filepath, "raw": text})
                                
                # Extract Routes
                if q_routes:
                    cursor = QueryCursor(q_routes)
                    for _, match in cursor.matches(tree.root_node):
                        route_data = {"file": filepath}
                        for cap_name, nodes in match.items():
                            for node in nodes:
                                text = content_bytes[node.start_byte:node.end_byte].decode("utf8")
                                if cap_name == "route.method":
                                    route_data["method"] = text.upper()
                                elif cap_name == "route.path":
                                    route_data["path"] = text.strip('"\\'')
                                elif cap_name == "route.handler":
                                    route_data["handler"] = text
                        if "path" in route_data:
                            routes_extracted.append(route_data)
                
                meta = MetadataExtractor.extract_from_file(content)
                metadata["total_loc"] += meta["loc"]
                metadata["total_todos"] += len(meta["todos"])
            except Exception as e:
                pass
                
        duration = time.time() - start_time
        return ParseResult(
            files=filepaths,
            ast=ast_nodes,
            symbols=symbols_extracted,
            imports=imports_extracted,
            routes=routes_extracted,
            language="python",
            parser_version="tree-sitter-python",
            parse_duration=duration,
            metadata=metadata
        )
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
