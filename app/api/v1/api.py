from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints import (admin, billing, denominations, products,
                                  static)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(products.router, prefix="/products", tags=["products"])

api_router.include_router(billing.router, prefix="/bills", tags=["billing"])

api_router.include_router(
    denominations.router, prefix="/denominations", tags=["denominations"]
)

# Include admin routes
api_router.include_router(admin.router, prefix="", tags=["admin"])

# Include static routes
api_router.include_router(static.router, prefix="", tags=["static"])
