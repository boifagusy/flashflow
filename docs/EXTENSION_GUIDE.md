# FlashFlow Extension Guide

This guide explains how to create plugins, extensions, and custom integrations for FlashFlow.

## Table of Contents

1. [Extension Types](#extension-types)
2. [Plugin Architecture](#plugin-architecture)
3. [Creating Services](#creating-services)
4. [Creating Integrations](#creating-integrations)
5. [Creating Generators](#creating-generators)
6. [Creating Commands](#creating-commands)
7. [Extension Distribution](#extension-distribution)
8. [Extension Testing](#extension-testing)
9. [Best Practices](#best-practices)

## Extension Types

FlashFlow supports several types of extensions:

### 1. Services
Business logic components that provide specific functionality (e.g., payment processing, SMS sending)

### 2. Integrations
Connect services to platforms and generate platform-specific code

### 3. Generators
Create code for new platforms or extend existing platform support

### 4. Commands
Add new CLI commands to extend FlashFlow functionality

### 5. Templates
Provide project templates for specific use cases

### 6. Middleware
Add processing steps to the build or deployment pipeline

## Plugin Architecture

FlashFlow uses a plugin architecture based on Python packages:

```
flashflow-extension-name/
├── flashflow_extension_name/
│   ├── __init__.py
│   ├── services/
│   ├── integrations/
│   ├── generators/
│   └── commands/
├── setup.py
├── README.md
└── tests/
```

### Extension Entry Point

Extensions are discovered through setuptools entry points:

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="flashflow-extension-name",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "flashflow.services": [
            "custom_service = flashflow_extension_name.services:CustomService",
        ],
        "flashflow.integrations": [
            "custom_integration = flashflow_extension_name.integrations:CustomIntegration",
        ],
        "flashflow.generators": [
            "custom_generator = flashflow_extension_name.generators:CustomGenerator",
        ],
        "flashflow.commands": [
            "custom_command = flashflow_extension_name.commands:custom",
        ],
    },
    install_requires=[
        "flashflow>=0.1.0",
    ],
)
```

## Creating Services

Services contain business logic and are the foundation of FlashFlow extensions.

### Service Structure

```python
# flashflow_extension_name/services/custom_service.py
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import requests

logger = logging.getLogger(__name__)

@dataclass
class CustomServiceConfig:
    """Configuration for custom service"""
    api_key: str
    api_url: str = "https://api.example.com"
    timeout: int = 30
    retries: int = 3

class CustomService:
    """Custom service implementation"""
    
    def __init__(self, config: Optional[CustomServiceConfig] = None):
        self.config = config or CustomServiceConfig(api_key="")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        })
    
    def do_something(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform custom service action"""
        try:
            response = self.session.post(
                f"{self.config.api_url}/something",
                json=data,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Custom service error: {e}")
            raise
    
    def validate_config(self) -> bool:
        """Validate service configuration"""
        if not self.config.api_key:
            logger.error("API key is required")
            return False
        return True
```

### Service Configuration

Services should support configuration through multiple methods:

1. **Constructor parameters**
2. **Environment variables**
3. **Configuration files**
4. **FlashFlow project configuration**

```python
import os
from typing import Optional

def create_service_from_config(config_dict: Optional[Dict[str, Any]] = None) -> CustomService:
    """Create service from configuration"""
    # Load from config dict
    if config_dict:
        config = CustomServiceConfig(
            api_key=config_dict.get("api_key", ""),
            api_url=config_dict.get("api_url", "https://api.example.com"),
            timeout=config_dict.get("timeout", 30),
            retries=config_dict.get("retries", 3)
        )
    # Load from environment variables
    else:
        config = CustomServiceConfig(
            api_key=os.getenv("CUSTOM_SERVICE_API_KEY", ""),
            api_url=os.getenv("CUSTOM_SERVICE_API_URL", "https://api.example.com"),
            timeout=int(os.getenv("CUSTOM_SERVICE_TIMEOUT", "30")),
            retries=int(os.getenv("CUSTOM_SERVICE_RETRIES", "3"))
        )
    
    return CustomService(config)
```

## Creating Integrations

Integrations connect services to platforms and generate platform-specific code.

### Integration Structure

```python
# flashflow_extension_name/integrations/custom_integration.py
import logging
from typing import Dict, Any, List
from flashflow_extension_name.services.custom_service import CustomService

logger = logging.getLogger(__name__)

class CustomIntegration:
    """Integration for custom service"""
    
    def __init__(self):
        self.service = None
        self.generated_components = {}
        self.generated_routes = {}
        self.generated_middleware = {}
    
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialize the integration"""
        try:
            # Initialize service
            from flashflow_extension_name.services import create_service_from_config
            self.service = create_service_from_config(config)
            
            # Validate configuration
            if not self.service.validate_config():
                return False
            
            logger.info("Custom integration initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize custom integration: {e}")
            return False
    
    def generate_react_components(self) -> Dict[str, str]:
        """Generate React components for frontend"""
        components = {}
        
        try:
            # Generate dashboard component
            components['CustomDashboard'] = self._generate_dashboard_component()
            
            # Generate configuration component
            components['CustomConfig'] = self._generate_config_component()
            
            self.generated_components = components
            logger.info(f"Generated {len(components)} React components")
            return components
        except Exception as e:
            logger.error(f"Failed to generate React components: {e}")
            return {}
    
    def generate_flask_routes(self) -> Dict[str, str]:
        """Generate Flask routes for backend"""
        routes = {}
        
        try:
            # Generate API routes
            routes['custom_api'] = self._generate_api_routes()
            
            # Generate webhook routes
            routes['custom_webhooks'] = self._generate_webhook_routes()
            
            self.generated_routes = routes
            logger.info(f"Generated {len(routes)} Flask routes")
            return routes
        except Exception as e:
            logger.error(f"Failed to generate Flask routes: {e}")
            return {}
    
    def generate_flask_middleware(self) -> Dict[str, str]:
        """Generate Flask middleware"""
        middleware = {}
        
        try:
            # Generate authentication middleware
            middleware['custom_auth'] = self._generate_auth_middleware()
            
            # Generate logging middleware
            middleware['custom_logging'] = self._generate_logging_middleware()
            
            self.generated_middleware = middleware
            logger.info(f"Generated {len(middleware)} Flask middleware")
            return middleware
        except Exception as e:
            logger.error(f"Failed to generate Flask middleware: {e}")
            return {}
    
    def _generate_dashboard_component(self) -> str:
        """Generate React dashboard component"""
        return '''
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  CircularProgress,
  Alert
} from '@mui/material';

export const CustomDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/custom/data');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Custom Service Dashboard
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="h6">
            Data from Custom Service
          </Typography>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CustomDashboard;
        '''.strip()
    
    def _generate_config_component(self) -> str:
        """Generate React configuration component"""
        # Implementation here
        pass
    
    def _generate_api_routes(self) -> str:
        """Generate Flask API routes"""
        return '''
@app.route('/api/custom/data', methods=['GET'])
@require_auth
def get_custom_data():
    try:
        # Use the service
        result = custom_service.do_something({"action": "get_data"})
        return jsonify(result)
    except Exception as e:
        logger.error(f"Custom API error: {e}")
        return jsonify({'error': str(e)}), 500
        '''.strip()
    
    def _generate_webhook_routes(self) -> str:
        """Generate Flask webhook routes"""
        # Implementation here
        pass
    
    def _generate_auth_middleware(self) -> str:
        """Generate authentication middleware"""
        # Implementation here
        pass
    
    def _generate_logging_middleware(self) -> str:
        """Generate logging middleware"""
        # Implementation here
        pass
```

## Creating Generators

Generators create code for specific platforms or extend existing platform support.

### Generator Structure

```python
# flashflow_extension_name/generators/custom_generator.py
from pathlib import Path
from typing import Dict, Any
from flashflow_cli.core import FlashFlowIR
import logging

logger = logging.getLogger(__name__)

class CustomGenerator:
    """Generator for custom platform"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
    
    def generate(self, ir: FlashFlowIR, config: Dict[str, Any]) -> bool:
        """Generate code for custom platform"""
        try:
            # Create output directory
            platform_dir = self.output_dir / "custom"
            platform_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate models
            self._generate_models(ir, platform_dir)
            
            # Generate API clients
            self._generate_api_clients(ir, platform_dir)
            
            # Generate UI components
            self._generate_ui_components(ir, platform_dir)
            
            logger.info("Custom platform code generated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to generate custom platform code: {e}")
            return False
    
    def _generate_models(self, ir: FlashFlowIR, output_dir: Path):
        """Generate data models"""
        models_dir = output_dir / "models"
        models_dir.mkdir(exist_ok=True)
        
        for model_name, model_def in ir.models.items():
            model_file = models_dir / f"{model_name}.py"
            with open(model_file, 'w') as f:
                f.write(self._generate_model_code(model_name, model_def))
    
    def _generate_model_code(self, name: str, definition: Dict[str, Any]) -> str:
        """Generate model code"""
        code = f"class {name}:\n"
        code += "    def __init__(self):\n"
        
        for field in definition.get('fields', []):
            field_name = field['name']
            code += f"        self.{field_name} = None\n"
        
        return code
    
    def _generate_api_clients(self, ir: FlashFlowIR, output_dir: Path):
        """Generate API clients"""
        # Implementation here
        pass
    
    def _generate_ui_components(self, ir: FlashFlowIR, output_dir: Path):
        """Generate UI components"""
        # Implementation here
        pass
```

## Creating Commands

Commands extend FlashFlow's CLI functionality.

### Command Structure

```python
# flashflow_extension_name/commands/custom.py
import click
from flashflow_cli.core import FlashFlowProject
from flashflow_extension_name.services import create_service_from_config
import logging

logger = logging.getLogger(__name__)

@click.command()
@click.option('--option', '-o', help='Custom option')
@click.pass_context
def custom(ctx, option):
    """Custom command description"""
    try:
        # Get project context
        project = FlashFlowProject(ctx.obj['project_root'])
        
        # Load configuration
        config = project.config
        custom_config = config.frameworks.get('custom', {})
        
        # Initialize service
        service = create_service_from_config(custom_config)
        
        # Execute command logic
        if option:
            result = service.do_something({"option": option})
            click.echo(f"Result: {result}")
        else:
            click.echo("Custom command executed successfully")
            
    except Exception as e:
        logger.error(f"Custom command error: {e}")
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
```

### Registering Commands

Commands must be registered in the extension's entry points:

```python
# setup.py
entry_points={
    "flashflow.commands": [
        "custom = flashflow_extension_name.commands.custom:custom",
    ],
}
```

## Extension Distribution

### Packaging Extensions

Create a proper Python package for your extension:

```python
# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flashflow-custom-extension",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Custom extension for FlashFlow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/flashflow-custom-extension",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flashflow>=0.1.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "flashflow.services": [
            "custom_service = flashflow_extension_name.services:CustomService",
        ],
        "flashflow.integrations": [
            "custom_integration = flashflow_extension_name.integrations:CustomIntegration",
        ],
        "flashflow.generators": [
            "custom_generator = flashflow_extension_name.generators:CustomGenerator",
        ],
        "flashflow.commands": [
            "custom = flashflow_extension_name.commands:custom",
        ],
    },
)
```

### Publishing to PyPI

1. **Create accounts**:
   - PyPI account: https://pypi.org/account/register/
   - Test PyPI account: https://test.pypi.org/account/register/

2. **Install packaging tools**:
```bash
pip install build twine
```

3. **Build the package**:
```bash
python -m build
```

4. **Upload to Test PyPI**:
```bash
twine upload --repository testpypi dist/*
```

5. **Upload to PyPI**:
```bash
twine upload dist/*
```

### Installing Extensions

Users can install extensions using pip:

```bash
# Install from PyPI
pip install flashflow-custom-extension

# Install from local directory
pip install -e /path/to/extension

# Install from Git repository
pip install git+https://github.com/username/flashflow-custom-extension.git
```

## Extension Testing

### Test Structure

Create comprehensive tests for your extension:

```
tests/
├── test_services.py
├── test_integrations.py
├── test_generators.py
├── test_commands.py
└── conftest.py
```

### Service Testing

```python
# tests/test_services.py
import pytest
from flashflow_extension_name.services import CustomService, CustomServiceConfig

def test_custom_service_initialization():
    """Test service initialization"""
    config = CustomServiceConfig(api_key="test-key")
    service = CustomService(config)
    assert service.config.api_key == "test-key"

def test_custom_service_validation():
    """Test service configuration validation"""
    # Valid configuration
    config = CustomServiceConfig(api_key="test-key")
    service = CustomService(config)
    assert service.validate_config() == True
    
    # Invalid configuration
    config = CustomServiceConfig(api_key="")
    service = CustomService(config)
    assert service.validate_config() == False

@pytest.mark.integration
def test_custom_service_api_call():
    """Test service API call (integration test)"""
    config = CustomServiceConfig(
        api_key="test-key",
        api_url="https://httpbin.org"
    )
    service = CustomService(config)
    
    # This would make a real API call in integration tests
    # For unit tests, you'd mock the requests
    pass
```

### Integration Testing

```python
# tests/test_integrations.py
import pytest
from flashflow_extension_name.integrations import CustomIntegration

def test_integration_initialization():
    """Test integration initialization"""
    integration = CustomIntegration()
    # Test with valid config
    result = integration.initialize({"api_key": "test-key"})
    assert result == True

def test_component_generation():
    """Test React component generation"""
    integration = CustomIntegration()
    integration.initialize({"api_key": "test-key"})
    
    components = integration.generate_react_components()
    assert 'CustomDashboard' in components
    assert isinstance(components['CustomDashboard'], str)
```

### Command Testing

```python
# tests/test_commands.py
from click.testing import CliRunner
from flashflow_extension_name.commands.custom import custom

def test_custom_command():
    """Test custom command execution"""
    runner = CliRunner()
    result = runner.invoke(custom, ['--option', 'test'])
    
    assert result.exit_code == 0
    assert 'Result:' in result.output
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_services.py

# Run with coverage
pytest --cov=flashflow_extension_name

# Run integration tests
pytest -m integration
```

## Best Practices

### Code Quality

1. **Follow PEP 8**: Use consistent code style
2. **Type hints**: Add type hints to all functions
3. **Documentation**: Write clear docstrings
4. **Error handling**: Implement proper error handling
5. **Logging**: Use appropriate logging levels

### Security

1. **Input validation**: Validate all inputs
2. **Configuration security**: Don't log sensitive configuration
3. **Dependency management**: Keep dependencies updated
4. **Authentication**: Implement proper authentication
5. **Authorization**: Check permissions appropriately

### Performance

1. **Caching**: Implement appropriate caching
2. **Connection pooling**: Reuse connections
3. **Async operations**: Use async where appropriate
4. **Resource cleanup**: Clean up resources properly
5. **Efficient algorithms**: Use efficient algorithms and data structures

### Compatibility

1. **Version compatibility**: Test with supported FlashFlow versions
2. **Python versions**: Support Python 3.8+
3. **Platform compatibility**: Test on different operating systems
4. **Dependency conflicts**: Avoid conflicting dependencies
5. **Backward compatibility**: Maintain backward compatibility when possible

### User Experience

1. **Clear error messages**: Provide helpful error messages
2. **Progress indication**: Show progress for long operations
3. **Configuration flexibility**: Allow flexible configuration
4. **Documentation**: Provide comprehensive documentation
5. **Examples**: Include usage examples

### Maintenance

1. **Versioning**: Follow semantic versioning
2. **Changelog**: Maintain a changelog
3. **Release notes**: Write clear release notes
4. **Deprecation policy**: Have a clear deprecation policy
5. **Community support**: Engage with the community

## Example Extension

Here's a complete example of a simple extension:

### Directory Structure

```
flashflow-helloworld/
├── flashflow_helloworld/
│   ├── __init__.py
│   ├── services/
│   │   └── hello_service.py
│   ├── integrations/
│   │   └── hello_integration.py
│   └── commands/
│       └── hello.py
├── setup.py
├── README.md
└── tests/
    ├── test_hello_service.py
    └── test_hello_command.py
```

### Implementation

```python
# flashflow_helloworld/services/hello_service.py
import logging
from typing import Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HelloConfig:
    greeting: str = "Hello"

class HelloService:
    def __init__(self, config: HelloConfig = None):
        self.config = config or HelloConfig()
    
    def say_hello(self, name: str) -> Dict[str, str]:
        message = f"{self.config.greeting}, {name}!"
        logger.info(f"Saying: {message}")
        return {"message": message}
```

```python
# flashflow_helloworld/commands/hello.py
import click
from flashflow_helloworld.services import HelloService, HelloConfig

@click.command()
@click.argument('name')
@click.option('--greeting', '-g', default='Hello', help='Greeting to use')
def hello(name, greeting):
    """Say hello to someone"""
    config = HelloConfig(greeting=greeting)
    service = HelloService(config)
    result = service.say_hello(name)
    click.echo(result['message'])
```

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="flashflow-helloworld",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "flashflow.commands": [
            "hello = flashflow_helloworld.commands.hello:hello",
        ],
    },
    install_requires=[
        "flashflow>=0.1.0",
    ],
)
```

## Conclusion

Creating extensions for FlashFlow allows you to extend its functionality and integrate with third-party services. By following this guide, you can create robust, well-tested extensions that enhance the FlashFlow ecosystem.

Remember to:
1. Follow best practices for code quality and security
2. Provide comprehensive documentation
3. Include thorough testing
4. Engage with the FlashFlow community
5. Maintain your extensions with regular updates

For more information, refer to:
- [User Guide](USER_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [API Reference](API_REFERENCE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)