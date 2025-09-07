from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import (BillingSystemException, BillNotFoundError,
                                 CustomerNotFoundError, DatabaseError,
                                 EmailError, InsufficientPaymentError,
                                 InsufficientStockError,
                                 InvalidDenominationError,
                                 MismatchPaymentError, ProductNotFoundError,
                                 ValidationError)
from app.db.session import engine
from app.models.models import Base
from scripts.seed_data import main

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Create database tables on startup
@app.on_event("startup")
async def create_tables():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("Database tables created or verified on startup")
    # Seed the products and denomoinations for testing purpose
    main()


# ---------- Custom Exception Handlers ----------
def register_exception_handlers(app: FastAPI):
    exception_mapping = {
        InsufficientStockError: 400,
        InvalidDenominationError: 400,
        InsufficientPaymentError: 400,
        BillingSystemException: 500,
        CustomerNotFoundError: 404,
        BillNotFoundError: 404,
        DatabaseError: 500,
        EmailError: 500,
        MismatchPaymentError: 400,
        ProductNotFoundError: 404,
        ValidationError: 422,
    }

    for exc_class, status_code in exception_mapping.items():

        @app.exception_handler(exc_class)
        async def custom_handler(
            request: Request, exc: exc_class, status_code=status_code
        ):
            return JSONResponse(
                status_code=status_code,
                content={"detail": str(exc)},
            )

    # Catch-all for any unhandled exceptions
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred", "error": str(exc)},
        )


# Register exception handlers
register_exception_handlers(app)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def default():
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
