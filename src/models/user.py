"""
User Model
Defines the structure and behavior for user entities in the application.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    """Represents a user in the system."""
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """Check if the user data is valid."""
        return bool(self.name and self.email)

    def __str__(self) -> str:
        """String representation of the user."""
        return f"User(id={self.id}, name='{self.name}', email='{self.email}')"