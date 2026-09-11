"""Model fetcher — fetch available models from provider APIs.

Flow:
1. User selects provider + enters API key
2. We call the provider's models endpoint
3. Return list of model IDs for the dropdown
"""

import httpx
from typing import Optional


async def fetch_models(provider: str, api_key: str) -> list[str]:
    """Fetch available model IDs from the provider's API.

    Returns a sorted list of model ID strings.
    """
    fetchers = {
        "gemini": _fetch_gemini_models,
        "openai": _fetch_openai_models,
        "anthropic": _fetch_anthropic_models,
    }

    fetcher = fetchers.get(provider)
    if not fetcher:
        return []

    try:
        return await fetcher(api_key)
    except Exception:
        return []


async def _fetch_gemini_models(api_key: str) -> list[str]:
    """Fetch Gemini models from Google AI API."""
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params={"key": api_key})
        resp.raise_for_status()
        data = resp.json()

    models = []
    for m in data.get("models", []):
        name = m.get("name", "")
        if name.startswith("models/"):
            name = name[7:]  # strip "models/" prefix
        if name:
            models.append(name)

    return sorted(models)


async def _fetch_openai_models(api_key: str) -> list[str]:
    """Fetch OpenAI models from the API."""
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    models = [m["id"] for m in data.get("data", []) if m.get("id")]
    return sorted(models)


async def _fetch_anthropic_models(api_key: str) -> list[str]:
    """Anthropic doesn't have a models list endpoint — return known models.

    Anthropic's API doesn't expose a /models endpoint, so we return
    the commonly used Claude models. User can also type a custom model.
    """
    return sorted([
        "claude-3-5-haiku-20241022",
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
    ])
