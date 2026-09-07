import httpx
from typing import AsyncGenerator

UPSTREAM_URL = "https://api.openaai.com/v1/chat/completions"

async def stream_upstream_request(
        payload: dict,
        headers: dict
) -> AsyncGenerator[bytes, None]:
    """
    Opens raw streaming pipeline to the upstream LLM provider
    as yields chunk as raw  bytes the microsecond they arrive
    """

    #Clean the headers so we don't send conflicting host length
    forward_headers = {
        "Authorization": headers.get("authorization", ""),
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            UPSTREAM_URL,
            json=payload,
            headers=forward_headers
        ) as upstream_response:
            upstream_response.raise_for_status() #raises the HTTP Error if occured

            


    