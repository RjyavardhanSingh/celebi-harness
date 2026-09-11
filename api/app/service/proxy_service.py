import httpx
import json
import logging
import uuid

from typing import AsyncGenerator

from app.config.db import conn

UPSTREAM_URL = "http://localhost:4000/v1/chat/completions" 
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

    #Clean the headers so we don't send conflicting host length
    forward_headers = {
        "Authorization": headers.get("authorization", "") or headers.get("Authorization",""),
        "Content-Type": "application/json"
    }

    try:
        prompt_id = str(uuid.uuid4())
        conn.execute(
            "CREATE (s:State {id: $id, step_type: 'prompt', payload: $payload})",
            {"id": prompt_id, "payload": json.dumps(payload)}
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
                {"parent_id": parent_id, "prompt_id": prompt_id}
                )
    except RuntimeError as e:
            logger.error(f"Failed to create parent state: {e}")
    
    try:

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                UPSTREAM_URL,
                json=payload,
                headers=forward_headers
            ) as upstream_response:
                
                if upstream_response.status_code != 200:
                    error_body = await upstream_response.aread()
                    error_msg = f"data: {{\"error\": \"Upstream Gemini Error {upstream_response.status_code}: {error_body.decode('utf-8')}\"}}\n\n"
                    yield error_msg.encode('utf-8')
                    return

                try:
                    accumalated_response = ""

                    #For sendind data byte by byte aiter)bytes is used
                    async for raw_chunk in upstream_response.aiter_bytes():
                        if raw_chunk:
                            accumalated_response += raw_chunk.decode('utf-8', errors='ignore')
                            yield raw_chunk


                    conn.execute(
                        "CREATE (s:State {id: $id, step_type: 'response', payload: $payload})",
                        {"id": response_id, "payload": accumalated_response}
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
                        {"prompt_id": prompt_id, "response_id": response_id}
                    )
                except RuntimeError as e:
                    logger.error(f"Failed to create transition edge: {e}")
    except httpx.ConnectError as e:
         yield f'data: {{"error": "Upstream connection failed: {e}"}}\n\n'.encode('utf-8')
    except httpx.TimeoutException as e:
         yield b'data: {"error": "Upstream timeout"}\n\n'
    