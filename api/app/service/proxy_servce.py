import httpx
import json
import uuid

from typing import AsyncGenerator

from app.config.db import conn

UPSTREAM_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

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

    prompt_id = str(uuid.uuid4())
    conn.execute(
        "CREATE (s:State {id: $id, step_type: 'prompt', payload: $payload})",
        {"id": prompt_id, "payload": json.dumps(payload)}
    )

    parent_id = headers.get("x-celebi-parent-id")

    if parent_id:
        conn.execute(
            """
            MATCH (parent:State), (prompt:State)
            WHERE parent.id = $parent_id AND prompt.id = $prompt_id
            CREATE (parent)-[:]
            """
        )

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

            accumalated_response = ""

            #For sendind data byte by byte aiter)bytes is used
            async for raw_chunk in upstream_response.aiter_bytes():
                if raw_chunk:
                    accumalated_response += raw_chunk.decode('utf-8', errors='ignore')
                    yield raw_chunk

            
            response_id = str(uuid.uuid4())

            conn.execute(
                "CREATE (s:State {id: $id, step_type: 'response', payload: $payload})",
                {"id": response_id, "payload": accumalated_response}
            )

            conn.execute(
                """
                MATCH (p:State), (r:State) 
                WHERE p.id = $prompt_id AND r.id = $response_id
                CREATE (p)-[:TRANSITIONED_TO]->(r)
                """,
                {"prompt_id": prompt_id, "response_id": response_id}
            )
    