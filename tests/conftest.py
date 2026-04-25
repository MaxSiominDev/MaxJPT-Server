import pytest_asyncio
from httpx import ASGITransport, AsyncClient

import app.db as db_module
import app.llm as llm_module
import app.routes.cleanup as cleanup_module


@pytest_asyncio.fixture
async def client(monkeypatch, tmp_path):
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("LLM_MOCK", "1")
    monkeypatch.setenv("MODEL_URL", "http://example.com/model/test-model.gguf")

    monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.db"))

    model_dir = tmp_path / "model"
    model_dir.mkdir()
    monkeypatch.setattr(llm_module, "MODEL_DIR", str(model_dir))
    monkeypatch.setattr(cleanup_module, "MODEL_DIR", str(model_dir))

    await db_module.init_db()

    from app.main import app
    app.state.system_prompt = "You are a test assistant."
    app.state.llm = None

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
