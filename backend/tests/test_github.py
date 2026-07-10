"""Tests for GitHub URL validation behavior."""

import pytest
from fastapi import HTTPException

from app.services.github import GitHubClient


def test_parse_url_returns_canonical_clone_url() -> None:
    """A GitHub page URL becomes its canonical clone URL."""
    assert GitHubClient().parse_url("https://github.com/openai/openai-python") == (
        "openai",
        "openai-python",
        "https://github.com/openai/openai-python.git",
    )


def test_parse_url_rejects_unsupported_provider() -> None:
    """Only HTTPS GitHub URLs are accepted in this milestone."""
    with pytest.raises(HTTPException) as error:
        GitHubClient().parse_url("https://gitlab.com/openai/openai-python")
    assert error.value.status_code == 422
