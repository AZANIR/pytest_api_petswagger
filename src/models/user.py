"""Pydantic models for User-related entities."""
import random
import string
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    """User model for pet store users."""
    id: Optional[int] = None
    username: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    userStatus: Optional[int] = None
    
    @classmethod
    def create(
        cls,
        id: Optional[int] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        phone: Optional[str] = None,
        user_status: Optional[int] = None
    ) -> "User":
        """
        Factory method to create a User instance with default test data.
        
        Args:
            id: User ID
            username: Username
            first_name: First name
            last_name: Last name
            email: Email address
            password: Password
            phone: Phone number
            user_status: User status code
            
        Returns:
            User instance with test data
        """
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        return cls(
            id=id or random.randint(10000, 99999),
            username=username or f"user_{random_suffix}",
            firstName=first_name or f"First_{random_suffix}",
            lastName=last_name or f"Last_{random_suffix}",
            email=email or f"user_{random_suffix}@example.com",
            password=password or f"pass_{random_suffix}",
            phone=phone or f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            userStatus=user_status or 1
        )
    
    @classmethod
    def create_minimal(cls, username: Optional[str] = None) -> "User":
        """Create a User with minimal data."""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return cls(
            username=username or f"user_{random_suffix}"
        )
    
    @classmethod
    def create_list(cls, count: int = 3) -> list["User"]:
        """Create a list of users for batch operations."""
        return [cls.create() for _ in range(count)]


class ApiResponse(BaseModel):
    """Generic API response model."""
    code: Optional[int] = None
    type: Optional[str] = None
    message: Optional[str] = None

