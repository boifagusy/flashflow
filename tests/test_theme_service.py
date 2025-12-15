"""
Unit tests for the Theme Service
"""

import sys
import os
import unittest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Directly import the theme service module
import importlib.util
spec = importlib.util.spec_from_file_location("theme_service", os.path.join(os.path.dirname(__file__), "..", "src", "services", "theme_service.py"))
theme_service_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(theme_service_module)

ThemeService = theme_service_module.ThemeService
initialize_theme_service = theme_service_module.initialize_theme_service

class TestThemeService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.theme_service = ThemeService()
    
    def test_theme_service_initialization(self):
        """Test that theme service initializes with default themes"""
        self.assertIn("light", self.theme_service.themes)
        self.assertIn("dark", self.theme_service.themes)
        self.assertEqual(self.theme_service.current_theme, "light")
    
    def test_add_theme(self):
        """Test adding a new theme"""
        new_theme = {
            "primary": "#FF0000",
            "secondary": "#00FF00"
        }
        self.theme_service.add_theme("custom", new_theme)
        self.assertIn("custom", self.theme_service.themes)
        self.assertEqual(self.theme_service.themes["custom"], new_theme)
    
    def test_get_theme(self):
        """Test getting themes"""
        # Test with the actual flet colors
        light_theme = self.theme_service.get_theme("light")
        self.assertIn("primary", light_theme)
        
        # Test getting current theme
        current_theme = self.theme_service.get_theme()
        self.assertEqual(current_theme, self.theme_service.get_theme("light"))
    
    def test_set_theme(self):
        """Test setting the current theme"""
        # Test setting valid theme
        result = self.theme_service.set_theme("dark")
        self.assertTrue(result)
        self.assertEqual(self.theme_service.current_theme, "dark")
        
        # Test setting invalid theme
        result = self.theme_service.set_theme("nonexistent")
        self.assertFalse(result)
        self.assertEqual(self.theme_service.current_theme, "dark")  # Should remain unchanged
    
    def test_get_available_themes(self):
        """Test getting available themes"""
        themes = self.theme_service.get_available_themes()
        self.assertIn("light", themes)
        self.assertIn("dark", themes)
        self.assertGreaterEqual(len(themes), 2)
    
    def test_initialize_theme_service(self):
        """Test initializing theme service with custom themes"""
        custom_themes = {
            "ocean": {
                "primary": "#0000FF",
                "secondary": "#00FFFF"
            }
        }
        
        service = initialize_theme_service(custom_themes)
        self.assertIn("ocean", service.themes)
        self.assertEqual(service.themes["ocean"], custom_themes["ocean"])

if __name__ == '__main__':
    unittest.main()