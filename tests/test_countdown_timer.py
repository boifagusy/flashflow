"""
Unit tests for the Countdown Timer component
"""

import unittest
import flet as ft
from src.components.countdown_timer import CountdownTimer

class TestCountdownTimer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass
    
    def test_timer_initialization(self):
        """Test that timer initializes with correct default values"""
        timer = CountdownTimer(title="Test Timer", duration=60)
        
        self.assertEqual(timer.title, "Test Timer")
        self.assertEqual(timer.duration, 60)
        self.assertEqual(timer.remaining_time, 60)
        self.assertFalse(timer.is_running)
        self.assertFalse(timer.is_paused)
    
    def test_timer_format_time(self):
        """Test time formatting function"""
        timer = CountdownTimer(title="Test Timer", duration=60)
        
        # Test seconds formatting
        self.assertEqual(timer.format_time(30), "00:30")
        self.assertEqual(timer.format_time(59), "00:59")
        
        # Test minutes formatting
        self.assertEqual(timer.format_time(60), "01:00")
        self.assertEqual(timer.format_time(120), "02:00")
        
        # Test hours formatting
        self.assertEqual(timer.format_time(3600), "01:00:00")
        self.assertEqual(timer.format_time(3661), "01:01:01")
    
    def test_timer_get_remaining_time(self):
        """Test getting remaining time"""
        timer = CountdownTimer(title="Test Timer", duration=60)
        self.assertEqual(timer.get_remaining_time(), 60)
    
    def test_timer_is_active(self):
        """Test checking if timer is active"""
        timer = CountdownTimer(title="Test Timer", duration=60)
        self.assertFalse(timer.is_active())

if __name__ == '__main__':
    unittest.main()