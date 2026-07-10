import asyncio
import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.retrieval.trace import RetrievalTraceModel
from app.retrieval.builder import ContextBuilder
from app.retrieval.domain.schemas import ContextPackage, UserQuery
from app.retrieval.fusion import ResultFusion
from app.retrieval.intent.detector import IntentDetector
from app.retrieval.planner import QueryPlanner
from app.retrieval.ranker import ContextRanker
from app.retrieval.registry import RetrievalRegistry
from app.retrieval.validator import RetrievalValidator


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
        intent = await self.detector.detect(query)
        
        # 2. Plan Query
        plan = self.planner.plan(intent)
        
        # 3. Execute Retrievers Concurrently
        tasks = []
        for retriever_name in plan.retrievers:
            retriever = RetrievalRegistry.get(retriever_name)
            if retriever:
                tasks.append(retriever.retrieve(query, self.db))
                
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
