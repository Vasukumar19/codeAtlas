"""Safe shallow-clone operations for repository snapshots."""

import shutil
import subprocess
from pathlib import Path


class GitCloneError(RuntimeError):
    """Raised when Git cannot prepare the requested snapshot."""


class GitService:
    """Perform shallow Git clones and guarantee cleanup after failed clones."""

    def clone(self, remote_url: str, branch: str, destination: Path) -> str:
        """Clone one branch, return its checked-out commit, and clean failures."""
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._run("clone", "--depth", "1", "--branch", branch, remote_url, str(destination))
            return self._run("-C", str(destination), "rev-parse", "HEAD").strip()
        except (OSError, subprocess.CalledProcessError) as error:
            shutil.rmtree(destination, ignore_errors=True)
            detail = error.stderr.strip() if isinstance(error, subprocess.CalledProcessError) else str(error)
            raise GitCloneError(detail) from error

    @staticmethod
    def _run(*arguments: str) -> str:
        """Run Git without invoking a shell or exposing credentials in output."""
        completed = subprocess.run(
            ["git", *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout
