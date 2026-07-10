import os

files = {
    "backend/app/embeddings/__init__.py": "",
    "backend/app/embeddings/schemas.py": """
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
""",
    "backend/app/embeddings/chunker.py": """
import hashlib
from typing import Optional, List
from app.embeddings.schemas import StructuredChunk
from app.enrichment.domain.schemas import KnowledgeNode

class ChunkValidator:
    ALLOWED_ENTITY_TYPES = {
        "Repository", "Directory", "Module", "Package", 
        "Class", "Interface", "Function", "Method", "Route", "Documentation"
    }
    
    @staticmethod
    def validate(chunk: StructuredChunk) -> bool:
        if chunk.entity_type not in ChunkValidator.ALLOWED_ENTITY_TYPES:
            return False
            
        if not chunk.text or len(chunk.text.strip()) < 10:
            return False
            
        if not chunk.knowledge_version_id or not chunk.repository_version_id:
            return False
            
        return True

class ChunkBuilder:
    @staticmethod
    def build(node: KnowledgeNode, knowledge_version_id: str) -> Optional[StructuredChunk]:
        # Semantic composition
        parts = []
        
        summary = node.semantics.summary[0] if node.semantics.summary else ""
        if summary:
            parts.append(f"Summary: {summary}")
            
        purposes = [p[0] for p in node.semantics.purposes]
        if purposes:
            parts.append(f"Purposes: {', '.join(purposes)}")
            
        deps = [d[0] for d in node.relationships.dependencies]
        if deps:
            parts.append(f"Dependencies: {', '.join(deps)}")
            
        text = "\\n".join(parts)
        
        chunk = StructuredChunk(
            id=str(node.identity.id),
            title=f"{node.identity.entity_type}",
            text=text,
            entity_type=node.identity.entity_type,
            layer=node.metadata.layer[0] if node.metadata.layer else None,
            framework=node.metadata.framework[0] if node.metadata.framework else None,
            keywords=[t[0] for t in node.metadata.tags],
            knowledge_node_id=node.identity.id,
            knowledge_version_id=knowledge_version_id,
            repository_version_id=node.identity.repository_version_id,
            repository_id=node.identity.repository_id
        )
        
        if ChunkValidator.validate(chunk):
            return chunk
        return None
        
    @staticmethod
    def compute_hash(chunk: StructuredChunk) -> str:
        return hashlib.sha256(chunk.text.encode('utf-8')).hexdigest()
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
