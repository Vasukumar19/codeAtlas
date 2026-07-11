import os
import re
import uuid
from collections import deque

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models import RepositoryVersion
from app.models.enrichment.node import KnowledgeNodeModel
from app.models.rim.models import (
    RIMFileModel,
    RIMRouteModel,
    RIMSymbolModel,
)
from app.models.skg.edge import SKGEdgeModel
from app.parser.analyzers.metadata.extractor import MetadataExtractor

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

async def describe_entities(version_id: uuid.UUID, entity_ids: set[uuid.UUID], db: AsyncSession) -> list[dict]:
    if not entity_ids:
        return []

    files = (await db.execute(
        select(RIMFileModel).filter(
            RIMFileModel.repository_version_id == version_id,
            RIMFileModel.id.in_(entity_ids),
        )
    )).scalars().all()
    symbols = (await db.execute(
        select(RIMSymbolModel).filter(
            RIMSymbolModel.repository_version_id == version_id,
            RIMSymbolModel.id.in_(entity_ids),
        )
    )).scalars().all()
    routes = (await db.execute(
        select(RIMRouteModel).filter(
            RIMRouteModel.repository_version_id == version_id,
            RIMRouteModel.id.in_(entity_ids),
        )
    )).scalars().all()

    nodes = [
        {"id": str(f.id), "type": "file", "name": f.path, "path": f.path, "language": f.language}
        for f in files
    ]
    nodes.extend(
        {"id": str(s.id), "type": "symbol", "name": s.name, "file_id": str(s.file_id), "symbol_type": s.symbol_type}
        for s in symbols
    )
    nodes.extend(
        {"id": str(r.id), "type": "route", "name": f"{r.method} {r.path}", "path": r.path, "method": r.method, "handler": r.handler}
        for r in routes
    )
    return nodes

@router.get("/{id}/graph")
async def get_repository_graph(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    version = await get_latest_version(id, db)
    
    # Get files as nodes
    files_res = await db.execute(select(RIMFileModel).filter(RIMFileModel.repository_version_id == version.id).limit(200))
    files = files_res.scalars().all()
    
    # Get symbols as nodes
    symbols_res = await db.execute(select(RIMSymbolModel).filter(RIMSymbolModel.repository_version_id == version.id).limit(300))
    symbols = symbols_res.scalars().all()

    routes_res = await db.execute(select(RIMRouteModel).filter(RIMRouteModel.repository_version_id == version.id).limit(100))
    routes = routes_res.scalars().all()
    
    # Get edges
    edges_res = await db.execute(select(SKGEdgeModel).filter(SKGEdgeModel.repository_version_id == version.id).limit(500))
    edges = edges_res.scalars().all()
    
    nodes = []
    for f in files:
        nodes.append({"id": str(f.id), "type": "file", "label": f.path.split('/')[-1], "data": {"path": f.path}})
    for s in symbols:
        nodes.append({"id": str(s.id), "type": "symbol", "label": s.name, "data": {"type": s.symbol_type}})
    for r in routes:
        nodes.append({"id": str(r.id), "type": "route", "label": f"{r.method} {r.path}", "data": {"handler": r.handler}})
        
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
    await get_latest_version(id, db)
    
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

    route_res = await db.execute(select(RIMRouteModel).filter(RIMRouteModel.id == entity_id))
    route = route_res.scalars().first()
    if route:
        return {
            "id": str(route.id),
            "name": f"{route.method} {route.path}",
            "type": "route",
            "method": route.method,
            "path": route.path,
            "handler": route.handler,
            "file_id": str(route.file_id),
            "risk": "Medium",
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
        
    with open(full_path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    return {"content": content, "path": file.path, "language": file.language}

@router.get("/{id}/search")
async def search_repository(id: uuid.UUID, q: str = Query(...), db: AsyncSession = Depends(get_db)):
    version = await get_latest_version(id, db)
    query = q.strip()
    
    # Search files
    file_res = await db.execute(
        select(RIMFileModel)
        .filter(RIMFileModel.repository_version_id == version.id)
        .filter(RIMFileModel.path.ilike(f"%{query}%"))
        .limit(10)
    )
    files = file_res.scalars().all()
    
    # Search symbols
    sym_res = await db.execute(
        select(RIMSymbolModel)
        .filter(RIMSymbolModel.repository_version_id == version.id)
        .filter(RIMSymbolModel.name.ilike(f"%{query}%"))
        .limit(10)
    )
    symbols = sym_res.scalars().all()

    route_res = await db.execute(
        select(RIMRouteModel)
        .filter(RIMRouteModel.repository_version_id == version.id)
        .filter(or_(RIMRouteModel.path.ilike(f"%{query}%"), RIMRouteModel.handler.ilike(f"%{query}%")))
        .limit(10)
    )
    routes = route_res.scalars().all()

    knowledge_res = await db.execute(
        select(KnowledgeNodeModel)
        .filter(KnowledgeNodeModel.repository_version_id == version.id)
        .filter(
            or_(
                KnowledgeNodeModel.semantics.cast(String).ilike(f"%{query}%"),
                KnowledgeNodeModel.documentation.cast(String).ilike(f"%{query}%"),
                KnowledgeNodeModel.metadata_.cast(String).ilike(f"%{query}%"),
            )
        )
        .limit(10)
    )
    knowledge_nodes = knowledge_res.scalars().all()
    
    results = []
    for f in files:
        results.append({"id": str(f.id), "name": f.path, "type": "file"})
    for s in symbols:
        results.append({"id": str(s.id), "name": s.name, "type": "symbol"})
    for r in routes:
        results.append({"id": str(r.id), "name": f"{r.method} {r.path}", "type": "route"})
    for k in knowledge_nodes:
        summary = (k.semantics or {}).get("summary")
        if isinstance(summary, list):
            summary = summary[0]
        results.append({"id": str(k.rim_entity_id), "name": summary or k.entity_type, "type": "knowledge"})

    if version.clone_path:
        file_rows = files or (await db.execute(
            select(RIMFileModel).filter(RIMFileModel.repository_version_id == version.id)
        )).scalars().all()
        for f in file_rows:
            full_path = os.path.join(version.clone_path, f.path)
            if not os.path.exists(full_path):
                continue
            with open(full_path, encoding="utf-8", errors="ignore") as source_file:
                todos = MetadataExtractor.extract_from_file(source_file.read()).get("todos", [])
            for todo in todos:
                if query.lower() in todo["text"].lower():
                    results.append({
                        "id": str(f.id),
                        "name": todo["text"],
                        "type": "todo",
                        "path": f.path,
                        "line": todo["line"],
                    })

    return results

@router.get("/{id}/impact/{entity_id}")
async def get_impact_analysis(
    id: uuid.UUID,
    entity_id: uuid.UUID,
    hops: int = Query(3, ge=1, le=5),
    db: AsyncSession = Depends(get_db),
):
    version = await get_latest_version(id, db)
    edge_rows = (await db.execute(
        select(SKGEdgeModel).filter(
            SKGEdgeModel.repository_version_id == version.id,
            SKGEdgeModel.edge_type.in_(["CALLS", "DEPENDS_ON", "ROUTES_TO", "IMPORTS"]),
        )
    )).scalars().all()

    adjacency: dict[uuid.UUID, list[SKGEdgeModel]] = {}
    for edge in edge_rows:
        adjacency.setdefault(edge.source_id, []).append(edge)

    visited = {entity_id}
    reached_edges = []
    queue = deque([(entity_id, 0)])
    while queue:
        current, depth = queue.popleft()
        if depth >= hops:
            continue
        for edge in adjacency.get(current, []):
            reached_edges.append(edge)
            if edge.target_id not in visited:
                visited.add(edge.target_id)
                queue.append((edge.target_id, depth + 1))

    nodes = await describe_entities(version.id, visited, db)
    return {
        "start_entity_id": str(entity_id),
        "hops": hops,
        "blast_radius": {
            "total_entities": max(len(visited) - 1, 0),
            "files": len([n for n in nodes if n["type"] == "file"]),
            "symbols": len([n for n in nodes if n["type"] == "symbol"]),
            "routes": len([n for n in nodes if n["type"] == "route"]),
        },
        "nodes": nodes,
        "edges": [
            {"id": str(e.id), "source": str(e.source_id), "target": str(e.target_id), "type": e.edge_type}
            for e in reached_edges
        ],
    }

@router.get("/{id}/execution-flow")
async def get_execution_flow(
    id: uuid.UUID,
    entity_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    version = await get_latest_version(id, db)
    start_id = entity_id
    if start_id is None:
        route = (await db.execute(
            select(RIMRouteModel).filter(RIMRouteModel.repository_version_id == version.id).limit(1)
        )).scalars().first()
        symbol = None if route else (await db.execute(
            select(RIMSymbolModel).filter(RIMSymbolModel.repository_version_id == version.id).limit(1)
        )).scalars().first()
        start_id = route.id if route else (symbol.id if symbol else None)

    if start_id is None:
        return {"steps": [], "edges": []}

    call_edges = (await db.execute(
        select(SKGEdgeModel)
        .filter(SKGEdgeModel.repository_version_id == version.id, SKGEdgeModel.edge_type.in_(["ROUTES_TO", "CALLS"]))
    )).scalars().all()
    adjacency: dict[uuid.UUID, list[SKGEdgeModel]] = {}
    for edge in call_edges:
        adjacency.setdefault(edge.source_id, []).append(edge)

    def edge_offset(edge: SKGEdgeModel) -> int:
        meta_offset = (edge.metadata_ or {}).get("byte_offset")
        if isinstance(meta_offset, int):
            return meta_offset
        return 2**31 - 1

    steps = []
    flow_edges = []
    visited = set()
    queue = deque([start_id])
    while queue and len(steps) < 25:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        steps.extend(await describe_entities(version.id, {current}, db))
        for edge in sorted(adjacency.get(current, []), key=edge_offset):
            flow_edges.append(edge)
            if edge.target_id not in visited:
                queue.append(edge.target_id)

    return {
        "start_entity_id": str(start_id),
        "steps": steps,
        "edges": [
            {"id": str(e.id), "source": str(e.source_id), "target": str(e.target_id), "type": e.edge_type}
            for e in flow_edges
        ],
    }

@router.get("/{id}/security-findings")
async def get_security_findings(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    version = await get_latest_version(id, db)
    if not version.clone_path:
        return []

    secret_pattern = re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]")
    sql_pattern = re.compile(r"(?i)(select|insert|update|delete)\s+.*(\+|f['\"]|format\()")
    dangerous_patterns = [
        ("dangerous-eval", re.compile(r"\b(eval|exec)\s*\("), "Dynamic code execution"),
        ("shell-execution", re.compile(r"\b(os\.system|subprocess\..*shell\s*=\s*True|child_process\.exec)\b"), "Shell execution"),
    ]

    files = (await db.execute(select(RIMFileModel).filter(RIMFileModel.repository_version_id == version.id))).scalars().all()
    findings = []
    for f in files:
        full_path = os.path.join(version.clone_path, f.path)
        if not os.path.exists(full_path):
            continue
        with open(full_path, encoding="utf-8", errors="ignore") as source_file:
            for line_no, line in enumerate(source_file, start=1):
                checks = [
                    ("hardcoded-secret", secret_pattern, "Hardcoded secret-like value"),
                    ("unsafe-sql", sql_pattern, "String-built SQL query"),
                    *dangerous_patterns,
                ]
                for rule_id, pattern, message in checks:
                    if pattern.search(line):
                        findings.append({
                            "rule_id": rule_id,
                            "severity": "high" if rule_id != "shell-execution" else "critical",
                            "message": message,
                            "path": f.path,
                            "line": line_no,
                            "snippet": line.strip()[:180],
                        })
    return findings

@router.get("/{id}/docs")
async def generate_documentation_draft(
    id: uuid.UUID,
    path: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    version = await get_latest_version(id, db)
    file_stmt = select(RIMFileModel).filter(RIMFileModel.repository_version_id == version.id)
    if path:
        file_stmt = file_stmt.filter(RIMFileModel.path.ilike(f"{path}%"))
    files = (await db.execute(file_stmt.limit(50))).scalars().all()
    file_ids = [f.id for f in files]
    symbols = []
    routes = []
    knowledge = []
    if file_ids:
        symbols = (await db.execute(select(RIMSymbolModel).filter(RIMSymbolModel.file_id.in_(file_ids)).limit(200))).scalars().all()
        routes = (await db.execute(select(RIMRouteModel).filter(RIMRouteModel.file_id.in_(file_ids)).limit(100))).scalars().all()
        knowledge = (await db.execute(select(KnowledgeNodeModel).filter(KnowledgeNodeModel.rim_entity_id.in_(file_ids)).limit(50))).scalars().all()

    title = f"Documentation Draft: {path or 'Repository'}"
    lines = [f"# {title}", "", "## Files"]
    lines.extend(f"- `{f.path}` ({f.language})" for f in files)
    lines.extend(["", "## Public Surface"])
    lines.extend(f"- `{s.name}` ({s.symbol_type})" for s in symbols[:80])
    if routes:
        lines.extend(["", "## Routes"])
        lines.extend(f"- `{r.method} {r.path}` -> `{r.handler}`" for r in routes)
    summaries = []
    for node in knowledge:
        summary = (node.semantics or {}).get("summary")
        if isinstance(summary, list) and summary:
            summaries.append(summary[0])
    if summaries:
        lines.extend(["", "## Generated Summary"])
        lines.extend(f"- {summary}" for summary in summaries[:20])

    return {"title": title, "markdown": "\n".join(lines)}

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
