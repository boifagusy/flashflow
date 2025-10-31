# UI Flexibility Guide

FlashFlow's enhanced UI flexibility features provide developers with powerful tools to create beautiful, consistent, and customizable user interfaces across all platforms. This guide covers the design token system, CSS framework integration, and flexible component rendering capabilities.

## Table of Contents

1. [Introduction](#introduction)
2. [Design Token System](#design-token-system)
3. [CSS Framework Integration](#css-framework-integration)
4. [Flexible Component Rendering](#flexible-component-rendering)
5. [Runtime Theme Customization](#runtime-theme-customization)
6. [Enhanced .flow Syntax](#enhanced-flow-syntax)
7. [Responsive Design](#responsive-design)
8. [Examples](#examples)

## Introduction

FlashFlow's UI flexibility system enhances the framework's ability to create consistent, beautiful interfaces across web, mobile, and desktop platforms. The system combines design tokens, CSS framework integration, and flexible component rendering to provide maximum customization while maintaining the simplicity of the .flow syntax.

## Design Token System

Design tokens are the foundation of FlashFlow's consistent theming system. They provide a centralized way to manage design decisions like colors, spacing, typography, and more.

### Available Design Tokens

#### Colors

FlashFlow provides a comprehensive color system with predefined palettes for primary, secondary, success, warning, danger, and neutral colors. Each palette has 10 shades (50-900).

```flow
// Example usage of color tokens
button {
    text: "Primary Button"
    style: {
        background: "token:colors.primary.500"
        text: "token:colors.neutral.50"
    }
}
```

Available color tokens:
- `colors.primary` - Main brand color
- `colors.secondary` - Supporting brand color
- `colors.success` - Success state color
- `colors.warning` - Warning state color
- `colors.danger` - Error/danger state color
- `colors.neutral` - Neutral/grayscale colors

#### Spacing

Consistent spacing is crucial for creating harmonious layouts. FlashFlow provides a scale of spacing tokens from extra small to extra large.

```flow
card {
    title: "Card with Custom Spacing"
    style: {
        padding: "token:spacing.xl"
        margin: "token:spacing.lg"
    }
}
```

Available spacing tokens:
- `spacing.xs` - 0.25rem
- `spacing.sm` - 0.5rem
- `spacing.md` - 1rem
- `spacing.lg` - 1.5rem
- `spacing.xl` - 2rem
- `spacing.2xl` - 3rem
- `spacing.3xl` - 4rem

#### Typography

Typography tokens ensure consistent text styling across your application.

```flow
text {
    content: "Large Heading"
    style: {
        font-size: "token:typography.fontSize.3xl"
        font-weight: "token:typography.fontWeight.bold"
    }
}
```

Available typography tokens:
- `typography.fontFamily.sans` - System UI fonts
- `typography.fontFamily.serif` - Serif fonts
- `typography.fontFamily.mono` - Monospace fonts
- `typography.fontSize` - Scale from xs to 9xl
- `typography.fontWeight` - From thin to black
- `typography.lineHeight` - From none to loose

#### Border Radius

Border radius tokens provide consistent corner styling.

```flow
card {
    title: "Rounded Card"
    style: {
        border-radius: "token:borderRadius.xl"
    }
}
```

Available border radius tokens:
- `borderRadius.none` - 0
- `borderRadius.sm` - 0.125rem
- `borderRadius.md` - 0.25rem
- `borderRadius.lg` - 0.5rem
- `borderRadius.xl` - 0.75rem
- `borderRadius.2xl` - 1rem
- `borderRadius.3xl` - 1.5rem
- `borderRadius.full` - 9999px

#### Shadows

Shadow tokens provide consistent depth and elevation effects.

```flow
card {
    title: "Card with Shadow"
    style: {
        box-shadow: "token:shadow.lg"
    }
}
```

Available shadow tokens:
- `shadow.sm` - Subtle shadow
- `shadow.md` - Medium shadow
- `shadow.lg` - Large shadow
- `shadow.xl` - Extra large shadow
- `shadow.2xl` - Double extra large shadow
- `shadow.inner` - Inset shadow
- `shadow.none` - No shadow

### Creating Custom Themes

You can create custom themes by overriding design tokens. This is particularly useful for branding or creating dark/light theme variants.

```python
# In your Python code
from flashflow_cli.services.ui_flexibility_service import ui_flexibility_service

# Create a custom theme
custom_theme = ui_flexibility_service.create_custom_theme("ocean", {
    "colors": {
        "primary": {
            "500": "#0ea5e9"  # Sky blue instead of default
        }
    }
})
```

## CSS Framework Integration

FlashFlow supports popular CSS frameworks like Tailwind CSS and Bootstrap, allowing you to use familiar utility classes in your .flow files.

### Tailwind CSS Integration

Tailwind CSS is the default CSS framework in FlashFlow. You can use Tailwind utility classes directly in your style properties.

```flow
button {
    text: "Tailwind Styled Button"
    style: {
        padding: "md"
        background: "blue-500"
        text: "white"
        rounded: "lg"
        hover: "bg-blue-600"
    }
}
```

### Bootstrap Integration

You can also use Bootstrap utility classes by configuring the CSS framework adapter.

```flow
button {
    text: "Bootstrap Styled Button"
    style: {
        "btn": "",
        "btn-primary": "",
        "btn-lg": ""
    }
}
```

### Responsive Prefixes

Both frameworks support responsive design through breakpoint prefixes.

```flow
card {
    title: "Responsive Card"
    style: {
        padding: {
            base: "md"
            md: "lg"
            lg: "xl"
        }
        background: "white"
    }
}
```

## Flexible Component Rendering

FlashFlow's flexible component rendering system allows you to create rich, customizable UI components with enhanced properties.

### Hero Component

The hero component is perfect for landing pages and section headers.

```flow
hero {
    title: "Welcome to FlashFlow"
    subtitle: "The revolutionary full-stack framework"
    
    cta: {
        text: "Get Started"
        link: "/dashboard"
    }
    
    style: {
        background: "gradient(135deg, token:colors.primary.500 0%, token:colors.secondary.800 100%)"
        padding: {
            base: "xl"
            md: "2xl"
        }
        text: "white"
    }
}
```

### Button Component

Buttons support multiple variants and sizes for different use cases.

```flow
button {
    text: "Primary Button"
    variant: "primary"
    size: "lg"
    
    style: {
        margin: "md"
    }
}
```

Available button variants:
- `primary` - Main action buttons
- `secondary` - Secondary actions
- `success` - Success actions
- `warning` - Warning actions
- `danger` - Destructive actions
- `outline` - Outlined buttons

Available button sizes:
- `sm` - Small buttons
- `md` - Medium (default) buttons
- `lg` - Large buttons

### Card Component

Cards are versatile containers for content.

```flow
card {
    title: "Feature Card"
    content: "This card demonstrates the flexibility of FlashFlow's UI system."
    
    actions: [
        {
            text: "Learn More"
            link: "/docs"
        },
        {
            text: "Try It"
            link: "/demo"
        }
    ]
    
    style: {
        padding: "lg"
        background: "white"
        border: "neutral.200"
        rounded: "lg"
        shadow: "md"
    }
}
```

### Form Component

Forms support various input types and flexible layouts.

```flow
form {
    fields: [
        {
            type: "text"
            name: "name"
            label: "Full Name"
            placeholder: "Enter your full name"
        },
        {
            type: "email"
            name: "email"
            label: "Email Address"
            placeholder: "Enter your email"
        },
        {
            type: "textarea"
            name: "message"
            label: "Message"
            placeholder: "Enter your message"
        }
    ]
    
    submitText: "Send Message"
    
    style: {
        max-width: "500px"
        margin: "auto"
        padding: "lg"
        background: "white"
        rounded: "md"
        shadow: "lg"
    }
}
```

## Runtime Theme Customization

FlashFlow provides APIs for runtime theme switching, allowing users to change themes without reloading the application.

### Theme API Endpoints

FlashFlow's development server includes RESTful API endpoints for theme management:

- `GET /api/ui/themes` - List available themes
- `GET /api/ui/themes/{theme_name}` - Get theme details
- `GET /api/ui/tokens` - List available design tokens
- `GET /api/ui/tokens/{token_path}` - Get specific token value

### Switching Themes

You can switch themes dynamically using JavaScript in your web applications:

```javascript
// Switch to dark theme
fetch('/api/ui/themes/dark')
    .then(response => response.json())
    .then(theme => {
        // Apply theme to your application
        document.body.className = theme.name;
    });
```

## Enhanced .flow Syntax

FlashFlow's enhanced .flow syntax provides more expressive ways to define UI components and their properties.

### Nested Properties

You can define nested properties for more complex styling:

```flow
hero {
    title: "Gradient Background"
    style: {
        background: {
            type: "gradient"
            direction: "135deg"
            colors: [
                "token:colors.primary.500",
                "token:colors.secondary.800"
            ]
        }
        padding: "xl"
    }
}
```

### Token References

Reference design tokens directly in your .flow files using the `token:` prefix:

```flow
button {
    text: "Themed Button"
    style: {
        background: "token:colors.primary.500"
        text: "token:colors.neutral.50"
        padding: "token:spacing.md"
        border-radius: "token:borderRadius.md"
    }
}
```

### Component Composition

Compose complex UI by combining multiple components:

```flow
section {
    components: [
        {
            type: "hero"
            title: "Welcome"
            subtitle: "This is a composed section"
        },
        {
            type: "card"
            title: "Feature 1"
            content: "Description of feature 1"
        },
        {
            type: "card"
            title: "Feature 2"
            content: "Description of feature 2"
        }
    ]
    
    style: {
        display: "flex"
        flex-direction: "column"
        gap: "token:spacing.xl"
    }
}
```

## Responsive Design

FlashFlow's responsive design capabilities allow you to create adaptive layouts that work on all device sizes.

### Breakpoint System

FlashFlow uses a standard breakpoint system based on common device sizes:

- `sm` - Small devices (640px and up)
- `md` - Medium devices (768px and up)
- `lg` - Large devices (1024px and up)
- `xl` - Extra large devices (1280px and up)
- `2xl` - 2X large devices (1536px and up)

### Responsive Properties

Apply different values for different breakpoints using object notation:

```flow
card {
    title: "Responsive Card"
    style: {
        padding: {
            base: "md"
            md: "lg"
            lg: "xl"
        }
        margin: {
            base: "sm"
            lg: "md"
        }
        font-size: {
            base: "base"
            md: "lg"
            xl: "xl"
        }
    }
}
```

### Grid Layouts

Create responsive grid layouts using CSS grid or flexbox utilities:

```flow
grid {
    columns: {
        base: 1
        md: 2
        lg: 3
    }
    
    gap: "md"
    
    items: [
        { type: "card", title: "Item 1" },
        { type: "card", title: "Item 2" },
        { type: "card", title: "Item 3" }
    ]
}
```

## Examples

### Complete Landing Page

Here's a complete example of a landing page using FlashFlow's UI flexibility features:

```flow
page Landing {
    title: "FlashFlow - Revolutionary Full-Stack Framework"
    route: "/"
    
    components: [
        {
            type: "hero"
            title: "Build Amazing Apps with a Single Syntax"
            subtitle: "FlashFlow generates complete web, mobile, desktop, and backend applications from .flow files"
            
            cta: {
                text: "Get Started"
                link: "/dashboard"
            }
            
            style: {
                background: "gradient(135deg, token:colors.primary.500 0%, token:colors.secondary.800 100%)"
                padding: {
                    base: "xl"
                    md: "2xl"
                }
                text: "white"
                text-align: "center"
            }
        },
        
        {
            type: "grid"
            columns: {
                base: 1
                md: 3
            }
            gap: "lg"
            padding: "xl"
            
            items: [
                {
                    type: "card"
                    title: "Single Syntax"
                    content: "Define your entire application with one simple .flow file syntax"
                    style: {
                        text-align: "center"
                    }
                },
                {
                    type: "card"
                    title: "Cross-Platform"
                    content: "Generate web, mobile, desktop, and backend code from one codebase"
                    style: {
                        text-align: "center"
                    }
                },
                {
                    type: "card"
                    title: "AI-Powered"
                    content: "Built-in AI features for smart forms, automation, and more"
                    style: {
                        text-align: "center"
                    }
                }
            ]
        },
        
        {
            type: "form"
            fields: [
                {
                    type: "text"
                    name: "name"
                    label: "Full Name"
                    placeholder: "Enter your name"
                },
                {
                    type: "email"
                    name: "email"
                    label: "Email Address"
                    placeholder: "Enter your email"
                }
            ]
            submitText: "Sign Up for Updates"
            style: {
                max-width: "600px"
                margin: "auto"
                padding: "xl"
                background: "token:colors.neutral.50"
                rounded: "lg"
            }
        }
    ]
}
```

### Dark Theme Implementation

Here's how to implement a dark theme using design tokens:

```flow
// In your .flow file
button {
    text: "Dark Theme Button"
    style: {
        background: "token:colors.primary.600"
        text: "token:colors.neutral.100"
        padding: "token:spacing.md"
        border-radius: "token:borderRadius.md"
        border: "token:colors.neutral.700"
    }
}
```

```python
# In your Python code for theme switching
from flashflow_cli.services.ui_flexibility_service import ui_flexibility_service

# Create dark theme
dark_theme = ui_flexibility_service.create_custom_theme("dark", {
    "colors": {
        "primary": {
            "50": "#172554",
            "100": "#1e3a8a",
            "200": "#1d4ed8",
            "300": "#2563eb",
            "400": "#3b82f6",
            "500": "#60a5fa",
            "600": "#93c5fd",
            "700": "#bfdbfe",
            "800": "#dbeafe",
            "900": "#eff6ff"
        },
        "neutral": {
            "50": "#0f172a",
            "100": "#1e293b",
            "200": "#334155",
            "300": "#475569",
            "400": "#64748b",
            "500": "#94a3b8",
            "600": "#cbd5e1",
            "700": "#e2e8f0",
            "800": "#f1f5f9",
            "900": "#f8fafc"
        }
    }
})
```

## Conclusion

FlashFlow's UI flexibility features provide a powerful yet simple way to create beautiful, consistent user interfaces across all platforms. By combining design tokens, CSS framework integration, and flexible component rendering, you can build applications that look great and are easy to maintain. The enhanced .flow syntax and runtime theme customization capabilities make it easy to create dynamic, responsive applications that adapt to user preferences and device constraints.