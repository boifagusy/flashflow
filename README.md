# FlashFlow Main Repository

This repository contains the core FlashFlow framework implementation.

## 🚀 New Features

### FlashFlow Engine
FlashFlow now includes a Python Flet-based engine that can render websites directly from .flow files without requiring a build step:

```bash
# Start the FlashFlow Engine automatically with the server
flashflow serve --all

# The engine will be available at http://localhost:8012

# Start with custom backend URL
flashflow serve --all --backend http://your-laravel-app.com
```

This new engine:

### FlashCore Integration
FlashFlow also includes FlashCore, a high-performance C++ library that provides:
- Vector search using HNSW index
- Native ML inference with ONNX runtime
- AES-256 encryption/decryption

FlashCore integrates seamlessly with the FlashFlow Engine through Python bindings.
- Uses pure Python Flet for all UI components (replacing HTML/CSS/JS)
- Supports deployment on cPanel and VPS hosting environments
- Automatically starts when you run `flashflow serve --all`
- Communicates with the Laravel backend through RESTful APIs

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Install FlashFlow
```bash
pip install flashflow
```

## 🚀 Quick Start

```bash
# Create a new project
flashflow new my-app
cd my-app

# Install dependencies
flashflow install core

# Start the development server (automatically starts FlashFlow Engine)
flashflow serve --all

# Visit http://localhost:8000 for backend
# Visit http://localhost:8012 for FlashFlow Engine frontend
```

## 📚 Documentation

| Command | Description |
|---------|-------------|
| `flashflow new <project>` | Create a new FlashFlow project |
| `flashflow build` | Generate application code |
| `flashflow serve [--all]` | Run unified development server (automatically starts FlashFlow Engine) |
| `flashflow test` | Run all tests |
| `flashflow deploy` | Deploy to production |
| `flashflow install <package>` | Install dependencies |

## 🌐 Deployment Options

FlashFlow supports multiple deployment environments:
- **Local Development**: Run on your machine for development
- **cPanel**: Deploy to shared hosting environments
- **VPS**: Deploy to virtual private servers
- **Docker**: Containerized deployment
- **Cloud Providers**: AWS, Google Cloud, Azure

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

FlashFlow is licensed under the MIT License. See [LICENSE](LICENSE) for more information.
