import app.llm as llm_module
from httpx import AsyncClient

from app.llm import MOCK_RESPONSE

AUTH = {"X-API-Key": "test-key"}


async def test_health(client: AsyncClient) -> None:
    r = await client.get("/health", headers=AUTH)
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_health_unauthorized(client: AsyncClient) -> None:
    r = await client.get("/health")
    assert r.status_code == 401


async def test_chat_ok(client: AsyncClient) -> None:
    r = await client.post("/chat", json={"user_prompt": "hello"}, headers=AUTH)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["model_response"] == MOCK_RESPONSE


async def test_chat_no_key(client: AsyncClient) -> None:
    r = await client.post("/chat", json={"user_prompt": "hello"})
    assert r.status_code == 401
    assert r.json() == {"status": "error", "message": "Unauthorized"}


async def test_chat_wrong_key(client: AsyncClient) -> None:
    r = await client.post("/chat", json={"user_prompt": "hello"}, headers={"X-API-Key": "wrong"})
    assert r.status_code == 401
    assert r.json() == {"status": "error", "message": "Unauthorized"}


async def test_chat_missing_field(client: AsyncClient) -> None:
    r = await client.post("/chat", json={}, headers=AUTH)
    assert r.status_code == 400
    assert r.json() == {"status": "error", "message": "Missing required field: user_prompt"}


async def test_chat_wrong_type(client: AsyncClient) -> None:
    r = await client.post("/chat", json={"user_prompt": 42}, headers=AUTH)
    assert r.status_code == 400
    assert r.json() == {"status": "error", "message": "Field user_prompt must be a string"}


async def test_chat_bad_json(client: AsyncClient) -> None:
    r = await client.post(
        "/chat",
        content=b"not json{{{",
        headers={**AUTH, "Content-Type": "application/json"},
    )
    assert r.status_code == 400
    assert r.json() == {"status": "error", "message": "Invalid JSON format"}


async def test_requests_empty(client: AsyncClient) -> None:
    r = await client.get("/requests", headers=AUTH)
    assert r.status_code == 200
    assert "No requests yet." in r.text


async def test_requests_shows_data(client: AsyncClient) -> None:
    await client.post("/chat", json={"user_prompt": "test prompt"}, headers=AUTH)
    r = await client.get("/requests", headers=AUTH)
    assert r.status_code == 200
    assert "test prompt" in r.text
    assert MOCK_RESPONSE in r.text


async def test_requests_no_key(client: AsyncClient) -> None:
    r = await client.get("/requests")
    assert r.status_code == 401
    assert r.json() == {"status": "error", "message": "Unauthorized"}


async def test_cleanup_no_stale_files(client: AsyncClient) -> None:
    r = await client.post("/cleanup_models", headers=AUTH)
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "deleted": []}


async def test_cleanup_deletes_stale_files(client: AsyncClient) -> None:
    import os
    from pathlib import Path
    model_dir = Path(llm_module.MODEL_DIR)
    (model_dir / "old-model.gguf").touch()
    (model_dir / "another-old.gguf").touch()

    r = await client.post("/cleanup_models", headers=AUTH)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert sorted(body["deleted"]) == ["another-old.gguf", "old-model.gguf"]
    assert not (model_dir / "old-model.gguf").exists()
    assert not (model_dir / "another-old.gguf").exists()


async def test_cleanup_preserves_current_model(client: AsyncClient) -> None:
    from pathlib import Path
    model_dir = Path(llm_module.MODEL_DIR)
    current = Path(llm_module.get_model_path()).name
    (model_dir / current).touch()
    (model_dir / "stale.gguf").touch()

    r = await client.post("/cleanup_models", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["deleted"] == ["stale.gguf"]
    assert (model_dir / current).exists()


async def test_cleanup_no_key(client: AsyncClient) -> None:
    r = await client.post("/cleanup_models")
    assert r.status_code == 401
