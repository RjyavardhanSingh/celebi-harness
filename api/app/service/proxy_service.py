import json
import logging
import uuid
from collections.abc import AsyncGenerator

import httpx

from app.config.api_config import api_config
from app.config.db import conn

UPSTREAM_URL = api_config.upstream_url
logger = logging.getLogger(__name__)


async def stream_upstream_request(
    payload: dict,
    headers: dict,
    response_id: str,
) -> AsyncGenerator[bytes, None]:
    """
    Opens raw streaming pipeline to the upstream LLM provider
    as yields chunk as raw  bytes the microsecond they arrive
    """

    # Clean the headers so we don't send conflicting host length
    forward_headers = {
        "Authorization": headers.get("authorization", "") or headers.get("Authorization", ""),
        "Content-Type": "application/json",
    }

    # Deprecated: Graph DB operations duplicated in api/app/router/interceptor.py.
    # Consider extracting a shared graph_service module.
    prompt_id = str(uuid.uuid4())
    try:
        conn.execute(
            "CREATE (s:State {id: $id, step_type: 'prompt', payload: $payload})",
            {"id": prompt_id, "payload": json.dumps(payload)},
        )
    except RuntimeError as e:
        logger.error(f"Failed to load prompt state: {e}")

    parent_id = headers.get("x-celebi-parent-id") or headers.get("X-Celebi-Parent-Id")

    try:
        if parent_id:
            conn.execute(
                """
                MATCH (parent:State), (prompt:State)
                WHERE parent.id = $parent_id AND prompt.id = $prompt_id
                CREATE (parent)-[:BRANCHED_TO]->(prompt)
                """,
                {"parent_id": parent_id, "prompt_id": prompt_id},
            )
    except RuntimeError as e:
        logger.error(f"Failed to create parent state: {e}")

    try:
        async with (
            httpx.AsyncClient(timeout=60.0) as client,
            client.stream(
                "POST", UPSTREAM_URL, json=payload, headers=forward_headers
            ) as upstream_response,
        ):
            if upstream_response.status_code != 200:
                error_body = await upstream_response.aread()
                error_text = error_body.decode("utf-8", errors="replace")
                error_payload = json.dumps(
                    {
                        "error": {
                            "message": f"Upstream Error {upstream_response.status_code}: {error_text}",
                            "type": "upstream_error",
                            "code": upstream_response.status_code,
                        }
                    }
                )
                yield f"data: {error_payload}\n\n".encode()
                return

            try:
                accumulated_response = ""

                # Stream response byte by byte using aiter_bytes()
                async for raw_chunk in upstream_response.aiter_bytes():
                    if raw_chunk:
                        accumulated_response += raw_chunk.decode("utf-8", errors="ignore")
                        yield raw_chunk

                conn.execute(
                    "CREATE (s:State {id: $id, step_type: 'response', payload: $payload})",
                    {"id": response_id, "payload": accumulated_response},
                )
            except RuntimeError as e:
                logger.error(f"Failed to create response state: {e}")

            try:
                conn.execute(
                    """
                        MATCH (p:State), (r:State)
                        WHERE p.id = $prompt_id AND r.id = $response_id
                        CREATE (p)-[:TRANSITIONED_TO]->(r)
                        """,
                    {"prompt_id": prompt_id, "response_id": response_id},
                )
            except RuntimeError as e:
                logger.error(f"Failed to create transition edge: {e}")
    except httpx.ConnectError as e:
        error_payload = json.dumps(
            {
                "error": {
                    "message": f"Upstream connection failed: {e}",
                    "type": "connection_error",
                    "code": 502,
                }
            }
        )
        yield f"data: {error_payload}\n\n".encode()
    except httpx.TimeoutException:
        error_payload = json.dumps(
            {"error": {"message": "Upstream timeout", "type": "timeout_error", "code": 504}}
        )
        yield f"data: {error_payload}\n\n".encode()
