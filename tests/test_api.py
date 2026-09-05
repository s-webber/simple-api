import pytest
from fastapi.testclient import TestClient

from app.github import (
    GitHubError,
    GitHubNotFoundError,
    GitHubRateLimitError,
)
from app.main import app, get_github_client
from app.models import RepositoryStats


@pytest.fixture
def client():
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


class FakeGitHubClient:
    async def get_repository(self, owner: str, repo: str) -> RepositoryStats:
        return RepositoryStats(
            name=repo,
            full_name=f"{owner}/{repo}",
            description="A test repository",
            stars=100,
            forks=20,
            open_issues=5,
            language="Python",
            default_branch="main",
        )


def test_repository_stats(client) -> None:
    app.dependency_overrides[get_github_client] = lambda: FakeGitHubClient()

    response = client.get("/repos/foo/bar")

    assert response.status_code == 200
    assert response.json() == {
        "name": "bar",
        "full_name": "foo/bar",
        "description": "A test repository",
        "stars": 100,
        "forks": 20,
        "open_issues": 5,
        "language": "Python",
        "default_branch": "main",
    }


class FakeGitHubClientNotFound:
    async def get_repository(
        self,
        owner: str,
        repo: str,
    ) -> RepositoryStats:
        raise GitHubNotFoundError()


def test_repository_not_found(client) -> None:
    app.dependency_overrides[get_github_client] = lambda: FakeGitHubClientNotFound()

    response = client.get("/repos/foo/bar")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Repository not found",
    }


class FakeGitHubClientRateLimited:
    async def get_repository(
        self,
        owner: str,
        repo: str,
    ) -> RepositoryStats:
        raise GitHubRateLimitError()


def test_github_rate_limit(client) -> None:
    app.dependency_overrides[get_github_client] = lambda: FakeGitHubClientRateLimited()

    response = client.get("/repos/foo/bar")

    assert response.status_code == 429
    assert response.json() == {
        "detail": "GitHub API rate limit exceeded",
    }


class FakeGitHubClientError:
    async def get_repository(
        self,
        owner: str,
        repo: str,
    ) -> RepositoryStats:
        raise GitHubError()


def test_github_error(client) -> None:
    app.dependency_overrides[get_github_client] = lambda: FakeGitHubClientError()

    response = client.get("/repos/foo/bar")

    assert response.status_code == 502
    assert response.json() == {
        "detail": "GitHub API is unavailable",
    }


def test_health(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
