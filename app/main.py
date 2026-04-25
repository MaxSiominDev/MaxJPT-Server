import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import requests as http
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.db import init_db
from app.llm import load_model
from app.routes import chat, cleanup, health, requests


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if not os.environ.get("MODEL_URL"):
        print("MODEL_URL environment variable is not set", file=sys.stderr)
        sys.exit(1)

    prompt_url = os.environ.get("PROMPT_URL", "")
    if not prompt_url:
        print("PROMPT_URL environment variable is not set", file=sys.stderr)
        sys.exit(1)

    try:
        resp = http.get(prompt_url, timeout=10)
        resp.raise_for_status()
        app.state.system_prompt = resp.text.strip()
    except Exception as e:
        print(f"Failed to fetch system prompt from {prompt_url}: {e}", file=sys.stderr)
        sys.exit(1)

    await init_db()
    app.state.llm = load_model()

    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


app.include_router(health.router)
app.include_router(chat.router)
app.include_router(requests.router)
app.include_router(cleanup.router)
