import uuid
import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.api.deps import get_db
from app.models import RepositoryVersion
from app.models.rim.models import RIMFileModel, RIMSymbolModel, RIMRouteModel, RIMDirectoryModel
from app.models.skg.edge import SKGEdgeModel

router = APIRouter()

async def get_latest_version(repository_id: uuid.UUID, db: AsyncSession):
    result = await db.execute(
        select(RepositoryVersion)
        .filter(RepositoryVersion.repository_id == repository_id)
        .order_by(RepositoryVersion.created_at.desc())
        .limit(1)
    )
    version = result.scalars().first()
    if not version:
        raise HTTPException(status_code=404, detail="Repository version not found")
    return version

@router.get("/{id}/graph")
async def get_repository_graph(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    version = await get_latest_version(id, db)
    
    # Get files as nodes
    files_res = await db.execute(select(RIMFileModel).filter(RIMFileModel.repository_version_id == version.id).limit(200))
    files = files_res.scalars().all()
    
    # Get symbols as nodes
    symbols_res = await db.execute(select(RIMSymbolModel).filter(RIMSymbolModel.repository_version_id == version.id).limit(300))
    symbols = symbols_res.scalars().all()
    
    # Get edges
    edges_res = await db.execute(select(SKGEdgeModel).filter(SKGEdgeModel.repository_version_id == version.id).limit(500))
    edges = edges_res.scalars().all()
    
    nodes = []
    for f in files:
        nodes.append({"id": str(f.id), "type": "file", "label": f.path.split('/')[-1], "data": {"path": f.path}})
    for s in symbols:
        nodes.append({"id": str(s.id), "type": "symbol", "label": s.name, "data": {"type": s.symbol_type}})
        
    formatted_edges = []
    for e in edges:
        formatted_edges.append({
            "id": str(e.id),
            "source": str(e.source_id),
            "target": str(e.target_id),
            "label": e.edge_type
        })
        
    return {"nodes": nodes, "edges": formatted_edges}

@router.get("/{id}/entities/{entity_id}")
async def get_entity_details(id: uuid.UUID, entity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    version = await get_latest_version(id, db)
    
    # Check if file
    file_res = await db.execute(select(RIMFileModel).filter(RIMFileModel.id == entity_id))
    file = file_res.scalars().first()
    if file:
        return {
            "id": str(file.id),
            "name": file.path.split('/')[-1],
            "type": "file",
            "path": file.path,
            "language": file.language,
            "risk": "Low" # Static for now, could be dynamic
        }
        
    # Check if symbol
    sym_res = await db.execute(select(RIMSymbolModel).filter(RIMSymbolModel.id == entity_id))
    sym = sym_res.scalars().first()
    if sym:
        return {
            "id": str(sym.id),
            "name": sym.name,
            "type": "symbol",
            "symbol_type": sym.symbol_type,
            "fully_qualified_name": sym.fully_qualified_name,
            "file_id": str(sym.file_id),
            "risk": "Medium"
        }
        
    raise HTTPException(status_code=404, detail="Entity not found")

@router.get("/{id}/files/{file_id}/content")
async def get_file_content(id: uuid.UUID, file_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    version = await get_latest_version(id, db)
    if not version.clone_path:
        raise HTTPException(status_code=400, detail="Repository not cloned locally")
        
    file_res = await db.execute(select(RIMFileModel).filter(RIMFileModel.id == file_id))
    file = file_res.scalars().first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
        
    full_path = os.path.join(version.clone_path, file.path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File content not found on disk")
        
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    return {"content": content, "path": file.path, "language": file.language}

@router.get("/{id}/search")
async def search_repository(id: uuid.UUID, q: str = Query(...), db: AsyncSession = Depends(get_db)):
    version = await get_latest_version(id, db)
    
    # Search files
    file_res = await db.execute(
        select(RIMFileModel)
        .filter(RIMFileModel.repository_version_id == version.id)
        .filter(RIMFileModel.path.ilike(f"%{q}%"))
        .limit(10)
    )
    files = file_res.scalars().all()
    
    # Search symbols
    sym_res = await db.execute(
        select(RIMSymbolModel)
        .filter(RIMSymbolModel.repository_version_id == version.id)
        .filter(RIMSymbolModel.name.ilike(f"%{q}%"))
        .limit(10)
    )
    symbols = sym_res.scalars().all()
    
    results = []
    for f in files:
        results.append({"id": str(f.id), "name": f.path, "type": "file"})
    for s in symbols:
        results.append({"id": str(s.id), "name": s.name, "type": "symbol"})
        
    return results

@router.get("/{id}/hot-files")
async def get_hot_files(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    version = await get_latest_version(id, db)
    
    # Calculate hotness based on number of symbols (functions/classes) extracted
    # A file with many symbols is more complex and potentially higher risk.
    stmt = (
        select(RIMFileModel, func.count(RIMSymbolModel.id).label('symbol_count'))
        .outerjoin(RIMSymbolModel, RIMSymbolModel.file_id == RIMFileModel.id)
        .filter(RIMFileModel.repository_version_id == version.id)
        .group_by(RIMFileModel.id)
        .order_by(func.count(RIMSymbolModel.id).desc())
        .limit(5)
    )
    res = await db.execute(stmt)
    files_with_counts = res.all()
    
    results = []
    for f, count in files_with_counts:
        risk = "High Risk" if count > 15 else ("Med Risk" if count > 5 else "Low Risk")
        results.append({"id": str(f.id), "name": f.path.split('/')[-1], "risk": risk})
        
    return results
