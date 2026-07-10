"""GitHub URL validation and public repository metadata retrieval."""

import asyncio
import re
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import HTTPException, status

from app.core.config import settings

GITHUB_URL_PATTERN = re.compile(
    r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<name>[A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)


@dataclass(frozen=True)
class GitHubRepositoryMetadata:
    """Validated metadata returned by the public GitHub repository API."""

    owner: str
    name: str
    remote_url: str
    description: str | None
    default_branch: str
    latest_commit: str
    primary_language: str | None
    topics: list[str]
    stars: int
    forks: int


class GitHubClient:
    """Small, dependency-free client for public GitHub repository metadata."""

    def parse_url(self, remote_url: str) -> tuple[str, str, str]:
        """Validate and canonicalize a public HTTPS GitHub repository URL."""
        match = GITHUB_URL_PATTERN.fullmatch(remote_url.strip())
        if match is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only HTTPS GitHub repository URLs are supported.",
            )
        owner, name = match.group("owner"), match.group("name")
        return owner, name, f"https://github.com/{owner}/{name}.git"

    async def get_repository(
        self, remote_url: str, branch: str | None = None, token: str | None = None
    ) -> GitHubRepositoryMetadata:
        """Validate repository existence/public access and obtain selected ref SHA."""
        owner, name, canonical_url = self.parse_url(remote_url)
        repository = await asyncio.to_thread(self._request_json, f"/repos/{owner}/{name}", token)
        if repository.get("private", False):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only public repositories are supported.",
            )
        selected_branch = branch or repository["default_branch"]
        commit = await asyncio.to_thread(
            self._request_json,
            f"/repos/{owner}/{name}/commits/{selected_branch}",
            token,
        )
        return GitHubRepositoryMetadata(
            owner=owner,
            name=name,
            remote_url=canonical_url,
            description=repository.get("description"),
            default_branch=repository["default_branch"],
            latest_commit=commit["sha"],
            primary_language=repository.get("language"),
            topics=repository.get("topics", []),
            stars=repository.get("stargazers_count", 0),
            forks=repository.get("forks_count", 0),
        )

    def _request_json(self, path: str, token: str | None) -> dict:
        """Perform a GitHub API request and map transport failures to HTTP errors."""
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "CodeAtlas"}
        if token or settings.github_token:
            headers["Authorization"] = f"Bearer {token or settings.github_token}"
        request = Request(f"{settings.github_api_url}{path}", headers=headers)
        try:
            with urlopen(request, timeout=15) as response:
                import json

                return json.load(response)
        except HTTPError as error:
            detail = "Repository was not found or is not publicly accessible."
            if error.code == 404:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from error
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail) from error
        except URLError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GitHub is unavailable; retry the import later.",
            ) from error
