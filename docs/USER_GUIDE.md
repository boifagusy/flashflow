ee# FlashFlow User Guide

Welcome to FlashFlow, the revolutionary single-syntax full-stack framework that generates complete applications from `.flow` files. This guide will walk you through everything you need to know to start building applications with FlashFlow.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Your First Project](#creating-your-first-project)
3. [Understanding .flow Files](#understanding-flow-files)
4. [Building and Running Your Application](#building-and-running-your-application)
5. [Core Concepts](#core-concepts)
6. [Advanced Features](#advanced-features)
7. [Testing Your Applications](#testing-your-applications)
8. [Deployment](#deployment)

## Getting Started

### Prerequisites

Before installing FlashFlow, ensure you have the following installed:
- Python 3.8 or higher
- Node.js 14 or higher (for frontend development)
- PHP 8.0 or higher (for backend development)
- Composer (for PHP dependencies)
- SQLite (default database) or MySQL/PostgreSQL

### Installation

1. Clone the FlashFlow repository:
```bash
git clone https://github.com/yourusername/flashflow.git
cd flashflow
```

2. Install FlashFlow in development mode:
```bash
pip install -e .
```

3. Verify installation:
```bash
flashflow --version
```

## Creating Your First Project

### Creating a New Project

To create a new FlashFlow project, use the `new` command:

```bash
flashflow new my-first-app
cd my-first-app
```

This creates a new directory with the basic project structure:

```
my-first-app/
├── flashflow.json     # Project configuration
├── src/              # Source directory
│   └── flows/        # Your .flow files go here
└── dist/             # Generated code (created after build)
    ├── backend/      # Laravel/PHP backend code
    ├── frontend/     # React/PWA frontend code
    └── mobile/       # Flet mobile app code
```

Note: The `dist/` directory is created when you run `flashflow build`. Initially, it won't exist until you generate code.

### Project Templates

FlashFlow comes with several templates to help you get started:

```bash
# Create a project with the todo template
flashflow new my-todo-app --template todo

# Create a project with the blog template
flashflow new my-blog --template blog

# Create a project with the e-commerce template
flashflow new my-store --template ecommerce
```

### Project Configuration

The `flashflow.json` file contains your project configuration:

```json
{
  "name": "my-first-app",
  "version": "0.1.0",
  "description": "My first FlashFlow application",
  "author": "Your Name",
  "frameworks": {
    "backend": "laravel",
    "frontend": "react",
    "mobile": "flet",
    "database": "sqlite"
  },
  "dependencies": []
}
```

## Understanding .flow Files

.flow files are the heart of FlashFlow. They use YAML syntax to define your entire application in one place.

### Basic Structure

A typical .flow file has this structure:

```yaml
# Application metadata
name: "My Application"
version: "1.0.0"
description: "A sample FlashFlow application"

# Data models
model:
  name: "User"
  fields:
    - name: "username"
      type: "string"
      required: true
      unique: true
    - name: "email"
      type: "string"
      required: true
    - name: "created_at"
      type: "datetime"
      default: "now"

# User interface
page:
  title: "User Dashboard"
  path: "/dashboard"
  layout: "default"
  body:
    - component: "header"
      content: "Welcome to Your Dashboard"
    - component: "card"
      title: "User Information"
      content: "{{ user.username }}"

# API endpoints
endpoint:
  path: "/api/users"
  method: "GET"
  auth: "jwt"
  response:
    type: "array"
    model: "User"
```

### Models

Models define your data structure:

```yaml
model:
  name: "Product"
  fields:
    - name: "name"
      type: "string"
      required: true
    - name: "price"
      type: "decimal"
      required: true
    - name: "description"
      type: "text"
    - name: "category"
      type: "string"
      enum: ["electronics", "clothing", "books"]
    - name: "in_stock"
      type: "boolean"
      default: true
    - name: "created_at"
      type: "datetime"
      default: "now"
```

### Pages

Pages define your user interface:

```yaml
page:
  title: "Product Catalog"
  path: "/products"
  layout: "default"
  auth: true
  body:
    - component: "navbar"
      items:
        - label: "Home"
          link: "/"
        - label: "Products"
          link: "/products"
    - component: "hero"
      title: "Our Products"
      subtitle: "Browse our amazing collection"
    - component: "product_list"
      data_source: "Product"
      filters:
        - field: "category"
          type: "select"
        - field: "price"
          type: "range"
```

### Endpoints

Endpoints define your API:

```yaml
endpoint:
  path: "/api/products"
  method: "POST"
  auth: "jwt"
  rate_limit: "100/hour"
  request:
    type: "object"
    model: "Product"
  response:
    type: "object"
    model: "Product"
  handler:
    action: "create_record"
    model: "Product"
```

## Building and Running Your Application

### Installing Dependencies

Before building, install the required dependencies:

```bash
flashflow install core
```

This command installs all dependencies for the backend, frontend, and mobile components.

### Building Your Application

Generate all code from your .flow files:

```bash
flashflow build
```

This command generates:
- Backend API code (Laravel/PHP)
- Frontend application (React/PWA)
- Mobile applications (Flet/Python)
- Database migrations
- API documentation

After building, your project structure will look like:

```
my-first-app/
├── flashflow.json
├── src/
│   └── flows/
│       ├── todo.flow
│       └── ... other .flow files
└── dist/
    ├── backend/
    │   ├── app/
    │   ├── config/
    │   ├── database/
    │   ├── routes/
    │   ├── .env
    │   └── ... Laravel files
    ├── frontend/
    │   ├── src/
    │   │   ├── components/
    │   │   ├── pages/
    │   │   └── services/
    │   ├── public/
    │   ├── package.json
    │   └── vite.config.js
    └── mobile/
        ├── main.py
        └── ... Flet files
```

### Running the Development Server

Start the unified development server:

```bash
flashflow serve --all
```

This starts a server that serves all platforms:
- Web application: http://localhost:8000
- API documentation: http://localhost:8000/api/docs
- Mobile previews: http://localhost:8000/android, http://localhost:8000/ios
- Admin panel: http://localhost:8000/admin

### Hot Reload

During development, FlashFlow supports hot reload:

```bash
flashflow serve --hot
```

Changes to .flow files are automatically detected and the application is rebuilt.

## Core Concepts

### Single Source of Truth

FlashFlow maintains a single source of truth for your application:
- Data models are defined once and used everywhere
- UI components are automatically generated from models
- API endpoints are synchronized with models
- Database schema is automatically generated

### Unified Development Experience

FlashFlow provides a unified development experience:
- Single command to run everything
- Single configuration file
- Single syntax for all platforms
- Single testing framework

### Extensibility

FlashFlow is designed to be extensible:
- Custom components can be added
- New platforms can be supported
- Plugins can extend functionality
- Integrations with third-party services

## Advanced Features

### Real-time Applications (.liveflow)

Create real-time applications with .liveflow files:

```yaml
# chat.liveflow
realtime:
  name: "Chat Application"
  channels:
    - name: "room"
      events:
        - name: "message_sent"
          payload:
            - field: "user_id"
              type: "string"
            - field: "message"
              type: "string"
```

### Background Jobs (.jobflow)

Define background jobs with .jobflow files:

```yaml
# tasks.jobflow
job:
  name: "Send Email Notifications"
  schedule: "every_10_minutes"
  handler:
    service: "mail"
    action: "send_bulk"
    template: "notification"
```

### Serverless Functions (.serverless)

Create serverless functions:

```yaml
# functions.serverless
function:
  name: "process_image"
  runtime: "python"
  trigger: "http"
  handler: "image_processor.handler"
```

### Smart Forms

FlashFlow supports smart forms with automatic validation:

```yaml
form:
  name: "user_registration"
  fields:
    - name: "email"
      type: "email"
      required: true
      validation:
        - rule: "unique"
          model: "User"
          field: "email"
    - name: "password"
      type: "password"
      required: true
      validation:
        - rule: "min_length"
          value: 8
        - rule: "complexity"
          requirements: ["uppercase", "lowercase", "number", "special"]
```

## Testing Your Applications

### Writing Tests (.testflow)

Create tests using .testflow files:

```yaml
# user.testflow
test:
  name: "User Registration Test"
  description: "Test user registration functionality"
  steps:
    - action: "visit"
      url: "/register"
    - action: "fill"
      field: "email"
      value: "test@example.com"
    - action: "fill"
      field: "password"
      value: "SecurePass123!"
    - action: "click"
      element: "submit_button"
    - action: "assert"
      condition: "status_code"
      value: 201
```

### Running Tests

Run all tests:

```bash
flashflow test
```

Run specific tests:

```bash
flashflow test --file user.testflow
flashflow test --tag integration
```

## Deployment

### Building for Production

Create a production build:

```bash
flashflow build --production
```

This optimizes all code for production deployment.

### Deploying Applications

Deploy your application:

```bash
flashflow deploy --all
```

This deploys:
- Backend API to your configured hosting
- Frontend to a CDN or static hosting
- Mobile apps to app stores
- Database to your production database

### Environment Configuration

Configure different environments:

```bash
# Development
flashflow serve --env development

# Staging
flashflow deploy --env staging

# Production
flashflow deploy --env production
```

## Next Steps

1. Explore the [examples](../examples/) directory for more .flow file examples
2. Read the [Developer Guide](DEVELOPER_GUIDE.md) to learn how to extend FlashFlow
3. Check the [API Reference](API_REFERENCE.md) for detailed command documentation
4. Review the [Deployment Guide](DEPLOYMENT_GUIDE.md) for production deployment strategies

## Getting Help

- Join our [community](https://github.com/yourusername/flashflow/discussions)
- Report issues on [GitHub](https://github.com/yourusername/flashflow/issues)
- Read the [documentation](https://yourusername.github.io/flashflow)