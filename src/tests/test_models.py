"""
Model Tests
Unit tests for the application models.
"""

import unittest
from datetime import datetime
from ..models.user import User
from ..models.post import Post

class TestUserModel(unittest.TestCase):
    """Test cases for the User model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.name, "John Doe")
        self.assertEqual(self.user.email, "john@example.com")
        self.assertTrue(self.user.is_valid())
    
    def test_user_validation(self):
        """Test user validation."""
        # Valid user
        self.assertTrue(self.user.is_valid())
        
        # Invalid user - missing name
        invalid_user = User(email="test@example.com")
        self.assertFalse(invalid_user.is_valid())
        
        # Invalid user - missing email
        invalid_user = User(name="Test User")
        self.assertFalse(invalid_user.is_valid())

class TestPostModel(unittest.TestCase):
    """Test cases for the Post model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.author = User(
            id=1,
            name="John Doe",
            email="john@example.com"
        )
        
        self.post = Post(
            id=1,
            title="Test Post",
            content="This is a test post.",
            author=self.author,
            published=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def test_post_creation(self):
        """Test post creation."""
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.author.name, "John Doe")
        self.assertTrue(self.post.is_valid())
        self.assertTrue(self.post.is_published())
    
    def test_post_validation(self):
        """Test post validation."""
        # Valid post
        self.assertTrue(self.post.is_valid())
        
        # Invalid post - missing title
        invalid_post = Post(author=self.author)
        self.assertFalse(invalid_post.is_valid())
        
        # Invalid post - missing author
        invalid_post = Post(title="Test Post")
        self.assertFalse(invalid_post.is_valid())

if __name__ == "__main__":
    unittest.main()