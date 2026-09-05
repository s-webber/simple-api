A small FastAPI application.

Setup
```
python -m venv venv
venv\Scripts\activate
pip install -e ".[dev,docs]"
pre-commit install
```

Quality checks
```
ruff check . && ruff format --check . && mypy app && pytest
```

Start application
```
uvicorn app.main:app --reload
```

Once the application is running, access Swagger documentation at:
```
http://127.0.0.1:8000/docs
```

`mkdocs serve` will generate code documentation. It will be viewable at http://localhost:8000/
