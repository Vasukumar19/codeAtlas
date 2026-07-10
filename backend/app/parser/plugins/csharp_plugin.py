import time

import tree_sitter_c_sharp as ts_c_sharp
from tree_sitter import Language, Parser

from app.parser.analyzers.metadata.extractor import MetadataExtractor
from app.parser.models import ParseResult
from app.parser.plugins.base import ParserPlugin


class CSharpPlugin(ParserPlugin):
    LANGUAGE = Language(ts_c_sharp.language())

    @classmethod
    def parse_files(cls, filepaths: list[str]) -> ParseResult:
        start_time = time.time()
        parser = Parser(cls.LANGUAGE)
        
        ast_nodes = {}
        metadata = {"total_loc": 0, "total_todos": 0}
        
        symbols_extracted = []
        imports_extracted = []
        routes_extracted = []
        
        for filepath in filepaths:
            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()
                content_bytes = bytes(content, "utf8")
                tree = parser.parse(content_bytes)
                ast_nodes[filepath] = tree
                
                features = cls.extract_features(tree, content_bytes, filepath, "c-sharp")
                symbols_extracted.extend(features["symbols"])
                imports_extracted.extend(features["imports"])
                routes_extracted.extend(features["routes"])
                
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
            language="c-sharp",
            parser_version="tree-sitter-c-sharp",
            parse_duration=time.time() - start_time,
            metadata=metadata
        )
