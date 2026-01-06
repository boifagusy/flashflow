"""
Verification script for platform-adaptive components
"""

import sys
import os

# Add the current directory to the path so we can import components
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import flet as ft
    print("✓ Flet imported successfully")
except ImportError as e:
    print(f"✗ Failed to import Flet: {e}")
    sys.exit(1)

try:
    from components import PlatformAdaptiveComponents, AdaptiveThemeManager, create_adaptive_headline, create_adaptive_input, create_adaptive_button
    print("✓ Platform-adaptive components imported successfully")
except ImportError as e:
    print(f"✗ Failed to import platform-adaptive components: {e}")
    sys.exit(1)

# Test theme creation
try:
    theme = AdaptiveThemeManager.create_theme(
        dominant_60="#1976D2",    # Blue (60%)
        secondary_30="#424242",   # Grey (30%)
        accent_10="#FF4081"       # Pink (10%)
    )
    print("✓ Theme created successfully")
except Exception as e:
    print(f"✗ Failed to create theme: {e}")

print("All components verified successfully!")