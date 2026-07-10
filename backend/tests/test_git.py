"""Tests for safe shallow-clone command construction and cleanup."""

import subprocess
from pathlib import Path

import pytest

from app.services.git import GitCloneError, GitService


def test_clone_uses_depth_and_branch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A clone requests only the chosen branch history."""
    calls: list[tuple[str, ...]] = []

    def run(*arguments: str) -> str:
        calls.append(arguments)
        return "abc123\n" if "rev-parse" in arguments else ""

    monkeypatch.setattr(GitService, "_run", staticmethod(run))
    commit = GitService().clone("https://github.com/acme/demo.git", "main", tmp_path / "snapshot")
    assert commit == "abc123"
    assert calls[0][:5] == ("clone", "--depth", "1", "--branch", "main")


def test_clone_converts_git_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Git failures are exposed as a domain error and remove partial output."""
    destination = tmp_path / "snapshot"
    destination.mkdir()
    monkeypatch.setattr(
        GitService,
        "_run",
        staticmethod(lambda *_: (_ for _ in ()).throw(subprocess.CalledProcessError(1, "git", stderr="failed"))),
    )
    with pytest.raises(GitCloneError):
        GitService().clone("https://github.com/acme/demo.git", "main", destination)
    assert not destination.exists()
