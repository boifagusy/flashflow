"""
FlashFlow 'new' command - Create new FlashFlow project
"""

import click
import os
import json
import shutil
from pathlib import Path

@click.command()
@click.argument('project_name')
@click.option('--template', '-t', default='basic', help='Project template (basic, todo, ecommerce)')
@click.option('--author', '-a', default='', help='Project author name')
def new(project_name, template, author):
    """Create a new FlashFlow project"""
    
    # Validate project name
    if not project_name.replace('-', '').replace('_', '').isalnum():
        click.echo("❌ Project name must contain only letters, numbers, hyphens, and underscores")
        return
    
    project_path = Path.cwd() / project_name
    
    # Check if directory already exists
    if project_path.exists():
        click.echo(f"❌ Directory '{project_name}' already exists")
        return
    
    try:
        # Create project structure
        click.echo(f"🚀 Creating FlashFlow project: {project_name}")
        
        # Main directories with standardized folder structure
        project_path.mkdir()
        src_path = project_path / "src"
        src_path.mkdir()
        
        # Create all required subdirectories
        (src_path / "flows").mkdir()        # FlashFlow definition files (.flow)
        (src_path / "models").mkdir()       # Data models and database schemas
        (src_path / "components").mkdir()   # Reusable UI components
        (src_path / "pages").mkdir()        # Page definitions and layouts
        (src_path / "services").mkdir()     # Business logic and API integrations
        (src_path / "utils").mkdir()        # Utility functions and helpers
        (src_path / "assets").mkdir()       # Static assets (images, icons, fonts)
        (src_path / "config").mkdir()       # Configuration files
        (src_path / "tests").mkdir()        # Test files (.testflow and unit tests)
        
        # Create dist directory for generated code
        (project_path / "dist").mkdir()
        
        # Create flashflow.json config
        config = {
            "name": project_name,
            "version": "0.1.0",
            "description": f"FlashFlow application: {project_name}",
            "author": author or "FlashFlow Developer",
            "frameworks": {
                "backend": "laravel",
                "frontend": "react",
                "mobile": "flet",
                "database": "sqlite"
            },
            "dependencies": []
        }
        
        with open(project_path / "flashflow.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create template files based on template type
        create_template_files(project_path, template, project_name)
        
        # Create .env.example
        env_content = """# FlashFlow Environment Configuration
# Copy this file to .env and update values

# Database
DB_CONNECTION=sqlite
DB_DATABASE=./database/app.db

# App Configuration
APP_NAME="{project_name}"
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:8000

# Security
APP_KEY=
JWT_SECRET=

# External Services (Optional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
""".format(project_name=project_name)
        
        with open(project_path / ".env.example", 'w') as f:
            f.write(env_content)
        
        # Create README.md
        readme_content = f"""# {project_name}

A FlashFlow application built with single-syntax full-stack development.

## Getting Started

1. Install dependencies:
   ```bash
   flashflow install
   ```

2. Build and run the application:
   ```bash
   flashflow build
   flashflow serve --all
   ```

3. Open your browser to:
   - Web App: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin/cpanel
   - API Docs: http://localhost:8000/api/docs

## Project Structure

```
src/
├── flows/              # FlashFlow definition files (.flow)
├── models/             # Data models and database schemas
├── components/         # Reusable UI components
├── pages/              # Page definitions and layouts
├── services/           # Business logic and API integrations
├── utils/              # Utility functions and helpers
├── assets/             # Static assets (images, icons, fonts)
├── config/             # Configuration files
└── tests/              # Test files (.testflow and unit tests)
```

## FlashFlow Commands

- `flashflow build` - Generate application code
- `flashflow serve --all` - Run unified development server
- `flashflow test` - Run all tests
- `flashflow deploy` - Deploy to production

## Learn More

Visit the FlashFlow documentation for detailed guides and examples.
"""
        
        with open(project_path / "README.md", 'w') as f:
            f.write(readme_content)
        
        # Display welcome message after successful creation
        display_welcome_message(project_name, project_path)
        
    except Exception as e:
        click.echo(f"❌ Error creating project: {str(e)}")
        # Cleanup on error
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)

def display_welcome_message(project_name: str, project_path: Path):
    """Display a Laravel-style welcome message after project creation"""
    
    welcome_message = f"""
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                                                                             │
    │        ███████╗██╗      █████╗  ██████╗██╗  ██╗███████╗██╗     ██████╗      │
    │        ██╔════╝██║     ██╔══██╗██╔════╝██║  ██║██╔════╝██║     ██╔══██╗     │
    │        █████╗  ██║     ███████║██║     ███████║█████╗  ██║     ██║  ██║     │
    │        ██╔══╝  ██║     ██╔══██║██║     ██╔══██║██╔══╝  ██║     ██║  ██║     │
    │        ██║     ███████╗██║  ██║╚██████╗██║  ██║███████╗███████╗██████╔╝     │
    │        ╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝      │
    │                                                                             │
    │    🚀 FlashFlow Project '{project_name}' created successfully!              │
    │                                                                             │
    │    Next steps:                                                              │
    │    1. cd {project_name}                                                     │
    │    2. flashflow install                                                     │
    │    3. flashflow build                                                       │
    │    4. flashflow serve --all                                                 │
    │                                                                             │
    │    🌐 Visit http://localhost:8000 to see your application                   │
    │                                                                             │
    │    📚 Documentation: https://docs.flashflow.dev                            │
    │                                                                             │
    └─────────────────────────────────────────────────────────────────────────────┘
    """
    
    click.echo(welcome_message)

def create_template_files(project_path: Path, template: str, project_name: str):
    """Create template-specific .flow files with standardized structure"""
    
    src_path = project_path / "src"
    flows_path = src_path / "flows"
    pages_path = src_path / "pages"
    components_path = src_path / "components"
    models_path = src_path / "models"
    services_path = src_path / "services"
    config_path = src_path / "config"
    tests_path = src_path / "tests"
    assets_path = src_path / "assets"
    
    # Create sample files in each directory to demonstrate structure
    
    # Create app.flow as the main application definition
    template_app_flow = Path(__file__).parent / "templates" / "flows" / "app.flow"
    if template_app_flow.exists():
        # Read template and replace placeholders
        with open(template_app_flow, 'r') as f:
            app_flow_content = f.read()
        app_flow = app_flow_content.replace("{{project_name}}", project_name)
    else:
        # Fallback to hardcoded template
        app_flow = f"""# Main Application Definition for {project_name}

# App metadata
app {{
    name: "{project_name}"
    description: "A FlashFlow application built with single-syntax full-stack development"
    version: "0.1.0"
}}

# Theme configuration with platform-adaptive UI support
theme {{
    colors {{
        primary: "#3B82F6"
        secondary: "#64748B"
        success: "#10B981"
        warning: "#F59E0B"
        danger: "#EF4444"
        light: "#F8FAFC"
        dark: "#0F172A"
    }}
}}

# Landing page showcasing platform-adaptive components
page {{
    title: "Welcome to {project_name}"
    path: "/"
    body: [
        hero {{
            title: "Welcome to {project_name}"
            subtitle: "Built with FlashFlow - Single-syntax full-stack development with platform-adaptive UI"
            cta {{
                text: "Get Started"
                link: "/welcome"
            }}
        }}
        features {{
            items: [
                {{
                    title: "Fast Development"
                    description: "Build complete applications from a single .flow file"
                }}
                {{
                    title: "All Platforms"
                    description: "Web, iOS, Android, and Desktop from one codebase"
                }}
                {{
                    title: "Platform-Adaptive UI"
                    description: "Automatic Material 3 on Android/Web and Cupertino on iOS/macOS"
                }}
                {{
                    title: "Auto-Generated Backend"
                    description: "Database, API, and admin panel created automatically"
                }}
            ]
        }}
    ]
}}
"""
    
    with open(flows_path / "app.flow", 'w') as f:
        f.write(app_flow)
    
    # Copy welcome.flow template if it exists
    template_welcome_flow = Path(__file__).parent / "templates" / "flows" / "welcome.flow"
    if template_welcome_flow.exists():
        shutil.copy(template_welcome_flow, flows_path / "welcome.flow")
    else:
        # Create a default welcome.flow if template doesn't exist
        welcome_flow = """# FlashFlow Welcome Page
# This is the default welcome page for new FlashFlow projects

page Welcome:
  title: "Welcome to FlashFlow"
  path: "/"
  
  body:
    - headline:
        text: "Welcome to FlashFlow!"
        level: 1
      
    - text:
        content: "Your new FlashFlow project has been created successfully. FlashFlow is a revolutionary full-stack framework that generates complete applications from a single .flow file."
      
    - headline:
        text: "🚀 Get Started"
        level: 2
      
    - card:
        title: "1. Explore Your Project"
        content: "Check out the src/flows/ directory to see your .flow files that define your application."
      
    - card:
        title: "2. Install Dependencies"
        content: "Run flashflow install to install all required dependencies."
      
    - card:
        title: "3. Build Your App"
        content: "Use flashflow build to generate code for all platforms."
      
    - card:
        title: "4. Start Development Server"
        content: "Run flashflow serve --all to start the unified development server."
      
    - headline:
        text: "✨ Platform-Adaptive UI"
        level: 2
      
    - text:
        content: "FlashFlow includes platform-adaptive components that automatically render the correct design language based on the operating system:"
      
    - card:
        title: "Material 3"
        content: "Used for Android, Web, Windows, and Linux platforms"
      
    - card:
        title: "Cupertino"
        content: "Used for iOS and macOS platforms"
      
    - text:
        content: "This ensures your application looks and feels native on every platform without any extra effort!"
      
    - headline:
        text: "🔗 Platform Previews"
        level: 2
      
    - primary_button:
        text: "💻 Web Preview"
        action: navigate
        link: "/preview/web"
      
    - primary_button:
        text: "🤖 Android Preview"
        action: navigate
        link: "/preview/android"
      
    - primary_button:
        text: "🍎 iOS Preview"
        action: navigate
        link: "/preview/ios"
      
    - primary_button:
        text: "🖥️ Desktop Preview"
        action: navigate
        link: "/preview/desktop"
      
    - headline:
        text: "📘 Preview Mockups"
        level: 2
      
    - text:
        content: "See visual mockups of how platform-adaptive components will look on different platforms:"
      
    - button:
        text: "Web Preview Mockup"
        action: navigate
        link: "/examples/web-preview-mockup.html"
      
    - button:
        text: "Android Preview Mockup"
        action: navigate
        link: "/examples/android-preview-mockup.html"
      
    - button:
        text: "iOS Preview Mockup"
        action: navigate
        link: "/examples/ios-preview-mockup.html"
      
    - button:
        text: "Desktop Preview Mockup"
        action: navigate
        link: "/examples/desktop-preview-mockup.html"
      
    - headline:
        text: "🎓 Platform-Adaptive Demonstration"
        level: 2
      
    - text:
        content: "See a live demonstration of how platform-adaptive components work in a single .flow file:"
      
    - button:
        text: "Adaptive Components Demo"
        action: navigate
        link: "/demo"
      
    - button:
        text: "Platform-Adaptive Mockup"
        action: navigate
        link: "/platform-adaptive-mockup"
      
    - headline:
        text: "📚 Learn More"
        level: 2
      
    - text:
        content: "Visit our documentation to learn how to build amazing applications with FlashFlow:"
      
    - button:
        text: "Official Documentation"
        action: navigate
        link: "https://docs.flashflow.dev"
      
    - button:
        text: "Getting Started Guide"
        action: navigate
        link: "https://docs.flashflow.dev/getting-started"
      
    - button:
        text: "Platform-Adaptive Components Guide"
        action: navigate
        link: "https://docs.flashflow.dev/guides/platform-adaptive-components.html"
      
    - button:
        text: "Example Projects"
        action: navigate
        link: "https://docs.flashflow.dev/examples"
"""
        with open(flows_path / "welcome.flow", 'w') as f:
            f.write(welcome_flow)
    
    # Copy platform-adaptive-mockup.flow template if it exists
    template_platform_mockup = Path(__file__).parent / "templates" / "flows" / "platform-adaptive-mockup.flow"
    if template_platform_mockup.exists():
        shutil.copy(template_platform_mockup, flows_path / "platform-adaptive-mockup.flow")
    else:
        # Create a default platform-adaptive-mockup.flow if template doesn't exist
        platform_mockup = """# Platform-Adaptive UI Components Mockup
# This file demonstrates how FlashFlow's platform-adaptive components 
# automatically adjust their appearance across different platforms

page PlatformAdaptiveMockup:
  title: "Platform-Adaptive UI Mockup"
  path: "/platform-adaptive-mockup"
  
  body:
    - headline:
        text: "Platform-Adaptive UI Components"
        level: 1
      
    - text:
        content: "This page demonstrates how FlashFlow's platform-adaptive components automatically adjust their appearance based on the target platform. The same .flow file renders differently on web, Android, iOS, and desktop platforms."
      
    - headline:
        text: "How Platform Adaptation Works"
        level: 2
      
    - card:
        title: "Automatic Detection"
        content: "FlashFlow automatically detects the target platform and applies the appropriate design system:"
      
    - features:
        items:
          - title: "Web & Android & Windows & Linux"
            description: "Uses Material 3 design system with dynamic color, elevation, and rounded corners"
          - title: "iOS & macOS"
            description: "Uses Cupertino design system with translucency, focus rings, and SF Pro fonts"
          - title: "Desktop"
            description: "Automatically switches between Material 3 (Windows/Linux) and Cupertino (macOS)"
      
    - headline:
        text: "Adaptive Form Components"
        level: 2
      
    - text:
        content: "Form components automatically adapt their styling and behavior:"
      
    - input:
        label: "Username"
        value: ""
        disabled: false
      
    - input:
        label: "Email Address"
        value: ""
        disabled: false
      
    - input:
        label: "Password"
        value: ""
        disabled: false
      
    - primary_button:
        text: "Sign Up"
        disabled: false
        action: alert
        message: "This is a platform-adaptive primary button! Notice how it looks different on different platforms."
      
    - headline:
        text: "Adaptive Navigation Components"
        level: 2
      
    - text:
        content: "Navigation components adapt to platform conventions:"
      
    - button:
        text: "Standard Button"
        action: alert
        message: "This is a platform-adaptive standard button! Notice how it looks different on different platforms."
      
    - headline:
        text: "Adaptive Cards & Content"
        level: 2
      
    - text:
        content: "Content containers and cards automatically adapt their styling:"
      
    - card:
        title: "Feature Card"
        content: "This card automatically adapts its styling based on the platform. On Material 3 platforms, it has elevation and rounded corners. On Cupertino platforms, it has a more subtle appearance with appropriate borders."
      
    - features:
        items:
          - title: "Cross-Platform Compatibility"
            description: "Automatically adapts to Material 3 on Android/Web/Windows/Linux and Cupertino on iOS/macOS"
          - title: "Consistent Experience"
            description: "Maintains the same functionality while providing native look and feel"
          - title: "Easy Implementation"
            description: "Simply use the new component types in your .flow files"
      
    - headline:
        text: "Platform-Specific Examples"
        level: 2
      
    - text:
        content: "See how the same components render differently on various platforms:"
      
    - card:
        title: "Web Preview (Material 3)"
        content: "On web platforms, components use Material 3 design with dynamic color schemes, elevation, and meaningful transitions."
      
    - card:
        title: "Android Preview (Material You)"
        content: "On Android, components use Material You with personalized color schemes that adapt to your device wallpaper."
      
    - card:
        title: "iOS Preview (Cupertino)"
        content: "On iOS, components use Cupertino design with translucency effects, focus rings, and SF Pro fonts."
      
    - card:
        title: "Desktop Preview (Adaptive)"
        content: "On desktop, components automatically switch between Material 3 (Windows/Linux) and Cupertino (macOS) based on the operating system."
      
    - headline:
        text: "Try It Yourself"
        level: 2
      
    - text:
        content: "To see these components in action, run 'flashflow serve --all' and visit the platform preview links:"
      
    - button:
        text: "💻 Web Preview"
        action: navigate
        link: "/preview/web"
      
    - button:
        text: "🤖 Android Preview"
        action: navigate
        link: "/preview/android"
      
    - button:
        text: "🍎 iOS Preview"
        action: navigate
        link: "/preview/ios"
      
    - button:
        text: "🖥️ Desktop Preview"
        action: navigate
        link: "/preview/desktop"
      
    - text:
        content: "Notice how the same .flow file renders differently on each platform while maintaining the same functionality and structure."
"""
        with open(flows_path / "platform-adaptive-mockup.flow", 'w') as f:
            f.write(platform_mockup)
    
    # Create a sample page that demonstrates platform-adaptive components
    sample_adaptive_page = """# Sample Page Demonstrating Platform-Adaptive Components

page AdaptiveDemo:
  title: "Platform-Adaptive Demo"
  path: "/demo"
  
  body:
    - headline:
        text: "Platform-Adaptive Components Demo"
        level: 1
      
    - text:
        content: "This page demonstrates how FlashFlow's platform-adaptive components automatically adjust their appearance based on the target platform."
      
    - headline:
        text: "Adaptive Form Elements"
        level: 2
      
    - input:
        label: "Username"
        value: ""
        disabled: false
      
    - input:
        label: "Email Address"
        value: ""
        disabled: false
      
    - input:
        label: "Password"
        value: ""
        disabled: false
      
    - primary_button:
        text: "Sign Up"
        disabled: false
        action: navigate
        link: "/dashboard"
      
    - headline:
        text: "Standard Components Still Work"
        level: 2
      
    - text:
        content: "You can still use standard components alongside the new adaptive ones:"
      
    - button:
        text: "Standard Button"
        action: navigate
        link: "/"
      
    - card:
        title: "Feature Card"
        content: "This is a standard card component that works across all platforms."
      
    - features:
        items:
          - title: "Cross-Platform Compatibility"
            description: "Automatically adapts to Material 3 on Android/Web and Cupertino on iOS/macOS"
          - title: "Consistent Experience"
            description: "Maintains the same functionality while providing native look and feel"
          - title: "Easy Implementation"
            description: "Simply use the new component types in your .flow files"
"""
    
    with open(flows_path / "adaptive-demo.flow", 'w') as f:
        f.write(sample_adaptive_page)
    
    # Create sample model
    user_model = """# User model definition

model User {
    id: integer primary_key auto_increment
    name: string required
    email: string required unique
    password: string required
    created_at: timestamp auto
    updated_at: timestamp auto
}
"""
    
    with open(flows_path / "user.flow", 'w') as f:
        f.write(user_model)
    
    # Create sample page
    dashboard_page = f"""# Dashboard page definition

page {{
    title: "Dashboard - {project_name}"
    path: "/dashboard"
    auth_required: true
    body: [
        header {{
            title: "Dashboard"
            user_menu: true
        }}
        stats {{
            items: [
                {{
                    title: "Welcome"
                    value: "{{{{ user.name }}}}"
                }}
                {{
                    title: "Status"
                    value: "Active"
                }}
            ]
        }}
        nav {{
            items: [
                {{
                    text: "Home"
                    link: "/dashboard"
                }}
                {{
                    text: "Profile"
                    link: "/profile"
                }}
                {{
                    text: "Settings"
                    link: "/settings"
                }}
            ]
        }}
    ]
}}
"""
    
    with open(flows_path / "dashboard.flow", 'w') as f:
        f.write(dashboard_page)
    
    # Create sample component
    button_component = """# Button component definition

component Button {
    props: {
        text: string required
        onClick: function
        variant: string default:"primary"
    }
    
    render: {
        element: "button"
        attributes: {
            className: "btn btn-{variant}"
            onClick: onClick
        }
        children: text
    }
}
"""
    
    with open(flows_path / "button.flow", 'w') as f:
        f.write(button_component)
    
    # Create sample service
    auth_service = """# Authentication service definition

service AuthService {
    methods: {
        login: {
            params: {
                email: string required
                password: string required
            }
            returns: {
                user: User
                token: string
            }
        }
        
        register: {
            params: {
                name: string required
                email: string required
                password: string required
            }
            returns: {
                user: User
                token: string
            }
        }
        
        logout: {
            returns: boolean
        }
    }
}
"""
    
    with open(flows_path / "auth.flow", 'w') as f:
        f.write(auth_service)
    
    # Create a basic test file
    basic_test = f"""# Basic API Test for {project_name}

test {{
    name: "Health Check Test"
    scenario: [
        {{
            description: "Check if API is running"
            request: {{
                method: "GET"
                path: "/api/health"
            }}
            expect: {{
                status: 200
                json: {{
                    status: "ok"
                }}
            }}
        }}
    ]
}}
"""
    
    with open(tests_path / "basic.testflow", 'w') as f:
        f.write(basic_test)
    
    # Create welcome page HTML template
    welcome_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to FlashFlow</title>
    <style>
        :root {
            --primary: #3B82F6;
            --secondary: #8B5CF6;
            --dark: #1E293B;
            --light: #F8FAFC;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f0f4f8, #e2e8f0);
            color: var(--dark);
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            max-width: 800px;
            width: 90%;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin: 2rem 0;
        }
        
        .header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .content {
            padding: 2rem;
        }
        
        .section {
            margin-bottom: 2rem;
        }
        
        .section h2 {
            color: var(--primary);
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        
        .steps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .step {
            background: var(--light);
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid var(--primary);
        }
        
        .step-number {
            display: inline-block;
            background: var(--primary);
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            margin-right: 10px;
            font-weight: bold;
        }
        
        .commands {
            background: #1a1a1a;
            color: #00ff00;
            padding: 1.5rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            margin: 1.5rem 0;
            overflow-x: auto;
        }
        
        .links {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .btn {
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        
        .btn:hover {
            background: #2563eb;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .btn-secondary {
            background: var(--secondary);
        }
        
        .btn-secondary:hover {
            background: #7c3aed;
        }
        
        .footer {
            text-align: center;
            padding: 1.5rem;
            border-top: 1px solid #e2e8f0;
            color: #64748b;
            font-size: 0.9rem;
        }
        
        .highlight {
            background: #fff9db;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-weight: 500;
        }
        
        @media (max-width: 768px) {
            .header {
                padding: 2rem 1rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .content {
                padding: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to FlashFlow!</h1>
            <p>Your new project has been created successfully</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>🚀 Get Started</h2>
                <p>You've just created a new FlashFlow project. FlashFlow is a revolutionary full-stack framework that generates complete applications from a single <span class="highlight">.flow</span> file.</p>
            </div>
            
            <div class="steps">
                <div class="step">
                    <h3><span class="step-number">1</span> Explore Your Project</h3>
                    <p>Check out the <span class="highlight">src/flows/</span> directory to see your .flow files that define your application.</p>
                </div>
                
                <div class="step">
                    <h3><span class="step-number">2</span> Install Dependencies</h3>
                    <p>Run <span class="highlight">flashflow install</span> to install all required dependencies.</p>
                </div>
                
                <div class="step">
                    <h3><span class="step-number">3</span> Build Your App</h3>
                    <p>Use <span class="highlight">flashflow build</span> to generate code for all platforms.</p>
                </div>
                
                <div class="step">
                    <h3><span class="step-number">4</span> Start Development Server</h3>
                    <p>Run <span class="highlight">flashflow serve --all</span> to start the unified development server.</p>
                </div>
            </div>
            
            <div class="section">
                <h2>✨ Platform-Adaptive UI</h2>
                <p>FlashFlow now includes platform-adaptive components that automatically render the correct design language based on the operating system:</p>
                <ul style="margin-top: 1rem; padding-left: 1.5rem;">
                    <li><strong>Material 3</strong> for Android, Web, Windows, and Linux</li>
                    <li><strong>Cupertino</strong> for iOS and macOS</li>
                </ul>
                <p style="margin-top: 1rem;">This ensures your application looks and feels native on every platform without any extra effort!</p>
            </div>
            
            <div class="section">
                <h2>⚡ Essential Commands</h2>
                <div class="commands">
                    # Install dependencies<br>
                    flashflow install<br><br>
                    
                    # Generate application code<br>
                    flashflow build<br><br>
                    
                    # Run development server<br>
                    flashflow serve --all<br><br>
                    
                    # Run tests<br>
                    flashflow test<br><br>
                    
                    # Deploy to production<br>
                    flashflow deploy
                </div>
            </div>
            
            <div class="links">
                <a href="http://localhost:8000" class="btn" target="_blank">🌐 View App</a>
                <a href="http://localhost:8000/preview/web" class="btn" target="_blank">💻 Web Preview</a>
                <a href="http://localhost:8000/preview/android" class="btn" target="_blank">🤖 Android Preview</a>
                <a href="http://localhost:8000/preview/ios" class="btn" target="_blank">🍎 iOS Preview</a>
                <a href="http://localhost:8000/preview/desktop" class="btn" target="_blank">🖥️ Desktop Preview</a>
            </div>
            
            <div class="section">
                <h2>📚 Learn More</h2>
                <p>Visit our documentation to learn how to build amazing applications with FlashFlow:</p>
                <ul style="margin-top: 1rem; padding-left: 1.5rem;">
                    <li><a href="https://docs.flashflow.dev" target="_blank">Official Documentation</a></li>
                    <li><a href="https://docs.flashflow.dev/getting-started" target="_blank">Getting Started Guide</a></li>
                    <li><a href="https://docs.flashflow.dev/guides/platform-adaptive-components.html" target="_blank">Platform-Adaptive Components Guide</a></li>
                    <li><a href="https://docs.flashflow.dev/examples" target="_blank">Example Projects</a></li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>FlashFlow v0.1.0 | Build complete applications with one file</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(assets_path / "welcome.html", 'w') as f:
        f.write(welcome_html)
    
    # Create preview page HTML template
    preview_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlashFlow Preview</title>
    <style>
        :root {
            --primary: #3B82F6;
            --secondary: #8B5CF6;
            --dark: #1E293B;
            --light: #F8FAFC;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f0f4f8, #e2e8f0);
            color: var(--dark);
            line-height: 1.6;
            min-height: 100vh;
            padding: 2rem;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .header h1 {
            font-size: 2.5rem;
            color: var(--primary);
            margin-bottom: 1rem;
        }
        
        .preview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .preview-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            transition: transform 0.3s ease;
        }
        
        .preview-card:hover {
            transform: translateY(-5px);
        }
        
        .preview-header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 1.5rem;
            text-align: center;
        }
        
        .preview-content {
            padding: 1.5rem;
        }
        
        .preview-content h3 {
            margin-top: 0;
            color: var(--dark);
        }
        
        .preview-content ul {
            padding-left: 1.5rem;
        }
        
        .preview-content li {
            margin-bottom: 0.5rem;
        }
        
        .btn {
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            margin: 0.5rem;
            text-align: center;
        }
        
        .btn:hover {
            background: #2563eb;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .btn-secondary {
            background: var(--secondary);
        }
        
        .btn-secondary:hover {
            background: #7c3aed;
        }
        
        .actions {
            text-align: center;
            margin-top: 2rem;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FlashFlow Preview</h1>
            <p>See how your application looks across different platforms with automatic platform-adaptive UI</p>
        </div>
        
        <div class="preview-grid">
            <div class="preview-card">
                <div class="preview-header">
                    <h2>🌐 Web Preview</h2>
                </div>
                <div class="preview-content">
                    <h3>Web Application</h3>
                    <p>Your responsive web application with Material 3 design system.</p>
                    <ul>
                        <li>Fully responsive design</li>
                        <li>Material 3 design system</li>
                        <li>SEO optimized</li>
                        <li>PWA support</li>
                    </ul>
                    <a href="http://localhost:8000/preview/web" class="btn" target="_blank">View Web App</a>
                </div>
            </div>
            
            <div class="preview-card">
                <div class="preview-header">
                    <h2>📱 Mobile Preview</h2>
                </div>
                <div class="preview-content">
                    <h3>Mobile Applications</h3>
                    <p>Native mobile apps with platform-adaptive UI:</p>
                    <ul>
                        <li>Material 3 on Android</li>
                        <li>Cupertino on iOS</li>
                        <li>Offline support</li>
                        <li>Push notifications</li>
                    </ul>
                    <a href="http://localhost:8000/preview/android" class="btn" target="_blank">Android Preview</a>
                    <a href="http://localhost:8000/preview/ios" class="btn" target="_blank">iOS Preview</a>
                </div>
            </div>
            
            <div class="preview-card">
                <div class="preview-header">
                    <h2>🖥️ Desktop Preview</h2>
                </div>
                <div class="preview-content">
                    <h3>Desktop Application</h3>
                    <p>Cross-platform desktop application with platform-adaptive UI:</p>
                    <ul>
                        <li>Material 3 on Windows/Linux</li>
                        <li>Cupertino on macOS</li>
                        <li>Native window controls</li>
                        <li>System tray integration</li>
                    </ul>
                    <a href="http://localhost:8000/preview/desktop" class="btn" target="_blank">Desktop Preview</a>
                </div>
            </div>
        </div>
        
        <div class="actions">
            <a href="http://localhost:8000" class="btn">🌐 Launch Application</a>
            <a href="http://localhost:8000/admin/cpanel" class="btn btn-secondary">🛠️ Admin Panel</a>
            <a href="http://localhost:8000/api/docs" class="btn">📚 API Documentation</a>
        </div>
    </div>
</body>
</html>
"""
    
    with open(assets_path / "preview.html", 'w') as f:
        f.write(preview_html)
    
    # Create __init__.py files to make directories proper Python packages
    init_files = [
        models_path / "__init__.py",
        components_path / "__init__.py",
        pages_path / "__init__.py",
        services_path / "__init__.py",
        utils_path / "__init__.py",
        config_path / "__init__.py",
        tests_path / "__init__.py"
    ]
    
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write("# This file makes the directory a Python package\n")
