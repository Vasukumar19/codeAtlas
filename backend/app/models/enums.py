import enum


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class RepositoryStatus(str, enum.Enum):
    NEW = "NEW"
    QUEUED = "QUEUED"
    CLONING = "CLONING"
    READY_TO_PARSE = "READY_TO_PARSE"
    PARSING = "PARSING"
    PARSED = "PARSED"
    EMBEDDING = "EMBEDDING"
    READY = "READY"
    FAILED = "FAILED"

class JobType(str, enum.Enum):
    IMPORT = "IMPORT"
    REFRESH = "REFRESH"
    PARSE = "PARSE"

class SKGEdgeType(str, enum.Enum):
    CONTAINS = "CONTAINS"
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    EXTENDS = "EXTENDS"
    IMPLEMENTS = "IMPLEMENTS"
    DECLARES = "DECLARES"
    USES = "USES"
    RETURNS = "RETURNS"
    ROUTES_TO = "ROUTES_TO"
    DEPENDS_ON = "DEPENDS_ON"
