"""
Post Model
Defines the structure and behavior for post entities in the application.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from .user import User

@dataclass
class Post:
    """Represents a post in the system."""
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    author: Optional[User] = None
    published: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """Check if the post data is valid."""
        return bool(self.title and self.author)

    def is_published(self) -> bool:
        """Check if the post is published."""
        return self.published

    def __str__(self) -> str:
        """String representation of the post."""
        return f"Post(id={self.id}, title='{self.title}', author='{self.author.name if self.author else 'Unknown'}')"