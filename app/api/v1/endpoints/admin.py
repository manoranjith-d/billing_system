from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Denomination, Product
from app.schemas.schemas import Denomination as DenominationSchema
from app.schemas.schemas import Product as ProductSchema

router = APIRouter()

# Configure templates directory
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent.parent.parent / "templates")
)


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Serve the admin dashboard page"""
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


@router.get("/admin/products", response_class=HTMLResponse)
async def admin_products(request: Request):
    """Serve the admin products management page"""
    return templates.TemplateResponse("admin_products.html", {"request": request})


@router.get("/admin/denominations", response_class=HTMLResponse)
async def admin_denominations(request: Request):
    """Serve the admin denominations management page"""
    return templates.TemplateResponse("admin_denominations.html", {"request": request})


@router.get("/admin/stats", response_class=HTMLResponse)
async def admin_stats(request: Request, db: Session = Depends(get_db)):
    """Get admin dashboard statistics"""
    try:
        # Get products statistics
        total_products = db.query(Product).count()
        low_stock_products = (
            db.query(Product).filter(Product.available_stocks < 10).count()
        )

        # Get denominations statistics
        total_denominations = db.query(Denomination).count()
        denominations = db.query(Denomination).all()
        total_cash_value = sum(d.value * d.count for d in denominations)

        # Get recent products (last 5)
        recent_products = (
            db.query(Product).order_by(Product.created_at.desc()).limit(5).all()
        )

        # Get recent denominations (last 5)
        recent_denominations = (
            db.query(Denomination)
            .order_by(Denomination.updated_at.desc())
            .limit(5)
            .all()
        )

        stats = {
            "products": {
                "total": total_products,
                "low_stock": low_stock_products,
                "recent": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "product_id": p.product_id,
                        "created_at": p.created_at.isoformat(),
                    }
                    for p in recent_products
                ],
            },
            "denominations": {
                "total": total_denominations,
                "total_value": total_cash_value,
                "recent": [
                    {
                        "id": d.id,
                        "value": d.value,
                        "count": d.count,
                        "updated_at": d.updated_at.isoformat()
                        if d.updated_at
                        else d.created_at.isoformat(),
                    }
                    for d in recent_denominations
                ],
            },
        }

        return stats

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching admin stats: {str(e)}"
        )
