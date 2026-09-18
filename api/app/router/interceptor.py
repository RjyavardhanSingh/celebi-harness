import uuid

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.service.proxy_service import stream_upstream_request

router = APIRouter()


async def _handle_chat_completions(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    headers = dict(request.headers)
    response_id = str(uuid.uuid4())

    byte_stream = stream_upstream_request(payload, headers, response_id)

    return StreamingResponse(
        byte_stream, media_type="text/event-stream", headers={"X-Celebi-Response-id": response_id}
    )


@router.post("/v1/chat/completions")
async def intercept_chat_completions_v1(request: Request):
    return await _handle_chat_completions(request)


@router.post("/chat/completions")
async def intercept_chat_completions(request: Request):
    return await _handle_chat_completions(request)


@router.post("/v1/replay")
async def intercept_replay(request: Request):
    """Replay endpoint — log prompt+response nodes created by direct litellm calls.

    The Celebi UI calls litellm directly (bypassing the proxy) to avoid
    double-logging when OpenCode is running. Then it POSTs here to log
    the prompt and response nodes to the graph DB.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    from app.config.db import conn

    prompt_id = body.get("prompt_id", str(uuid.uuid4()))
    response_id = body.get("response_id", str(uuid.uuid4()))
    parent_id = body.get("parent_id")
    prompt_payload = body.get("prompt_payload", "{}")
    response_payload = body.get("response_payload", "")

    try:
        conn.execute(
            "CREATE (s:State {id: $id, step_type: 'prompt', payload: $payload})",
            {
                "id": prompt_id,
                "payload": prompt_payload
                if isinstance(prompt_payload, str)
                else __import__("json").dumps(prompt_payload),
            },
        )
    except RuntimeError as e:
        return JSONResponse({"error": f"Failed to create prompt: {e}"}, status_code=500)

    if parent_id:
        try:
            conn.execute(
                """
                MATCH (parent:State), (prompt:State)
                WHERE parent.id = $parent_id AND prompt.id = $prompt_id
                CREATE (parent)-[:BRANCHED_TO]->(prompt)
                """,
                {"parent_id": parent_id, "prompt_id": prompt_id},
            )
        except RuntimeError:
            pass

    try:
        conn.execute(
            "CREATE (s:State {id: $id, step_type: 'response', payload: $payload})",
            {"id": response_id, "payload": response_payload},
        )
    except RuntimeError as e:
        return JSONResponse({"error": f"Failed to create response: {e}"}, status_code=500)

    try:
        conn.execute(
            """
            MATCH (p:State), (r:State)
            WHERE p.id = $prompt_id AND r.id = $response_id
            CREATE (p)-[:TRANSITIONED_TO]->(r)
            """,
            {"prompt_id": prompt_id, "response_id": response_id},
        )
    except RuntimeError:
        pass

    return JSONResponse({"status": "ok", "prompt_id": prompt_id, "response_id": response_id})
