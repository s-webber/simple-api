from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from .github import (
    GitHubClient,
    GitHubError,
    GitHubNotFoundError,
    GitHubRateLimitError,
)
from .models import RepositoryStats


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.http_client = httpx.AsyncClient(timeout=10.0)
    yield
    await app.state.http_client.aclose()


app = FastAPI(
    title="GitHub Repository Stats",
    lifespan=lifespan,
)


def get_github_client(request: Request) -> GitHubClient:
    return GitHubClient(request.app.state.http_client)


@app.exception_handler(GitHubNotFoundError)
async def github_not_found_handler(
    request: Request,
    exc: GitHubNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": "Repository not found"},
    )


@app.exception_handler(GitHubRateLimitError)
async def github_rate_limit_handler(
    request: Request,
    exc: GitHubRateLimitError,
) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "GitHub API rate limit exceeded"},
    )


@app.exception_handler(GitHubError)
async def github_error_handler(
    request: Request,
    exc: GitHubError,
) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={"detail": "GitHub API is unavailable"},
    )


@app.get("/repos/{owner}/{repo}", response_model=RepositoryStats)
async def repository_stats(
    owner: str,
    repo: str,
    github: GitHubClient = Depends(get_github_client),  # noqa: B008
) -> RepositoryStats:
    return await github.get_repository(owner, repo)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
