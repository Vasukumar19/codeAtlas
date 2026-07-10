import uuid
from typing import List, Optional
from pydantic import BaseModel

class StructuredChunk(BaseModel):
    id: str # typically vector_id or knowledge_node_id mapped
    title: str
    text: str
    entity_type: str
    layer: Optional[str] = None
    framework: Optional[str] = None
    keywords: List[str] = []
    knowledge_node_id: uuid.UUID
    knowledge_version_id: str
    repository_version_id: uuid.UUID
    repository_id: uuid.UUID
