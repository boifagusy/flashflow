# FlashCore Service

This service provides the Go interface to the FlashCore C++ library, which implements the high-performance core components of the FlashFlow Engine.

## Features

1. **Vector Search**: High-performance similarity search using HNSW index
2. **ML Inference**: Native ONNX runtime for fast machine learning inference
3. **Security**: AES-256 encryption/decryption for data protection

## Building

To build the FlashCore service:

```bash
./build.bat
```

This will:
1. Build the FlashCore C++ library
2. Build the Go service that interfaces with the C++ library

## Running

To run the service:

```bash
./flashcore-service.exe
```

The service will start on port 8080 and provide the following endpoints:
- `/vector-search`: Vector similarity search
- `/inference`: Machine learning inference
- `/encrypt`: Data encryption
- `/decrypt`: Data decryption
- `/health`: Health check

## Integration with FlashFlow

The FlashCore service integrates with the FlashFlow Engine through:
1. Direct C++ library calls via cgo
2. HTTP API endpoints for remote access
3. Shared memory interfaces for high-performance local access

## Architecture

The service follows the FlashFlow modular architecture:
- C++ core for performance-critical operations
- Go orchestration layer for service management
- HTTP API for external access
- Direct library calls for internal FlashFlow components

## Testing

Run the tests to verify the service:

```bash
go test ./...
```

## Dependencies

- Go 1.19+
- CMake 3.10+
- C++17 compatible compiler
- FlashCore C++ library (built automatically)