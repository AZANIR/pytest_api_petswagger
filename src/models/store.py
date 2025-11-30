"""Pydantic models for Store-related entities."""
import random
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class OrderStatus(str, Enum):
    """Order status enum."""
    PLACED = "placed"
    APPROVED = "approved"
    DELIVERED = "delivered"


class Order(BaseModel):
    """Order model for pet store orders."""
    id: Optional[int] = None
    petId: Optional[int] = None
    quantity: Optional[int] = None
    shipDate: Optional[str] = None
    status: Optional[OrderStatus] = None
    complete: Optional[bool] = None
    
    @classmethod
    def create(
        cls,
        id: Optional[int] = None,
        pet_id: Optional[int] = None,
        quantity: Optional[int] = None,
        ship_date: Optional[str] = None,
        status: Optional[OrderStatus] = None,
        complete: Optional[bool] = None
    ) -> "Order":
        """
        Factory method to create an Order instance with default test data.
        
        Args:
            id: Order ID (auto-generated if not provided)
            pet_id: ID of the pet being ordered
            quantity: Quantity of pets
            ship_date: Ship date in ISO format
            status: Order status
            complete: Whether order is complete
            
        Returns:
            Order instance with test data
        """
        return cls(
            id=id or random.randint(1, 10),  # Valid range per API spec is 1-10
            petId=pet_id or random.randint(1000, 9999),
            quantity=quantity or random.randint(1, 5),
            shipDate=ship_date or datetime.now(timezone.utc).isoformat(),
            status=status or OrderStatus.PLACED,
            complete=complete if complete is not None else False
        )
    
    @classmethod
    def create_minimal(cls) -> "Order":
        """Create an Order with minimal data."""
        return cls(
            id=random.randint(1, 10),
            petId=random.randint(1000, 9999),
            quantity=1
        )
    
    @classmethod
    def create_with_invalid_id(cls, invalid_id: int = 0) -> "Order":
        """Create an Order with invalid ID (outside 1-10 range)."""
        return cls(
            id=invalid_id,
            petId=random.randint(1000, 9999),
            quantity=1,
            status=OrderStatus.PLACED
        )

