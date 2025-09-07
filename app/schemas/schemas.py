from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, EmailStr, Field, root_validator, validator
from sqlalchemy import Boolean


# Product Schemas
class ProductBase(BaseModel):
    name: str
    product_id: str
    available_stocks: int
    unit_price: Decimal = Field(..., ge=0)
    tax_percentage: Decimal = Field(..., ge=0, le=100)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    name: Optional[str] = None
    available_stocks: Optional[int] = None
    unit_price: Optional[Decimal] = Field(None, ge=0)
    tax_percentage: Optional[Decimal] = Field(None, ge=0, le=100)


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Bill Item Schemas
class BillItemBase(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)


class BillItemCreate(BillItemBase):
    pass


class BillItem(BaseModel):
    id: int
    product_id: str
    quantity: int
    unit_price: Decimal
    tax_percentage: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    created_at: datetime

    @validator("product_id", pre=True)
    def convert_product_id_to_str(cls, v):
        return str(v) if v is not None else None

    class Config:
        from_attributes = True


# Bill Schemas
class BillBase(BaseModel):
    customer_email: EmailStr
    items: List[BillItemCreate]
    paid_amount: Decimal = Field(..., ge=0)


class Bill(BaseModel):
    id: int
    total_amount: Decimal
    rounded_total_amount: Decimal
    tax_amount: Decimal
    balance_amount: Decimal
    mail_sent: bool
    created_at: datetime
    items: List[BillItem]
    paid_amount: Decimal
    customer_email: Optional[EmailStr] = None  # Make it optional initially

    @root_validator(pre=True)
    def extract_customer_email(cls, values):
        # If values is a database model object
        if hasattr(values, "customer") and values.customer is not None:
            if isinstance(values, dict):
                values["customer_email"] = (
                    values.get("customer_email") or values["customer"].email
                )
            else:
                # Convert model object to dict and add customer_email
                model_dict = {}
                for field in [
                    "id",
                    "total_amount",
                    "rounded_total_amount",
                    "mail_sent",
                    "tax_amount",
                    "balance_amount",
                    "created_at",
                    "items",
                    "paid_amount",
                ]:
                    if hasattr(values, field):
                        model_dict[field] = getattr(values, field)
                model_dict["customer_email"] = values.customer.email
                return model_dict
        return values

    class Config:
        from_attributes = True


# Denomination Schemas
class DenominationBase(BaseModel):
    value: int = Field(..., gt=0)
    count: int = Field(..., ge=0)


class DenominationCreate(DenominationBase):
    pass


class DenominationUpdate(BaseModel):
    count: int = Field(..., ge=0)


class Denomination(DenominationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CustomerGivenDenominationBase(BaseModel):
    customerDenomination: List[DenominationBase]


# Bill Denomination Schemas
class BillDenominationBase(BaseModel):
    denomination_id: int
    count: int = Field(..., gt=0)


class BillDenominationCreate(BillDenominationBase):
    pass


class BillDenomination(BillDenominationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Response Schemas
class MessageResponse(BaseModel):
    detail: str


class BillWithCustomerEmail(Bill):
    customer_email: EmailStr


class BillResponse(BaseModel):
    bill: BillWithCustomerEmail
    balance_denominations: List


class CustomerPurchaseHistory(BaseModel):
    customer_email: EmailStr
    bills: List[Bill]


class BillCreate(BillBase):
    denomination: List[DenominationBase]
