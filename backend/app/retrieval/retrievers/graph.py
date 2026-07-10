import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.retrieval.retrievers.base import BaseRetriever, RetrievalResult, UserQuery
from app.skg.queries import SKGQueries


class GraphRetriever(BaseRetriever):
    async def retrieve(self, query: UserQuery, db: AsyncSession) -> list[RetrievalResult]:
        # If query contains a path-like string, use SKG Queries
        q = query.query.lower()
        if "/" in q:
            route_path = q.split(" ")[-1] if " " in q else q
            skg_queries = SKGQueries(db)
            path_nodes = await skg_queries.find_route_to_service(query.repository_version_id, route_path)
            
            return [
                RetrievalResult(
                    node_id=n["node_id"] if "node_id" in n else n.get("target_id", uuid.uuid4()),
                    entity_type=n.get("type", "GraphPath"),
                    relevance_score=0.9,
                    evidence=[f"Graph traversal found node at depth {n.get('depth', 0)}"]
                ) for n in path_nodes
            ]
        return []
