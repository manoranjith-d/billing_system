from datetime import datetime
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (CustomerNotFoundError, EmailError,
                                 InsufficientPaymentError,
                                 InsufficientStockError, ProductNotFoundError)
from app.db.session import get_db
from app.models.models import BillDenomination, Denomination
from app.schemas.schemas import (Bill, BillCreate, BillResponse,
                                 CustomerPurchaseHistory, MessageResponse)
from app.services.billing_service import BillingService

router = APIRouter()


@router.post("/", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
async def create_bill(
    bill: BillCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """Create a new bill and send email notification"""
    try:
        billing_service = BillingService(db)
        bill_obj, balance_denominations = await billing_service.create_bill(
            bill, background_tasks
        )
        bill_obj.customer_email = bill.customer_email
        print(balance_denominations)
        return BillResponse(bill=bill_obj, balance_denominations=balance_denominations)
    except (
        InsufficientStockError,
        InsufficientPaymentError,
        ProductNotFoundError,
    ) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except EmailError as e:
        # Don't fail the bill creation if email fails
        # Log the error and continue
        print(f"Email sending failed: {str(e)}")
        return BillResponse(bill=bill_obj, balance_denominations=balance_denominations)


@router.get("/customer/{email}", response_model=CustomerPurchaseHistory)
async def get_customer_bills(email: str, db: Session = Depends(get_db)):
    """Get all bills for a customer"""
    try:
        billing_service = BillingService(db)
        bills = billing_service.get_customer_bills(email)
        return CustomerPurchaseHistory(customer_email=email, bills=bills)
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{bill_id}", response_model=Bill)
async def get_bill(bill_id: int, db: Session = Depends(get_db)):
    """Get a specific bill by ID"""
    try:
        billing_service = BillingService(db)
        return billing_service.get_bill(bill_id)
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/test-email", response_model=MessageResponse)
async def test_email(
    email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """Send a test email to verify email configuration"""
    try:
        billing_service = BillingService(db)
        await billing_service.email_service.send_test_email(email)
        return MessageResponse(detail="Test email sent successfully")
    except EmailError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
