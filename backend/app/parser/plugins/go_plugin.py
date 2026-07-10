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
