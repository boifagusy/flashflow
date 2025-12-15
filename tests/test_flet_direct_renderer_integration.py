#!/usr/bin/env python3
"""
Test script for Flet Direct Renderer integration with Laravel backend
"""

import sys
import os
from pathlib import Path

# Add the python-services directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "python-services" / "flet-direct-renderer"))

from main import FlashFlowEngine
import unittest
from unittest.mock import patch, MagicMock

class TestFlashFlowEngineIntegration(unittest.TestCase):
    """Test cases for Flet Direct Renderer integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.project_root = Path(__file__).parent.parent
        self.engine = FlashFlowEngine(str(self.project_root), "http://localhost:8000")
    
    def test_engine_initialization(self):
        """Test that the engine initializes correctly with backend URL"""
        self.assertEqual(self.engine.backend_url, "http://localhost:8000")
        self.assertTrue(self.engine.project_root.exists())
    
    @patch('main.requests.get')
    def test_api_get_request(self, mock_get):
        """Test GET API request"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = {"users": [{"id": 1, "name": "John"}]}
        mock_response.content = '{"users": [{"id": 1, "name": "John"}]}'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Make the API request
        result = self.engine._make_api_request("GET", "/api/users")
        
        # Verify the request was made
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/users",
            headers={'Content-Type': 'application/json'}
        )
        
        # Verify the result
        self.assertEqual(result, {"users": [{"id": 1, "name": "John"}]})
    
    @patch('main.requests.post')
    def test_api_post_request(self, mock_post):
        """Test POST API request"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "John", "email": "john@example.com"}
        mock_response.content = '{"id": 1, "name": "John", "email": "john@example.com"}'
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Make the API request
        data = {"name": "John", "email": "john@example.com"}
        result = self.engine._make_api_request("POST", "/api/users", data)
        
        # Verify the request was made
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/users",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Verify the result
        self.assertEqual(result, {"id": 1, "name": "John", "email": "john@example.com"})
    
    def test_component_creation_with_api_action(self):
        """Test creating a component with API action"""
        # Create a button component with API action
        component_data = {
            "component": "button",
            "text": "Get Users",
            "action": "api_call",
            "method": "GET",
            "endpoint": "/api/users"
        }
        
        # Create the component
        component = self.engine._create_component(component_data)
        
        # Verify it's an ElevatedButton
        self.assertTrue(hasattr(component, 'text'))
        self.assertEqual(component.text, "Get Users")

if __name__ == "__main__":
    unittest.main()