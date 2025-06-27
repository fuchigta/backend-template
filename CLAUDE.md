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
uv run ruff check . && uv run mypy src/ && uv run pytest && uv run lizard src/ && uv run python schema_test.py && uv run detect-secrets scan --baseline .secrets.baseline .
```

**Pre-commit Hooks:**
```bash
uv run pre-commit install           # Install pre-commit hooks (one-time setup)
uv run pre-commit run --all-files   # Run all hooks manually
git commit -m "message"             # Hooks run automatically on commit
```

**✅ Automated Contract Testing**
Schema-driven contract testing is integrated into pre-commit hooks and runs automatically on every commit.

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
uv run python schema_test.py        # Schema-driven testing with schemathesis
```

**4. Quality Assurance:**
```bash
uv run pre-commit run --all-files   # Run all quality checks
```

### 🚨 CRITICAL RULES - NEVER VIOLATE THESE

**⚠️ SCHEMA-FIRST ENFORCEMENT:**
1. **NEVER implement API changes before updating OpenAPI schema** - The specification is the source of truth. Any deviation invalidates contract testing
2. **NEVER deploy if schema tests fail** - `uv run python schema_test.py` must pass 100% before any commit

**⚠️ TDD ENFORCEMENT:**
3. **NEVER write production code without failing tests** - Always follow Red-Green-Refactor cycle strictly
4. **NEVER commit without running full test suite** - All tests (unit + integration + schema) must pass

**⚠️ QUALITY GATE ENFORCEMENT:**
5. **NEVER bypass pre-commit hooks** - Use `git commit --no-verify` is FORBIDDEN
6. **NEVER ignore linting/type errors** - All Ruff, MyPy, and Lizard checks must pass
7. **NEVER commit if complexity thresholds exceeded** - CCN ≤ 8, Length ≤ 50, Parameters ≤ 5

**⚠️ TOOL INTEGRITY ENFORCEMENT:**
8. **NEVER create custom implementations of existing tools** - Always invest time to properly configure established libraries
9. **NEVER disable checks to "make it work"** - Fix root causes, never mask symptoms

**⚠️ DECISION TRANSPARENCY ENFORCEMENT:**
10. **NEVER make assumptions on ambiguous requirements** - Always present options and ask for explicit guidance
11. **NEVER implement multiple approaches without justification** - Document all design decisions with rationale

### 🛡️ MANDATORY PRE-COMMIT VERIFICATION

**STOP!** Before every commit, verify ALL of these pass:

```bash
# 1. Schema compliance check
uv run python schema_test.py                    # MUST show "No issues found"

# 2. Test suite compliance
uv run pytest                                   # MUST show "100% passed"

# 3. Code quality compliance
uv run ruff check . && uv run mypy src/         # MUST show "All checks passed"

# 4. Complexity compliance
uv run lizard src/ --CCN 8 --length 50 --arguments 5  # MUST show no violations

# 5. Secret detection compliance
uv run detect-secrets scan --baseline .secrets.baseline .  # MUST show no new secrets

# 6. Pre-commit hook compliance
uv run pre-commit run --all-files               # MUST show all hooks "Passed"
```

**❌ COMMIT BLOCKERS:**
- Any schema test failure → Implementation violates contract
- Any unit test failure → Code logic is broken
- Any linting/type error → Code quality standards violated
- Any complexity violation → Code maintainability at risk
- Any secret detection → Sensitive information exposure risk
- Any pre-commit failure → Development standards not met

**If ANY check fails: DO NOT COMMIT. Fix the root cause first.**

### 🚨 EMERGENCY PROCEDURES

**When Quality Gates Fail:**

1. **NEVER use `git commit --no-verify`** - This bypasses all safety mechanisms
2. **NEVER temporarily disable checks** - Fix the underlying issue instead
3. **NEVER commit with TODO comments** - All code must be production-ready
4. **NEVER merge without green CI** - All automated checks must pass

**Escalation Path:**
- First attempt: Fix the failing check by addressing root cause
- Second attempt: Research proper solution in documentation/community
- Final resort: Ask for explicit guidance with detailed problem description

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

## Development Best Practices

### Library and Tool Integration Philosophy

**⚠️ Avoid Custom Implementations**
When encountering issues with established libraries or tools, **never resort to custom implementations** as the first solution. This approach leads to:
- Increased maintenance burden
- Loss of community support and updates
- Reinvention of solved problems
- Technical debt accumulation

**✅ Proper Approach for Tool Integration Issues:**

1. **Investigate thoroughly** - Read documentation, check version compatibility, examine error messages carefully
2. **Seek community solutions** - Search issues, Stack Overflow, and community forums
3. **Try different approaches** - Configuration changes, alternative parameters, different usage patterns
4. **Consult official examples** - Review official documentation and sample projects
5. **Only then consider alternatives** - Look for other established tools that solve the same problem

**Example: Schema Testing Tool Selection**
- **Problem**: Initial dredd configuration had issues with OpenAPI schema parsing
- **Wrong approach**: Immediately build custom contract testing with hardcoded scenarios
- **Correct approach**: Investigate schemathesis as an alternative, learn its CLI options, configure properly
- **Result**: Robust, maintainable schema-driven testing with community support

**Benefits of Using Established Tools:**
- **Continuous improvement** - Tools evolve with community contributions
- **Bug fixes and security updates** - Maintained by dedicated teams
- **Documentation and examples** - Extensive resources for troubleshooting
- **Integration ecosystem** - Works well with other standard tools
- **Reduced maintenance** - Focus on business logic instead of infrastructure

**Decision Framework:**
```
Tool not working? → Investigate configuration → Try alternatives → Research community solutions → Document learnings
                                                                                            ↓
                                                                                    Only build custom if:
                                                                                    - No existing solution exists
                                                                                    - Requirements are truly unique
                                                                                    - Team has capacity for long-term maintenance
```

### Design Decision Making

**⚠️ Always Seek Clarification for Ambiguous Requirements**

When encountering design decisions that could be implemented in multiple valid ways, **never make assumptions**. Instead:

**✅ MANDATORY Approach for Ambiguous Requirements:**
1. **STOP implementation immediately** - Do not proceed with any coding
2. **Identify the ambiguity precisely** - Clearly articulate what aspects are unclear
3. **Research existing patterns** - Check codebase, documentation, and industry standards
4. **Present structured options** - List ALL valid approaches with trade-offs in this format:
   ```
   **Option A**: [Approach]
   - Pros: [List benefits]
   - Cons: [List drawbacks]
   - Impact: [Performance/maintenance/compatibility implications]

   **Option B**: [Alternative approach]
   - Pros: [List benefits]
   - Cons: [List drawbacks]
   - Impact: [Performance/maintenance/compatibility implications]
   ```
5. **Ask for explicit guidance** - Request specific direction with clear question
6. **Wait for confirmation** - Do not assume or proceed until explicit approval
7. **Document the decision** - Record chosen approach, rationale, and alternatives considered

**Example: Field Validation Requirements**
When schema validation reveals inconsistencies, present clear options:

- **Option A**: Allow null/empty values (more permissive)
- **Option B**: Reject empty strings but allow null (moderate)
- **Option C**: Require non-empty values (most restrictive)

**Questions to Ask:**
- What level of data validation strictness is desired?
- Should the API be backward-compatible with existing clients?
- Are there business rules that dictate field requirements?
- What is the expected user experience for validation errors?

**Benefits of Explicit Clarification:**
- **Avoids rework** - Prevents implementing the wrong approach
- **Ensures alignment** - All stakeholders agree on the direction
- **Creates documentation** - Decisions are recorded for future reference
- **Reduces technical debt** - Proper design from the start

**🚫 FORBIDDEN ASSUMPTIONS:**
- **NEVER assume field requirements** - Always clarify required vs optional with validation rules
- **NEVER assume error response formats** - Always confirm status codes and message structures
- **NEVER assume backwards compatibility needs** - Always clarify migration requirements
- **NEVER assume performance requirements** - Always clarify latency/throughput expectations
- **NEVER assume security requirements** - Always clarify authentication/authorization needs

**⚠️ Common Ambiguous Scenarios Requiring Clarification:**
- Field validation rules (required vs optional, format constraints)
- Error response formats and status codes
- API versioning strategies
- Authentication and authorization requirements
- Performance vs simplicity trade-offs
- Data persistence and backup strategies
- Logging and monitoring requirements
- Rate limiting and throttling policies

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
- detect-secrets: Automated secret detection to prevent sensitive information leaks

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
