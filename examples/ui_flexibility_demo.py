"""
UI Flexibility Demo
Demonstrates the enhanced UI flexibility features of FlashFlow
"""

import sys
import os

# Add the current directory to the path so we can import the services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flashflow_cli.services.ui_flexibility_service import UIFlexibilityService


def demo_design_tokens():
    """Demonstrate design token system"""
    print("=== Design Token System Demo ===")
    
    ui_service = UIFlexibilityService()
    
    # Get specific token values
    primary_color = ui_service.get_design_token("colors.primary.500")
    print(f"Primary color: {primary_color}")
    
    secondary_color = ui_service.get_design_token("colors.secondary.500")
    print(f"Secondary color: {secondary_color}")
    
    large_spacing = ui_service.get_design_token("spacing.xl")
    print(f"Large spacing: {large_spacing}")
    
    base_font_size = ui_service.get_design_token("typography.fontSize.base")
    print(f"Base font size: {base_font_size}")
    
    # Create a custom theme
    custom_theme = ui_service.create_custom_theme("ocean", {
        "colors": {
            "primary": {
                "500": "#0ea5e9"  # Sky blue
            },
            "secondary": {
                "500": "#06b6d4"  # Cyan
            }
        }
    })
    print(f"Custom theme primary color: {custom_theme['colors']['primary']['500']}")
    print()


def demo_css_framework_adapter():
    """Demonstrate CSS framework adapter"""
    print("=== CSS Framework Adapter Demo ===")
    
    ui_service = UIFlexibilityService()
    
    # Convert styles to Tailwind classes
    styles = {
        "padding": "lg",
        "margin": "md",
        "background": "primary.500",
        "text": "white",
        "responsive": {
            "md": {
                "padding": "xl"
            }
        }
    }
    
    # This would normally be handled internally by the renderer
    classes = ui_service.css_adapter.convert_styles_to_classes(styles)
    print(f"Converted classes: {classes}")
    print()


def demo_component_rendering():
    """Demonstrate flexible component rendering"""
    print("=== Flexible Component Rendering Demo ===")
    
    ui_service = UIFlexibilityService()
    
    # Render a hero component with enhanced props
    hero_props = {
        "title": "Welcome to FlashFlow",
        "subtitle": "The revolutionary full-stack framework",
        "cta": {
            "text": "Get Started",
            "link": "/dashboard",
            "className": "btn btn-primary"
        },
        "style": {
            "background": "gradient(135deg, token:colors.primary.500 0%, token:colors.secondary.800 100%)",
            "padding": {
                "base": "xl",
                "md": "2xl"
            },
            "text": "white"
        }
    }
    
    hero_html = ui_service.generate_flexible_component("hero", hero_props)
    print("Hero component HTML:")
    print(hero_html)
    print()
    
    # Render a button with different variants
    button_props = {
        "text": "Primary Button",
        "variant": "primary",
        "size": "lg"
    }
    
    button_html = ui_service.generate_flexible_component("button", button_props)
    print("Primary button HTML:")
    print(button_html)
    print()
    
    # Render a card with actions
    card_props = {
        "title": "Feature Card",
        "content": "This card demonstrates the flexibility of FlashFlow's UI system.",
        "actions": [
            {
                "text": "Learn More",
                "link": "/docs",
                "className": "btn btn-secondary"
            },
            {
                "text": "Try It",
                "link": "/demo",
                "className": "btn btn-primary"
            }
        ],
        "style": {
            "padding": "lg",
            "background": "white",
            "border": "neutral.200",
            "rounded": "lg",
            "shadow": "md"
        }
    }
    
    card_html = ui_service.generate_flexible_component("card", card_props)
    print("Card component HTML:")
    print(card_html)
    print()


def demo_form_rendering():
    """Demonstrate form rendering with flexibility"""
    print("=== Form Rendering Demo ===")
    
    ui_service = UIFlexibilityService()
    
    form_props = {
        "fields": [
            {
                "type": "text",
                "name": "name",
                "label": "Full Name",
                "placeholder": "Enter your full name"
            },
            {
                "type": "email",
                "name": "email",
                "label": "Email Address",
                "placeholder": "Enter your email"
            },
            {
                "type": "textarea",
                "name": "message",
                "label": "Message",
                "placeholder": "Enter your message"
            }
        ],
        "submitText": "Send Message",
        "style": {
            "max-width": "500px",
            "margin": "auto",
            "padding": "lg",
            "background": "white",
            "rounded": "md",
            "shadow": "lg"
        }
    }
    
    form_html = ui_service.generate_flexible_component("form", form_props)
    print("Form component HTML:")
    print(form_html)
    print()


def main():
    """Run all demos"""
    print("FlashFlow UI Flexibility Demo")
    print("============================")
    print()
    
    try:
        demo_design_tokens()
        demo_css_framework_adapter()
        demo_component_rendering()
        demo_form_rendering()
        
        print("All demos completed successfully!")
        print()
        print("These features enhance FlashFlow's UI flexibility by providing:")
        print("1. Design token system for consistent theming")
        print("2. CSS framework adapter for familiar styling")
        print("3. Flexible component rendering with responsive capabilities")
        print("4. Runtime theme customization")
        print("5. Enhanced .flow file syntax support")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())