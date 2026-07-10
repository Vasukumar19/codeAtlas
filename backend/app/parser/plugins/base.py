from abc import ABC, abstractmethod
from typing import List
from app.parser.models import ParseResult

class ParserPlugin(ABC):
    @classmethod
    @abstractmethod
    def parse_files(cls, filepaths: List[str]) -> ParseResult:
        pass
