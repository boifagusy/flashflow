# FlashFlow Key Concepts

This document explains the key concepts of FlashFlow and how they work together.

## Core Concepts

### 1. Declarative Development
FlashFlow uses a declarative approach where you describe what you want, not how to build it.

Instead of writing code like this:
```python
# Traditional approach - imperative
app = Flask()
@app.route('/users')
def get_users():
    users = database.query('SELECT * FROM users')
    return jsonify(users)
```

You write code like this:
```yaml
# FlashFlow approach - declarative
endpoint:
  path: "/api/users"
  method: "GET"
  handler:
    action: "list_records"
    model: "User"
```

### 2. Single Source of Truth
One .flow file defines the entire application:
- Data models
- User interface
- API endpoints
- Business logic

### 3. Real-time Development
Changes to .flow files are reflected immediately in the running application.

## Key Components

### .flow Files
YAML-based files that define your application:

```yaml
# Structure of a .flow file
model:
  # Data structure definitions
  
page:
  # User interface definitions
  
endpoint:
  # API endpoint definitions
  
theme:
  # Styling and theming
  
authentication:
  # Auth configuration
```

### FlashFlow Engine
The runtime that interprets .flow files and creates interactive applications.

Key features:
- Parses .flow files in real-time
- Converts definitions to Flet UI components
- Handles routing between pages
- Manages API communication
- Provides hot-reloading

### Flet (Underlying Framework)
The Python UI framework that powers the FlashFlow Engine:

Benefits:
- Cross-platform (Web, Desktop, Mobile)
- Native look and feel
- Rich component library
- Real-time updates

## How It Fits Together

### Development Workflow
```
Developer writes .flow files
        ↓
FlashFlow Engine watches for changes
        ↓
Engine parses files and updates UI in real-time
        ↓
User interacts with application
        ↓
Application makes API calls to Laravel backend
        ↓
Backend processes requests and returns data
        ↓
Engine updates UI with response data
```

### Production Workflow
```
.flow files
        ↓
Go code generation services
        ↓
Optimized code for target platforms
        ↓
Applications deployed to respective platforms
        ↓
Users interact with generated applications
        ↓
Applications communicate with Laravel backend
```

## Technology Stack Roles

### Python Layer (FlashFlow Engine)
- Real-time .flow file processing
- Flet UI component creation
- API request handling
- Development server

### Go Layer (CLI & Services)
- Command-line interface
- Code generation for production
- File watching and hot reloading
- Process management

### PHP Layer (Laravel Backend)
- RESTful API endpoints
- Database operations
- Authentication
- Business logic

### Infrastructure (FranklinPHP/GoFastHTTP)
- High-performance application serving
- HTTP/2 and HTTPS support
- Optional Go-based HTTP engine for concurrency

## Integration Patterns

### API Communication
The FlashFlow Engine communicates with the backend through RESTful APIs:

```yaml
# In .flow file
component: "button"
action: "api_call"
method: "POST"
endpoint: "/api/users"
data:
  name: "{{user_name}}"
  email: "{{user_email}}"
```

This gets converted to:
```python
# In FlashFlow Engine
requests.post(
    "http://backend-url/api/users",
    json={"name": user_name, "email": user_email},
    headers={"Content-Type": "application/json"}
)
```

### Data Binding
Dynamic data binding in .flow files:

```yaml
# Template syntax
text: "Hello {{user.name}}, you have {{user.messages.count}} messages"
```

Gets processed as:
```python
# In FlashFlow Engine
text_content = f"Hello {user_data['name']}, you have {user_data['messages']['count']} messages"
```

## Benefits of This Architecture

### 1. Developer Productivity
- Write once, run everywhere
- No context switching between frontend and backend
- Immediate feedback during development

### 2. Consistency
- Single source of truth eliminates inconsistencies
- Automatically synchronized frontend and backend
- Centralized business logic

### 3. Performance
- Go services for code generation
- FranklinPHP for backend serving
- Optional GoFastHTTP for high concurrency
- Flet for efficient UI rendering

### 4. Scalability
- Easy horizontal scaling with containerization
- Microservices-ready architecture
- Cloud deployment friendly

### 5. Maintainability
- Clear separation of concerns
- Declarative definitions are easy to understand
- Version control friendly
- Automated testing capabilities

This architecture allows developers to focus on what their application should do rather than how to build it, while still providing the performance and scalability needed for production applications.