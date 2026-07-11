import os
import time
import uuid
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import event_bus
from app.core.logger import get_logger
from app.enrichment.pipeline import KnowledgePipeline
from app.models import ParsingReport, RepositoryVersion
from app.models.enrichment.node import KnowledgeNodeModel
from app.models.enums import RepositoryStatus
from app.models.rim.models import (
    RIMCallModel,
    RIMDirectoryModel,
    RIMFileModel,
    RIMImportModel,
    RIMRouteModel,
    RIMSymbolModel,
    RIMInheritanceModel,
    RIMReturnModel,
)
from app.parser import initialize_registry
from app.parser.detector import LanguageDetector
from app.parser.models import ParseResult
from app.parser.registry import ParserRegistry
from app.rim.domain.models import (
    DomainCall,
    DomainDirectory,
    DomainFile,
    DomainImport,
    DomainRoute,
    DomainSymbol,
    DomainInheritance,
    DomainReturn,
)
from app.skg.builder import SKGBuilder

logger = get_logger(__name__)

class ParsingOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Ensure plugins are registered
        initialize_registry()

    async def parse_repository_version(self, version_id: str | uuid.UUID):
        if isinstance(version_id, str):
            import uuid
            version_id = uuid.UUID(version_id)
        result = await self.db.execute(select(RepositoryVersion).filter(RepositoryVersion.id == version_id))
        version = result.scalars().first()
        
        if not version or not version.clone_path:
            logger.error("RepositoryVersion not found or has no clone_path", version_id=str(version_id))
            return
            
        version.status = RepositoryStatus.PARSING
        await self.db.commit()
        await self.db.refresh(version)
        await event_bus.publish("ParsingStarted", version_id=str(version_id))
        
        start_time = time.time()
        
        # 1. Walk directory and group files by language
        files_by_lang: dict[str, list[str]] = defaultdict(list)
        for root, _, files in os.walk(version.clone_path):
            if ".git" in root:
                continue
            for file in files:
                filepath = os.path.join(root, file)
                lang = LanguageDetector.detect(filepath)
                files_by_lang[lang].append(filepath)
                
        # 2. Track stats
        report = ParsingReport(repository_version_id=version.id)
        report.languages_detected = list(files_by_lang.keys())
        
        unsupported_count = len(files_by_lang.get("unsupported", []))
        report.unsupported_files = unsupported_count
        report.skipped_files = unsupported_count
        
        parsed_count = 0
        failed_count = 0
        
        # 3. Parse files per language
        for lang, filepaths in files_by_lang.items():
            if lang == "unsupported":
                continue
                
            plugin_cls = ParserRegistry.get_plugin(lang)
            if not plugin_cls:
                report.skipped_files += len(filepaths)
                logger.warning("No plugin found for language", language=lang)
                continue
                
            try:
                # In-memory ParseResult returned
                parse_result = plugin_cls.parse_files(filepaths)
                parsed_count += len(parse_result.files)
                await self.persist_rim(version, parse_result)
            except Exception as e:
                logger.error("Plugin parsing failed", language=lang, error=str(e))
                failed_count += len(filepaths)
                report.errors_count += 1
                
        report.parsed_files = parsed_count
        report.failed_files = failed_count
        report.parse_time_ms = int((time.time() - start_time) * 1000)
        
        self.db.add(report)
        version.status = RepositoryStatus.PARSED
        await self.db.commit()
        await self.db.refresh(report)
        await self.db.refresh(version)
        
        # Build SKG
        await self.build_skg_and_knowledge(version)
        
        await event_bus.publish("ParsingCompleted", version_id=str(version_id), report_id=str(report.id))
        logger.info("Parsing completed", version_id=str(version_id), report_id=str(report.id))

    async def build_skg_and_knowledge(self, version: RepositoryVersion):
        # 1. Fetch domain models from DB
        dirs = (await self.db.execute(select(RIMDirectoryModel).filter_by(repository_version_id=version.id))).scalars().all()
        files = (await self.db.execute(select(RIMFileModel).filter_by(repository_version_id=version.id))).scalars().all()
        symbols = (await self.db.execute(select(RIMSymbolModel).filter_by(repository_version_id=version.id))).scalars().all()
        imports = (await self.db.execute(select(RIMImportModel).filter_by(repository_version_id=version.id))).scalars().all()
        routes = (await self.db.execute(select(RIMRouteModel).filter_by(repository_version_id=version.id))).scalars().all()
        calls = (await self.db.execute(select(RIMCallModel).filter_by(repository_version_id=version.id))).scalars().all()
        inheritance = (await self.db.execute(select(RIMInheritanceModel).filter_by(repository_version_id=version.id))).scalars().all()
        returns = (await self.db.execute(select(RIMReturnModel).filter_by(repository_version_id=version.id))).scalars().all()

        domain_dirs = [DomainDirectory(id=d.id, repository_id=d.repository_id, repository_version_id=d.repository_version_id, path=d.path, parent_id=d.parent_id) for d in dirs]
        domain_files = [DomainFile(id=f.id, repository_id=f.repository_id, repository_version_id=f.repository_version_id, path=f.path, directory_id=f.directory_id, language=f.language) for f in files]
        domain_symbols = [DomainSymbol(id=s.id, repository_id=s.repository_id, repository_version_id=s.repository_version_id, file_id=s.file_id, name=s.name, fully_qualified_name=s.fully_qualified_name, symbol_type=s.symbol_type, parent_symbol_id=s.parent_symbol_id) for s in symbols]
        domain_imports = [DomainImport(id=i.id, repository_id=i.repository_id, repository_version_id=i.repository_version_id, file_id=i.file_id, raw_statement=i.raw_statement) for i in imports]
        domain_routes = [DomainRoute(id=r.id, repository_id=r.repository_id, repository_version_id=r.repository_version_id, file_id=r.file_id, method=r.method, path=r.path, handler=r.handler) for r in routes]
        domain_calls = [DomainCall(id=c.id, repository_id=c.repository_id, repository_version_id=c.repository_version_id, file_id=c.file_id, function_name=c.function_name, receiver=c.receiver, caller_function_name=c.caller_function_name, byte_offset=c.byte_offset) for c in calls]
        domain_inheritance = [DomainInheritance(id=h.id, repository_id=h.repository_id, repository_version_id=h.repository_version_id, file_id=h.file_id, class_name=h.class_name, parent_name=h.parent_name, inheritance_type=h.inheritance_type) for h in inheritance]
        domain_returns = [DomainReturn(id=n.id, repository_id=n.repository_id, repository_version_id=n.repository_version_id, file_id=n.file_id, function_name=n.function_name, return_type=n.return_type) for n in returns]

        # 2. Build SKG
        builder = SKGBuilder(self.db, version.id)
        builder.build_structural_edges(domain_dirs, domain_files, domain_symbols)
        builder.build_route_edges(domain_routes, domain_symbols)
        builder.build_import_edges(domain_imports, domain_files)
        builder.build_call_edges(domain_calls, domain_symbols)
        builder.build_dependency_edges(domain_files, domain_dirs)
        builder.build_inheritance_edges(domain_inheritance, domain_symbols)
        builder.build_return_type_edges(domain_returns, domain_symbols)
        await builder.commit_to_database()

        # 3. Knowledge Pipeline
        pipeline = KnowledgePipeline()
        # For this scope, let's just enrich files
        # A full system would persist KnowledgeNodes in a NoSQL/graph db or a separate table
        knowledge_nodes = []
        for f in domain_files:
            node = await pipeline.execute(f, "File", builder.edges, None)
            if node:
                knowledge_nodes.append(node)
                self.db.add(KnowledgeNodeModel(
                    id=node.identity.id,
                    repository_id=node.identity.repository_id,
                    repository_version_id=node.identity.repository_version_id,
                    rim_entity_id=node.identity.rim_entity_id,
                    skg_node_id=node.identity.skg_node_id,
                    entity_type=node.identity.entity_type,
                    semantics=node.semantics.model_dump(mode="json"),
                    metrics=node.metrics.model_dump(mode="json"),
                    documentation=node.documentation.model_dump(mode="json"),
                    relationships=node.relationships.model_dump(mode="json"),
                    metadata_=node.metadata.model_dump(mode="json"),
                    provenance={key: value.model_dump(mode="json") for key, value in node.provenance.items()},
                ))
        await self.db.commit()

        # 4. Embeddings
        if knowledge_nodes:
            version.status = RepositoryStatus.EMBEDDING
            await self.db.commit()
            
            from app.embeddings.orchestrator import EmbeddingOrchestrator
            collection_id = version.repository_id # Using repository_id as collection_id
            embedding_orch = EmbeddingOrchestrator(self.db, collection_id)
            embedded_count = await embedding_orch.process_nodes(knowledge_nodes, str(version.id))
            logger.info("Embeddings completed", embedded_count=embedded_count)
            
        version.status = RepositoryStatus.READY
        await self.db.commit()

    async def persist_rim(self, version: RepositoryVersion, parse_result: ParseResult):
        # We need a robust way to avoid duplicate directories. 
        # Using a simple dictionary to track created directories by relative path.
        dir_map = {}
        file_map = {}
        
        # Create a root directory
        root_dir = RIMDirectoryModel(
            repository_id=version.repository_id,
            repository_version_id=version.id,
            path="/",
            parent_id=None
        )
        self.db.add(root_dir)
        await self.db.flush()
        root_dir_id = root_dir.id

        for filepath in parse_result.files:
            rel_path = os.path.relpath(filepath, version.clone_path)
            parts = rel_path.split(os.sep)
            
            # Create directories
            parent_id = root_dir_id
            current_dir_path = ""
            for i in range(len(parts) - 1):
                part = parts[i]
                current_dir_path = os.path.join(current_dir_path, part) if current_dir_path else part
                
                if current_dir_path not in dir_map:
                    dir_model = RIMDirectoryModel(
                        repository_id=version.repository_id,
                        repository_version_id=version.id,
                        path=current_dir_path,
                        parent_id=parent_id
                    )
                    self.db.add(dir_model)
                    await self.db.flush() # Flush to get UUID
                    dir_map[current_dir_path] = dir_model.id
                
                parent_id = dir_map[current_dir_path]
            
            # Create file
            file_model = RIMFileModel(
                repository_id=version.repository_id,
                repository_version_id=version.id,
                directory_id=parent_id,
                path=rel_path,
                language=parse_result.language
            )
            self.db.add(file_model)
            await self.db.flush()
            file_map[filepath] = file_model.id

        # Insert symbols
        for sym in parse_result.symbols:
            if sym["file"] in file_map:
                self.db.add(RIMSymbolModel(
                    repository_id=version.repository_id,
                    repository_version_id=version.id,
                    file_id=file_map[sym["file"]],
                    name=sym["name"],
                    fully_qualified_name=sym["name"],
                    symbol_type=sym["type"]
                ))
                
        # Insert imports
        for imp in parse_result.imports:
            if imp["file"] in file_map:
                self.db.add(RIMImportModel(
                    repository_id=version.repository_id,
                    repository_version_id=version.id,
                    file_id=file_map[imp["file"]],
                    raw_statement=imp["raw"]
                ))
                
        # Insert routes
        for route in parse_result.routes:
            if route["file"] in file_map:
                self.db.add(RIMRouteModel(
                    repository_id=version.repository_id,
                    repository_version_id=version.id,
                    file_id=file_map[route["file"]],
                    method=route.get("method", "GET"),
                    path=route.get("path", "/"),
                    handler=route.get("handler", "unknown")
                ))

        # Insert raw call references so SKG can resolve CALLS edges later.
        for call in parse_result.calls:
            if call["file"] in file_map:
                self.db.add(RIMCallModel(
                    repository_id=version.repository_id,
                    repository_version_id=version.id,
                    file_id=file_map[call["file"]],
                    function_name=call.get("function", "unknown"),
                    receiver=call.get("receiver"),
                    caller_function_name=call.get("caller_function_name"),
                    byte_offset=call.get("byte_offset"),
                ))

        for inh in parse_result.inheritance:
            if inh["file"] in file_map:
                self.db.add(RIMInheritanceModel(
                    repository_id=version.repository_id,
                    repository_version_id=version.id,
                    file_id=file_map[inh["file"]],
                    class_name=inh["class"],
                    parent_name=inh["parent"],
                    inheritance_type=inh["type"],
                ))

        for ret in parse_result.returns:
            if ret["file"] in file_map:
                self.db.add(RIMReturnModel(
                    repository_id=version.repository_id,
                    repository_version_id=version.id,
                    file_id=file_map[ret["file"]],
                    function_name=ret["function"],
                    return_type=ret["returns"],
                ))
