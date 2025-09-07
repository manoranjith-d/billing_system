import math
from typing import Dict, List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import DatabaseError, InvalidDenominationError
from app.models.models import Denomination
from app.schemas.schemas import DenominationCreate, DenominationUpdate


class DenominationService:
    def __init__(self, db: Session):
        self.db = db

    def create_denomination(self, denomination: DenominationCreate) -> Denomination:
        """Create a new denomination"""
        try:
            if denomination.value <= 0:
                raise InvalidDenominationError("Denomination value must be positive")

            db_denomination = Denomination(
                value=denomination.value, count=denomination.count
            )
            self.db.add(db_denomination)
            self.db.commit()
            self.db.refresh(db_denomination)
            return db_denomination

        except IntegrityError:
            self.db.rollback()
            raise DatabaseError(
                f"Denomination with value {denomination.value} already exists"
            )
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create denomination: {str(e)}")

    def get_denomination(self, value: int) -> Denomination:
        """Get a denomination by value"""
        denomination = (
            self.db.query(Denomination).filter(Denomination.value == value).first()
        )
        if not denomination:
            raise InvalidDenominationError(f"Denomination with value {value} not found")
        return denomination

    def get_all_denominations(self) -> List[Denomination]:
        """Get all denominations ordered by value descending"""
        return self.db.query(Denomination).order_by(Denomination.value.desc()).all()

    def update_denomination_count(
        self, value: int, update: DenominationUpdate
    ) -> Denomination:
        """Update denomination count"""
        try:
            denomination = self.get_denomination(value)

            if update.count < 0:
                raise InvalidDenominationError("Count cannot be negative")

            denomination.count = update.count
            self.db.commit()
            self.db.refresh(denomination)
            return denomination

        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update denomination: {str(e)}")
    
    def delete_denomination(self, value: int) -> bool:
        """Delete denomination"""
        try:
            denomination = self.get_denomination(value)

            if denomination:
                self.db.delete(denomination)   # ✅ actually delete the object
                self.db.commit()
                return True

            return False  # no denomination found

        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to Delete denomination: {str(e)}")


    def calculate_change(self, amount: float) -> Dict[int, int]:
        """Calculate optimal change distribution for given amount"""
        denominations = self.get_all_denominations()
        remaining = math.floor(amount)
        distribution = {}

        for denom in denominations:
            if remaining <= 0:
                break

            denom_value = denom.value
            if remaining >= denom_value and denom.count > 0:
                count = min(remaining // denom_value, denom.count)
                if count > 0:
                    distribution[denom.value] = count
                    remaining -= count * denom_value

        if remaining > 0:
            raise InvalidDenominationError(
                "Cannot provide exact change with available denominations"
            )

        return distribution

    def validate_denominations_availability(self, distribution: Dict[int, int]) -> bool:
        """Validate if required denominations are available"""
        for value, count in distribution.items():
            denomination = self.get_denomination(value)
            if denomination.count < count:
                return False
        return True

    def update_denominations_after_transaction(
        self, distribution: Dict[int, int]
    ) -> None:
        """Update denomination counts after a transaction"""
        try:
            for value, count in distribution.items():
                denomination = self.get_denomination(value)
                denomination.count -= count

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update denominations: {str(e)}")
