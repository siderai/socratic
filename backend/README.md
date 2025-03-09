# Backend API

This is the backend API for the application.

## Setup

1. Install Poetry (dependency management):
   ```bash
   # Linux, macOS, Windows (WSL)
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Windows (PowerShell)
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env` and update the values
   - For testing, use `.env.test`

4. Run database migrations:
   ```bash
   poetry run alembic upgrade head
   ```

## Running the Application

```bash
# Activate the virtual environment
poetry shell

# Run the application
uvicorn app.main:app --reload

# Or run without activating the virtual environment
poetry run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/endpoints/test_auth.py

# Run with verbose output
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=app
```

## Development Tools

Poetry includes several development tools:

```bash
# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run ruff check .
poetry run mypy .
```

## Project Structure

- `app/`: Main application package
  - `api/`: API endpoints and dependencies
  - `db/`: Database models and repositories
  - `schemas/`: Pydantic models for request/response validation
  - `services/`: Business logic services
  - `caching/`: Redis caching functionality
  - `main.py`: Application entry point
  - `settings.py`: Application settings

- `tests/`: Test package
  - `endpoints/`: API endpoint tests
  - `conftest.py`: Test fixtures and configuration 