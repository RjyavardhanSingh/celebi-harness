# Contributing

Thank you for your interest in contributing to Celebi!

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Quick Start

```bash
# Fork and clone the repo
git clone https://github.com/YOUR_USERNAME/celebi-harness.git
cd celebi-harness

# Install dependencies
uv sync

# Run linting
uv run ruff check celebi/

# Run the GUI
python -m celebi
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow the [Coding Standards](#coding-standards)
- Write tests for new functionality
- Update documentation if needed

### 3. Test Your Changes

```bash
# Linting
uv run ruff check celebi/
uv run ruff format --check celebi/

# Auto-fix
uv run ruff check --fix celebi/
uv run ruff format celebi/
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/your-feature-name
```

### 5. Create a Pull Request

## Coding Standards

### Python Style

- **Formatter/Linter**: Ruff
- **Line Length**: 100 characters
- **Quotes**: Double quotes
- **Import Sorting**: Ruff isort

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Functions | snake_case | `fetch_models()` |
| Classes | PascalCase | `ProjectDashboard` |
| Constants | UPPER_SNAKE_CASE | `UPSTREAM_URL` |
| Files | snake_case | `proxy_service.py` |
| UI Methods | camelCase (Qt) | `hoverEnterEvent()` |

### Commit Messages

```
<type>: <description>

feat: add replay branching for conversation history
fix: resolve litellm config generation on Windows
docs: add setup instructions to README
```

## Building Installers

To build platform installers locally:

```bash
# Linux .deb
./packaging/linux/build-deb.sh

# macOS .dmg (requires macOS)
./packaging/macos/build-dmg.sh

# Windows .exe (requires NSIS)
.\packaging\windows\build-exe.ps1
```

## Questions?

- Open an issue on [GitHub](https://github.com/RjyavardhanSingh/celebi-harness/issues)
- Start a discussion on [GitHub Discussions](https://github.com/RjyavardhanSingh/celebi-harness/discussions)
