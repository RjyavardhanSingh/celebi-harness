# Supported Agents

Celebi generates agent-specific configuration files so your coding agent routes through the proxy automatically.

## Supported Agents

| Agent | Config File | Description |
|-------|------------|-------------|
| **OpenCode** | `opencode.json` | AI-native coding agent |
| **Claude Code** | `.claude/settings.json` | Anthropic's CLI coding agent |
| **Codex** | `.codex/config.json` | OpenAI's Codex CLI |
| **Kiro** | `.kiro/config.json` | AWS's AI IDE |

## How It Works

When you select an agent during setup, Celebi writes a configuration file to your project folder that redirects the agent's LLM requests through the Celebi proxy.

### OpenCode

Celebi writes an `opencode.json` in your project root:

```json
{
  "provider": {
    "celebi": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Celebi Proxy",
      "options": { "baseURL": "http://localhost:8000" },
      "models": { "your-model": { "name": "your-model (via Celebi)" } }
    }
  }
}
```

### Claude Code

Celebi writes `.claude/settings.json`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:8000/v1",
    "ANTHROPIC_MODEL": "your-model"
  }
}
```

### Codex

Celebi writes `.codex/config.json`:

```json
{
  "model": "your-model",
  "api_base": "http://localhost:8000/v1"
}
```

### Kiro

Celebi writes `.kiro/config.json`:

```json
{
  "provider": {
    "endpoint": "http://localhost:8000",
    "model": "your-model"
  }
}
```

## Adding a New Agent

To add support for a new agent:

1. Add a writer function in `celebi/agents.py`
2. Register it in the `AGENTS` dictionary
3. The setup wizard will automatically pick it up
