# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python REST API sample application built with FastAPI following TDD practices. The project implements a task management API with full CRUD operations and is designed as a template for backend development.

## Development Commands

**Project Setup:**
```bash
uv sync --dev  # Install dependencies including dev tools
```

**Development Server:**
```bash
uv run python main.py                    # Start development server on port 8000
uv run uvicorn src.api.main:app --reload # Alternative with hot reload
```

**Testing:**
```bash
uv run pytest                           # Run all tests
uv run pytest tests/test_api.py -v      # Run specific test file with verbose output
uv run pytest -k "test_create_task"     # Run specific test by name
uv run python contract_test.py          # Run API contract tests against OpenAPI spec
```

**Code Quality:**
```bash
uv run ruff check .                     # Lint code
uv run ruff check --fix .               # Auto-fix linting issues
uv run mypy src/                        # Type checking
uv run lizard src/                      # Complexity analysis
```

**Quality Check All:**
```bash
uv run ruff check . && uv run mypy src/ && uv run pytest && uv run lizard src/
```

**Pre-commit Hooks:**
```bash
uv run pre-commit install           # Install pre-commit hooks (one-time setup)
uv run pre-commit run --all-files   # Run all hooks manually
git commit -m "message"             # Hooks run automatically on commit
```

**⚠️ Important: Manual Contract Testing Required**
OpenAPI contract testing is excluded from pre-commit hooks. **Always run manually before committing API changes:**
```bash
uv run python contract_test.py      # Verify API matches OpenAPI specification
```

## Architecture

**API Structure:**
- FastAPI application with OpenAPI 3.0 specification (`openapi.yaml`)
- RESTful endpoints for task management (GET, POST, PUT, DELETE)
- Pydantic models for request/response validation and serialization
- Custom exception handlers for consistent error responses

**Data Layer:**
- In-memory database implementation (`src/api/database.py`)
- Global singleton pattern with `TaskDatabase` class
- CRUD operations with proper typing and error handling

**Model Hierarchy:**
- `TaskBase`: Base model with common fields (title, description)
- `TaskCreate`: Input model for creating tasks (inherits from TaskBase)
- `TaskUpdate`: Partial update model with optional fields
- `Task`: Full model with computed fields (id, timestamps, completed status)

**Testing Strategy:**
- Unit tests using pytest with FastAPI TestClient
- Database reset fixture for test isolation
- Contract testing with custom script to verify OpenAPI compliance
- TDD approach with Red-Green-Refactor cycle

**Development Tools Configuration:**
- Ruff: Modern Python linter with strict rules for code quality
- MyPy: Type checking with strict configuration requiring type annotations
- Pytest: Test discovery in `tests/` directory with standard naming conventions
- Lizard: Complexity analysis to maintain code maintainability

## Important Implementation Details

**Database State Management:**
- The in-memory database (`src/api/database.py`) uses a global singleton instance
- Test fixtures reset the database state between tests via `db._tasks.clear()`
- Production deployments should replace this with a persistent database

**Error Handling:**
- Custom exception handlers convert FastAPI exceptions to consistent JSON format
- Validation errors (422) are mapped to 400 status codes with generic messages
- HTTP exceptions maintain their status codes but use standardized error format

**API Contract:**
- Implementation strictly follows the OpenAPI specification
- Contract tests verify response schemas and status codes match specification
- Dredd configuration exists but custom contract testing script is more reliable
