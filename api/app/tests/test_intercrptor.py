import pytest

@pytest.mark.anyio
async def test_invalid_json_return_400(client):
    response = await client.post(
        "/v1/chat/completions",
        content="not json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400