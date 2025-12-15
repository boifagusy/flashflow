# FlashCore V1.0

FlashCore is the high-performance, universal core of the FlashFlow Engine upgrade. It provides the foundational C++ modules that power the entire system.

## Features

1. **Vector Search (HNSW Index)**: High-performance similarity search using Hierarchical Navigable Small World graphs
2. **Native Inference Engine (ONNX Runtime)**: Fast machine learning inference using ONNX models
3. **Vault Security (AES-256)**: Secure data encryption and decryption using industry-standard cryptography

## Architecture

FlashCore is built as a C++ library with bindings for multiple languages:
- C++ native API
- Go bindings via cgo
- JavaScript bindings via WebAssembly

## Building FlashCore

### Prerequisites

- CMake 3.10 or higher
- C++17 compatible compiler
- Go 1.16 or higher (for Go bindings)
- Emscripten (for WASM builds)

### Building on Linux/macOS

```bash
./build.sh
```

### Building on Windows

```cmd
build.bat
```

## Running Tests

Tests are automatically run during the build process. You can also run them manually:

```bash
cd build
ctest --verbose
```

## WASM Build

To build the WebAssembly version for browser use:

```bash
cd wasm
./build_wasm.sh
```

Then open `index.html` in a web browser to test the WASM implementation.

## API Reference

### Vector Search

```cpp
hnsw_index_t* create_hnsw_index(int dimensions, int max_elements);
void destroy_hnsw_index(hnsw_index_t* index);
int add_vector_to_index(hnsw_index_t* index, float* vector, int id);
int search_vector_in_index(hnsw_index_t* index, float* query_vector, int k, int* result_ids, float* result_distances);
```

### Inference Engine

```cpp
onnx_runtime_t* create_onnx_runtime(const char* model_path);
void destroy_onnx_runtime(onnx_runtime_t* runtime);
int run_inference(onnx_runtime_t* runtime, float* input_data, int input_size, float* output_data, int output_size);
```

### Vault Security

```cpp
aes_vault_t* create_aes_vault(const char* key);
void destroy_aes_vault(aes_vault_t* vault);
int encrypt_data(aes_vault_t* vault, const unsigned char* plaintext, int plaintext_len, unsigned char* ciphertext);
int decrypt_data(aes_vault_t* vault, const unsigned char* ciphertext, int ciphertext_len, unsigned char* plaintext);
```

## Go Bindings Usage

```go
import "flashcore/bindings/go"

// Vector search example
index := flashcore.NewHNSWIndex(4, 100)
defer index.Destroy()

vector := []float32{1.0, 2.0, 3.0, 4.0}
index.AddVector(vector, 1)

query := []float32{1.5, 2.5, 3.5, 4.5}
results, _ := index.Search(query, 1)
```

## WASM Usage

```javascript
import FlashCore from './flashcore.js';

const flashcore = await FlashCore();
const index = flashcore._create_hnsw_index(4, 100);
// ... use the API as described in the C++ reference
```

## License

FlashCore is released under the MIT License.