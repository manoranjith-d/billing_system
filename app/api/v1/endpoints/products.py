from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.product_service import ProductService
from app.schemas.schemas import Product, ProductCreate, ProductUpdate, MessageResponse
from app.core.exceptions import ProductNotFoundError, DatabaseError

router = APIRouter()

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product"""
    try:
        product_service = ProductService(db)
        return product_service.create_product(product)
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[Product])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of products with pagination"""
    product_service = ProductService(db)
    return product_service.get_products(skip=skip, limit=limit)

@router.get("/search", response_model=List[Product])
async def search_products(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search products by name or ID"""
    product_service = ProductService(db)
    return product_service.search_products(query, skip=skip, limit=limit)

@router.get("/{id}", response_model=Product)
async def get_product(
    id: str,
    db: Session = Depends(get_db)
):
    """Get a specific product by ID"""
    try:
        product_service = ProductService(db)
        return product_service.get_product(id)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{id}", response_model=Product)
async def update_product(
    id: str,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update a product"""
    try:
        product_service = ProductService(db)
        return product_service.update_product(id, product)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{id}", response_model=MessageResponse)
async def delete_product(
    id: str,
    db: Session = Depends(get_db)
):
    """Delete a product"""
    try:
        product_service = ProductService(db)
        product_service.delete_product(id)
        return MessageResponse(detail=f"Product {id} deleted successfully")
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{id}/stock", response_model=Product)
async def update_stock(
    id: int,
    quantity: int,
    db: Session = Depends(get_db)
):
    """Update product stock"""
    try:
        product_service = ProductService(db)
        return product_service.update_stock(id, quantity)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )