"""Model fetcher — fetch available models from provider APIs.

Flow:
1. User selects provider + enters API key
2. We call the provider's models endpoint
3. Return list of model IDs for the dropdown
"""

import httpx


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
        raise ValueError(f"Unknown provider: {provider!r}")

    try:
        models = await fetcher(api_key)
    except httpx.HTTPStatusError as e:
        status = e.response.status_code if e.response is not None else None
        if status in (400, 401, 403):
            raise RuntimeError(
                f"Invalid API key for {provider} (HTTP {status}). "
                "Check the key and try again."
            ) from e
        raise RuntimeError(f"Failed to fetch {provider} models (HTTP {status}).") from e
    except httpx.RequestError as e:
        raise RuntimeError(f"Network error fetching {provider} models: {e}") from e

    if not models:
        raise RuntimeError(
            f"No models returned for {provider}. Check the API key and try again."
        )
    return models


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
        name = name.removeprefix("models/")  # strip "models/" prefix
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
    return sorted(
        [
            "claude-3-5-haiku-20241022",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
        ]
    )
