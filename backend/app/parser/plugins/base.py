from abc import ABC, abstractmethod
from pathlib import Path

from tree_sitter import Query, QueryCursor, Tree

from app.core.logger import get_logger
from app.parser.models import ParseResult

logger = get_logger(__name__)

class ParserPlugin(ABC):
    @classmethod
    def load_query(cls, language_name: str, query_name: str) -> Query | None:
        # Fallback typescript to javascript queries
        if language_name == "typescript":
            language_name = "javascript"
            
        query_path = Path(__file__).parent.parent / "queries" / language_name / f"{query_name}.scm"
        if query_path.exists():
            return Query(cls.LANGUAGE, query_path.read_text("utf-8"))
        return None

    @classmethod
    def extract_features(cls, tree: Tree, content_bytes: bytes, filepath: str, language_name: str) -> dict[str, list[dict]]:
        features = {"symbols": [], "imports": [], "routes": [], "calls": [], "inheritance": [], "returns": []}
        
        q_symbols = cls.load_query(language_name, "symbols")
        q_imports = cls.load_query(language_name, "imports")
        q_routes = cls.load_query(language_name, "routes")
        q_calls = cls.load_query(language_name, "calls")
        q_inheritance = cls.load_query(language_name, "inheritance")
        q_returns = cls.load_query(language_name, "returns")
        
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

        if q_calls:
            cursor = QueryCursor(q_calls)
            for _, match in cursor.matches(tree.root_node):
                call_data = {"file": filepath}
                call_node = None
                for cap_name, nodes in match.items():
                    for node in nodes:
                        text = content_bytes[node.start_byte:node.end_byte].decode("utf8")
                        if cap_name == "call.function":
                            call_data["function"] = text
                            call_node = node
                        elif cap_name == "call.receiver":
                            call_data["receiver"] = text
                if "function" in call_data and call_node:
                    call_data["byte_offset"] = call_node.start_byte
                    # Walk up the AST to find enclosing function
                    curr = call_node.parent
                    while curr:
                        if curr.type in ["function_definition", "method_declaration", "method_definition", "arrow_function", "function_declaration", "function", "class_declaration"]:
                            # Attempt to find identifier child
                            for child in curr.children:
                                if child.type == "identifier":
                                    call_data["caller_function_name"] = content_bytes[child.start_byte:child.end_byte].decode("utf8")
                                    break
                            if "caller_function_name" in call_data:
                                break
                        curr = curr.parent
                    features["calls"].append(call_data)

        if q_inheritance:
            cursor = QueryCursor(q_inheritance)
            for _, match in cursor.matches(tree.root_node):
                for cap_name, nodes in match.items():
                    for node in nodes:
                        parent_name = content_bytes[node.start_byte:node.end_byte].decode("utf8")
                        inheritance_type = "extends" if "extends" in cap_name else "implements"
                        # Walk up the AST to find enclosing class definition
                        curr = node.parent
                        class_name = None
                        while curr:
                            if curr.type in ["class_definition", "class_declaration"]:
                                for child in curr.children:
                                    if child.type == "identifier":
                                        class_name = content_bytes[child.start_byte:child.end_byte].decode("utf8")
                                        break
                                if class_name:
                                    break
                            curr = curr.parent
                        if class_name:
                            features["inheritance"].append({
                                "file": filepath,
                                "class": class_name,
                                "parent": parent_name,
                                "type": inheritance_type
                            })

        if q_returns:
            cursor = QueryCursor(q_returns)
            for _, match in cursor.matches(tree.root_node):
                for cap_name, nodes in match.items():
                    for node in nodes:
                        return_type_text = content_bytes[node.start_byte:node.end_byte].decode("utf8")
                        if return_type_text.startswith(":"):
                            return_type_text = return_type_text[1:].strip()
                        # Walk up to find enclosing function definition
                        curr = node.parent
                        function_name = None
                        while curr:
                            if curr.type in ["function_definition", "method_declaration", "method_definition", "function_declaration", "function"]:
                                for child in curr.children:
                                    if child.type == "identifier":
                                        function_name = content_bytes[child.start_byte:child.end_byte].decode("utf8")
                                        break
                                if function_name:
                                    break
                            curr = curr.parent
                        if function_name:
                            features["returns"].append({
                                "file": filepath,
                                "function": function_name,
                                "returns": return_type_text
                            })
                            
        return features

    @classmethod
    @abstractmethod
    def parse_files(cls, filepaths: list[str]) -> ParseResult:
        pass
