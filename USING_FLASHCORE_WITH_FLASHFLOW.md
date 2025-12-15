# Using FlashCore with FlashFlow

This guide explains how to use FlashCore with FlashFlow to enhance your applications with high-performance computing capabilities.

## Prerequisites

Before using FlashCore with FlashFlow, ensure you have:

1. **FlashFlow Installed**: FlashFlow framework with the upgraded engine
2. **FlashCore Built**: Compiled FlashCore library and bindings
3. **Dependencies**: Python with NumPy, C++ compiler, CMake

## Building FlashCore

### Automatic Build

Run the build script to automatically build all FlashCore components:

```bash
# On Windows
build-flashcore.bat

# On Unix/Linux/macOS
./build-flashcore.sh
```

### Manual Build

If you prefer to build manually:

1. **Build C++ Library**:
   ```bash
   cd flashcore
   mkdir build
   cd build
   cmake ..
   cmake --build .
   ```

2. **Build Python Bindings**:
   ```bash
   cd flashcore/bindings/python
   python setup.py build_ext --inplace
   ```

3. **Build Go Service** (optional):
   ```bash
   cd go-services/flashcore-service
   go build
   ```

## Running FlashCore Demo

### Quick Start

Run the demo script to quickly see FlashCore in action:

```bash
# On Windows
RUN_FLASHCORE_DEMO.bat

# On Unix/Linux/macOS
./RUN_FLASHCORE_DEMO.sh
```

### Manual Execution

1. **Navigate to test project**:
   ```bash
   cd test-projects/flashcore-test
   ```

2. **Run FlashFlow Engine**:
   ```bash
   python ../../python-services/flet-direct-renderer/main.py .
   ```

3. **Open browser**: Visit `http://localhost:8013`

## Using FlashCore in Your Projects

### Vector Search

To use vector search in your FlashFlow components:

```python
# In your FlashFlow Engine (python-services/flet-direct-renderer/main.py)
def perform_vector_search(self, query_vector):
    if self.flashcore_enabled and self.vector_index:
        # Use FlashCore for high-performance search
        return self.vector_index.search(query_vector, 5)
    else:
        # Fallback implementation
        return [{"id": i, "distance": 0.0} for i in range(3)]
```

In your `.flow` files:
```yaml
- component: flashcore_demo
  title: Vector Search Demo
  demo_type: vector_search
```

### ML Inference

To use ML inference:

```python
def run_ml_inference(self, input_data):
    if self.flashcore_enabled and self.inference_runtime:
        # Use FlashCore for fast inference
        return self.inference_runtime.run_inference(input_data, 10)
    else:
        # Fallback implementation
        return np.zeros(10, dtype=np.float32)
```

### Encryption

To use encryption:

```python
def encrypt_sensitive_data(self, plaintext):
    if self.flashcore_enabled and self.security_vault:
        # Use FlashCore for secure encryption
        return self.security_vault.encrypt(plaintext)
    else:
        # Fallback (no encryption)
        return plaintext
```

## Creating Custom FlashCore Components

### 1. Add Component to Engine

In `python-services/flet-direct-renderer/main.py`, add your component to the `_create_component` method:

```python
elif component_type == 'my_flashcore_component':
    # Your custom FlashCore-powered component
    return self._create_my_flashcore_component(component_data)
```

### 2. Implement Component Logic

```python
def _create_my_flashcore_component(self, component_data):
    """Create a custom component that uses FlashCore"""
    title = component_data.get('title', 'My Component')
    
    # Use FlashCore features
    if self.flashcore_enabled:
        # Perform FlashCore operations
        result = self.vector_search(np.random.rand(128).astype(np.float32), 3)
        
        content = [
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"FlashCore result: {result}")
        ]
    else:
        content = [
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            ft.Text("FlashCore not available")
        ]
    
    return ft.Container(
        content=ft.Column(content),
        padding=20,
        border=ft.border.all(1, ft.Colors.BLUE_200),
        border_radius=8
    )
```

### 3. Use in Flow Files

```yaml
- component: my_flashcore_component
  title: My Custom FlashCore Component
```

## Performance Optimization

### Best Practices

1. **Reuse Instances**: Keep FlashCore instances alive for multiple operations
2. **Batch Operations**: Process multiple items together when possible
3. **Cache Results**: Store results of expensive operations
4. **Handle Errors**: Always provide fallback implementations

### Monitoring Performance

```python
import time

def timed_vector_search(self, query_vector):
    start_time = time.time()
    results = self.vector_search(query_vector, 5)
    end_time = time.time()
    
    print(f"Vector search took {end_time - start_time:.4f} seconds")
    return results
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure FlashCore is built and Python can find the bindings
2. **Library Loading**: Check that C++ libraries are in the system path
3. **Version Mismatches**: Verify compatible versions of all components

### Debugging Tips

1. **Enable Verbose Logging**: Set logging level to DEBUG
2. **Test Components Separately**: Isolate FlashCore functionality
3. **Use Test Suite**: Run `python test-flashcore.py` to verify integration

## Advanced Features

### WASM Integration

For client-side execution, FlashCore can be compiled to WebAssembly:

1. **Build WASM**:
   ```bash
   cd flashcore/wasm
   ./build_wasm.sh
   ```

2. **Use in Browser**:
   ```javascript
   import FlashCore from './flashcore.js';
   
   const flashcore = await FlashCore();
   const index = flashcore._create_hnsw_index(128, 1000);
   ```

### Distributed Computing

For distributed applications, use the FlashCore Go service:

1. **Start Service**:
   ```bash
   cd go-services/flashcore-service
   ./flashcore-service
   ```

2. **Access via REST API**:
   ```bash
   curl http://localhost:8080/vector-search
   ```

## Security Considerations

### Data Protection

1. **Encrypt Sensitive Data**: Use FlashCore's AES-256 encryption
2. **Secure Key Management**: Store keys securely
3. **Protect Communications**: Use HTTPS for service communication

### Access Control

1. **Authenticate Requests**: Implement authentication for service endpoints
2. **Authorize Operations**: Check permissions for privileged operations
3. **Audit Logging**: Log security-relevant events

## Extending FlashCore

### Adding New Algorithms

1. **Implement in C++**: Add new functionality to `flashcore/src/`
2. **Update API**: Modify `flashcore/include/flashcore_api.h`
3. **Create Bindings**: Add Python/Go bindings
4. **Test Thoroughly**: Write comprehensive tests

### Contributing

1. **Fork Repository**: Create your own fork
2. **Make Changes**: Implement your enhancements
3. **Test Extensively**: Verify all functionality
4. **Submit Pull Request**: Contribute back to the community

## Conclusion

FlashCore integration with FlashFlow provides powerful high-performance computing capabilities while maintaining ease of use. By following this guide, you can leverage vector search, ML inference, and encryption in your FlashFlow applications with minimal effort.

The modular architecture allows for easy extension and customization, making it simple to add new features and algorithms as needed. Whether you're building a simple web application or a complex AI-powered system, FlashCore enhances FlashFlow's capabilities to meet your performance requirements.