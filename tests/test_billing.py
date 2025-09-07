import os
import sys

import pytest

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base_class import Base
from app.db.session import get_db
from app.main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

# Test client
client = TestClient(app)


# Override dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Test data
test_product = {
    "name": "Test Product",
    "product_id": "TEST001",
    "available_stocks": 100,
    "unit_price": "99.99",  # String format for Decimal
    "tax_percentage": "18.0",  # String format for Decimal
}

test_bill = {
    "customer_email": "test@example.com",
    "items": [{"product_id": "TEST001", "quantity": 2}],
    "paid_amount": "250.0",  # String format for Decimal
    "denomination": [],  # Required field for BillCreate
}

test_denomination = {"value": 500, "count": 10}


@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def setup_test_data(test_db):
    """Setup test data for tests that need products and denominations"""
    # Create test product
    product_response = client.post("/api/v1/products/", json=test_product)
    assert product_response.status_code == 201

    # Create test denominations
    denominations = [
        {"value": 500, "count": 10},
        {"value": 200, "count": 20},
        {"value": 100, "count": 30},
        {"value": 50, "count": 40},
        {"value": 20, "count": 50},
        {"value": 10, "count": 60},
        {"value": 5, "count": 70},
        {"value": 2, "count": 80},
        {"value": 1, "count": 90},
    ]

    for denom in denominations:
        response = client.post("/api/v1/denominations/", json=denom)
        assert response.status_code == 201


# Product Tests
def test_create_product(test_db):
    response = client.post("/api/v1/products/", json=test_product)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_product["name"]
    assert data["product_id"] == test_product["product_id"]
    assert str(data["unit_price"]) == test_product["unit_price"]
    assert str(data["tax_percentage"]) == test_product["tax_percentage"]
    assert data["available_stocks"] == test_product["available_stocks"]


def test_get_products(test_db):
    # Create multiple products
    client.post("/api/v1/products/", json=test_product)
    product2 = test_product.copy()
    product2["product_id"] = "TEST002"
    product2["name"] = "Test Product 2"
    client.post("/api/v1/products/", json=product2)

    # Get all products
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_product_by_id(test_db):
    # First create a product
    create_response = client.post("/api/v1/products/", json=test_product)
    product_data = create_response.json()

    # Then get it by product_id
    response = client.get(f"/api/v1/products/{test_product['product_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_product["name"]
    assert data["product_id"] == test_product["product_id"]


def test_update_product(test_db):
    # First create a product
    create_response = client.post("/api/v1/products/", json=test_product)
    product_data = create_response.json()

    # Update the product
    update_data = {
        "name": "Updated Test Product",
        "unit_price": "149.99",  # String format for Decimal
        "tax_percentage": "20.0",  # String format for Decimal
        "available_stocks": 150,
    }

    response = client.put(
        f"/api/v1/products/{test_product['product_id']}", json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert str(data["unit_price"]) == update_data["unit_price"]


def test_delete_product(test_db):
    # First create a product
    client.post("/api/v1/products/", json=test_product)

    # Delete the product
    response = client.delete(f"/api/v1/products/{test_product['product_id']}")
    assert response.status_code == 200
    data = response.json()
    assert "deleted successfully" in data["detail"]

    # Verify it's deleted
    get_response = client.get(f"/api/v1/products/{test_product['product_id']}")
    assert get_response.status_code == 404


# Bill Tests
def test_create_bill(setup_test_data):
    response = client.post("/api/v1/bills/", json=test_bill)
    assert response.status_code == 201
    data = response.json()
    assert "bill" in data
    assert "balance_denominations" in data
    assert data["bill"]["customer_email"] == test_bill["customer_email"]
    assert data["bill"]["total_amount"] > 0
    assert data["bill"]["tax_amount"] > 0


def test_insufficient_stock(setup_test_data):
    # Try to create bill with quantity > available_stocks
    invalid_bill = test_bill.copy()
    invalid_bill["items"][0]["quantity"] = 1000

    response = client.post("/api/v1/bills/", json=invalid_bill)
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]


def test_insufficient_payment(setup_test_data):
    # Try to create bill with insufficient payment
    invalid_bill = test_bill.copy()
    invalid_bill["paid_amount"] = "10.0"  # String format for Decimal

    response = client.post("/api/v1/bills/", json=invalid_bill)
    assert response.status_code == 400
    assert "Insufficient payment" in response.json()["detail"]


def test_get_customer_bills(setup_test_data):
    # First create a bill
    bill_response = client.post("/api/v1/bills/", json=test_bill)
    assert bill_response.status_code == 201

    # Then get customer bills
    response = client.get(f"/api/v1/bills/customer/{test_bill['customer_email']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["bills"]) > 0
    assert data["customer_email"] == test_bill["customer_email"]
    assert data["bills"][0]["customer_email"] == test_bill["customer_email"]


def test_get_bill_by_id(setup_test_data):
    # First create a bill
    bill_response = client.post("/api/v1/bills/", json=test_bill)
    assert bill_response.status_code == 201
    bill_data = bill_response.json()
    bill_id = bill_data["bill"]["id"]

    # Then get the specific bill
    response = client.get(f"/api/v1/bills/{bill_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == bill_id
    assert data["customer_email"] == test_bill["customer_email"]


# Denomination Tests
def test_create_denomination(test_db):
    response = client.post("/api/v1/denominations/", json=test_denomination)
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == test_denomination["value"]
    assert data["count"] == test_denomination["count"]


def test_get_denominations(test_db):
    # Create multiple denominations
    client.post("/api/v1/denominations/", json=test_denomination)
    denom2 = {"value": 200, "count": 5}
    client.post("/api/v1/denominations/", json=denom2)

    # Get all denominations
    response = client.get("/api/v1/denominations/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_update_denomination(test_db):
    # First create a denomination
    create_response = client.post("/api/v1/denominations/", json=test_denomination)
    denom_data = create_response.json()

    # Update the denomination count using value (not id)
    update_data = {"count": 25}
    response = client.put(
        f"/api/v1/denominations/{denom_data['value']}", json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == update_data["count"]


def test_get_denomination_by_value(test_db):
    # First create a denomination
    create_response = client.post("/api/v1/denominations/", json=test_denomination)
    denom_data = create_response.json()

    # Get the denomination by value
    response = client.get(f"/api/v1/denominations/{denom_data['value']}")
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == test_denomination["value"]
    assert data["count"] == test_denomination["count"]


# Error Tests
def test_product_not_found(test_db):
    response = client.get("/api/v1/products/NONEXISTENT")
    assert response.status_code == 404


def test_bill_not_found(test_db):
    response = client.get("/api/v1/bills/99999")
    assert response.status_code == 404


def test_customer_not_found(test_db):
    response = client.get("/api/v1/bills/customer/nonexistent@example.com")
    assert response.status_code == 404
