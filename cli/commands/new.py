"""
FlashFlow 'new' command - Create new FlashFlow project
"""

import click
import os
import json
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
        
        # Main directories
        project_path.mkdir()
        (project_path / "src").mkdir()
        (project_path / "src" / "flows").mkdir()
        (project_path / "src" / "components").mkdir()
        (project_path / "src" / "tests").mkdir()
        (project_path / "src" / "models").mkdir()
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
   flashflow install core
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

- `src/flows/` - FlashFlow definition files (.flow)
- `src/tests/` - Test files (.testflow)
- `dist/` - Generated application code
- `flashflow.json` - Project configuration

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
    │    2. flashflow install core                                                │
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
    """Create template-specific .flow files"""
    
    flows_path = project_path / "src" / "flows"
    
    if template == "todo":
        # Create todo.flow - the example from documentation
        todo_flow = """# FlashFlow Todo Application
# This demonstrates the power of single-syntax development

model:
  name: "Todo"
  fields:
    - name: "task_name"
      type: "string"
      required: true
    - name: "is_completed"
      type: "boolean" 
      default: false
    - name: "created_at"
      type: "timestamp"
      auto: true

page:
  title: "My Todo List"
  path: "/todos"
  body:
    - component: "list"
      data_source: "Todo"
      item_template:
        - component: "checkbox"
          label: "{{ task_name }}"
          checked: "{{ is_completed }}"
          action: "toggle_todo"
        - component: "button"
          label: "Delete"
          action: "delete_todo"
          style:
            color: "danger"
    - component: "form"
      action: "create_todo"
      fields:
        - name: "task_name"
          type: "text"
          placeholder: "What needs to be done?"
          required: true
      button_text: "Add Todo"

endpoint:
  path: "/api/todos"
  method: "GET"
  handler:
    action: "list_records"
    model: "Todo"

endpoint:
  path: "/api/todos"
  method: "POST"
  handler:
    action: "create_record"
    model: "Todo"
    values:
      task_name: "{{ request.body.task_name }}"

endpoint:
  path: "/api/todos/:id"
  method: "PUT"
  handler:
    action: "update_record"
    model: "Todo"
    values:
      is_completed: "{{ request.body.is_completed }}"

endpoint:
  path: "/api/todos/:id"
  method: "DELETE"
  handler:
    action: "delete_record"
    model: "Todo"
"""
        
        with open(flows_path / "todo.flow", 'w') as f:
            f.write(todo_flow)
    
    # Always create basic template files
    
    # landing-page.flow
    landing_flow = f"""# Landing Page Configuration

page:
  title: "{project_name}"
  path: "/"
  meta:
    description: "Welcome to {project_name} - Built with FlashFlow"
  body:
    - component: "hero"
      title: "Welcome to {project_name}"
      subtitle: "Built with FlashFlow - Single-syntax full-stack development"
      cta:
        text: "Get Started"
        link: "/dashboard"
    - component: "features"
      items:
        - title: "Fast Development"
          description: "Build complete applications from a single .flow file"
        - title: "All Platforms"
          description: "Web, iOS, Android, and PWA from one codebase"
        - title: "Auto-Generated Backend"
          description: "Database, API, and admin panel created automatically"
"""
    
    with open(flows_path / "landing-page.flow", 'w') as f:
        f.write(landing_flow)
    
    # dashboard.flow
    dashboard_flow = f"""# User Dashboard

page:
  title: "Dashboard - {project_name}"
  path: "/dashboard"
  auth_required: true
  body:
    - component: "header"
      title: "Dashboard"
      user_menu: true
    - component: "stats"
      items:
        - title: "Welcome"
          value: "{{ user.name }}"
        - title: "Status"
          value: "Active"
    - component: "nav"
      items:
        - text: "Home"
          link: "/dashboard"
        - text: "Profile"
          link: "/profile"
        - text: "Settings"
          link: "/settings"
"""
    
    with open(flows_path / "dashboard.flow", 'w') as f:
        f.write(dashboard_flow)
    
    # auth.flow
    auth_flow = """# Authentication Configuration

authentication:
  model: "User"
  login:
    fields: ["email", "password"]
    form_component: true
    redirect_after: "/dashboard"
  register:
    fields: ["name", "email", "password"]
    form_component: true
    redirect_after: "/dashboard"
  password_reset:
    form_component: true
  social_login:
    providers: ["google", "facebook"]

model:
  name: "User"
  fields:
    - name: "name"
      type: "string"
      required: true
    - name: "email"
      type: "string"
      unique: true
      required: true
    - name: "password"
      type: "password"
      required: true
    - name: "email_verified_at"
      type: "timestamp"
    - name: "created_at"
      type: "timestamp"
      auto: true
    - name: "updated_at"
      type: "timestamp"
      auto: true
"""
    
    with open(flows_path / "auth.flow", 'w') as f:
        f.write(auth_flow)
    
    # theme.flow
    theme_flow = f"""# Theme Configuration for {project_name}

theme:
  colors:
    primary: "#3B82F6"
    secondary: "#64748B"
    success: "#10B981"
    warning: "#F59E0B"
    danger: "#EF4444"
    light: "#F8FAFC"
    dark: "#0F172A"
  
  typography:
    font_family: "Inter, sans-serif"
    font_sizes:
      xs: "0.75rem"
      sm: "0.875rem"
      base: "1rem"
      lg: "1.125rem"
      xl: "1.25rem"
      "2xl": "1.5rem"
      "3xl": "1.875rem"
  
  spacing:
    xs: "0.25rem"
    sm: "0.5rem"
    md: "1rem"
    lg: "1.5rem"
    xl: "3rem"
  
  components:
    button:
      border_radius: "0.375rem"
      padding: "0.5rem 1rem"
    form:
      border_radius: "0.375rem"
      border_color: "#D1D5DB"
"""
    
    with open(flows_path / "theme.flow", 'w') as f:
        f.write(theme_flow)
    
    # Create a basic test file
    tests_path = project_path / "src" / "tests"
    basic_test = f"""# Basic API Test for {project_name}

test:
  name: "Health Check Test"
  scenario:
    - step:
        description: "Check if API is running"
        request:
          method: "GET"
          path: "/api/health"
        expect:
          status: 200
          json:
            status: "ok"
"""
    
    with open(tests_path / "basic.testflow", 'w') as f:
        f.write(basic_test)