from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from app.service.proxy_servce import stream_upstream_request

router = APIRouter()

@router.post("v1/chat/completions")
async def intercept_chat_completions(
    request: Request
):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=404,detail="Invalid JSON body")
    
    headers = dict(request.headers)

    byte_stream = stream_upstream_request(payload, headers)

    return StreamingResponse(
        byte_stream,
        media_type="text/event-stream"
    )