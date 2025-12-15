# FlashCore Test Project

This is a test project demonstrating the integration of FlashCore with FlashFlow.

## Project Structure

```
flashcore-test/
├── src/
│   └── flows/
│       ├── app.flow           # Main entry point
│       └── flashcore-demo.flow # FlashCore demo page
├── flashflow.json             # Project configuration
└── README.md                 # This file
```

## How to Run

1. Navigate to this directory:
   ```bash
   cd test-projects/flashcore-test
   ```

2. Run the FlashFlow Engine:
   ```bash
   python ../../python-services/flet-direct-renderer/main.py .
   ```

3. Open your browser and navigate to `http://localhost:8013`

## Features Demonstrated

1. **Basic Navigation**: The main page includes a button to navigate to the FlashCore demo
2. **FlashCore Integration**: The demo page showcases vector search, ML inference, and encryption
3. **Component Reusability**: Custom components demonstrate FlashCore capabilities

## FlashCore Components

The project includes the following FlashCore-powered components:

1. `flashcore_demo`: A reusable component that demonstrates different FlashCore features
2. Custom event handlers that call FlashCore methods

## Testing FlashCore Integration

To test the FlashCore integration:

1. Make sure FlashCore is properly built and installed
2. Run the project as described above
3. Navigate to the FlashCore demo page
4. Click the demo buttons to see FlashCore in action

## Extending the Demo

You can extend this demo by:

1. Adding more FlashCore-powered components
2. Creating additional demo pages for different FlashCore features
3. Integrating FlashCore with other FlashFlow components