"""Pydantic models for Pet-related entities."""
import random
import string
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PetStatus(str, Enum):
    """Pet status in the store."""
    AVAILABLE = "available"
    PENDING = "pending"
    SOLD = "sold"


class Category(BaseModel):
    """Pet category model."""
    id: Optional[int] = None
    name: Optional[str] = None
    
    @classmethod
    def create(cls, id: Optional[int] = None, name: Optional[str] = None) -> "Category":
        """Factory method to create a Category instance."""
        return cls(
            id=id or random.randint(1, 100),
            name=name or f"category_{''.join(random.choices(string.ascii_lowercase, k=6))}"
        )


class Tag(BaseModel):
    """Pet tag model."""
    id: Optional[int] = None
    name: Optional[str] = None
    
    @classmethod
    def create(cls, id: Optional[int] = None, name: Optional[str] = None) -> "Tag":
        """Factory method to create a Tag instance."""
        return cls(
            id=id or random.randint(1, 100),
            name=name or f"tag_{''.join(random.choices(string.ascii_lowercase, k=6))}"
        )


class Pet(BaseModel):
    """Pet model with required fields validation."""
    id: Optional[int] = None
    category: Optional[Category] = None
    name: str = Field(..., description="Name of the pet (required)")
    photoUrls: list[str] = Field(..., description="Photo URLs (required)")
    tags: Optional[list[Tag]] = None
    status: Optional[PetStatus] = None
    
    @classmethod
    def create(
        cls,
        id: Optional[int] = None,
        name: Optional[str] = None,
        photo_urls: Optional[list[str]] = None,
        category: Optional[Category] = None,
        tags: Optional[list[Tag]] = None,
        status: Optional[PetStatus] = None
    ) -> "Pet":
        """
        Factory method to create a Pet instance with default test data.
        
        Args:
            id: Pet ID (auto-generated if not provided)
            name: Pet name (auto-generated if not provided)
            photo_urls: List of photo URLs (default single URL if not provided)
            category: Category instance
            tags: List of Tag instances
            status: Pet status
            
        Returns:
            Pet instance with test data
        """
        return cls(
            id=id or random.randint(1000, 9999),
            name=name or f"pet_{''.join(random.choices(string.ascii_lowercase, k=6))}",
            photoUrls=photo_urls or [f"https://example.com/photo_{random.randint(1, 100)}.jpg"],
            category=category or Category.create(),
            tags=tags or [Tag.create()],
            status=status or PetStatus.AVAILABLE
        )
    
    @classmethod
    def create_minimal(cls, name: Optional[str] = None) -> "Pet":
        """Create a Pet with only required fields."""
        return cls(
            name=name or f"pet_{''.join(random.choices(string.ascii_lowercase, k=6))}",
            photoUrls=[f"https://example.com/photo_{random.randint(1, 100)}.jpg"]
        )
    
    @classmethod
    def create_invalid_missing_name(cls) -> dict:
        """Create invalid pet data without required 'name' field."""
        return {
            "photoUrls": ["https://example.com/photo.jpg"],
            "status": "available"
        }
    
    @classmethod
    def create_invalid_missing_photo_urls(cls) -> dict:
        """Create invalid pet data without required 'photoUrls' field."""
        return {
            "name": "test_pet",
            "status": "available"
        }

