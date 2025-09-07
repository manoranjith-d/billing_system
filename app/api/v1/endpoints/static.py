from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

# Configure templates directory
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent.parent.parent / "templates")
)


@router.get("/", response_class=HTMLResponse)
async def billing_page(request: Request):
    """Serve the billing page"""
    return templates.TemplateResponse("billing.html", {"request": request})


@router.get("/history", response_class=HTMLResponse)
async def purchase_history(request: Request):
    """Serve the purchase history page"""
    return templates.TemplateResponse("history.html", {"request": request})
