"""
Post Service
Handles business logic related to posts in the application.
"""

from typing import List, Optional
from ..models.post import Post
from ..models.user import User

class PostService:
    """Service for managing posts."""
    
    def __init__(self):
        # In a real application, this would connect to a database
        self.posts: List[Post] = []
        self.next_id = 1
    
    def create_post(self, title: str, content: str, author: User, published: bool = False) -> Post:
        """Create a new post."""
        post = Post(
            id=self.next_id,
            title=title,
            content=content,
            author=author,
            published=published
        )
        self.next_id += 1
        self.posts.append(post)
        return post
    
    def get_all_posts(self) -> List[Post]:
        """Get all posts."""
        return self.posts
    
    def get_published_posts(self) -> List[Post]:
        """Get only published posts."""
        return [post for post in self.posts if post.is_published()]
    
    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        """Get a post by its ID."""
        for post in self.posts:
            if post.id == post_id:
                return post
        return None
    
    def update_post(self, post_id: int, title: str = None, content: str = None, published: bool = None) -> Optional[Post]:
        """Update a post."""
        post = self.get_post_by_id(post_id)
        if post:
            if title is not None:
                post.title = title
            if content is not None:
                post.content = content
            if published is not None:
                post.published = published
        return post
    
    def delete_post(self, post_id: int) -> bool:
        """Delete a post."""
        post = self.get_post_by_id(post_id)
        if post:
            self.posts.remove(post)
            return True
        return False

# Global instance of the service
post_service = PostService()