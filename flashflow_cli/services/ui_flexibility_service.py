"""
UI Flexibility Service for FlashFlow
Provides enhanced UI capabilities through design tokens, CSS framework integration, template rendering, and icon management
"""

import json
from typing import Dict, Any, List, Union, Optional
from pathlib import Path

# Import the icon service
from .icon_service import icon_service


class DesignTokenSystem:
    """Manages design tokens for consistent theming"""
    
    def __init__(self):
        self.tokens = {
            "colors": {
                "primary": {
                    "50": "#eff6ff",
                    "100": "#dbeafe",
                    "200": "#bfdbfe",
                    "300": "#93c5fd",
                    "400": "#60a5fa",
                    "500": "#3b82f6",
                    "600": "#2563eb",
                    "700": "#1d4ed8",
                    "800": "#1e40af",
                    "900": "#1e3a8a"
                },
                "secondary": {
                    "50": "#f8fafc",
                    "100": "#f1f5f9",
                    "200": "#e2e8f0",
                    "300": "#cbd5e1",
                    "400": "#94a3b8",
                    "500": "#64748b",
                    "600": "#475569",
                    "700": "#334155",
                    "800": "#1e293b",
                    "900": "#0f172a"
                },
                "success": {
                    "50": "#f0fdf4",
                    "100": "#dcfce7",
                    "200": "#bbf7d0",
                    "300": "#86efac",
                    "400": "#4ade80",
                    "500": "#22c55e",
                    "600": "#16a34a",
                    "700": "#15803d",
                    "800": "#166534",
                    "900": "#14532d"
                },
                "warning": {
                    "50": "#fffbeb",
                    "100": "#fef3c7",
                    "200": "#fde68a",
                    "300": "#fcd34d",
                    "400": "#fbbf24",
                    "500": "#f59e0b",
                    "600": "#d97706",
                    "700": "#b45309",
                    "800": "#92400e",
                    "900": "#78350f"
                },
                "danger": {
                    "50": "#fef2f2",
                    "100": "#fee2e2",
                    "200": "#fecaca",
                    "300": "#fca5a5",
                    "400": "#f87171",
                    "500": "#ef4444",
                    "600": "#dc2626",
                    "700": "#b91c1c",
                    "800": "#991b1b",
                    "900": "#7f1d1d"
                },
                "neutral": {
                    "50": "#fafafa",
                    "100": "#f5f5f5",
                    "200": "#e5e5e5",
                    "300": "#d4d4d4",
                    "400": "#a3a3a3",
                    "500": "#737373",
                    "600": "#525252",
                    "700": "#404040",
                    "800": "#262626",
                    "900": "#171717"
                }
            },
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.5rem",
                "md": "1rem",
                "lg": "1.5rem",
                "xl": "2rem",
                "2xl": "3rem",
                "3xl": "4rem"
            },
            "typography": {
                "fontFamily": {
                    "sans": "'Segoe UI', system-ui, -apple-system, sans-serif",
                    "serif": "Georgia, Cambria, serif",
                    "mono": "SFMono-Regular, Consolas, monospace"
                },
                "fontSize": {
                    "xs": "0.75rem",
                    "sm": "0.875rem",
                    "base": "1rem",
                    "lg": "1.125rem",
                    "xl": "1.25rem",
                    "2xl": "1.5rem",
                    "3xl": "1.875rem",
                    "4xl": "2.25rem",
                    "5xl": "3rem",
                    "6xl": "3.75rem",
                    "7xl": "4.5rem",
                    "8xl": "6rem",
                    "9xl": "8rem"
                },
                "fontWeight": {
                    "thin": "100",
                    "extralight": "200",
                    "light": "300",
                    "normal": "400",
                    "medium": "500",
                    "semibold": "600",
                    "bold": "700",
                    "extrabold": "800",
                    "black": "900"
                },
                "lineHeight": {
                    "none": "1",
                    "tight": "1.25",
                    "snug": "1.375",
                    "normal": "1.5",
                    "relaxed": "1.625",
                    "loose": "2"
                }
            },
            "borderRadius": {
                "none": "0",
                "sm": "0.125rem",
                "md": "0.25rem",
                "lg": "0.5rem",
                "xl": "0.75rem",
                "2xl": "1rem",
                "3xl": "1.5rem",
                "full": "9999px"
            },
            "shadow": {
                "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
                "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
                "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)",
                "none": "none"
            }
        }
    
    def get_token(self, path: str) -> Any:
        """Get a design token value by path (e.g., 'colors.primary.500')"""
        keys = path.split('.')
        value = self.tokens
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None
    
    def resolve_tokens_in_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively resolve design tokens in a dictionary"""
        resolved = {}
        for key, value in data.items():
            if isinstance(value, dict):
                resolved[key] = self.resolve_tokens_in_dict(value)
            elif isinstance(value, str) and value.startswith('token:'):
                token_path = value[6:]  # Remove 'token:' prefix
                resolved[key] = self.get_token(token_path)
            else:
                resolved[key] = value
        return resolved
    
    def create_theme(self, name: str, overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom theme based on tokens with overrides"""
        theme = self.tokens.copy()
        # Apply overrides
        for key, value in overrides.items():
            if key in theme:
                if isinstance(value, dict):
                    theme[key] = {**theme[key], **value}
                else:
                    theme[key] = value
        return theme


class CSSFrameworkAdapter:
    """Adapts UI components to different CSS frameworks"""
    
    def __init__(self, framework: str = "tailwind"):
        self.framework = framework
        self.framework_configs = {
            "tailwind": {
                "prefix": "",
                "utilities": {
                    "margin": "m",
                    "padding": "p",
                    "background": "bg",
                    "text": "text",
                    "border": "border",
                    "flex": "flex",
                    "grid": "grid",
                    "width": "w",
                    "height": "h"
                },
                "responsive_prefixes": {
                    "sm": "sm:",
                    "md": "md:",
                    "lg": "lg:",
                    "xl": "xl:",
                    "2xl": "2xl:"
                }
            },
            "bootstrap": {
                "prefix": "",
                "utilities": {
                    "margin": "m",
                    "padding": "p",
                    "background": "bg",
                    "text": "text",
                    "border": "border",
                    "flex": "d-flex",
                    "grid": "d-grid",
                    "width": "w",
                    "height": "h"
                },
                "responsive_prefixes": {
                    "sm": "sm-",
                    "md": "md-",
                    "lg": "lg-",
                    "xl": "xl-",
                    "xxl": "xxl-"
                }
            }
        }
        self.config = self.framework_configs.get(framework, self.framework_configs["tailwind"])
    
    def convert_styles_to_classes(self, styles: Dict[str, Any]) -> str:
        """Convert style dictionary to CSS framework classes"""
        classes = []
        
        for property_name, value in styles.items():
            if property_name in self.config["utilities"]:
                utility_prefix = self.config["utilities"][property_name]
                if isinstance(value, dict):
                    # Handle responsive values
                    for breakpoint, breakpoint_value in value.items():
                        if breakpoint in self.config["responsive_prefixes"]:
                            prefix = self.config["responsive_prefixes"][breakpoint]
                            classes.append(f"{prefix}{utility_prefix}-{breakpoint_value}")
                        else:
                            classes.append(f"{utility_prefix}-{breakpoint_value}")
                else:
                    classes.append(f"{utility_prefix}-{value}")
            else:
                # Handle direct class names
                classes.append(str(value))
        
        return " ".join(classes)


class TemplateRenderer:
    """Renders UI components using templates with enhanced flexibility"""
    
    def __init__(self):
        self.design_tokens = DesignTokenSystem()
        self.css_adapter = CSSFrameworkAdapter()
        self.icon_service = icon_service  # Add icon service reference
    
    def render_component(self, component_type: str, props: Dict[str, Any]) -> str:
        """Render a component with enhanced flexibility"""
        # Resolve design tokens in props
        resolved_props = self.design_tokens.resolve_tokens_in_dict(props)
        
        # Convert style properties to CSS classes
        if "style" in resolved_props:
            classes = self.css_adapter.convert_styles_to_classes(resolved_props["style"])
            if "className" in resolved_props:
                resolved_props["className"] = f"{resolved_props['className']} {classes}"
            else:
                resolved_props["className"] = classes
        
        # Render based on component type
        if component_type == "hero":
            return self._render_hero(resolved_props)
        elif component_type == "button":
            return self._render_button(resolved_props)
        elif component_type == "card":
            return self._render_card(resolved_props)
        elif component_type == "form":
            return self._render_form(resolved_props)
        else:
            return self._render_generic_component(component_type, resolved_props)
    
    def _render_hero(self, props: Dict[str, Any]) -> str:
        """Render a hero component"""
        title = props.get("title", "")
        subtitle = props.get("subtitle", "")
        cta = props.get("cta", {})
        class_name = props.get("className", "hero-section")
        
        cta_html = ""
        if cta:
            cta_text = cta.get("text", "Get Started")
            cta_link = cta.get("link", "#")
            cta_class = cta.get("className", "btn btn-primary")
            cta_html = f'<a href="{cta_link}" class="{cta_class}">{cta_text}</a>'
        
        return f"""
        <div class="{class_name}">
            <h1 class="hero-title">{title}</h1>
            <p class="hero-subtitle">{subtitle}</p>
            {cta_html}
        </div>
        """
    
    def _render_button(self, props: Dict[str, Any]) -> str:
        """Render a button component with icon support"""
        text = props.get("text", "Button")
        variant = props.get("variant", "primary")
        size = props.get("size", "md")
        icon = props.get("icon")  # Get icon property
        icon_position = props.get("iconPosition", "left")  # Icon position (left/right)
        class_name = props.get("className", "")
        
        # Map variants to classes
        variant_classes = {
            "primary": "bg-primary-500 hover:bg-primary-600 text-white",
            "secondary": "bg-secondary-500 hover:bg-secondary-600 text-white",
            "success": "bg-success-500 hover:bg-success-600 text-white",
            "warning": "bg-warning-500 hover:bg-warning-600 text-white",
            "danger": "bg-danger-500 hover:bg-danger-600 text-white",
            "outline": "border border-primary-500 text-primary-500 hover:bg-primary-50"
        }
        
        # Map sizes to classes
        size_classes = {
            "sm": "px-3 py-1.5 text-sm",
            "md": "px-4 py-2 text-base",
            "lg": "px-6 py-3 text-lg"
        }
        
        button_classes = f"btn {variant_classes.get(variant, variant_classes['primary'])} {size_classes.get(size, size_classes['md'])} {class_name}"
        
        # Add icon if specified
        if icon:
            icon_html = self._render_icon(icon)
            if icon_position == "left":
                return f'<button class="{button_classes}">{icon_html} {text}</button>'
            else:
                return f'<button class="{button_classes}">{text} {icon_html}</button>'
        else:
            return f'<button class="{button_classes}">{text}</button>'
    
    def _render_card(self, props: Dict[str, Any]) -> str:
        """Render a card component with icon support"""
        title = props.get("title", "")
        content = props.get("content", "")
        actions = props.get("actions", [])
        icon = props.get("icon")  # Get icon property for card
        class_name = props.get("className", "card")
        
        # Add icon to title if specified
        title_html = f"<h3 class=\"card-title\">{title}</h3>"
        if icon:
            icon_html = self._render_icon(icon)
            title_html = f"<h3 class=\"card-title\">{icon_html} {title}</h3>"
        
        actions_html = ""
        if actions:
            actions_html = '<div class="card-actions">'
            for action in actions:
                action_text = action.get("text", "Action")
                action_link = action.get("link", "#")
                action_class = action.get("className", "btn btn-secondary")
                action_icon = action.get("icon")  # Get icon for action
                
                # Add icon to action if specified
                if action_icon:
                    action_icon_html = self._render_icon(action_icon)
                    actions_html += f'<a href="{action_link}" class="{action_class}">{action_icon_html} {action_text}</a>'
                else:
                    actions_html += f'<a href="{action_link}" class="{action_class}">{action_text}</a>'
            actions_html += '</div>'
        
        return f"""
        <div class="{class_name}">
            {title_html}
            <div class="card-content">{content}</div>
            {actions_html}
        </div>
        """
    
    def _render_form(self, props: Dict[str, Any]) -> str:
        """Render a form component"""
        fields = props.get("fields", [])
        submit_text = props.get("submitText", "Submit")
        class_name = props.get("className", "form")
        
        fields_html = ""
        for field in fields:
            field_type = field.get("type", "text")
            field_name = field.get("name", "")
            field_label = field.get("label", "")
            field_placeholder = field.get("placeholder", "")
            field_icon = field.get("icon")  # Get icon for field
            
            # Add icon to label if specified
            label_html = f'<label for="{field_name}">{field_label}</label>'
            if field_icon:
                icon_html = self._render_icon(field_icon)
                label_html = f'<label for="{field_name}">{icon_html} {field_label}</label>'
            
            if field_type == "textarea":
                fields_html += f"""
                <div class="form-group">
                    {label_html}
                    <textarea 
                        id="{field_name}" 
                        name="{field_name}" 
                        placeholder="{field_placeholder}"
                        class="form-control"
                    ></textarea>
                </div>
                """
            else:
                fields_html += f"""
                <div class="form-group">
                    {label_html}
                    <input 
                        type="{field_type}" 
                        id="{field_name}" 
                        name="{field_name}" 
                        placeholder="{field_placeholder}"
                        class="form-control"
                    />
                </div>
                """
        
        return f"""
        <form class="{class_name}">
            {fields_html}
            <button type="submit" class="btn btn-primary">{submit_text}</button>
        </form>
        """
    
    def _render_generic_component(self, component_type: str, props: Dict[str, Any]) -> str:
        """Render a generic component"""
        class_name = props.get("className", f"component-{component_type}")
        content = props.get("content", "")
        
        return f'<div class="{class_name}">{content}</div>'
    
    def _render_icon(self, icon_spec: str) -> str:
        """Render an icon based on specification"""
        # Handle different icon specification formats
        if isinstance(icon_spec, str):
            # Simple icon name (e.g., "home")
            if ":" in icon_spec:
                # Format: "pack:icon_name" (e.g., "font-awesome:home")
                pack_name, icon_name = icon_spec.split(":", 1)
                icon_class = self.icon_service.get_prefixed_icon(icon_name, pack_name)
            else:
                # Use default pack
                icon_class = self.icon_service.get_prefixed_icon(icon_spec)
            
            if icon_class:
                return f'<i class="{icon_class}"></i>'
            else:
                # Fallback to simple text
                return f'<i>{icon_spec}</i>'
        else:
            # Return empty string for invalid icon spec
            return ""


class UIFlexibilityService:
    """Main service for UI flexibility features"""
    
    def __init__(self):
        self.design_tokens = DesignTokenSystem()
        self.css_adapter = CSSFrameworkAdapter()
        self.template_renderer = TemplateRenderer()
        self.icon_service = icon_service  # Add icon service reference
    
    def enhance_flow_syntax(self, flow_content: str) -> str:
        """Enhance .flow syntax with flexibility features"""
        # This would parse and enhance .flow files with new syntax features
        # For now, we'll just return the content as-is
        return flow_content
    
    def generate_flexible_component(self, component_type: str, props: Dict[str, Any]) -> str:
        """Generate a flexible UI component"""
        return self.template_renderer.render_component(component_type, props)
    
    def create_custom_theme(self, name: str, overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom theme"""
        return self.design_tokens.create_theme(name, overrides)
    
    def get_design_token(self, path: str) -> str:
        """Get a design token value"""
        return self.design_tokens.get_token(path)
    
    def get_icon(self, icon_name: str, pack_name: Optional[str] = None) -> str:
        """Get an icon from a specific pack or the default pack"""
        # Handle None case explicitly to satisfy type checker
        if pack_name is None:
            icon = self.icon_service.get_prefixed_icon(icon_name)
        else:
            icon = self.icon_service.get_prefixed_icon(icon_name, pack_name)
        return icon if icon is not None else ""
    
    def get_available_icon_packs(self) -> List[str]:
        """Get list of available icon pack names"""
        return self.icon_service.get_available_packs()
    
    def set_default_icon_pack(self, pack_name: str) -> bool:
        """Set the default icon pack"""
        return self.icon_service.set_default_pack(pack_name)


# Global instance
ui_flexibility_service = UIFlexibilityService()