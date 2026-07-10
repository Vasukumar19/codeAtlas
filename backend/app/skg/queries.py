import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SKGQueries:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_route_to_service(self, repository_version_id: uuid.UUID, route_path: str):
        # Natively traverses the SKG using a recursive CTE!
        # This answers: "Find every Route -> Function -> Service"
        # Since we mapped Routes -> ROUTES_TO -> Function, we can just follow edges.
        
        query = text("""
            WITH RECURSIVE skg_path AS (
                -- 1. Find the Route Node
                SELECT r.id as node_id, r.path as name, 0 as depth, 'ROUTE' as type
                FROM rim_routes r
                WHERE r.repository_version_id = :version_id AND r.path = :route_path
                
                UNION ALL
                
                -- 2. Traverse ROUTES_TO or CONTAINS or DECLARES
                SELECT e.target_id, e.edge_type, p.depth + 1, 'NODE'
                FROM skg_edges e
                JOIN skg_path p ON e.source_id = p.node_id
                WHERE e.repository_version_id = :version_id
                  AND e.edge_type IN ('ROUTES_TO', 'CONTAINS', 'DECLARES')
                  AND p.depth < 10
            )
            SELECT * FROM skg_path;
        """)
        
        result = await self.db.execute(query, {"version_id": str(repository_version_id), "route_path": route_path})
        return [dict(row._mapping) for row in result]
