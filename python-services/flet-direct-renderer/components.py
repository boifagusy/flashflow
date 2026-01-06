"""
FlashFlow Platform-Adaptive Components
Implements Material 3 and Cupertino design standards with automatic platform detection
"""

import flet as ft
from typing import Optional, Dict, Any


class PlatformAdaptiveComponents:
    """Platform-adaptive components that automatically switch between Material 3 and Cupertino styles"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.platform = self._detect_platform()
        
    def _detect_platform(self) -> str:
        """Detect the current platform"""
        if hasattr(self.page, 'platform'):
            if self.page.platform in [ft.PagePlatform.IOS, ft.PagePlatform.MACOS]:
                return "cupertino"
            else:
                return "material"
        else:
            # Default to material if platform detection fails
            return "material"
    
    def headline(self, text: str, level: int = 1, **kwargs) -> ft.Control:
        """
        Create a platform-adaptive headline component
        
        Args:
            text (str): Headline text
            level (int): Headline level (1-6)
            **kwargs: Additional properties for the text component
        """
        # Apply system font and typography scale
        font_family = self._get_system_font()
        
        # Define typography scale based on level
        typography_scale = {
            1: {"size": 32, "weight": ft.FontWeight.BOLD},
            2: {"size": 28, "weight": ft.FontWeight.BOLD},
            3: {"size": 24, "weight": ft.FontWeight.BOLD},
            4: {"size": 20, "weight": ft.FontWeight.BOLD},
            5: {"size": 18, "weight": ft.FontWeight.BOLD},
            6: {"size": 16, "weight": ft.FontWeight.BOLD},
        }
        
        style = typography_scale.get(level, typography_scale[1])
        style["font_family"] = font_family
        
        # Apply secondary color from theme if available
        if hasattr(self.page, 'theme') and hasattr(self.page.theme, 'color_scheme'):
            style["color"] = self.page.theme.color_scheme.secondary
        
        # Merge with any additional kwargs
        style.update(kwargs)
        
        return ft.Text(text, **style)
    
    def input_field(self, label: str, value: str = "", disabled: bool = False, **kwargs) -> ft.Control:
        """
        Create a platform-adaptive input field component
        
        Args:
            label (str): Input field label
            value (str): Initial value
            disabled (bool): Whether the field is disabled
            **kwargs: Additional properties for the input component
        """
        if self.platform == "cupertino":
            # Render Cupertino-style text field
            field = ft.CupertinoTextField(
                placeholder_text=label,
                value=value,
                disabled=disabled,
                **kwargs
            )
        else:
            # Render Material 3-style text field
            field = ft.TextField(
                label=label,
                value=value,
                disabled=disabled,
                **kwargs
            )
        
        # Apply focus state styling
        if not disabled:
            self._apply_focus_styling(field)
            
        return field
    
    def primary_button(self, text: str, disabled: bool = False, on_click=None, **kwargs) -> ft.Control:
        """
        Create a platform-adaptive primary button component
        
        Args:
            text (str): Button text
            disabled (bool): Whether the button is disabled
            on_click: Click handler
            **kwargs: Additional properties for the button component
        """
        if self.platform == "cupertino":
            # Render Cupertino-style button
            button = ft.CupertinoFilledButton(
                text=text,
                disabled=disabled,
                on_click=on_click,
                **kwargs
            )
        else:
            # Render Material 3-style elevated button
            button = ft.ElevatedButton(
                text=text,
                disabled=disabled,
                on_click=on_click,
                **kwargs
            )
        
        # Apply disabled state styling
        if disabled and hasattr(self.page.theme, 'disabled_overlay_color'):
            # The styling will be handled by Flet based on theme
            pass
            
        return button
    
    def _get_system_font(self) -> str:
        """Get the system font based on platform"""
        if self.platform == "cupertino":
            return "San Francisco"  # iOS/macOS system font
        else:
            return "Roboto"  # Android/system default
    
    def _apply_focus_styling(self, control: ft.Control):
        """Apply focus state styling to a control"""
        # Focus styling is handled by Flet based on theme
        # The accent color will be applied automatically
        pass


class AdaptiveThemeManager:
    """Manages platform-adaptive theming for FlashFlow applications"""
    
    @staticmethod
    def create_theme(dominant_60: str, secondary_30: str, accent_10: str, 
                    disabled_opacity: float = 0.45) -> ft.Theme:
        """
        Create a platform-adaptive theme with 60-30-10 color balance
        
        Args:
            dominant_60 (str): Dominant color (60%)
            secondary_30 (str): Secondary color (30%)
            accent_10 (str): Accent color (10%)
            disabled_opacity (float): Opacity for disabled states
        """
        # Create color scheme with 60-30-10 balance
        color_scheme = ft.ColorScheme(
            primary=dominant_60,
            secondary=secondary_30,
            tertiary=accent_10,
            on_primary="#FFFFFF",  # White text on primary
            on_secondary="#FFFFFF",  # White text on secondary
            on_tertiary="#000000",  # Black text on accent
        )
        
        # Create theme with Material 3 enabled
        theme = ft.Theme(
            use_material3=True,
            color_scheme=color_scheme,
            font_family="Roboto",  # Default to Roboto, will be overridden per platform
            disabled_overlay_color=ft.colors.with_opacity(disabled_opacity, "#000000"),
        )
        
        return theme


# Convenience functions for easier usage
def create_adaptive_headline(page: ft.Page, text: str, level: int = 1, **kwargs) -> ft.Control:
    """Create a platform-adaptive headline"""
    components = PlatformAdaptiveComponents(page)
    return components.headline(text, level, **kwargs)


def create_adaptive_input(page: ft.Page, label: str, value: str = "", disabled: bool = False, **kwargs) -> ft.Control:
    """Create a platform-adaptive input field"""
    components = PlatformAdaptiveComponents(page)
    return components.input_field(label, value, disabled, **kwargs)


def create_adaptive_button(page: ft.Page, text: str, disabled: bool = False, on_click=None, **kwargs) -> ft.Control:
    """Create a platform-adaptive primary button"""
    components = PlatformAdaptiveComponents(page)
    return components.primary_button(text, disabled, on_click, **kwargs)