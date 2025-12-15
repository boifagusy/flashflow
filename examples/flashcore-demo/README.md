# FlashCore Demo

This example demonstrates the integration of FlashCore with the FlashFlow Engine.

## Features Demonstrated

1. **Vector Search**: High-performance similarity search using HNSW index
2. **ML Inference**: Native ONNX runtime for fast machine learning inference
3. **Encryption**: AES-256 encryption/decryption for data protection

## How to Run

1. Make sure you have FlashCore properly installed and configured
2. Navigate to your FlashFlow project directory
3. Copy the `flashcore-demo.flow` file to your project's `src/flows/` directory
4. Run the FlashFlow Engine:

```bash
python python-services/flet-direct-renderer/main.py
```

5. Open your browser and navigate to `http://localhost:8013/flashcore-demo`

## Components

The demo includes several custom components that showcase FlashCore capabilities:

- `flashcore_demo`: A reusable component that demonstrates different FlashCore features
- `features`: A standard FlashFlow component showing the benefits of FlashCore

## FlashCore Integration Points

The FlashFlow Engine integrates with FlashCore through:

1. **Direct Library Calls**: Using the FlashCore Python bindings for maximum performance
2. **Fallback Implementations**: Gracefully degrading when FlashCore is not available
3. **Component-Based Architecture**: Encapsulating FlashCore functionality in reusable components

## Customization

You can customize this demo by:

1. Modifying the `.flow` file to change the layout or content
2. Extending the `_run_*_demo()` methods in the FlashFlow Engine
3. Adding new FlashCore-powered components to the `_create_component()` method