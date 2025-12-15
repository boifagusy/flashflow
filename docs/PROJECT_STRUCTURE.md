# FlashFlow Project Structure and Code Logic

This document explains the FlashFlow project structure and how the different components work together.

## Project Structure Overview

```
flashflow-project/
├── src/
│   ├── flows/              # FlashFlow definition files (.flow)
│   ├── models/             # Data models and database schemas
│   ├── components/         # Reusable UI components
│   ├── pages/              # Page definitions and layouts
│   ├── services/           # Business logic and API integrations
│   ├── utils/              # Utility functions and helpers
│   ├── assets/             # Static assets (images, icons, fonts)
│   ├── config/             # Configuration files
│   └── tests/              # Test files (.testflow and unit tests)
├── dist/                   # Generated application code
├── python-services/
│   └── flet-direct-renderer/  # FlashFlow Engine implementation
│       ├── main.py         # Main engine implementation
│       ├── requirements.txt # Python dependencies
│       └── build.py        # Build script
├── flashflow.json          # Project configuration
└── README.md               # Project documentation
```

## Core Components

### 1. FlashFlow Definition Files (.flow)
These files define the application structure using a declarative syntax:

```yaml
# Example .flow file
model:
  name: "User"
  fields:
    - name: "name"
      type: "string"
      required: true
    - name: "email"
      type: "string"
      required: true

page:
  title: "User Management"
  path: "/users"
  body:
    - component: "list"
      data_source: "User"
    - component: "form"
      action: "create_user"
```

### 2. FlashFlow Engine
The FlashFlow Engine is responsible for rendering .flow files directly without requiring a build step. It uses Flet as the underlying UI framework.

Key components:
- `main.py`: Entry point and core logic
- `FlashFlowEngine` class: Main engine implementation
- API integration methods: Communicate with Laravel backend

### 3. Backend Integration
The FlashFlow Engine integrates with the Laravel backend through RESTful APIs:

```python
# API request example
def _make_api_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
    """Make API request to Laravel backend"""
    url = urljoin(self.backend_url, endpoint)
    headers = {'Content-Type': 'application/json'}
    
    if method.upper() == 'GET':
        response = requests.get(url, headers=headers)
    elif method.upper() == 'POST':
        response = requests.post(url, json=data, headers=headers)
    # ... other HTTP methods
```

## How It Works

### 1. File Parsing
The engine parses .flow files and converts them into Flet UI components:

```python
def _parse_flow_file(self, file_path: Path) -> Dict[str, Any]:
    """Parse a .flow file and return structured data"""
    with open(file_path, 'r') as f:
        content = f.read()
    return yaml.safe_load(content) or {}
```

### 2. Component Creation
Parsed data is converted into Flet components:

```python
def _create_component(self, component_data: Dict[str, Any]) -> ft.Control:
    """Create a Flet component from component data"""
    component_type = component_data.get('component', '').lower()
    
    if component_type == 'button':
        return ft.ElevatedButton(
            component_data.get('text', 'Button'),
            on_click=self._handle_button_click
        )
    # ... other component types
```

### 3. API Integration
Components can trigger API calls to the Laravel backend:

```python
def _handle_button_click(self, e):
    """Handle button click events"""
    if action == 'api_call':
        endpoint = component_data.get('endpoint')
        method = component_data.get('method', 'GET')
        data = component_data.get('data', {})
        if endpoint:
            result = self._make_api_request(method, endpoint, data)
```

## Technology Stack Integration

### Laravel Backend
- Provides RESTful APIs
- Handles database operations
- Manages authentication and authorization

### FranklinPHP
- Serves the Laravel application
- Can be configured with GoFastHTTP for better performance

### Go Services
- CLI wrapper written in Go
- Manages process execution
- Provides high-performance operations

### Flet (Underlying UI Framework)
- Python UI framework for building cross-platform applications
- Used by the FlashFlow Engine for rendering
- Provides native look and feel on all platforms

## Deployment Architecture

```
┌─────────────────┐    ┌──────────────────────┐    ┌──────────────────┐
│   Flet Client   │◄──►│  FlashFlow Engine    │◄──►│ Laravel Backend  │
└─────────────────┘    └──────────────────────┘    └──────────────────┘
                            │                           │
                            ▼                           ▼
                    ┌───────────────┐         ┌──────────────────────┐
                    │ Python/Flet   │         │ FranklinPHP/Go       │
                    └───────────────┘         └──────────────────────┘
```

## Example Usage

### Starting the Engine
```bash
# Start the FlashFlow Engine
flashflow flashflow-engine

# Start with custom backend URL
flashflow flashflow-engine --backend http://your-laravel-app.com
```

### Creating a .flow File
```yaml
# users.flow
page:
  title: "User Management"
  path: "/users"
  body:
    - component: "button"
      text: "Load Users"
      action: "api_call"
      method: "GET"
      endpoint: "/api/users"
```

The FlashFlow Engine will automatically detect this file and make it available at the `/users` route, with a button that makes a GET request to `/api/users` on the Laravel backend.