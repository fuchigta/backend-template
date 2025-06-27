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

## Development Workflow

This project follows a strict **Schema-First + TDD** approach for all API development.

### API Development Process

**1. Schema First Design:**
```bash
# ALWAYS start by updating the OpenAPI specification
vim openapi.yaml                    # Define/modify API endpoints, models, responses
```

**2. TDD Implementation (t-wada approach):**
```bash
# Red: Write failing tests first
vim tests/test_api.py               # Add tests for new functionality
uv run pytest                      # Confirm tests fail (Red phase)

# Green: Implement minimal code to pass tests
vim src/api/models.py               # Update Pydantic models if needed
vim src/api/main.py                 # Implement API endpoints
uv run pytest                      # Confirm tests pass (Green phase)

# Refactor: Improve code quality while keeping tests green
uv run ruff check --fix .           # Fix code style issues
uv run mypy src/                    # Ensure type safety
uv run lizard src/ --CCN 8 --length 50 --arguments 5  # Check complexity thresholds
uv run pytest                      # Confirm tests still pass
```

**3. Contract Verification:**
```bash
uv run python contract_test.py      # Verify implementation matches OpenAPI spec
```

**4. Quality Assurance:**
```bash
uv run pre-commit run --all-files   # Run all quality checks
```

### ⚠️ Critical Rules

1. **Never implement before updating OpenAPI schema** - The specification is the source of truth
2. **Always follow Red-Green-Refactor cycle** - Write failing tests first, then implement
3. **Verify contract compliance** - API must match OpenAPI specification exactly
4. **All commits must pass quality gates** - Pre-commit hooks enforce code standards

### TDD Principles (t-wada approach)

- **Red Phase**: Write the simplest test that fails
- **Green Phase**: Write the minimal code to make the test pass
- **Refactor Phase**: Improve code structure without changing behavior
- **Repeat**: Small iterations with frequent feedback

### Code Complexity Management

**Lizard Static Analysis Thresholds:**
- **Cyclomatic Complexity (CCN)**: ≤ 8 - Functions exceeding this must be refactored
- **Function Length**: ≤ 50 lines - Long functions should be split into smaller ones
- **Parameter Count**: ≤ 5 parameters - Too many parameters indicate design issues

**When Complexity Thresholds Are Exceeded:**
```bash
uv run lizard src/ --CCN 8 --length 50 --arguments 5  # Identify violations
# Refactor the flagged functions by:
# 1. Extract smaller functions from complex ones
# 2. Use parameter objects instead of many parameters
# 3. Simplify conditional logic with early returns
# 4. Consider design patterns (Strategy, Command, etc.)
uv run pytest                                         # Ensure refactoring doesn't break functionality
```

**Refactoring Guidelines:**
- **High CCN**: Extract methods, reduce nesting, use guard clauses
- **Long functions**: Split into logical sub-functions with clear responsibilities
- **Many parameters**: Create data classes or use dependency injection

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
