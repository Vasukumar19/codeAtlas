import os

files = {
    "backend/app/models/embeddings/__init__.py": "",
    "backend/app/models/embeddings/collection.py": """
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from app.db.base_class import Base, UUIDMixin, TimestampMixin

class EmbeddingCollectionModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "embedding_collections"
    
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    embedding_model: Mapped[str] = mapped_column(String)
    dimension: Mapped[int] = mapped_column(Integer)
    vector_store: Mapped[str] = mapped_column(String)
""",
    "backend/app/models/embeddings/metadata.py": """
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON
from app.db.base_class import Base, UUIDMixin, TimestampMixin

class EmbeddingMetadataModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "embedding_metadata"
    
    collection_id: Mapped[uuid.UUID] = mapped_column(index=True)
    knowledge_node_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    knowledge_version_id: Mapped[str] = mapped_column(String, index=True)
    
    chunk_hash: Mapped[str] = mapped_column(String, index=True)
    vector_id: Mapped[str] = mapped_column(String, index=True)
    
    structured_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# Update base.py
base_path = "c:/Users/kumar/project/codeAtlas/backend/app/db/base.py"
with open(base_path, "r", encoding="utf-8") as f:
    base_content = f.read()

if "EmbeddingMetadataModel" not in base_content:
    base_content = base_content.replace(
        "from app.models.enrichment.node import KnowledgeNodeModel",
        "from app.models.embeddings.collection import EmbeddingCollectionModel\nfrom app.models.embeddings.metadata import EmbeddingMetadataModel\nfrom app.models.enrichment.node import KnowledgeNodeModel"
    )
    base_content = base_content.replace(
        '"KnowledgeNodeModel"',
        '"KnowledgeNodeModel", "EmbeddingCollectionModel", "EmbeddingMetadataModel"'
    )
    with open(base_path, "w", encoding="utf-8") as f:
        f.write(base_content)
