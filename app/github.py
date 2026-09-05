import httpx

from .models import RepositoryStats


class GitHubError(Exception):
    """Base exception for GitHub API errors."""


class GitHubNotFoundError(GitHubError):
    """GitHub resource was not found."""


class GitHubRateLimitError(GitHubError):
    """GitHub API rate limit was exceeded."""


class GitHubClient:
    """Client for retrieving repository information from GitHub."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Create a GitHub client using the supplied HTTP client."""
        self.client = client

    async def get_repository(
        self,
        owner: str,
        repo: str,
    ) -> RepositoryStats:
        """Return statistics for a GitHub repository.

        Args:
            owner: GitHub repository owner.
            repo: Repository name.

        Returns:
            Repository statistics validated by Pydantic.

        Raises:
            httpx.HTTPStatusError: If GitHub returns an error response.
        """
        try:
            response = await self.client.get(
                f"https://api.github.com/repos/{owner}/{repo}"
            )
            response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise GitHubNotFoundError(
                    f"Repository {owner}/{repo} was not found"
                ) from exc

            if exc.response.status_code == 403:
                raise GitHubRateLimitError(
                    "GitHub API access was forbidden or rate limited"
                ) from exc

            raise GitHubError("GitHub API returned an unexpected error") from exc

        except httpx.RequestError as exc:
            raise GitHubError("Unable to connect to GitHub") from exc

        data = response.json()

        return RepositoryStats(
            name=data["name"],
            full_name=data["full_name"],
            description=data["description"],
            stars=data["stargazers_count"],
            forks=data["forks_count"],
            open_issues=data["open_issues_count"],
            language=data["language"],
            default_branch=data["default_branch"],
        )
