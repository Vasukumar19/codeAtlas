import os
import time
from collections import defaultdict
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import RepositoryVersion, ParsingReport
from app.models.enums import RepositoryStatus
from app.parser.detector import LanguageDetector
from app.parser.registry import ParserRegistry
from app.parser import initialize_registry
from app.core.logger import get_logger
from app.core.events import event_bus

logger = get_logger(__name__)

class ParsingOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Ensure plugins are registered
        initialize_registry()

    async def parse_repository_version(self, version_id: str):
        result = await self.db.execute(select(RepositoryVersion).filter(RepositoryVersion.id == version_id))
        version = result.scalars().first()
        
        if not version or not version.clone_path:
            logger.error("RepositoryVersion not found or has no clone_path", version_id=str(version_id))
            return
            
        version.status = RepositoryStatus.PARSING
        await self.db.commit()
        await event_bus.publish("ParsingStarted", version_id=str(version_id))
        
        start_time = time.time()
        
        # 1. Walk directory and group files by language
        files_by_lang: Dict[str, List[str]] = defaultdict(list)
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
        
        await event_bus.publish("ParsingCompleted", version_id=str(version_id), report_id=str(report.id))
        logger.info("Parsing completed", version_id=str(version_id), report_id=str(report.id))
