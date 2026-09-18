# Contributing to Celebi

Thank you for your interest in contributing to Celebi! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Linting](#linting)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- Docker (optional, for containerized development)

### Quick Start

```bash
# Fork and clone the repo
git clone https://github.com/YOUR_USERNAME/celebi-harness.git
cd celebi-harness

# Install dependencies
uv sync

# Run linting
make lint

# Run tests
make test

# Launch the GUI
python -m celebi
```

## Development Setup

### Option A: Local Development

```bash
# Install all dependencies including dev tools
uv sync

# Verify installation
make lint
make test
```

### Option B: Docker Development

No local Python installation required — everything runs in Docker.

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Start backend services (LiteLLM + FastAPI)
docker compose -f docker-compose.dev.yml up

# In another terminal — run linting
docker compose -f docker-compose.dev.yml --profile lint run celebi-lint

# In another terminal — run tests
docker compose -f docker-compose.dev.yml --profile test run celebi-test

# Run GUI locally (connects to Docker backend on :8000)
python -m celebi
```

### Option C: Using Make

```bash
make install    # Install dependencies
make lint       # Run linting
make format     # Auto-fix linting issues
make test       # Run tests
make build      # Build standalone binary
make docker-up  # Start Docker backend
```

## Project Structure

```
celebi-harness/
├── celebi/                    # Desktop GUI (PySide6/Qt)
│   ├── __init__.py
│   ├── __main__.py            # Entry point: python -m celebi
│   ├── app.py                 # QApplication bootstrap
│   ├── config.py              # Configuration management
│   ├── agents.py              # Agent config writers
│   ├── model_fetcher.py       # Async model list fetcher
│   ├── workers.py             # QThread background workers
│   └── ui/
│       ├── main_window.py     # Main window
│       ├── setup_wizard.py    # Setup wizard
│       ├── projects_sidebar.py
│       ├── project_dashboard.py
│       ├── graph_view.py      # Graph visualization
│       └── settings_tab.py
│
├── api/                       # Backend proxy server
│   ├── main.py                # Entrypoint
│   ├── Dockerfile             # Production Docker
│   ├── pyproject.toml         # Dependencies
│   └── app/
│       ├── main.py            # FastAPI app
│       ├── config/
│       │   ├── api_config.py  # API config reader
│       │   ├── db.py          # Kuzu graph DB
│       │   └── litellm-config.yaml
│       ├── router/
│       │   └── interceptor.py # Request interceptor
│       ├── service/
│       │   └── proxy_service.py  # Core proxy logic
│       └── tests/             # Test suite
│
├── .github/workflows/         # CI/CD pipelines
├── docker-compose.yml         # Production Docker Compose
├── docker-compose.dev.yml     # Development Docker Compose
├── Dockerfile.dev             # Development Dockerfile
├── Makefile                   # Developer commands
├── ruff.toml                  # Linting config
├── celebi.spec                # PyInstaller spec
├── build.py                   # Build script
└── README.md
```

## How to Contribute

### Types of Contributions

1. **Bug Fixes** — Fix issues in existing functionality
2. **Features** — Add new capabilities
3. **Documentation** — Improve docs, add examples
4. **Tests** — Add or improve test coverage
5. **Refactoring** — Improve code quality without changing behavior
6. **UI/UX** — Improve the desktop application interface

### Finding Issues

- Check the [Issues](https://github.com/RjyavardhanSingh/celebi-harness/issues) page
- Look for issues labeled `good first issue` for beginners
- Look for issues labeled `help wanted` for experienced contributors

## Development Workflow

### 1. Create a Branch

```bash
# From main
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Follow the [Coding Standards](#coding-standards)
- Write tests for new functionality
- Update documentation if needed

### 3. Test Your Changes

```bash
# Run linting
make lint

# Run tests
make test

# Auto-fix linting issues
make format
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style

- **Formatter/Linter**: Ruff (configured in `ruff.toml`)
- **Line Length**: 100 characters
- **Quotes**: Double quotes
- **Import Sorting**: Ruff isort

### Code Guidelines

```python
# GOOD: Clear function names, type hints
async def fetch_models(provider: str, api_key: str) -> list[str]:
    """Fetch available models from the provider's API."""
    ...


# BAD: Unclear names, no types
async def fetch(p, k): ...
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Functions | snake_case | `fetch_models()` |
| Classes | PascalCase | `ProjectDashboard` |
| Constants | UPPER_SNAKE_CASE | `UPSTREAM_URL` |
| Files | snake_case | `proxy_service.py` |
| UI Methods | camelCase (Qt) | `hoverEnterEvent()` |

### Docstrings

```python
def my_function(param: str) -> int:
    """Short description of what this function does.

    Args:
        param: Description of param

    Returns:
        Description of return value
    """
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
cd api && uv run pytest app/tests/test_proxy_service.py -v

# Run with coverage
cd api && uv run pytest app/tests/ -v --tb=short
```

### Writing Tests

Tests are located in `api/app/tests/`. All async tests use `pytest.mark.anyio`.

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.anyio
@patch("app.service.proxy_service.conn")
async def test_my_feature(mock_conn):
    """Test description."""
    # Arrange
    mock_conn.execute.return_value = None

    # Act
    result = await my_function()

    # Assert
    assert result == expected
```

### Test Conventions

- Use `@pytest.mark.anyio` for async tests
- Mock external dependencies (LLM providers, database)
- Test both success and failure paths
- Keep tests independent — no shared state

## Linting

### Running Linting

```bash
# Check for issues
make lint

# Auto-fix issues
make format
```

### Ruff Rules

| Rule | Description |
|------|-------------|
| E | pycodestyle errors |
| F | Pyflakes |
| W | pycodestyle warnings |
| I | isort |
| N | pep8-naming |
| UP | pyupgrade |
| B | flake8-bugbear |
| A | flake8-builtins |
| SIM | flake8-simplify |

### Ignored Rules

These rules are intentionally ignored in `ruff.toml`:

- `E501` — Line length (handled by formatter)
- `N802` — Qt method names must be camelCase
- `N807` — `__init_db__` is intentional
- `SIM105` — try-except-pass is clearer for simple cases
- `SIM108` — ternary isn't always more readable
- `B904` — not always needed for HTTPException

## Commit Messages

### Format

```
<type>: <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation changes |
| style | Code style changes (formatting, no logic change) |
| refactor | Code refactoring (no feature or fix) |
| test | Adding or updating tests |
| chore | Maintenance tasks |
| ci | CI/CD changes |

### Examples

```
feat: add replay branching for conversation history

fix: resolve litellm config generation on Windows

docs: add setup instructions to README

test: add tests for proxy error handling

refactor: extract shared graph service module
```

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass (`make test`)
- [ ] Linting passes (`make lint`)
- [ ] Documentation is updated (if applicable)
- [ ] Commit messages follow the format

### PR Description

```markdown
## What does this PR do?

Brief description of changes.

## How to test

Steps to verify the changes work correctly.

## Related issues

Fixes #123
```

### Review Process

1. PR will be reviewed by maintainers
2. Address any feedback
3. Once approved, PR will be merged

## Reporting Issues

### Bug Reports

Include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version
- OS (Linux/macOS/Windows)
- Screenshots (if UI issue)

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternatives considered

---

## Questions?

If you have questions about contributing, feel free to:
- Open an issue
- Start a discussion on GitHub

Thank you for contributing to Celebi!
