import os

files = {
    "backend/app/retrieval/fusion.py": """
from typing import List, Dict
import uuid
from app.retrieval.domain.schemas import RetrievalResult

class ResultFusion:
    def fuse(self, results_lists: List[List[RetrievalResult]]) -> List[RetrievalResult]:
        fused_map: Dict[uuid.UUID, RetrievalResult] = {}
        
        for results in results_lists:
            if not results:
                continue
            for r in results:
                if r.node_id in fused_map:
                    # Merge evidence and boost score
                    existing = fused_map[r.node_id]
                    existing.evidence.extend([e for e in r.evidence if e not in existing.evidence])
                    existing.relevance_score = min(1.0, existing.relevance_score + (r.relevance_score * 0.2))
                else:
                    fused_map[r.node_id] = r
                    
        return list(fused_map.values())
""",
    "backend/app/retrieval/ranker.py": """
from typing import List
from app.retrieval.domain.schemas import RetrievalResult

class ContextRanker:
    def rank(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        # Sort by relevance_score descending
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)
""",
    "backend/app/retrieval/validator.py": """
from typing import List
from app.retrieval.domain.schemas import ContextPackage

class RetrievalValidator:
    def validate(self, package: ContextPackage) -> bool:
        # Check if empty context
        if not package.relevant_entities and not package.relevant_routes and not package.relevant_graph_paths:
            return False
        return True
""",
    "backend/app/retrieval/builder.py": """
from typing import List
from app.retrieval.domain.schemas import ContextPackage, RetrievalResult

class ContextBuilder:
    def build(self, ranked_results: List[RetrievalResult], repository_id: str) -> ContextPackage:
        package = ContextPackage(repository_summary="Automated repo summary")
        
        for r in ranked_results:
            if r.entity_type == "Route":
                package.relevant_routes.append(r)
            elif r.entity_type == "GraphPath":
                package.relevant_graph_paths.append(str(r.node_id))
            else:
                package.relevant_entities.append(r)
                
            package.confidence_scores[str(r.node_id)] = r.relevance_score
            
        return package
""",
    "backend/app/retrieval/engine.py": """
import time
import uuid
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.retrieval.domain.schemas import UserQuery, ContextPackage
from app.retrieval.intent.detector import IntentDetector
from app.retrieval.planner import QueryPlanner
from app.retrieval.registry import RetrievalRegistry
from app.retrieval.fusion import ResultFusion
from app.retrieval.ranker import ContextRanker
from app.retrieval.builder import ContextBuilder
from app.retrieval.validator import RetrievalValidator
from app.models.retrieval.trace import RetrievalTraceModel

class HybridRetrievalEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.detector = IntentDetector()
        self.planner = QueryPlanner()
        self.fusion = ResultFusion()
        self.ranker = ContextRanker()
        self.builder = ContextBuilder()
        self.validator = RetrievalValidator()
        
    async def retrieve(self, query: UserQuery) -> ContextPackage:
        start_time = time.time()
        
        # 1. Detect Intent
        intent = self.detector.detect(query)
        
        # 2. Plan Query
        plan = self.planner.plan(intent)
        
        # 3. Execute Retrievers Concurrently
        tasks = []
        for retriever_name in plan.retrievers:
            retriever = RetrievalRegistry.get(retriever_name)
            if retriever:
                tasks.append(retriever.retrieve(query))
                
        results_lists = await asyncio.gather(*tasks) if tasks else []
        
        # 4. Result Fusion
        fused_results = self.fusion.fuse(results_lists)
        
        # 5. Rank Context
        ranked_results = self.ranker.rank(fused_results)
        
        # 6. Build Context Package
        package = self.builder.build(ranked_results, str(query.repository_id))
        
        # 7. Validate
        if not self.validator.validate(package):
            # If invalid/empty, maybe fallback? For now return empty.
            package = ContextPackage()
            
        # 8. Trace
        execution_time_ms = int((time.time() - start_time) * 1000)
        trace = RetrievalTraceModel(
            id=uuid.uuid4(),
            repository_id=query.repository_id,
            user_query=query.query,
            intent=intent.value,
            plan={"retrievers": plan.retrievers},
            execution_time_ms=execution_time_ms,
            final_context_hash="mock_hash",
            details={"ranked_results": len(ranked_results)}
        )
        self.db.add(trace)
        await self.db.commit()
        
        return package
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
