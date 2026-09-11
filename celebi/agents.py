"""Agent config writers.

Each agent (OpenCode, Claude Code, Codex, Kiro) has its own config format.
Celebi generates the correct config file so the agent routes through the proxy.
"""

import json
from pathlib import Path
from typing import Callable


def write_opencode_config(project_path: str, proxy_port: int, model: str) -> Path:
    """Write opencode.json for OpenCode."""
    config = {
        "$schema": "https://opencode.ai/config.json",
        "provider": {
            "celebi": {
                "npm": "@ai-sdk/openai-compatible",
                "name": "Celebi Proxy",
                "options": {
                    "baseURL": f"http://localhost:{proxy_port}"
                },
                "models": {
                    model: {
                        "name": f"{model} (via Celebi)"
                    }
                }
            }
        }
    }
    path = Path(project_path) / "opencode.json"
    path.write_text(json.dumps(config, indent=2))
    return path


def write_claude_config(project_path: str, proxy_port: int, model: str) -> Path:
    """Write .claude/settings.json for Claude Code."""
    config_dir = Path(project_path) / ".claude"
    config_dir.mkdir(exist_ok=True)

    config = {
        "env": {
            "ANTHROPIC_BASE_URL": f"http://localhost:{proxy_port}/v1",
            "ANTHROPIC_MODEL": model,
        }
    }
    path = config_dir / "settings.json"
    path.write_text(json.dumps(config, indent=2))
    return path


def write_codex_config(project_path: str, proxy_port: int, model: str) -> Path:
    """Write .codex/config.json for OpenAI Codex."""
    config_dir = Path(project_path) / ".codex"
    config_dir.mkdir(exist_ok=True)

    config = {
        "model": model,
        "api_base": f"http://localhost:{proxy_port}/v1",
    }
    path = config_dir / "config.json"
    path.write_text(json.dumps(config, indent=2))
    return path


def write_kiro_config(project_path: str, proxy_port: int, model: str) -> Path:
    """Write .kiro/config.json for Kiro."""
    config_dir = Path(project_path) / ".kiro"
    config_dir.mkdir(exist_ok=True)

    config = {
        "provider": {
            "endpoint": f"http://localhost:{proxy_port}",
            "model": model,
        }
    }
    path = config_dir / "config.json"
    path.write_text(json.dumps(config, indent=2))
    return path


# Registry of agent config writers
AGENTS: dict[str, dict] = {
    "opencode": {
        "name": "OpenCode",
        "write_config": write_opencode_config,
        "config_file": "opencode.json",
    },
    "claude-code": {
        "name": "Claude Code",
        "write_config": write_claude_config,
        "config_file": ".claude/settings.json",
    },
    "codex": {
        "name": "Codex",
        "write_config": write_codex_config,
        "config_file": ".codex/config.json",
    },
    "kiro": {
        "name": "Kiro",
        "write_config": write_kiro_config,
        "config_file": ".kiro/config.json",
    },
}


def get_agent_names() -> list[str]:
    return list(AGENTS.keys())


def get_agent_display_name(agent_key: str) -> str:
    return AGENTS.get(agent_key, {}).get("name", agent_key)


def generate_agent_config(agent_key: str, project_path: str, proxy_port: int, model: str) -> Path:
    """Generate the agent-specific config file in the project folder."""
    agent = AGENTS.get(agent_key)
    if not agent:
        raise ValueError(f"Unknown agent: {agent_key}")
    return agent["write_config"](project_path, proxy_port, model)
