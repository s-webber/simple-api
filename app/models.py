from pydantic import BaseModel


class RepositoryStats(BaseModel):
    name: str
    full_name: str
    description: str | None
    stars: int
    forks: int
    open_issues: int
    language: str | None
    default_branch: str
