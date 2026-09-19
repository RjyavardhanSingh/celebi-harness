# Architecture

## Overview

Celebi operates as a transparent proxy layer between your coding agent and LLM providers. Your agent doesn't know Celebi is there — every token is logged and available for inspection.

```
┌─────────────────────────────────────────────────────────────┐
│                    Coding Agent                              │
│          (OpenCode / Claude Code / Codex / Kiro)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ POST /v1/chat/completions
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
│         └───────────▶│  Replay      │◀───────────┘          │
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

## Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Desktop GUI** | PySide6 (Qt6) | Setup wizard, graph visualization, search, analytics |
| **Proxy Server** | FastAPI + Uvicorn | Intercepts and forwards LLM API requests |
| **LLM Gateway** | LiteLLM | Unified interface to multiple LLM providers |
| **Graph Database** | Kuzu | Stores conversation timeline as a directed graph |
| **HTTP Client** | httpx | Async streaming proxy between Celebi and LLM |

## Graph Schema

```
State (node)
├── id: UUID
├── step_type: "prompt" | "response"
└── payload: JSON string

Edges
├── TRANSITIONED_TO: prompt -> response (linear flow)
└── BRANCHED_TO: parent_prompt -> new_prompt (replay/branch)
```

## Data Flow

1. **Agent sends request** → Celebi interceptor captures the full request body
2. **Prompt stored** → Creates a `State` node with `step_type="prompt"`
3. **Request forwarded** → Proxied to LiteLLM, then to the LLM provider
4. **Response captured** → Streaming response is assembled and stored
5. **Response stored** → Creates a `State` node with `step_type="response"`
6. **Edge created** → `TRANSITIONED_TO` edge connects prompt to response
7. **Response returned** → Agent receives the response as if Celebi wasn't there
