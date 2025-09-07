import math
from decimal import Decimal
from typing import Dict, List, Tuple

from fastapi.background import BackgroundTasks
from sqlalchemy.orm import Session

from app.core.exceptions import (CustomerNotFoundError,
                                 InsufficientPaymentError,
                                 InsufficientStockError,
                                 InvalidDenominationError,
                                 MismatchPaymentError, ProductNotFoundError)
from app.models.models import (Bill, BillDenomination, BillItem, Customer,
                               Denomination, Product)
from app.schemas.schemas import BillCreate, BillItemCreate, DenominationBase
from app.services.email_service import EmailService


class BillingService:
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()

    async def create_bill(
        self, bill_create: BillCreate, background_tasks: BackgroundTasks
    ) -> Tuple[Bill, List[Dict[str, int]]]:
        """Create a new bill with items and calculate balance denominations"""

        # Get or create customer
        customer = (
            self.db.query(Customer)
            .filter(Customer.email == bill_create.customer_email)
            .first()
        )
        if not customer:
            customer = Customer(email=bill_create.customer_email)
            self.db.add(customer)
            self.db.flush()

        # Check if all customer-given denominations exist in the DB; if not, raise error with missing value(s)
        # Fix: denomination may be a list of tuples, not objects with .value/.count
        denominations_from_request = bill_create.denomination
        given_values = [int(d.value) for d in denominations_from_request]
        denom_counts = [
            (int(d.value), int(d.count)) for d in denominations_from_request
        ]

        db_denominations = (
            self.db.query(Denomination.value)
            .filter(Denomination.value.in_(given_values))
            .all()
        )
        db_values = {d[0] for d in db_denominations}
        missing_values = [v for v in given_values if v not in db_values]

        if missing_values:
            raise InvalidDenominationError(
                f"We do not accept this denomination value(s): {', '.join(str(v) for v in missing_values)}"
            )

        # Check that the sum of the given denominations matches the paid amount
        denomination_sum = sum(value * count for value, count in denom_counts)
        if Decimal(denomination_sum) != bill_create.paid_amount:
            raise MismatchPaymentError(
                f"Sum of given denominations ({denomination_sum}) does not match paid amount ({bill_create.paid_amount})"
            )

        # Calculate bill totals and create bill items
        total_amount = Decimal("0")
        tax_amount = Decimal("0")
        bill_items = []

        for item in bill_create.items:
            product = (
                self.db.query(Product)
                .filter(Product.product_id == item.product_id)
                .first()
            )
            if not product:
                raise ProductNotFoundError(item.product_id)

            if product.available_stocks < item.quantity:
                raise InsufficientStockError(
                    product_id=item.product_id,
                    available=product.available_stocks,
                    requested=item.quantity,
                )

            # Calculate item amounts
            item_price = (
                Decimal(str(product.unit_price)).quantize(Decimal("0.00"))
                * item.quantity
            )
            item_tax = (
                item_price * (Decimal(str(product.tax_percentage)) / 100)
            ).quantize(Decimal("0.00"))
            item_total = (item_price + item_tax).quantize(Decimal("0.00"))

            # Update totals
            total_amount = (total_amount + item_total).quantize(Decimal("0.00"))
            tax_amount = (tax_amount + item_tax).quantize(Decimal("0.00"))

            # Create bill item
            bill_items.append(
                BillItem(
                    product_id=product.id,  # Use product's database ID (integer)
                    quantity=item.quantity,
                    unit_price=product.unit_price,
                    tax_percentage=product.tax_percentage,
                    tax_amount=item_tax,
                    total_amount=item_total,
                )
            )

            # Update product stock
            product.available_stocks -= item.quantity

        # Calculate rounded total amount
        rounded_total_amount = math.floor(total_amount)
        # Validate payment amount
        if bill_create.paid_amount < rounded_total_amount:
            raise InsufficientPaymentError(
                float(rounded_total_amount), float(bill_create.paid_amount)
            )

        # Calculate balance amount
        balance_amount = (bill_create.paid_amount - rounded_total_amount).quantize(
            Decimal("0.00")
        )

        # Create bill
        bill = Bill(
            customer_id=customer.id,
            total_amount=total_amount,
            rounded_total_amount=float(rounded_total_amount),
            tax_amount=tax_amount,
            paid_amount=bill_create.paid_amount,
            balance_amount=balance_amount,
            items=bill_items,
        )

        self.db.add(bill)
        self.db.flush()

        # Calculate balance denominations
        balance_denominations = self.calculate_balance_denominations(
            int(balance_amount)
        )

        # Create bill denominations
        for denom in balance_denominations:
            denomination = (
                self.db.query(Denomination)
                .filter(Denomination.value == denom["value"])
                .first()
            )

            if denomination and denomination.count >= denom["count"]:
                bill_denom = BillDenomination(
                    bill_id=bill.id,
                    denomination_id=denomination.id,
                    count=denom["count"],
                )
                denomination.count -= denom["count"]
                self.db.add(bill_denom)

        # Update the given Customer Denomination intothe Denomination Table

        for denom in denominations_from_request:
            db_denom = (
                self.db.query(Denomination)
                .filter(Denomination.value == denom.value)
                .first()
            )
            if db_denom:
                db_denom.count += denom.count

        # Commit changes
        self.db.commit()
        self.db.refresh(bill)

        # Send email asynchronously
        await self.email_service.send_bill_email(
            background_tasks, bill_create.customer_email, bill
        )

        return bill, balance_denominations

    def calculate_balance_denominations(self, balance: int) -> List[Dict[str, int]]:
        """Calculate optimal denomination distribution for balance amount"""
        denominations = (
            self.db.query(Denomination).order_by(Denomination.value.desc()).all()
        )
        result = []

        for denom in denominations:
            print("denom", denom.value, "count", denom.count)
            denom_value = denom.value
            if balance >= denom_value and denom.count > 0:
                count = min(balance // denom_value, denom.count)
                if count > 0:
                    result.append({"value": denom.value, "count": count})
                    balance -= count * denom_value
        print(result)
        if balance > 0:
            print(f"Remaining balance: {balance}")

            raise InvalidDenominationError(
                f"Unable to provide exact change with available denominations: {balance}"
            )

        return result

    def get_customer_bills(self, customer_email: str) -> List[Bill]:
        """Get all bills for a customer"""
        customer = (
            self.db.query(Customer).filter(Customer.email == customer_email).first()
        )
        if not customer:
            raise CustomerNotFoundError(customer_email)

        # Load bills with their items and product relationships
        from sqlalchemy.orm import joinedload

        bills = (
            self.db.query(Bill)
            .options(joinedload(Bill.items).joinedload(BillItem.product))
            .filter(Bill.customer_id == customer.id)
            .order_by(Bill.id.desc())
            .all()
        )

        return bills

    def get_bill(self, bill_id: int) -> Bill:
        """Get a specific bill by ID"""
        bill = self.db.query(Bill).filter(Bill.id == bill_id).first()
        if not bill:
            raise CustomerNotFoundError(f"Bill not found with ID: {bill_id}")
        return bill
