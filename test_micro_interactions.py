#!/usr/bin/env python3
"""
Test script for micro-interactions components
"""

from flashflow_cli.components.micro_interactions import MicroInteractions

def test_micro_interactions():
    """Test the micro-interactions component generation"""
    print("Testing Micro-Interactions Component Generation")
    print("=" * 50)
    
    # Initialize micro-interactions
    micro_interactions = MicroInteractions()
    
    # Test floating label input
    print("1. Testing Floating Label Input:")
    floating_input = micro_interactions.generate_floating_label_input(
        "email", "Email Address", "Enter your email"
    )
    print(floating_input[:100] + "..." if len(floating_input) > 100 else floating_input)
    print()
    
    # Test password field
    print("2. Testing Password Field:")
    password_field = micro_interactions.generate_password_field(
        "password", "Password", "Enter your password"
    )
    print(password_field[:100] + "..." if len(password_field) > 100 else password_field)
    print()
    
    # Test validation input
    print("3. Testing Validation Input:")
    validation_input = micro_interactions.generate_validation_input(
        "username", "Username", "text", "Enter username"
    )
    print(validation_input[:100] + "..." if len(validation_input) > 100 else validation_input)
    print()
    
    # Test loading spinner
    print("4. Testing Loading Spinner:")
    spinner = micro_interactions.generate_loading_spinner("test-spinner", "md")
    print(spinner[:100] + "..." if len(spinner) > 100 else spinner)
    print()
    
    # Test progress ring
    print("5. Testing Progress Ring:")
    progress_ring = micro_interactions.generate_progress_ring("test-ring", 100, 8)
    print(progress_ring[:100] + "..." if len(progress_ring) > 100 else progress_ring)
    print()
    
    # Test toast notification
    print("6. Testing Toast Notification:")
    toast = micro_interactions.generate_toast_notification(
        "test-toast", "This is a test message", "success"
    )
    print(toast[:100] + "..." if len(toast) > 100 else toast)
    print()
    
    # Test flash feedback
    print("7. Testing Flash Feedback:")
    flash = micro_interactions.generate_flash_feedback("test-flash", "form-section")
    print(flash[:100] + "..." if len(flash) > 100 else flash)
    print()
    
    # Test confirm dialog
    print("8. Testing Confirm Dialog:")
    dialog = micro_interactions.generate_confirm_dialog(
        "test-dialog", "Confirm Action", "Are you sure you want to proceed?"
    )
    print(dialog[:100] + "..." if len(dialog) > 100 else dialog)
    print()
    
    # Test progress bar
    print("9. Testing Progress Bar:")
    progress_bar = micro_interactions.generate_progress_bar("test-bar", 50)
    print(progress_bar[:100] + "..." if len(progress_bar) > 100 else progress_bar)
    print()
    
    # Test hover card
    print("10. Testing Hover Card:")
    card = micro_interactions.generate_hover_card("test-card", "This is card content")
    print(card[:100] + "..." if len(card) > 100 else card)
    print()
    
    # Test pulse indicator
    print("11. Testing Pulse Indicator:")
    pulse = micro_interactions.generate_pulse_indicator("test-pulse", "active")
    print(pulse[:100] + "..." if len(pulse) > 100 else pulse)
    print()
    
    # Test CSS generation
    print("12. Testing CSS Generation:")
    css = micro_interactions.generate_css()
    print(f"Generated CSS length: {len(css)} characters")
    print()
    
    # Test JavaScript generation
    print("13. Testing JavaScript Generation:")
    js = micro_interactions.generate_javascript()
    print(f"Generated JavaScript length: {len(js)} characters")
    print()
    
    print("All micro-interactions tests completed successfully!")

if __name__ == "__main__":
    test_micro_interactions()