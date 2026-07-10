import uuid

from pydantic import BaseModel


class StructuredChunk(BaseModel):
    id: str # typically vector_id or knowledge_node_id mapped
    title: str
    text: str
    entity_type: str
    layer: str | None = None
    framework: str | None = None
    keywords: list[str] = []
    knowledge_node_id: uuid.UUID
    knowledge_version_id: str
    repository_version_id: uuid.UUID
    repository_id: uuid.UUID
