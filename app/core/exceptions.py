class BillingSystemException(Exception):
    """Base exception for billing system"""

    pass


class InsufficientStockError(BillingSystemException):
    """Raised when product stock is insufficient for the requested quantity"""

    def __init__(self, product_id: str, available: int, requested: int):
        self.product_id = product_id
        self.available = available
        self.requested = requested
        self.message = f"Insufficient stock for product {product_id}. Available: {available}, Requested: {requested}"
        super().__init__(self.message)


class InvalidDenominationError(BillingSystemException):
    """Raised when denomination value or count is invalid"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InsufficientPaymentError(BillingSystemException):
    """Raised when paid amount is less than total bill amount"""

    def __init__(self, total_amount: float, paid_amount: float):
        self.total_amount = total_amount
        self.paid_amount = paid_amount
        self.message = f"Insufficient payment. Total amount: {total_amount}, Paid amount: {paid_amount}"
        super().__init__(self.message)


class MismatchPaymentError(BillingSystemException):
    """Raised when paid amount is less than total bill amount"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ProductNotFoundError(BillingSystemException):
    """Raised when product is not found"""

    def __init__(self, product_id: str):
        self.product_id = product_id
        self.message = f"Product not found with ID: {product_id}"
        super().__init__(self.message)


class CustomerNotFoundError(BillingSystemException):
    """Raised when customer is not found"""

    def __init__(self, email: str):
        self.email = email
        self.message = f"Customer not found with email: {email}"
        super().__init__(self.message)


class BillNotFoundError(BillingSystemException):
    """Raised when bill is not found"""

    def __init__(self, bill_id: int):
        self.bill_id = bill_id
        self.message = f"Bill not found with ID: {bill_id}"
        super().__init__(self.message)


class EmailError(BillingSystemException):
    """Raised when there is an error sending email"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ValidationError(BillingSystemException):
    """Raised when input validation fails"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DatabaseError(BillingSystemException):
    """Raised when database operation fails"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
