<p align="center">
  <img src="assets/logo.png" alt="Celebi Logo" width="200"/>
</p>

<h1 align="center">Celebi</h1>

<p align="center">
  <strong>Time-Travel Harness for LLM API Streams</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue" alt="version">
  <img src="https://img.shields.io/badge/python-3.11+-green" alt="python">
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="license">
  <img src="https://img.shields.io/badge/status-alpha-orange" alt="status">
</p>

---

## What is Celebi?

Celebi is a **man-in-the-middle proxy** that sits between your coding agent and LLM providers. It captures every request/response pair in a graph database, forming a **timeline of conversations** that you can visualize, search, and replay.

Named after the time-traveling Pokemon — because debugging LLMs should feel like time travel.

## Scope

Celebi is designed to provide **full observability** into LLM interactions during software development. It operates as an invisible proxy layer — your coding agent doesn't know it's there, but every token is logged and available for inspection.

### Core Capabilities

- **Request/Response Capture**: Every API call between your agent and the LLM is intercepted and stored
- **Graph-based Timeline**: Conversations are stored as a directed graph (prompt -> response nodes with transition edges)
- **Visual Inspection**: Card-based graph visualization showing the full conversation flow
- **Replay & Branching**: Re-send any prompt to get a fresh response and compare outputs
- **Full-text Search**: Search across all stored conversations by content
- **Token Analytics**: Track prompt vs completion token usage per request

### What Celebi Is NOT

- Celebi is **not** a debugger or step-through tool
- Celebi is **not** an LLM provider — it proxies to your existing provider
- Celebi is **not** a replacement for your coding agent — it augments it with observability
- Celebi does **not** automatically detect hallucinations — it gives you the tools to find them manually

## Use Cases

### 1. Catching Hallucinations

When your coding agent produces unexpected output, Celebi lets you:
- Inspect the exact prompt that was sent to the LLM
- See the full response that came back
- Replay the same prompt to check if the hallucination is consistent
- Branch from any point to test alternative phrasings

### 2. Debugging Agent Behavior

When your agent makes a wrong decision:
- Trace back through the conversation timeline to find where it went wrong
- Search for similar past conversations that worked correctly
- Compare token usage patterns across requests

### 3. Cost Optimization

- Track token usage per request to identify expensive interactions
- Compare different models' token efficiency for the same tasks
- Identify prompts that consistently produce long (expensive) responses

### 4. Conversation History & Audit

- Maintain a complete audit trail of all LLM interactions
- Search across projects and sessions
- Export conversation data for analysis

### 5. Agent Development & Testing

- Test how different prompt phrasings affect LLM responses
- Build a library of effective prompts by replaying and comparing
- Validate that agent config changes don't break existing workflows

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Coding Agent                              │
│          (OpenCode / Claude Code / Codex / Kiro)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ POST /v1/chat/completions
                            │ (OpenAI-compatible API)
                            v
┌─────────────────────────────────────────────────────────────┐
│                   Celebi Proxy (:8000)                       │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Interceptor  │───▶│  Graph DB    │───▶│   Proxy      │  │
│  │  (FastAPI)    │    │  (Kuzu)      │    │   Service    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                                        │          │
│         │            ┌──────────────┐            │          │
│         │            │  Replay      │            │          │
│         └───────────▶│  Endpoint    │◀───────────┘          │
│                      └──────────────┘                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP (streaming)
                            v
┌─────────────────────────────────────────────────────────────┐
│                     LiteLLM (:4000)                          │
│              (Unified LLM API Gateway)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────────┐
│                   LLM Provider                               │
│        (Gemini / OpenAI / Anthropic / others)               │
└─────────────────────────────────────────────────────────────┘
```

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Desktop GUI** | PySide6 (Qt6) | Setup wizard, graph visualization, search, analytics |
| **Proxy Server** | FastAPI + Uvicorn | Intercepts and forwards LLM API requests |
| **LLM Gateway** | LiteLLM | Unified interface to multiple LLM providers |
| **Graph Database** | Kuzu | Stores conversation timeline as a directed graph |
| **HTTP Client** | httpx | Async streaming proxy between Celebi and LLM |

### Graph Schema

```
State (node)
├── id: UUID
├── step_type: "prompt" | "response"
└── payload: JSON string

Edges
├── TRANSITIONED_TO: prompt -> response (linear flow)
└── BRANCHED_TO: parent_prompt -> new_prompt (replay/branch)
```

## Download

| Platform | Installer |
|----------|-----------|
| macOS (Apple Silicon / Intel) | [celebi-macos.dmg](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest) |
| Linux (Debian / Ubuntu) | [celebi-linux-amd64.deb](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest) |
| Windows (x64) | [celebi-windows-setup.exe](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest) |

**[Full installation guides](https://rjyavardhansingh.github.io/celebi-harness/install/)** | **[Documentation](https://rjyavardhansingh.github.io/celebi-harness/)**

## Quick Start

### 1. Download and Launch

```bash
# Linux / macOS
./celebi

# Windows
celebi.exe
```

### 2. Setup Wizard

**Page 1 — Select Project:**
- Enter a project name
- Browse to your project folder
- Select your coding agent (OpenCode / Claude Code / Codex / Kiro)

**Page 2 — Provider Credentials:**
- Select provider (Gemini / OpenAI / Anthropic)
- Enter your API key
- Click **Fetch Models** — select a model from the dropdown

### 3. Start and Use

- Click **Start** on the dashboard
- Open your coding agent in the project folder
- Use the **Graph**, **Search**, and **Analytics** tabs to inspect interactions

### 4. Post-Install Verification

```bash
# Verify proxy is running
curl http://localhost:8000/
# Expected: {"message":"Hello Traveller"}

# Check graph endpoint
curl http://localhost:8000/graph
# Expected: {"nodes":0,"edges":0,"data":[]}
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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributing guide.

## License

MIT License

Copyright (c) 2026 Rajyavardhan Singh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
