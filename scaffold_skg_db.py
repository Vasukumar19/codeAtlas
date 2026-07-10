import os
import re

# 1. Update enums.py
enums_path = "backend/app/models/enums.py"
with open(enums_path, "r", encoding="utf-8") as f:
    content = f.read()
    
if "SKGEdgeType" not in content:
    content += """
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
"""
    with open(enums_path, "w", encoding="utf-8") as f:
        f.write(content)

# 2. Create skg edge model
os.makedirs("backend/app/models/skg", exist_ok=True)
with open("backend/app/models/skg/__init__.py", "w", encoding="utf-8") as f:
    pass

with open("backend/app/models/skg/edge.py", "w", encoding="utf-8") as f:
    f.write("""
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, String, ForeignKey
from app.db.base_class import Base, UUIDMixin, TimestampMixin

class SKGEdgeModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "skg_edges"
    
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(index=True)
    target_id: Mapped[uuid.UUID] = mapped_column(index=True)
    edge_type: Mapped[str] = mapped_column(String, index=True)
    metadata_: Mapped[dict] = mapped_column(JSON, default=dict)
""")

# 3. Update base.py
base_path = "backend/app/db/base.py"
with open(base_path, "r", encoding="utf-8") as f:
    base_content = f.read()

if "SKGEdgeModel" not in base_content:
    base_content = base_content.replace(
        "from app.models.rim.models import ",
        "from app.models.skg.edge import SKGEdgeModel\nfrom app.models.rim.models import "
    )
    base_content = base_content.replace(
        '"RIMRouteModel"',
        '"RIMRouteModel", "SKGEdgeModel"'
    )
    with open(base_path, "w", encoding="utf-8") as f:
        f.write(base_content)
