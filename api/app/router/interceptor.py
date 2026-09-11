import uuid
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
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
        byte_stream,
        media_type="text/event-stream",
        headers={"X-Celebi-Response-id": response_id}
    )

@router.post("/v1/chat/completions")
async def intercept_chat_completions_v1(request: Request):
    return await _handle_chat_completions(request)

@router.post("/chat/completions")
async def intercept_chat_completions(request: Request):
    return await _handle_chat_completions(request)
