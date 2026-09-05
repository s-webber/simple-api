from unittest.mock import AsyncMock

import httpx
import pytest

from app.github import (
    GitHubClient,
    GitHubError,
    GitHubNotFoundError,
    GitHubRateLimitError,
)


def make_response(status_code: int, json_data: dict | None = None):
    request = httpx.Request(
        "GET",
        "https://api.github.com/repos/foo/bar",
    )

    return httpx.Response(
        status_code,
        json=json_data,
        request=request,
    )


# TODO remove @pytest.mark.asyncio
async def test_get_repository() -> None:
    http_client = AsyncMock()

    http_client.get.return_value = make_response(
        200,
        {
            "name": "bar",
            "full_name": "foo/bar",
            "description": "A test repository",
            "stargazers_count": 100,
            "forks_count": 20,
            "open_issues_count": 5,
            "language": "Python",
            "default_branch": "main",
        },
    )

    github = GitHubClient(http_client)

    result = await github.get_repository("foo", "bar")

    assert result.name == "bar"
    assert result.full_name == "foo/bar"
    assert result.stars == 100
    assert result.forks == 20
    assert result.open_issues == 5
    assert result.language == "Python"
    assert result.default_branch == "main"

    http_client.get.assert_awaited_once_with("https://api.github.com/repos/foo/bar")


# TODO remove @pytest.mark.asyncio
async def test_get_repository_not_found() -> None:
    http_client = AsyncMock()

    http_client.get.return_value = make_response(404)

    github = GitHubClient(http_client)

    with pytest.raises(GitHubNotFoundError):
        await github.get_repository("foo", "bar")


# TODO remove @pytest.mark.asyncio
async def test_get_repository_rate_limited() -> None:
    http_client = AsyncMock()

    http_client.get.return_value = make_response(403)

    github = GitHubClient(http_client)

    with pytest.raises(GitHubRateLimitError):
        await github.get_repository("foo", "bar")


# TODO remove @pytest.mark.asyncio
async def test_get_repository_request_error() -> None:
    http_client = AsyncMock()

    http_client.get.side_effect = httpx.RequestError("Connection failed")

    github = GitHubClient(http_client)

    with pytest.raises(GitHubError):
        await github.get_repository("foo", "bar")
