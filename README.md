# FlashFlow

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

FlashFlow is a revolutionary full-stack framework that generates complete applications from `.flow` files. With a single syntax, you can create web, mobile, desktop, and backend applications with built-in features like SEO optimization and VPS deployment.

<p align="center">
  <img src="assets/flashflow-logo.png" alt="FlashFlow Logo" width="200">
</p>

## 🚀 Quick Start

```bash
# Install FlashFlow CLI
pip install flashflow

# Create a new project
flashflow new myproject

# Navigate to your project
cd myproject

# Install dependencies
flashflow install core

# Build your application
flashflow build

# Run the development server
flashflow serve --all
```

Visit `http://localhost:8000` to see your new FlashFlow application!

## 🌟 Key Features

- **Single Syntax Development**: Define your entire application with `.flow` files
- **Cross-Platform Generation**: Create web (React), mobile (Flet), desktop (Flet), and backend (Laravel) apps from one codebase
- **Built-in Testing**: Comprehensive testing framework included
- **Smart AI Features**: AI-powered smart forms and automation
- **Enterprise Ready**: Built-in authentication, payments, SMS, file storage, and more
- **Multiple Deployment Options**: Standard hosting, edge network, or VPS with FranklinPHP
- **Laravel-like Welcome Message**: Familiar onboarding experience for new projects
- **SEO Optimized**: Automatic meta tags, structured data, and performance optimization
- **Instant Deployment**: Deploy with a single command

## 📁 Project Structure

```
myproject/
├── src/
│   ├── flows/           # FlashFlow definition files (.flow)
│   ├── components/      # Reusable UI components
│   ├── tests/           # Test files (.testflow)
│   └── models/          # Data models
├── dist/               # Generated application code
├── flashflow.json      # Project configuration
└── README.md           # Project documentation
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install FlashFlow CLI
```bash
pip install flashflow
```

### Verify Installation
```bash
flashflow --version
```

## 📖 Documentation

### Getting Started
1. [Introduction to FlashFlow](docs/index.md)
2. [Installation Guide](docs/SYSTEM_WIDE_INSTALLATION.md)
3. [Quick Start Tutorial](docs/STEP_BY_STEP_GUIDE.md)
4. [Understanding .flow Files](docs/FLASHFLOW_QUICK_REFERENCE.md)

### Core Concepts
- [Models](docs/DEVELOPER_GUIDE.md) - Define your data structures
- [Pages](docs/DEVELOPER_GUIDE.md) - Create user interfaces
- [Endpoints](docs/API_REFERENCE.md) - Build APIs automatically
- [Themes](docs/DEVELOPER_GUIDE.md) - Customize the look and feel

### Platform Guides
- [Web Applications](docs/DEVELOPER_GUIDE.md) - Build responsive web apps with React
- [Mobile Applications](docs/DEVELOPER_GUIDE.md) - Create iOS and Android apps with Flet
- [Desktop Applications](docs/DEVELOPER_GUIDE.md) - Build cross-platform desktop apps
- [Backend Services](docs/DEVELOPER_GUIDE.md) - Generate Laravel APIs and databases

### Advanced Features
- [SEO Optimization](docs/FLASHFLOW_SEO_GUIDE.md) - Improve search engine visibility
- [Internationalization](docs/DEVELOPER_GUIDE.md) - Support multiple languages
- [Payments Integration](docs/DEVELOPER_GUIDE.md) - Add payment processing
- [Deployment Options](docs/DEPLOYMENT_GUIDE.md) - Deploy to various environments

### Specialized Guides
- [Building an Uber-like App](docs/UBER_LIKE_APP_GUIDE.md)
- [GitHub Integration](docs/github-integration.md)
- [FranklinPHP Deployment](docs/FRANKLINPHP_DEPLOYMENT_GUIDE.md)
- [Team Management](docs/TEAM_MANAGEMENT.md)

## 🚀 Example

Create a simple todo application with a single `.flow` file:

```flow
model Todo {
  task_name: string required
  is_completed: boolean default:false
  created_at: timestamp auto
}

page Home {
  title: "My Todo List"
  route: "/todos"
  
  list Todo {
    checkbox task_name {
      checked: is_completed
      action: toggle_todo
    }
    
    button "Delete" {
      action: delete_todo
      style: danger
    }
  }
  
  form Todo {
    input task_name {
      placeholder: "What needs to be done?"
      required: true
    }
    
    button "Add Todo"
  }
}
```

## 📦 Commands

| Command | Description |
|---------|-------------|
| `flashflow new <project>` | Create a new FlashFlow project |
| `flashflow build` | Generate application code |
| `flashflow serve [--all]` | Run unified development server |
| `flashflow test` | Run all tests |
| `flashflow deploy` | Deploy to production |
| `flashflow install <package>` | Install dependencies |

## 🌐 Deployment Options

- **Standard Hosting**: Deploy to traditional web hosts
- **Edge Networks**: Deploy to global CDN with edge computing
- **VPS with FranklinPHP**: Deploy to virtual private servers
- **Cloud Platforms**: Deploy to AWS, Google Cloud, Azure

## 🤝 Contributing

We welcome contributions to FlashFlow! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape FlashFlow
- Inspired by the need for faster, more efficient full-stack development
- Built with modern technologies like React, Flet, Laravel, and FranklinPHP

## 📞 Support

- [Documentation](https://docs.flashflow.dev)
- [GitHub Issues](https://github.com/boifagusy/flashflow/issues)
- [Community Forum](https://community.flashflow.dev)
- [Twitter](https://twitter.com/flashflow)

---

<p align="center">
  Built with ❤️ by the FlashFlow Team
</p>