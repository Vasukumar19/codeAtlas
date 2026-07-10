from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
from tree_sitter import Query, QueryCursor, Node, Tree
from app.parser.models import ParseResult
from app.core.logger import get_logger

logger = get_logger(__name__)

class ParserPlugin(ABC):
    @classmethod
    def load_query(cls, language_name: str, query_name: str) -> Optional[Query]:
        # Fallback typescript to javascript queries
        if language_name == "typescript":
            language_name = "javascript"
            
        query_path = Path(__file__).parent.parent / "queries" / language_name / f"{query_name}.scm"
        if query_path.exists():
            return Query(cls.LANGUAGE, query_path.read_text("utf-8"))
        return None

    @classmethod
    def extract_features(cls, tree: Tree, content_bytes: bytes, filepath: str, language_name: str) -> Dict[str, List[Dict]]:
        features = {"symbols": [], "imports": [], "routes": []}
        
        q_symbols = cls.load_query(language_name, "symbols")
        q_imports = cls.load_query(language_name, "imports")
        q_routes = cls.load_query(language_name, "routes")
        
        if q_symbols:
            cursor = QueryCursor(q_symbols)
            for _, match in cursor.matches(tree.root_node):
                for cap_name, nodes in match.items():
                    for node in nodes:
                        if cap_name in ["symbol.function.name", "symbol.class.name"]:
                            text = content_bytes[node.start_byte:node.end_byte].decode("utf8")
                            features["symbols"].append({"file": filepath, "name": text, "type": cap_name})
                            
        if q_imports:
            cursor = QueryCursor(q_imports)
            for _, match in cursor.matches(tree.root_node):
                for cap_name, nodes in match.items():
                    for node in nodes:
                        text = content_bytes[node.start_byte:node.end_byte].decode("utf8")
                        features["imports"].append({"file": filepath, "raw": text})
                        
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
                            route_data["path"] = text.strip('"\'`')
                        elif cap_name == "route.handler":
                            route_data["handler"] = text
                if "path" in route_data:
                    features["routes"].append(route_data)
                    
        return features

    @classmethod
    @abstractmethod
    def parse_files(cls, filepaths: List[str]) -> ParseResult:
        pass
