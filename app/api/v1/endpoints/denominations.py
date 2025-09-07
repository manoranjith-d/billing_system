from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseError, InvalidDenominationError
from app.db.session import get_db
from app.schemas.schemas import (Denomination, DenominationCreate,
                                 DenominationUpdate)
from app.services.denomination_service import DenominationService

router = APIRouter()


@router.post("/", response_model=Denomination, status_code=status.HTTP_201_CREATED)
async def create_denomination(
    denomination: DenominationCreate, db: Session = Depends(get_db)
):
    """Create a new denomination"""
    try:
        denomination_service = DenominationService(db)
        return denomination_service.create_denomination(denomination)
    except (InvalidDenominationError, DatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[Denomination])
async def get_denominations(db: Session = Depends(get_db)):
    """Get all denominations"""
    denomination_service = DenominationService(db)
    return denomination_service.get_all_denominations()


@router.get("/{value}", response_model=Denomination)
async def get_denomination(value: int, db: Session = Depends(get_db)):
    """Get a specific denomination by value"""
    try:
        denomination_service = DenominationService(db)
        return denomination_service.get_denomination(value)
    except InvalidDenominationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{value}", response_model=Denomination)
async def update_denomination(
    value: int, update: DenominationUpdate, db: Session = Depends(get_db)
):
    """Update denomination count"""
    try:
        denomination_service = DenominationService(db)
        return denomination_service.update_denomination_count(value, update)
    except InvalidDenominationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/calculate-change", response_model=Dict[int, int])
async def calculate_change(amount: float, db: Session = Depends(get_db)):
    """Calculate optimal change distribution for given amount"""
    try:
        denomination_service = DenominationService(db)
        return denomination_service.calculate_change(amount)
    except InvalidDenominationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/validate-availability")
async def validate_denominations(
    distribution: Dict[int, int], db: Session = Depends(get_db)
):
    """Validate if required denominations are available"""
    try:
        denomination_service = DenominationService(db)
        is_available = denomination_service.validate_denominations_availability(
            distribution
        )
        return {"available": is_available}
    except InvalidDenominationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
