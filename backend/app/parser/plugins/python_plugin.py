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
    def parse_files(cls, filepaths: List[str]) -> ParseResult:
        start_time = time.time()
        parser = Parser(cls.LANGUAGE)
        
        ast_nodes = {}
        metadata = {"total_loc": 0, "total_todos": 0}
        
        symbols_extracted = []
        imports_extracted = []
        routes_extracted = []
        
        for filepath in filepaths:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                content_bytes = bytes(content, "utf8")
                tree = parser.parse(content_bytes)
                ast_nodes[filepath] = tree
                
                features = cls.extract_features(tree, content_bytes, filepath, "python")
                symbols_extracted.extend(features["symbols"])
                imports_extracted.extend(features["imports"])
                routes_extracted.extend(features["routes"])
                
                meta = MetadataExtractor.extract_from_file(content)
                metadata["total_loc"] += meta["loc"]
                metadata["total_todos"] += len(meta["todos"])
            except Exception as e:
                logger.error("Failed to parse file", filepath=filepath, error=str(e))
                
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
