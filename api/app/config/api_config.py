"""API-side config reader.

Reads env vars set by the process manager, or falls back to ~/.celebi/global.json.
No hardcoded models — everything comes from the user's config.
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass

CONFIG_DIR = Path.home() / ".celebi"
GLOBAL_FILE = CONFIG_DIR / "global.json"

PROVIDER_PREFIXES = {
    "gemini": "gemini/",
    "anthropic": "anthropic/",
    "openai": "",
    "deepseek": "deepseek/",
    "groq": "groq/",
    "mistral": "mistral/",
}


@dataclass
class APIConfig:
    upstream_port: int = 4000
    proxy_port: int = 8000
    provider: str = ""
    model: str = ""
    api_key: str = ""

    @property
    def upstream_url(self) -> str:
        return f"http://127.0.0.1:{self.upstream_port}/v1/chat/completions"

    def litellm_model_name(self) -> str:
        prefix = PROVIDER_PREFIXES.get(self.provider, "")
        if prefix and not self.model.startswith(prefix):
            return f"{prefix}{self.model}"
        return self.model

    @property
    def env_key(self) -> str:
        return f"{self.provider.upper()}_KEY"


def load_api_config() -> APIConfig:
    upstream_port = os.environ.get("CELEBI_UPSTREAM_PORT")
    proxy_port = os.environ.get("CELEBI_PROXY_PORT")

    if upstream_port and proxy_port:
        return APIConfig(
            upstream_port=int(upstream_port),
            proxy_port=int(proxy_port),
        )

    if GLOBAL_FILE.exists():
        try:
            with open(GLOBAL_FILE) as f:
                data = json.load(f)
            return APIConfig(
                provider=data.get("provider", ""),
                model=data.get("model", ""),
                api_key=data.get("api_key", ""),
            )
        except (json.JSONDecodeError, KeyError):
            pass

    return APIConfig()


api_config = load_api_config()
