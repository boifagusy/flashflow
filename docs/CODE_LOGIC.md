# FlashFlow Code Logic Explanation

This document explains the core logic and flow of the FlashFlow system.

## Core Logic Flow

### 1. File Processing Pipeline

```
.flow File → Parser → Data Structure → Flet Components → UI
```

The FlashFlow Engine processes .flow files through these stages:

1. **File Reading**: Read .flow files from the `src/flows/` directory
2. **Parsing**: Convert YAML content to Python data structures
3. **Component Creation**: Transform data structures into Flet UI components
4. **Rendering**: Display components in a Flet application

### 2. Engine Initialization

When the FlashFlow Engine starts:

```python
# 1. Initialize engine
engine = FlashFlowEngine(project_root, backend_url)

# 2. Load route mappings
engine._load_route_mappings()

# 3. Start Flet application
ft.app(target=engine.main, port=8012)
```

### 3. Route Registration

The engine automatically discovers .flow files and registers their routes:

```python
def _load_route_mappings(self):
    """Load route mappings from .flow files"""
    for flow_file in self.flow_files_dir.glob("*.flow"):
        flow_data = self._parse_flow_file(flow_file)
        if 'page' in flow_data and 'path' in flow_data['page']:
            route = flow_data['page']['path']
            self.page_registry[route] = flow_file
```

### 4. Request Handling

When a user navigates to a route:

```python
def main(self, page: ft.Page):
    """Main Flet application entry point"""
    # 1. Get requested route
    route = page.route or "/"
    
    # 2. Find matching .flow file
    flow_file_path = self.page_registry.get(route)
    
    # 3. Parse and render the page
    if flow_file_path:
        flow_data = self._parse_flow_file(flow_file_path)
        controls = self._render_page(flow_data)
        page.add(ft.Column(controls))
```

## Component Creation Logic

### Text Components
```python
def _create_component(self, component_data):
    component_type = component_data.get('component', '').lower()
    
    if component_type == 'text':
        return ft.Text(
            component_data.get('content', ''),
            size=16
        )
```

### Button Components with API Integration
```python
elif component_type == 'button':
    action = component_data.get('action')
    if action == 'api_call':
        def on_click(e):
            endpoint = component_data.get('endpoint')
            method = component_data.get('method', 'GET')
            data = component_data.get('data', {})
            self._make_api_request(method, endpoint, data)
        
        return ft.ElevatedButton(
            component_data.get('text', 'Button'),
            on_click=on_click
        )
```

## API Integration Logic

### Making API Requests
```python
def _make_api_request(self, method, endpoint, data=None):
    """Make API request to Laravel backend"""
    url = urljoin(self.backend_url, endpoint)
    headers = {'Content-Type': 'application/json'}
    
    if method.upper() == 'GET':
        response = requests.get(url, headers=headers)
    elif method.upper() == 'POST':
        response = requests.post(url, json=data, headers=headers)
    # ... other methods
    
    return response.json()
```

## Technology Stack Integration Logic

### Python/Flet Layer
- Handles UI rendering and user interactions
- Parses .flow files
- Makes HTTP requests to backend

### Go/CLI Layer
- Manages process execution
- Provides command-line interface
- Handles file watching and hot reloading

### PHP/Laravel Layer
- Provides RESTful APIs
- Handles database operations
- Manages business logic

## Data Flow Logic

### Development Mode Data Flow
```
User Interaction → Flet Event → API Request → Laravel Backend → Database
                                      ↖              ↙
                                   Response      Processing
                                      ↖              ↙
                                   Flet UI ← JSON Response
```

### File Change Detection
```python
# Pseudo-code for file watching
def watch_flow_files():
    for file_change in watched_files:
        if file_change.type == 'modified':
            reload_route_mapping(file_change.file)
            if current_page_affected(file_change.file):
                refresh_current_page()
```

## Error Handling Logic

### File Parsing Errors
```python
def _parse_flow_file(self, file_path):
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in {file_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return {}
```

### API Request Errors
```python
def _make_api_request(self, method, endpoint, data=None):
    try:
        # ... make request
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        return {"error": str(e)}
```

## Performance Optimization Logic

### Route Caching
```python
# Cache parsed flow files to avoid repeated parsing
self._flow_cache = {}

def _parse_flow_file(self, file_path):
    if file_path in self._flow_cache:
        return self._flow_cache[file_path]
    
    # Parse file and cache result
    result = parse_yaml_file(file_path)
    self._flow_cache[file_path] = result
    return result
```

### Component Reuse
```python
# Reuse components when possible
def _create_component(self, component_data):
    cache_key = hash(str(component_data))
    if cache_key in self._component_cache:
        return self._component_cache[cache_key]
    
    # Create new component and cache it
    component = create_flet_component(component_data)
    self._component_cache[cache_key] = component
    return component
```

## Extensibility Logic

### Adding New Component Types
```python
def _create_component(self, component_data):
    component_type = component_data.get('component', '').lower()
    
    # Existing component types
    if component_type == 'text':
        return create_text_component(component_data)
    elif component_type == 'button':
        return create_button_component(component_data)
    
    # Easy to extend with new types
    elif component_type == 'custom_component':
        return create_custom_component(component_data)
    
    # Default fallback
    return create_unknown_component(component_data)
```

This logic structure allows the FlashFlow Engine to:
1. Dynamically render UI from .flow files
2. Integrate with backend services
3. Handle errors gracefully
4. Be easily extended with new features
5. Maintain good performance through caching