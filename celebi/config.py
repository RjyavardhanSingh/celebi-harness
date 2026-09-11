"""Configuration management for Celebi.

Two-level config:
  ~/.celebi/global.json   — credentials, provider settings (set once)
  ~/.celebi/projects.json — registry of all projects
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional

CONFIG_DIR = Path.home() / ".celebi"
GLOBAL_FILE = CONFIG_DIR / "global.json"
PROJECTS_FILE = CONFIG_DIR / "projects.json"

# Provider prefixes for litellm model name derivation
PROVIDER_PREFIXES = {
    "gemini": "gemini/",
    "anthropic": "anthropic/",
    "openai": "",
    "deepseek": "deepseek/",
    "groq": "groq/",
    "mistral": "mistral/",
    "cohere": "cohere/",
    "bedrock": "bedrock/",
}


@dataclass
class GlobalConfig:
    """User fills once — credentials and provider settings."""
    provider: str = ""
    api_key: str = ""
    model: str = ""

    def litellm_model_name(self) -> str:
        """Derive litellm model name from provider + model.

        Examples:
            provider="gemini", model="gemini-3.5-flash-lite"
                -> "gemini/gemini-3.5-flash-lite"
            provider="openai", model="gpt-4o"
                -> "gpt-4o"
            provider="gemini", model="gemini/gemini-3.5-flash-lite"
                -> "gemini/gemini-3.5-flash-lite"  (already has prefix)
        """
        prefix = PROVIDER_PREFIXES.get(self.provider, "")
        if prefix and not self.model.startswith(prefix):
            return f"{prefix}{self.model}"
        return self.model

    @property
    def env_key(self) -> str:
        """Derive the env var name for this provider."""
        return f"{self.provider.upper()}_KEY"

    def litellm_env(self) -> dict:
        env = os.environ.copy()
        if self.api_key:
            env[self.env_key] = self.api_key
        return env


@dataclass
class ProjectConfig:
    """One per project — agent type, ports, project path."""
    name: str = ""
    path: str = ""
    agent: str = "opencode"
    proxy_port: int = 8000
    litellm_port: int = 4000

    @property
    def proxy_url(self) -> str:
        return f"http://localhost:{self.proxy_port}"

    @property
    def upstream_url(self) -> str:
        return f"http://127.0.0.1:{self.litellm_port}/v1/chat/completions"


# --- Load / Save ---

def load_global() -> GlobalConfig:
    if GLOBAL_FILE.exists():
        try:
            with open(GLOBAL_FILE) as f:
                data = json.load(f)
            return GlobalConfig(**{
                k: v for k, v in data.items()
                if k in GlobalConfig.__dataclass_fields__
            })
        except (json.JSONDecodeError, TypeError):
            pass
    return GlobalConfig()


def save_global(config: GlobalConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(GLOBAL_FILE, "w") as f:
        json.dump(asdict(config), f, indent=2)


def load_projects() -> List[ProjectConfig]:
    if PROJECTS_FILE.exists():
        try:
            with open(PROJECTS_FILE) as f:
                data = json.load(f)
            return [ProjectConfig(**p) for p in data]
        except (json.JSONDecodeError, TypeError):
            pass
    return []


def save_projects(projects: List[ProjectConfig]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROJECTS_FILE, "w") as f:
        json.dump([asdict(p) for p in projects], f, indent=2)


def next_port(projects: List[ProjectConfig]) -> tuple:
    used_proxy = {p.proxy_port for p in projects}
    used_litellm = {p.litellm_port for p in projects}
    proxy_port = 8000
    while proxy_port in used_proxy:
        proxy_port += 1
    litellm_port = 4000
    while litellm_port in used_litellm:
        litellm_port += 1
    return proxy_port, litellm_port


def add_project(name: str, path: str, agent: str) -> ProjectConfig:
    projects = load_projects()
    proxy_port, litellm_port = next_port(projects)
    project = ProjectConfig(
        name=name, path=path, agent=agent,
        proxy_port=proxy_port, litellm_port=litellm_port,
    )
    projects.append(project)
    save_projects(projects)
    return project


def remove_project(name: str) -> None:
    projects = load_projects()
    projects = [p for p in projects if p.name != name]
    save_projects(projects)


def get_project(name: str) -> Optional[ProjectConfig]:
    for p in load_projects():
        if p.name == name:
            return p
    return None


def update_project(config: ProjectConfig) -> None:
    projects = load_projects()
    for i, p in enumerate(projects):
        if p.name == config.name:
            projects[i] = config
            break
    save_projects(projects)
