from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest


class MockStreamResponse:
    def __init__(self, chunks, status_code=200, body=b""):
        self.status_code = status_code
        self._chunks = chunks
        self._body = body

    async def aiter_bytes(self):
        for chunk in self._chunks:
            yield chunk

    async def aread(self):
        return self._body


@pytest.mark.anyio
@patch("app.service.proxy_service.conn")
@patch("app.service.proxy_service.httpx.AsyncClient")
async def test_stream_returns_upstream_chunks(mock_client_cls, mock_conn):
    mock_response = MockStreamResponse(chunks=[b"hello", b"world"])

    mock_stream_ctx = MagicMock()
    mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_client = MagicMock()
    mock_client.stream.return_value = mock_stream_ctx

    mock_client_ctx = MagicMock()
    mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_client_cls.return_value = mock_client_ctx

    from app.service.proxy_service import stream_upstream_request

    chunks = []
    async for chunk in stream_upstream_request(
        payload={"messages": [{"role": "user", "content": "hi"}]},
        headers={"authorization": "Bearer test"},
        response_id="test-id",
    ):
        chunks.append(chunk)

    assert chunks == [b"hello", b"world"]
    # prompt node + response node + TRANSITIONED_TO edge = 3 calls
    assert mock_conn.execute.call_count == 3


@pytest.mark.anyio
@patch("app.service.proxy_service.conn")
@patch("app.service.proxy_service.httpx.AsyncClient")
async def test_branching_creates_branched_to_edge(mock_client_cls, mock_conn):
    mock_response = MockStreamResponse(chunks=[b"data"])

    mock_stream_ctx = MagicMock()
    mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_client = MagicMock()
    mock_client.stream.return_value = mock_stream_ctx

    mock_client_ctx = MagicMock()
    mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_client_cls.return_value = mock_client_ctx

    from app.service.proxy_service import stream_upstream_request

    headers = {"authorization": "Bearer test", "x-celebi-parent-id": "parent-123"}

    chunks = []
    async for chunk in stream_upstream_request(
        payload={"messages": [{"role": "user", "content": "hi"}]},
        headers=headers,
        response_id="resp-456",
    ):
        chunks.append(chunk)

    # Check BRANCHED_TO was called
    calls = [str(c) for c in mock_conn.execute.call_args_list]
    branched_calls = [c for c in calls if "BRANCHED_TO" in c]
    assert len(branched_calls) == 1


@pytest.mark.anyio
@patch("app.service.proxy_service.conn")
@patch("app.service.proxy_service.httpx.AsyncClient")
async def test_gemini_failure(mock_client_cls, mock_conn):
    mock_response = MockStreamResponse(
        chunks=[b"data"], status_code=500, body=b'{"error": internal}'
    )

    mock_stream_ctx = MagicMock()
    mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_client = MagicMock()
    mock_client.stream.return_value = mock_stream_ctx

    mock_client_ctx = MagicMock()
    mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_client_cls.return_value = mock_client_ctx

    from app.service.proxy_service import stream_upstream_request

    chunks = []
    async for chunk in stream_upstream_request(
        payload={"messages": [{"role": "user", "content": "hi"}]},
        headers={"authorization": "Bearer test"},
        response_id="test-id",
    ):
        chunks.append(chunk)

    assert b"error" in b"".join(chunks)
    assert mock_conn.execute.call_count == 1


@pytest.mark.anyio
@patch("app.service.proxy_service.conn")
@patch("app.service.proxy_service.httpx.AsyncClient")
async def test_connection_failure(mock_client_cls, mock_conn):
    mock_client = MagicMock()
    mock_client.stream.side_effect = httpx.ConnectError("connection refused")

    mock_client_ctx = MagicMock()
    mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_client_cls.return_value = mock_client_ctx

    from app.service.proxy_service import stream_upstream_request

    chunks = []
    async for chunk in stream_upstream_request(
        payload={"messages": [{"role": "user", "content": "hi"}]},
        headers={"authorization": "Bearer test"},
        response_id="test-id",
    ):
        chunks.append(chunk)

    assert b"connection failed" in b"".join(chunks)
    assert mock_conn.execute.call_count == 1


@pytest.mark.anyio
@patch("app.service.proxy_service.conn")
@patch("app.service.proxy_service.httpx.AsyncClient")
async def test_time_out_events(mock_client_cls, mock_conn):
    mock_client = MagicMock()
    mock_client.stream.side_effect = httpx.TimeoutException("timed out")

    mock_client_ctx = MagicMock()
    mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_client_cls.return_value = mock_client_ctx

    from app.service.proxy_service import stream_upstream_request

    chunks = []
    async for chunk in stream_upstream_request(
        payload={"messages": [{"role": "user", "content": "hi"}]},
        headers={"authorization": "Bearer test"},
        response_id="test-id",
    ):
        chunks.append(chunk)

    assert b"Upstream timeout" in b"".join(chunks)
    assert mock_conn.execute.call_count == 1
