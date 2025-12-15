"""
Utility Helpers
Common utility functions used throughout the application.
"""

from datetime import datetime
from typing import Any, Optional

def format_date(date: Optional[datetime]) -> str:
    """Format a datetime object as a string."""
    if date:
        return date.strftime("%B %d, %Y")
    return "Unknown date"

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length and add ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def is_valid_email(email: str) -> bool:
    """Simple email validation."""
    return "@" in email and "." in email

def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    return text.lower().replace(" ", "-").replace("_", "-")

def get_initials(name: str) -> str:
    """Get initials from a name."""
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    elif parts:
        return parts[0][0].upper()
    return ""

def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary with a default."""
    try:
        return dictionary[key]
    except KeyError:
        return default