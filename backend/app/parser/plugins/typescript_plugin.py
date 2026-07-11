import time

import tree_sitter_typescript as ts_typescript
from tree_sitter import Language, Parser

from app.parser.analyzers.metadata.extractor import MetadataExtractor
from app.parser.models import ParseResult
from app.parser.plugins.base import ParserPlugin


class TypeScriptPlugin(ParserPlugin):
    LANGUAGE = Language(ts_typescript.language_typescript())

    @classmethod
    def parse_files(cls, filepaths: list[str]) -> ParseResult:
        start_time = time.time()
        parser = Parser(cls.LANGUAGE)
        
        ast_nodes = {}
        metadata = {"total_loc": 0, "total_todos": 0}
        
        symbols_extracted = []
        imports_extracted = []
        routes_extracted = []
        calls_extracted = []
        inheritance_extracted = []
        returns_extracted = []
        
        for filepath in filepaths:
            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()
                content_bytes = bytes(content, "utf8")
                tree = parser.parse(content_bytes)
                ast_nodes[filepath] = tree
                
                features = cls.extract_features(tree, content_bytes, filepath, "typescript")
                symbols_extracted.extend(features["symbols"])
                imports_extracted.extend(features["imports"])
                routes_extracted.extend(features["routes"])
                calls_extracted.extend(features["calls"])
                inheritance_extracted.extend(features["inheritance"])
                returns_extracted.extend(features["returns"])
                
                meta = MetadataExtractor.extract_from_file(content)
                metadata["total_loc"] += meta["loc"]
                metadata["total_todos"] += len(meta["todos"])
            except Exception as e:
                from app.core.logger import get_logger
                get_logger(__name__).error("Failed to parse file", filepath=filepath, error=str(e))
                
        return ParseResult(
            files=filepaths,
            ast=ast_nodes,
            symbols=symbols_extracted,
            imports=imports_extracted,
            routes=routes_extracted,
            calls=calls_extracted,
            inheritance=inheritance_extracted,
            returns=returns_extracted,
            language="typescript",
            parser_version="tree-sitter-typescript",
            parse_duration=time.time() - start_time,
            metadata=metadata
        )
