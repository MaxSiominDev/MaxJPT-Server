import logging
import traceback

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.auth import require_api_key
from app.db import insert_request
from app.llm import run_inference

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat")
async def chat(request: Request, _: None = Depends(require_api_key)) -> JSONResponse:
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid JSON format"},
        )

    if "user_prompt" not in body:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Missing required field: user_prompt"},
        )

    user_prompt = body["user_prompt"]
    if not isinstance(user_prompt, str):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Field user_prompt must be a string"},
        )

    try:
        model_response = run_inference(
            request.app.state.llm,
            request.app.state.system_prompt,
            user_prompt,
        )
    except Exception:
        logger.error("Inference failed:\n%s", traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "An error occurred processing your request"},
        )

    await insert_request(user_prompt, model_response)
    return JSONResponse({"status": "ok", "model_response": model_response})
