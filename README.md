A small FastAPI application.

Setup
```
uv sync
pre-commit install
```

Quality checks
```
uv run ruff check .
uv run ruff format --check .
uv run mypy app
uv run pytest
```

Start application
```
uv run fastapi run
```

Once the application is running, access Swagger documentation at:
```
http://127.0.0.1:8000/docs
```

`mkdocs serve` will generate code documentation. It will be viewable at http://localhost:8000/
