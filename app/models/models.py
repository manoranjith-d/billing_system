from datetime import datetime
from typing import List

from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, UniqueConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    product_id = Column(String(50), unique=True, nullable=False, index=True)
    available_stocks = Column(Integer, nullable=False)
    unit_price = Column(Float(precision=2), nullable=False)
    tax_percentage = Column(Float(precision=2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    bill_items = relationship("BillItem", back_populates="product")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    bills = relationship("Bill", back_populates="customer")


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    total_amount = Column(Float(precision=2), nullable=False)
    rounded_total_amount = Column(Float(precision=2), nullable=False)
    tax_amount = Column(Float(precision=2), nullable=False)
    paid_amount = Column(Float(precision=2), nullable=False)
    balance_amount = Column(Float(precision=2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    mail_sent = Column(Boolean, nullable=False, default=False, server_default="0")
    # Relationships
    customer = relationship("Customer", back_populates="bills")
    items = relationship("BillItem", back_populates="bill")
    denominations = relationship("BillDenomination", back_populates="bill")


class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float(precision=2), nullable=False)
    tax_percentage = Column(Float(precision=2), nullable=False)
    tax_amount = Column(Float(precision=2), nullable=False)
    total_amount = Column(Float(precision=2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    bill = relationship("Bill", back_populates="items")
    product = relationship("Product", back_populates="bill_items")


class Denomination(Base):
    __tablename__ = "denominations"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, nullable=False, unique=True)
    count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    bill_denominations = relationship("BillDenomination", back_populates="denomination")


class BillDenomination(Base):
    __tablename__ = "bill_denominations"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    denomination_id = Column(Integer, ForeignKey("denominations.id"))
    count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    bill = relationship("Bill", back_populates="denominations")
    denomination = relationship("Denomination", back_populates="bill_denominations")
