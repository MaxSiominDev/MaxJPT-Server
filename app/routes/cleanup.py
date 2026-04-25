import os

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.auth import require_api_key
from app.llm import MODEL_DIR, get_model_path

router = APIRouter()


@router.post("/cleanup_models")
async def cleanup_models(_: None = Depends(require_api_key)) -> JSONResponse:
    current = get_model_path()
    deleted = []
    for name in os.listdir(MODEL_DIR):
        if not name.endswith(".gguf"):
            continue
        path = os.path.join(MODEL_DIR, name)
        if path == current:
            continue
        os.remove(path)
        deleted.append(name)
    return JSONResponse({"status": "ok", "deleted": deleted})
