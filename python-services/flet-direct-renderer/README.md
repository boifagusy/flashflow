# FlashFlow Engine

The FlashFlow Engine is a Python-based rendering engine that can render websites directly from .flow files without requiring a build step. It uses Flet as the underlying UI framework.

## How It Works

The FlashFlow Engine parses .flow files and converts them into interactive web applications using Flet components. It can communicate with a Laravel backend through RESTful APIs.

## Key Components

### FlashFlowEngine Class
The main class that handles:
- Parsing .flow files
- Converting them to Flet UI components
- Managing API communication with the backend
- Routing between different pages

### API Integration
The engine can make HTTP requests to a Laravel backend:
- GET requests for retrieving data
- POST requests for creating records
- PUT requests for updating records
- DELETE requests for removing records

## Usage

### Command Line
```bash
# Start the engine
python main.py

# Start with custom project directory
python main.py /path/to/project

# Start with custom backend URL
python main.py /path/to/project http://your-backend.com
```

### Programmatic Usage
```python
from main import FlashFlowEngine

# Create engine instance
engine = FlashFlowEngine("/path/to/project", "http://localhost:8000")

# The engine will automatically start a Flet web application
```

## Underlying Technology

### Flet
Flet is a Python framework for building interactive web, desktop, and mobile applications. It provides:
- Cross-platform UI components
- Real-time updates
- Native look and feel
- Easy deployment

### Python
The engine is written in Python, making it easy to extend and customize.

### Requests Library
Used for making HTTP requests to the backend API.

## File Structure
```
flet-direct-renderer/
├── main.py          # Main engine implementation
├── requirements.txt # Python dependencies
└── build.py         # Build script for creating executable
```

## Integration with Technology Stack

The FlashFlow Engine integrates with:
- **Laravel**: Provides the backend API
- **FranklinPHP**: Serves the Laravel application
- **Go**: CLI wrapper for process management
- **FastHTTP**: Optional high-performance HTTP engine

This integration allows for rapid development and deployment of full-stack applications.