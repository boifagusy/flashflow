# FlashFlow Developer Guide

This guide is for developers who want to extend FlashFlow, contribute to the project, or understand its internal architecture.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Code Structure](#code-structure)
3. [Core Components](#core-components)
4. [Extending FlashFlow](#extending-flashflow)
5. [Creating Services](#creating-services)
6. [Creating Integrations](#creating-integrations)
7. [Adding New Platforms](#adding-new-platforms)
8. [Testing Framework](#testing-framework)
9. [Contributing](#contributing)

## Architecture Overview

FlashFlow follows a modular architecture with clear separation of concerns:

```
flashflow/
├── flashflow_cli/           # Main CLI package
│   ├── commands/           # CLI commands
│   ├── core.py             # Core classes
│   ├── parser.py           # .flow file parser
│   ├── generators/         # Code generators
│   ├── services/           # Business logic services
│   └── integrations/       # Platform integrations
├── docs/                   # Documentation
├── examples/               # Example .flow files
└── tests/                  # Test suite
```

When a user creates a project with `flashflow new`, they get:

```
my-project/
├── flashflow.json          # Project configuration
├── src/                   # Source files
│   └── flows/             # .flow definition files
└── dist/                  # Generated code (after build)
    ├── backend/           # Generated backend code
    ├── frontend/          # Generated frontend code
    └── mobile/            # Generated mobile code
```

## Code Structure

### Main Components

1. **CLI Layer**: Command-line interface and argument parsing
2. **Parser Layer**: .flow file parsing and validation
3. **IR Layer**: FlashFlow Intermediate Representation
4. **Generator Layer**: Code generation for different platforms
5. **Service Layer**: Business logic and domain services
6. **Integration Layer**: Platform-specific integrations

### Data Flow

```
.flow file → Parser → FlashFlow IR → Generators → Platform Code
```

## Core Components

### FlashFlowProject

The [FlashFlowProject](file:///c%3A/Users/VineMaster/Desktop/flashflow/flashflow_cli/core.py#L29-L64) class represents a FlashFlow project and handles:
- Project configuration management
- File system operations
- Flow file discovery
- Test file discovery

### FlashFlowIR

The [FlashFlowIR](file:///c%3A/Users/VineMaster/Desktop/flashflow/flashflow_cli/core.py#L66-L145) (Intermediate Representation) class is the core data structure that:
- Stores parsed .flow file data
- Provides a unified interface for all platforms
- Handles data transformations
- Manages relationships between components

### Parser

The parser in [parser.py](file:///c%3A/Users/VineMaster/Desktop/flashflow/flashflow_cli/parser.py) handles:
- YAML parsing of .flow files
- Syntax validation
- Conversion to FlashFlow IR
- Error reporting

## Extending FlashFlow

### Creating Custom Commands

To add a new CLI command:

1. Create a new file in `flashflow_cli/commands/`
2. Implement the command using Click decorators
3. Register the command in `flashflow_cli/main.py`

Example command:

```python
# flashflow_cli/commands/custom.py
import click
from flashflow_cli.core import FlashFlowProject

@click.command()
@click.pass_context
def custom(ctx):
    """Custom command description"""
    project = FlashFlowProject(ctx.obj['project_root'])
    # Implementation here
    click.echo("Custom command executed")

# Register in main.py
cli.add_command(custom)
```

### Adding New Configuration Options

To add new configuration options:

1. Update the [FlashFlowConfig](file:///c%3A/Users/VineMaster/Desktop/flashflow/flashflow_cli/core.py#L8-L27) dataclass in `core.py`
2. Update the JSON schema in `flashflow.json`
3. Handle the new options in relevant components

## Creating Services

Services contain business logic and are located in `flashflow_cli/services/`.

### Service Structure

```python
# flashflow_cli/services/custom_service.py
import logging
from typing import Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CustomConfig:
    """Configuration for custom service"""
    option1: str = "default"
    option2: int = 10

class CustomService:
    """Custom service implementation"""
    
    def __init__(self, config: CustomConfig = None):
        self.config = config or CustomConfig()
    
    def do_something(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform custom logic"""
        try:
            # Implementation here
            result = {"status": "success"}
            return result
        except Exception as e:
            logger.error(f"Error in custom service: {e}")
            raise
```

### Service Integration

Services are integrated through the integration layer:

```python
# flashflow_cli/integrations/custom_integration.py
from flashflow_cli.services.custom_service import CustomService

class CustomIntegration:
    def __init__(self):
        self.service = CustomService()
    
    def generate_code(self):
        # Use service to generate code
        pass
```

## Creating Integrations

Integrations connect services to platforms and are located in `flashflow_cli/integrations/`.

### Integration Structure

```python
# flashflow_cli/integrations/custom_integration.py
import logging
from typing import Dict, Any
from flashflow_cli.services.custom_service import CustomService

logger = logging.getLogger(__name__)

class CustomIntegration:
    """Integration for custom platform"""
    
    def __init__(self):
        self.service = CustomService()
        self.generated_components = {}
        self.generated_routes = {}
    
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialize the integration"""
        try:
            # Initialize service with config
            return True
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False
    
    def generate_react_components(self) -> Dict[str, str]:
        """Generate React components"""
        components = {}
        # Generate components
        return components
    
    def generate_flask_routes(self) -> Dict[str, str]:
        """Generate Flask routes"""
        routes = {}
        # Generate routes
        return routes
```

## Adding New Platforms

To add support for a new platform:

### 1. Create a Generator

Create a new generator in `flashflow_cli/generators/`:

```python
# flashflow_cli/generators/newplatform.py
from pathlib import Path
from typing import Dict, Any
from flashflow_cli.core import FlashFlowIR

class NewPlatformGenerator:
    """Generator for NewPlatform"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
    
    def generate(self, ir: FlashFlowIR, config: Dict[str, Any]):
        """Generate NewPlatform code"""
        # Implementation here
        pass
```

### 2. Update the Build Command

Update `flashflow_cli/commands/build.py` to use the new generator.

### 3. Update the Serve Command

Update `flashflow_cli/commands/serve.py` to serve the new platform.

## Testing Framework

FlashFlow includes a comprehensive testing framework.

### Test Structure

Tests are organized as:
- Unit tests for individual components
- Integration tests for combined functionality
- End-to-end tests for complete workflows

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_parser.py

# Run tests with coverage
python -m pytest --cov=flashflow_cli
```

### Writing Tests

```python
# tests/test_custom.py
import pytest
from flashflow_cli.services.custom_service import CustomService

def test_custom_service():
    service = CustomService()
    result = service.do_something({"test": "data"})
    assert result["status"] == "success"
```

## Contributing

### Code Standards

1. Follow PEP 8 for Python code
2. Use type hints for all function signatures
3. Write docstrings for all public functions and classes
4. Include unit tests for new functionality
5. Keep functions focused and small

### Git Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Update documentation
6. Submit a pull request

### Pull Request Process

1. Ensure all tests pass
2. Update documentation as needed
3. Follow the code style guidelines
4. Include a clear description of changes
5. Reference any related issues

### Issue Reporting

When reporting issues:
1. Include a clear description
2. Provide steps to reproduce
3. Include expected vs actual behavior
4. Add relevant code snippets
5. Specify environment details

## API Documentation

### Core Classes

#### FlashFlowProject
- `__init__(root_path: Path)`: Initialize project
- `config`: Get project configuration
- `get_flow_files()`: Get all .flow files
- `get_test_files()`: Get all .testflow files

#### FlashFlowIR
- `add_model(name: str, definition: Dict)`: Add model
- `add_page(path: str, definition: Dict)`: Add page
- `add_endpoint(path: str, definition: Dict)`: Add endpoint
- `to_dict()`: Convert to dictionary

### Parser Functions

#### parse_flow_file
```python
def parse_flow_file(file_path: Path) -> FlashFlowIR:
    """Parse a .flow file and return FlashFlowIR"""
    pass
```

### Generator Classes

#### BackendGenerator
- `generate(ir: FlashFlowIR, config: Dict)`: Generate backend code

#### FrontendGenerator
- `generate(ir: FlashFlowIR, config: Dict)`: Generate frontend code

#### MobileGenerator
- `generate(ir: FlashFlowIR, config: Dict)`: Generate mobile code

## Performance Considerations

### Memory Usage

- Use generators for large data sets
- Implement proper caching strategies
- Clean up resources after use

### Processing Speed

- Optimize parsing algorithms
- Use efficient data structures
- Minimize file I/O operations

## Security Considerations

### Input Validation

- Validate all user inputs
- Sanitize file paths
- Check configuration values

### Secure Coding

- Use parameterized queries
- Implement proper error handling
- Follow security best practices

## Debugging

### Logging

FlashFlow uses Python's logging module:

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Debugging Tools

- Use Python debugger (pdb)
- Enable verbose logging
- Use IDE debugging features

## Common Patterns

### Factory Pattern

Used for creating platform-specific generators:

```python
def get_generator(platform: str, output_dir: Path):
    if platform == "laravel":
        return BackendGenerator(output_dir)
    elif platform == "react":
        return FrontendGenerator(output_dir)
    # ...
```

### Observer Pattern

Used for progress reporting and event handling.

### Strategy Pattern

Used for different parsing and generation strategies.

## Troubleshooting

### Common Issues

1. **Import Errors**: Check Python path and virtual environment
2. **Permission Errors**: Ensure proper file permissions
3. **Dependency Issues**: Verify all dependencies are installed
4. **Parsing Errors**: Check .flow file syntax

### Debugging Steps

1. Enable verbose logging
2. Check error messages and stack traces
3. Verify configuration files
4. Test with minimal examples
5. Consult documentation and examples

## Further Reading

- [User Guide](USER_GUIDE.md)
- [API Reference](API_REFERENCE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Extension Guide](EXTENSION_GUIDE.md)