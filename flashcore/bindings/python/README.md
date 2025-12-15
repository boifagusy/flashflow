# FlashCore Python Bindings

This package provides Python bindings for the FlashCore C++ library, allowing Python applications to leverage the high-performance capabilities of FlashCore.

## Installation

First, install the required dependencies:

```bash
pip install -r requirements.txt
```

Then build and install the FlashCore Python bindings:

```bash
python setup.py build_ext --inplace
```

## Usage

### Vector Search (HNSW Index)

```python
import numpy as np
import flashcore

# Create an HNSW index
index = flashcore.HNSWIndex(4, 100)  # 4-dimensional vectors, max 100 elements

# Add vectors to the index
vec1 = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
vec2 = np.array([2.0, 3.0, 4.0, 5.0], dtype=np.float32)

index.add_vector(vec1, 1)
index.add_vector(vec2, 2)

# Search for nearest neighbors
query = np.array([1.5, 2.5, 3.5, 4.5], dtype=np.float32)
results = index.search(query, 3)  # Find 3 nearest neighbors

print(results)  # [{'id': 1, 'distance': 0.0}, {'id': 2, 'distance': 2.0}]
```

### Inference Engine (ONNX Runtime)

```python
import numpy as np
import flashcore

# Create an ONNX runtime
runtime = flashcore.ONNXRuntime("model.onnx")

# Run inference
input_data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
output_data = runtime.run_inference(input_data, 4)  # Expect 4 outputs

print(output_data)
```

### Vault Security (AES-256)

```python
import flashcore

# Create an AES vault
vault = flashcore.AESVault("my_secret_key")

# Encrypt data
plaintext = b"Secret message"
ciphertext = vault.encrypt(plaintext)

# Decrypt data
decrypted = vault.decrypt(ciphertext)

print(decrypted)  # b'Secret message'
```

## API Reference

### HNSWIndex

- `HNSWIndex(dimensions: int, max_elements: int)` - Create a new HNSW index
- `add_vector(vector: numpy.ndarray, id: int)` - Add a vector to the index
- `search(query: numpy.ndarray, k: int)` - Search for k nearest neighbors

### ONNXRuntime

- `ONNXRuntime(model_path: str)` - Create a new ONNX runtime
- `run_inference(input: numpy.ndarray, output_size: int)` - Run inference on input data

### AESVault

- `AESVault(key: str)` - Create a new AES vault
- `encrypt(plaintext: bytes)` - Encrypt data
- `decrypt(ciphertext: bytes)` - Decrypt data

## Integration with FlashFlow

The FlashCore Python bindings are designed to integrate seamlessly with the FlashFlow framework:

```python
import flashcore
from flashflow.python-services.flet-direct-renderer import main as flet_renderer

# Use FlashCore for vector search in a FlashFlow component
def create_recommendation_component(user_preferences):
    index = flashcore.HNSWIndex(128, 10000)  # 128-dimensional preference vectors
    
    # Add item vectors to index
    # ... populate index with item vectors ...
    
    # Find similar items
    results = index.search(user_preferences, 10)
    
    # Render recommendations using Flet
    return flet_renderer.create_list_component(results)
```

## Testing

Run the tests to verify the installation:

```bash
python test_flashcore.py
```

Run integration tests:

```bash
python integration_test.py
```

## License

FlashCore Python bindings are released under the MIT License.