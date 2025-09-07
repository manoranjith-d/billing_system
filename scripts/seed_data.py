import asyncio
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.models import Denomination, Product


def seed_products(db: Session):
    """Seed initial products"""
    products = [
        {
            "name": "Laptop",
            "product_id": "PROD001",
            "available_stocks": 50,
            "unit_price": 999.99,
            "tax_percentage": 18.0,
        },
        {
            "name": "Smartphone",
            "product_id": "PROD002",
            "available_stocks": 100,
            "unit_price": 599.99,
            "tax_percentage": 18.0,
        },
        {
            "name": "Headphones",
            "product_id": "PROD003",
            "available_stocks": 200,
            "unit_price": 99.99,
            "tax_percentage": 18.0,
        },
        {
            "name": "Mouse",
            "product_id": "PROD004",
            "available_stocks": 150,
            "unit_price": 29.99,
            "tax_percentage": 18.0,
        },
        {
            "name": "Keyboard",
            "product_id": "PROD005",
            "available_stocks": 150,
            "unit_price": 49.99,
            "tax_percentage": 18.0,
        },
    ]
    if not db.query(Product).all():
        for product_data in products:
            product = (
                db.query(Product)
                .filter(Product.product_id == product_data["product_id"])
                .first()
            )
            if not product:
                product = Product(**product_data)
                db.add(product)

        db.commit()
        print("Products seeded successfully!")
    else:
        print("Products already seeded!")


def seed_denominations(db: Session):
    """Seed initial denominations"""
    if not db.query(Denomination).all():
        for value in settings.DEFAULT_DENOMINATIONS:
            denomination = (
                db.query(Denomination).filter(Denomination.value == value).first()
            )
            if not denomination:
                denomination = Denomination(value=value, count=100)
                db.add(denomination)

        db.commit()
        print("Denominations seeded successfully!")
    else:
        print("Denominations already seeded!")


def main():
    db = SessionLocal()
    try:
        # Seed initial data
        seed_products(db)
        seed_denominations(db)
        print("All data seeded successfully!")
    except Exception as e:
        print(f"Error seeding data: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
