from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth import require_api_key
from app.db import fetch_all_requests

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/requests", response_class=HTMLResponse)
async def list_requests(request: Request, _: None = Depends(require_api_key)) -> HTMLResponse:
    rows = await fetch_all_requests()
    return templates.TemplateResponse(request, "requests.html", {"rows": rows})
