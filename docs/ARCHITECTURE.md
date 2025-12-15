# FlashFlow Architecture

This document explains the architecture of the FlashFlow system and how the different components interact.

## System Overview

FlashFlow consists of several interconnected components that work together to provide a full-stack development experience:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DEVELOPMENT MODE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────────────┐   │
│  │   .flow     │    │                  │    │        LARAVEL           │   │
│  │   Files     │───▶│ FlashFlow Engine │◀──▶│        Backend           │   │
│  │             │    │                  │    │                          │   │
│  │(YAML/JSON)  │    │   (Python/Flet)  │    │    (PHP/FranklinPHP)     │   │
│  └─────────────┘    └──────────────────┘    └──────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                             PRODUCTION MODE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌──────────────────┐    ┌──────────────────────────┐   │
│  │   .flow     │    │                  │    │        LARAVEL           │   │
│  │   Files     │───▶│   Code Gen.      │───▶│        Backend           │   │
│  │             │    │                  │    │                          │   │
│  │(YAML/JSON)  │    │  (Go Services)   │    │    (PHP/FranklinPHP)     │   │
│  └─────────────┘    └──────────────────┘    └──────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FlashFlow Definition Files (.flow)
These are YAML-based files that define:
- Data models (similar to database schemas)
- User interface pages
- API endpoints
- Application configuration

Example:
```yaml
model:
  name: "User"
  fields:
    - name: "name"
      type: "string"
      required: true

page:
  title: "User List"
  path: "/users"
  body:
    - component: "list"
      data_source: "User"
```

### 2. FlashFlow Engine
A Python-based engine that can render .flow files directly without requiring a build step. It uses Flet as the underlying UI framework.

Key responsibilities:
- Parse .flow files
- Convert definitions to Flet UI components
- Handle routing between pages
- Communicate with backend via RESTful APIs
- Provide real-time rendering during development

### 3. Code Generation (Go Services)
In production mode, Go-based services generate optimized code for all platforms:
- Web (React/Vue)
- Mobile (iOS/Android)
- Desktop (Electron/Tauri)
- Backend (Laravel/Node.js)

### 4. Laravel Backend
The backend is generated from .flow files and provides:
- RESTful APIs
- Database operations
- Authentication
- Business logic

It runs on FranklinPHP for optimal performance and can be enhanced with GoFastHTTP.

### 5. FranklinPHP
A modern PHP application server that serves the Laravel backend with:
- High performance
- Built-in HTTP/2 and HTTPS support
- Automatic HTTPS with Let's Encrypt
- Optional GoFastHTTP integration for even better performance

## Data Flow

### Development Mode
1. Developer creates/modifies .flow files
2. FlashFlow Engine watches for changes
3. Engine parses files and converts to Flet components
4. UI updates in real-time
5. User interactions trigger API calls to Laravel backend
6. Backend processes requests and returns data

### Production Mode
1. .flow files are processed by Go code generation services
2. Optimized code is generated for all target platforms
3. Applications are built and deployed
4. Users interact with generated applications
5. Applications communicate with Laravel backend

## Technology Stack Integration

### Python Layer
- **FlashFlow Engine**: Real-time rendering during development
- **Flet**: Cross-platform UI framework
- **Requests**: HTTP client for API communication

### Go Layer
- **CLI Wrapper**: Command-line interface
- **Code Generation Services**: Transform .flow files to production code
- **Development Server**: Serve generated applications during development

### PHP Layer
- **Laravel Backend**: Generated from .flow files
- **FranklinPHP**: High-performance application server
- **GoFastHTTP**: Optional performance enhancement

## Deployment Options

### 1. Development Deployment
- FlashFlow Engine runs locally
- Laravel backend runs on FranklinPHP
- Real-time updates as .flow files change

### 2. Production Deployment
- Code generation creates optimized applications
- Applications deployed to respective platforms
- Laravel backend deployed with FranklinPHP
- Optional GoFastHTTP for high-concurrency scenarios

## Benefits

1. **Rapid Development**: Direct rendering without build steps
2. **Single Source of Truth**: One .flow file defines entire application
3. **Multi-platform**: Generate code for web, mobile, and desktop from same source
4. **Performance**: Go services and GoFastHTTP for high performance
5. **Flexibility**: Choice between direct rendering (development) and code generation (production)
6. **Scalability**: Easy horizontal scaling with containerization