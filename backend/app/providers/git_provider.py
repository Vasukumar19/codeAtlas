import asyncio
from typing import Optional
from git import Repo
from app.providers.base import GitProvider
from app.core.logger import get_logger

logger = get_logger(__name__)

class GitPythonProvider(GitProvider):
    async def clone(self, remote_url: str, clone_path: str, branch: Optional[str] = None) -> str:
        logger.info("Starting git clone", remote_url=remote_url, clone_path=clone_path, branch=branch)
        def _clone():
            kwargs = {"depth": 1}
            if branch:
                kwargs["branch"] = branch
            repo = Repo.clone_from(remote_url, clone_path, **kwargs)
            return repo.head.commit.hexsha

        loop = asyncio.get_event_loop()
        commit_hash = await loop.run_in_executor(None, _clone)
        logger.info("Clone complete", commit_hash=commit_hash)
        return commit_hash

    async def get_remote_hash(self, remote_url: str, branch: Optional[str] = None) -> str:
        logger.info("Fetching remote hash", remote_url=remote_url, branch=branch)
        def _get_hash():
            import git
            g = git.cmd.Git()
            # ls-remote returns "<hash>\t<ref>"
            refs = g.ls_remote(remote_url, branch if branch else "HEAD").split('\n')
            if not refs or not refs[0]:
                raise ValueError(f"Could not fetch remote hash for {remote_url}")
            return refs[0].split('\t')[0]
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_hash)
