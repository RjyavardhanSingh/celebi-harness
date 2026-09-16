# Celebi — Time-Travel Harness for LLM API Streams

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue" alt="version">
  <img src="https://img.shields.io/badge/python-3.11+-green" alt="python">
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="license">
</p>

Celebi is a **man-in-the-middle proxy** that sits between your coding agent (OpenCode, Claude Code, Codex, Kiro) and LLM providers (Gemini, OpenAI, Anthropic). Every request/response pair is captured and stored in a graph database, forming a **timeline of conversations** that you can visualize, search, and replay.

Named after the time-traveling Pokemon — because debugging LLMs should feel like time travel.

## Why Celebi?

LLM-powered coding agents make mistakes. Celebi gives you **full visibility** into what your agent actually sent to the LLM and what came back. When something looks wrong:

1. **Inspect** the exact prompt and response in the graph
2. **Replay** any prompt to get a fresh response and compare
3. **Branch** the conversation timeline to test alternatives
4. **Search** across all past interactions to find patterns

## Architecture

```
Coding Agent (OpenCode / Claude Code / Codex / Kiro)
       |
       | POST /v1/chat/completions (OpenAI-compatible)
       v
Celebi FastAPI Proxy (:8000)
       |
       |-- Logs prompt to Kuzu graph DB
       |-- Forwards request to LiteLLM
       |-- Streams response back to agent
       |-- Logs response to Kuzu graph DB
       |-- Creates TRANSITIONED_TO edge
       v
LiteLLM (:4000) --> LLM Provider (Gemini / OpenAI / Anthropic)
```

## Download

Download the latest release for your platform:

| Platform | Download |
|----------|----------|
| Linux (x64) | [celebi-linux-x64.tar.gz](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest) |
| macOS (ARM64) | [celebi-macos-arm64.tar.gz](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest) |
| macOS (x64) | [celebi-macos-x64.tar.gz](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest) |
| Windows (x64) | [celebi-windows-x64.zip](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest) |

## Quick Start — Desktop App

### 1. Download and Launch

Download the binary for your platform, extract it, and run:

```bash
# Linux / macOS
./celebi

# Windows
celebi.exe
```

### 2. Setup Wizard — Select Project

When Celebi opens for the first time, you'll see the setup wizard:

- **Name**: Enter a name for your project
- **Folder**: Browse to and select your project folder
- **Agent**: Select your coding agent from the dropdown:
  - OpenCode
  - Claude Code
  - Codex
  - Kiro

Click **Next**.

### 3. Setup Wizard — Provider Credentials

- **Provider**: Select your LLM provider (Gemini, OpenAI, or Anthropic)
- **API Key**: Enter your API key
- Click **Fetch Models** — the dropdown will populate with available models
- **Model**: Select a model from the dropdown

Click **Finish**.

### 4. Start the Proxy

You'll see the project dashboard:

- Click the green **Start** button — this launches LiteLLM and the FastAPI proxy
- The status indicator turns green when running
- Celebi auto-generates the agent config file in your project folder:
  - OpenCode: `opencode.json` (model listed as `<model> (via Celebi)`)
  - Claude Code: `.claude/settings.json`
  - Codex: `.codex/config.json`
  - Kiro: `.kiro/config.json`

### 5. Use Your Agent

Open your coding agent in the project folder. It will automatically route all LLM requests through Celebi.

### 6. Inspect and Catch Hallucinations

- **Graph tab**: Visual timeline of prompt/response pairs — click any card to inspect the full payload
- **Replay (Branch)**: Click any prompt node to re-send it and create a branch in the timeline
- **Search tab**: Full-text search across all stored conversations
- **Analytics tab**: Token usage per request (prompt vs completion tokens)

### 7. Stop

Click **Stop** or close the app. The graph data persists in `~/.celebi/`.

## Post-Install Verification

After starting the proxy, verify it's running correctly:

```bash
# Health check
curl http://localhost:8000/
# Expected: {"message":"Hello Traveller"}

# Check graph endpoint (empty before first agent request)
curl http://localhost:8000/graph
# Expected: {"nodes":0,"edges":0,"data":[]}

# Test the proxy endpoint directly
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"model":"gemini-3.5-flash-lite","messages":[{"role":"user","content":"hello"}]}'
```

## Supported Agents

| Agent | Config File Generated |
|-------|----------------------|
| OpenCode | `opencode.json` |
| Claude Code | `.claude/settings.json` |
| Codex | `.codex/config.json` |
| Kiro | `.kiro/config.json` |

## Supported Providers

| Provider | Models |
|----------|--------|
| Gemini | All Gemini models (auto-fetched) |
| OpenAI | All OpenAI models (auto-fetched) |
| Anthropic | Claude 3.5 Haiku, Claude 3.5 Sonnet, Claude 3 Opus, Claude Sonnet 4, Claude Opus 4 |

## Configuration

Celebi stores configuration in `~/.celebi/`:

- `global.json` — Provider credentials and model selection
- `projects.json` — Registry of all projects

Agent config files are auto-generated in each project folder when you start the proxy.

## Contributing (Docker Dev Environment)

Contributors can use Docker to avoid installing dependencies locally:

```bash
# Clone the repo
git clone https://github.com/RjyavardhanSingh/celebi-harness.git
cd celebi-harness

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Start the backend (LiteLLM + FastAPI) in Docker
docker compose -f docker-compose.dev.yml up

# In another terminal — run the GUI locally
python -m celebi
```

### Linting and Testing

```bash
# Run linting via Docker
docker compose -f docker-compose.dev.yml --profile lint run celebi-lint

# Run tests via Docker
docker compose -f docker-compose.dev.yml --profile test run celebi-test

# Or run locally with Make
make lint
make test
```

### Local Development

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/):

```bash
# Install dependencies
uv sync

# Run linting
make lint

# Run tests
make test

# Launch the GUI
python -m celebi
```

## Docker / Server Mode

Run Celebi as a headless proxy server (no GUI):

```bash
# Set your API key in .env
cp .env.example .env
# Edit .env

# Start the server
docker compose up --build

# Point any OpenAI-compatible tool at http://localhost:8000
```

## How Celebi Catches Hallucinations

Celebi provides the infrastructure to inspect every LLM interaction:

1. **Full Request/Response Capture** — Every token from the LLM is logged to the graph DB
2. **Graph Visualization** — See the complete conversation timeline as connected cards
3. **Replay** — Re-send any prompt to get a fresh response and compare outputs
4. **Branching** — Create alternative conversation branches from any point
5. **Search** — Find past conversations by content
6. **Analytics** — Track token usage to identify suspicious patterns

## License

MIT
