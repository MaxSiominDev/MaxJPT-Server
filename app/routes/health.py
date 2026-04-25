from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.auth import require_api_key

router = APIRouter()


@router.get("/health")
async def health(_: None = Depends(require_api_key)) -> JSONResponse:
    return JSONResponse({"status": "ok"})
