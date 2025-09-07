from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.models import Product
from app.schemas.schemas import ProductCreate, ProductUpdate
from app.core.exceptions import ProductNotFoundError, DatabaseError

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def create_product(self, product: ProductCreate) -> Product:
        """Create a new product"""
        try:
            db_product = Product(
                name=product.name,
                product_id=product.product_id,
                available_stocks=product.available_stocks,
                unit_price=float(product.unit_price),
                tax_percentage=float(product.tax_percentage)
            )
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            return db_product

        except IntegrityError:
            self.db.rollback()
            raise DatabaseError(f"Product with ID {product.product_id} already exists")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create product: {str(e)}")

    def get_product(self, id: int) -> Product:
        """Get a product by ID"""
        product = self.db.query(Product).filter(Product.id == id).first()
        if not product:
            raise ProductNotFoundError(id)
        return product

    def get_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get list of products with pagination"""
        return self.db.query(Product).offset(skip).limit(limit).all()

    def update_product(self, id: int, product_update: ProductUpdate) -> Product:
        """Update a product"""
        db_product = self.get_product(id)
        print(db_product)
        try:
            update_data = product_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    if field in ['unit_price', 'tax_percentage']:
                        value = float(value)
                    setattr(db_product, field, value)

            self.db.commit()
            self.db.refresh(db_product)
            return db_product

        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update product: {str(e)}")

    def delete_product(self, id: int) -> None:
        """Delete a product"""
        db_product = self.get_product(id)

        try:
            self.db.delete(db_product)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to delete product: {str(e)}")

    def update_stock(self, id: int, quantity: int) -> Product:
        """Update product stock"""
        db_product = self.get_product(id)

        try:
            db_product.available_stocks = quantity
            self.db.commit()
            self.db.refresh(db_product)
            return db_product

        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update stock: {str(e)}")

    def check_stock_availability(self, id: int, quantity: int) -> bool:
        """Check if product has sufficient stock"""
        product = self.get_product(id)
        return product.available_stocks >= quantity

    def search_products(self, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Search products by name or ID"""
        return self.db.query(Product).filter(
            (Product.name.ilike(f"%{query}%")) |
            (Product.product_id.ilike(f"%{query}%"))
        ).offset(skip).limit(limit).all()