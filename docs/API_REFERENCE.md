# FlashFlow API Reference

This document provides detailed reference information for all FlashFlow commands, configuration options, and APIs.

## Table of Contents

1. [CLI Commands](#cli-commands)
2. [Configuration Files](#configuration-files)
3. [.flow File Syntax](#flow-file-syntax)
4. [.testflow File Syntax](#testflow-file-syntax)
5. [.liveflow File Syntax](#liveflow-file-syntax)
6. [.jobflow File Syntax](#jobflow-file-syntax)
7. [.serverless File Syntax](#serverless-file-syntax)
8. [Environment Variables](#environment-variables)
9. [API Endpoints](#api-endpoints)

## CLI Commands

### flashflow

The main FlashFlow command.

```bash
flashflow [OPTIONS] COMMAND [ARGS]...
```

**Options:**
- `--version`: Show the version and exit
- `--help`: Show this message and exit

**Commands:**
- [new](#flashflow-new): Create a new FlashFlow project
- [install](#flashflow-install): Install project dependencies
- [build](#flashflow-build): Generate application code
- [serve](#flashflow-serve): Start development server
- [test](#flashflow-test): Run tests
- [deploy](#flashflow-deploy): Deploy application
- [migrate](#flashflow-migrate): Run database migrations
- [setup](#flashflow-setup): Setup project configuration
- [config](#flashflow-config): Manage configuration
- [doctor](#flashflow-doctor): Diagnose project issues

### flashflow new

Create a new FlashFlow project.

```bash
flashflow new [OPTIONS] PROJECT_NAME
```

**Arguments:**
- `PROJECT_NAME`: Name of the new project

**Options:**
- `--template TEXT`: Project template to use (todo, blog, ecommerce)
- `--description TEXT`: Project description
- `--author TEXT`: Project author
- `--framework-backend TEXT`: Backend framework (laravel)
- `--framework-frontend TEXT`: Frontend framework (react)
- `--framework-mobile TEXT`: Mobile framework (flet)
- `--database TEXT`: Database type (sqlite, mysql, postgresql)
- `--help`: Show this message and exit

**Examples:**
```bash
# Create a basic project
flashflow new myapp

# Create a project with todo template
flashflow new my-todo-app --template todo

# Create a project with custom configuration
flashflow new myapp --author "John Doe" --description "My awesome app"
```

### flashflow install

Install project dependencies.

```bash
flashflow install [OPTIONS] [DEPENDENCIES]...
```

**Arguments:**
- `DEPENDENCIES`: Specific dependencies to install

**Options:**
- `--core`: Install core dependencies
- `--dev`: Install development dependencies
- `--all`: Install all dependencies
- `--help`: Show this message and exit

**Examples:**
```bash
# Install core dependencies
flashflow install core

# Install specific dependencies
flashflow install react-router axios

# Install all dependencies
flashflow install --all
```

### flashflow build

Generate application code from .flow files.

```bash
flashflow build [OPTIONS]
```

**Options:**
- `--production`: Build for production environment
- `--watch`: Watch for file changes and rebuild
- `--clean`: Clean build directory before building
- `--platform TEXT`: Build for specific platform (backend, frontend, mobile)
- `--verbose`: Show detailed build output
- `--help`: Show this message and exit

**Examples:**
```bash
# Build all platforms
flashflow build

# Build for production
flashflow build --production

# Build only backend
flashflow build --platform backend

# Watch for changes
flashflow build --watch
```

### flashflow serve

Start the development server.

```bash
flashflow serve [OPTIONS]
```

**Options:**
- `--all`: Serve all platforms
- `--backend`: Serve backend only
- `--frontend`: Serve frontend only
- `--mobile`: Serve mobile apps
- `--port INTEGER`: Port to serve on (default: 8000)
- `--host TEXT`: Host to serve on (default: localhost)
- `--hot`: Enable hot reload
- `--verbose`: Show detailed server output
- `--help`: Show this message and exit

**Examples:**
```bash
# Serve all platforms
flashflow serve --all

# Serve on custom port
flashflow serve --all --port 3000

# Serve with hot reload
flashflow serve --all --hot

# Serve only frontend
flashflow serve --frontend
```

### flashflow test

Run tests for the project.

```bash
flashflow test [OPTIONS]
```

**Options:**
- `--file TEXT`: Specific test file to run
- `--tag TEXT`: Run tests with specific tag
- `--verbose`: Show detailed test output
- `--coverage`: Generate coverage report
- `--help`: Show this message and exit

**Examples:**
```bash
# Run all tests
flashflow test

# Run specific test file
flashflow test --file user.testflow

# Run tests with tag
flashflow test --tag integration

# Generate coverage report
flashflow test --coverage
```

### flashflow deploy

Deploy the application.

```bash
flashflow deploy [OPTIONS]
```

**Options:**
- `--all`: Deploy all platforms
- `--backend`: Deploy backend only
- `--frontend`: Deploy frontend only
- `--mobile`: Deploy mobile apps
- `--env TEXT`: Environment to deploy to (development, staging, production)
- `--provider TEXT`: Cloud provider (aws, gcp, azure, netlify, vercel)
- `--help`: Show this message and exit

**Examples:**
```bash
# Deploy entire application
flashflow deploy --all

# Deploy to production
flashflow deploy --all --env production

# Deploy backend to AWS
flashflow deploy --backend --provider aws

# Deploy frontend to Netlify
flashflow deploy --frontend --provider netlify
```

### flashflow migrate

Run database migrations.

```bash
flashflow migrate [OPTIONS]
```

**Options:**
- `--up`: Run migrations up
- `--down`: Rollback migrations
- `--status`: Show migration status
- `--create TEXT`: Create new migration
- `--help`: Show this message and exit

**Examples:**
```bash
# Run all pending migrations
flashflow migrate

# Rollback last migration
flashflow migrate --down

# Show migration status
flashflow migrate --status

# Create new migration
flashflow migrate --create create_users_table
```

### flashflow setup

Setup project configuration.

```bash
flashflow setup [OPTIONS]
```

**Options:**
- `--gui`: Use web-based setup wizard
- `--interactive`: Interactive setup
- `--defaults`: Use default configuration
- `--help`: Show this message and exit

**Examples:**
```bash
# Interactive setup
flashflow setup --interactive

# Web-based setup
flashflow setup --gui

# Use defaults
flashflow setup --defaults
```

### flashflow config

Manage project configuration.

```bash
flashflow config [OPTIONS] COMMAND [ARGS]...
```

**Commands:**
- `show`: Show current configuration
- `set`: Set configuration value
- `get`: Get configuration value
- `edit`: Edit configuration file
- `validate`: Validate configuration

**Examples:**
```bash
# Show configuration
flashflow config show

# Set configuration value
flashflow config set DB_HOST=localhost

# Get configuration value
flashflow config get DB_HOST

# Edit configuration
flashflow config edit
```

### flashflow doctor

Diagnose project issues.

```bash
flashflow doctor [OPTIONS]
```

**Options:**
- `--verbose`: Show detailed diagnosis
- `--fix`: Attempt to fix issues automatically
- `--help`: Show this message and exit

**Examples:**
```bash
# Run diagnosis
flashflow doctor

# Run detailed diagnosis
flashflow doctor --verbose

# Fix issues automatically
flashflow doctor --fix
```

## Configuration Files

### flashflow.json

Main project configuration file.

```json
{
  "name": "string",
  "version": "string",
  "description": "string",
  "author": "string",
  "frameworks": {
    "backend": "string",
    "frontend": "string",
    "mobile": "string",
    "database": "string"
  },
  "dependencies": ["string"],
  "environments": {
    "development": {},
    "staging": {},
    "production": {}
  }
}
```

**Properties:**
- `name`: Project name
- `version`: Project version
- `description`: Project description
- `author`: Project author
- `frameworks`: Framework configuration
- `dependencies`: Project dependencies
- `environments`: Environment-specific configuration

### .flashflowrc

User-level configuration file.

```json
{
  "default_template": "string",
  "editor": "string",
  "github_token": "string",
  "cloud_providers": {}
}
```

## .flow File Syntax

.flow files define your application using YAML syntax.

### Basic Structure

```yaml
# Application metadata
name: "string"
version: "string"
description: "string"

# Data models
model:
  name: "string"
  fields:
    - name: "string"
      type: "string"
      required: boolean
      unique: boolean
      default: "any"
      validation: []

# User interface
page:
  title: "string"
  path: "string"
  layout: "string"
  auth: boolean|string
  body: []

# API endpoints
endpoint:
  path: "string"
  method: "string"
  auth: "string"
  rate_limit: "string"
  request: {}
  response: {}
  handler: {}
```

### Model Fields

Supported field types:
- `string`: Text field
- `text`: Long text field
- `integer`: Integer number
- `decimal`: Decimal number
- `boolean`: True/false value
- `datetime`: Date and time
- `date`: Date only
- `time`: Time only
- `email`: Email address
- `url`: Web URL
- `uuid`: UUID identifier
- `json`: JSON data

Field properties:
- `name`: Field name
- `type`: Field type
- `required`: Required field
- `unique`: Unique constraint
- `default`: Default value
- `validation`: Validation rules

### Validation Rules

```yaml
validation:
  - rule: "min_length"
    value: 8
  - rule: "max_length"
    value: 255
  - rule: "email"
  - rule: "url"
  - rule: "regex"
    pattern: "^[A-Za-z0-9]+$"
  - rule: "enum"
    values: ["option1", "option2"]
```

### Page Components

Supported components:
- `header`: Page header
- `navbar`: Navigation bar
- `hero`: Hero section
- `card`: Card component
- `list`: List component
- `form`: Form component
- `table`: Table component
- `chart`: Chart component
- `button`: Button component
- `input`: Input field
- `select`: Select dropdown
- `textarea`: Text area
- `checkbox`: Checkbox
- `radio`: Radio button

### Endpoint Handlers

Handler actions:
- `create_record`: Create database record
- `read_record`: Read database record
- `update_record`: Update database record
- `delete_record`: Delete database record
- `list_records`: List database records
- `custom`: Custom handler

## .testflow File Syntax

.testflow files define automated tests.

### Basic Structure

```yaml
test:
  name: "string"
  description: "string"
  tags: ["string"]
  environment: "string"
  steps: []
```

### Test Steps

Supported steps:
- `visit`: Navigate to URL
- `fill`: Fill form field
- `click`: Click element
- `assert`: Assert condition
- `wait`: Wait for condition
- `screenshot`: Take screenshot
- `api_call`: Make API call

### Assert Conditions

```yaml
assert:
  condition: "status_code"
  value: 200

assert:
  condition: "contains_text"
  selector: ".message"
  text: "Success"

assert:
  condition: "element_exists"
  selector: "#submit-button"
```

## .liveflow File Syntax

.liveflow files define real-time applications.

### Basic Structure

```yaml
realtime:
  name: "string"
  description: "string"
  channels: []
  events: []
```

### Channels

```yaml
channels:
  - name: "string"
    auth: boolean
    presence: boolean
  - name: "string"
    events: []
```

### Events

```yaml
events:
  - name: "string"
    payload:
      - field: "string"
        type: "string"
    handler: "string"
```

## .jobflow File Syntax

.jobflow files define background jobs.

### Basic Structure

```yaml
job:
  name: "string"
  description: "string"
  schedule: "string"
  handler: {}
```

### Schedule Formats

- `every_minute`: Every minute
- `every_5_minutes`: Every 5 minutes
- `every_hour`: Every hour
- `every_day`: Every day
- `every_week`: Every week
- `cron(0 0 * * *)`: Cron expression

## .serverless File Syntax

.serverless files define serverless functions.

### Basic Structure

```yaml
function:
  name: "string"
  description: "string"
  runtime: "string"
  trigger: "string"
  handler: "string"
  timeout: integer
  memory: integer
```

### Runtime Options

- `python`: Python runtime
- `nodejs`: Node.js runtime
- `php`: PHP runtime
- `go`: Go runtime

### Trigger Options

- `http`: HTTP trigger
- `schedule`: Scheduled trigger
- `event`: Event trigger
- `webhook`: Webhook trigger

## Environment Variables

### Core Variables

- `FLASHFLOW_ENV`: Environment (development, staging, production)
- `FLASHFLOW_DEBUG`: Debug mode (true/false)
- `FLASHFLOW_LOG_LEVEL`: Log level (debug, info, warning, error)

### Database Variables

- `DB_CONNECTION`: Database type (sqlite, mysql, postgresql)
- `DB_HOST`: Database host
- `DB_PORT`: Database port
- `DB_DATABASE`: Database name
- `DB_USERNAME`: Database username
- `DB_PASSWORD`: Database password

### Cache Variables

- `CACHE_DRIVER`: Cache driver (file, redis, memcached)
- `REDIS_HOST`: Redis host
- `REDIS_PORT`: Redis port
- `REDIS_PASSWORD`: Redis password

### Mail Variables

- `MAIL_MAILER`: Mail driver (smtp, mailgun, ses)
- `MAIL_HOST`: Mail host
- `MAIL_PORT`: Mail port
- `MAIL_USERNAME`: Mail username
- `MAIL_PASSWORD`: Mail password
- `MAIL_ENCRYPTION`: Mail encryption (tls, ssl)

### Cloud Provider Variables

AWS:
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_DEFAULT_REGION`: AWS region

Google Cloud:
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key

## API Endpoints

### Development Server Endpoints

When running `flashflow serve --all`, the following endpoints are available:

#### Main Application
- `GET /`: Welcome page
- `GET /dashboard`: User dashboard

#### API Endpoints
- `GET /api/docs`: API documentation
- `GET /api/tester`: API testing tool
- `GET /api/health`: Health check

#### Admin Panel
- `GET /admin/cpanel`: Admin control panel
- `GET /admin/users`: User management
- `GET /admin/settings`: System settings

#### Mobile Previews
- `GET /android`: Android app preview
- `GET /ios`: iOS app preview

#### Development Tools
- `GET /dev/logs`: Application logs
- `GET /dev/metrics`: Performance metrics
- `GET /dev/debug`: Debug information

### Generated API Endpoints

Based on your .flow files, FlashFlow generates REST API endpoints:

#### CRUD Operations
- `GET /api/{model}`: List records
- `POST /api/{model}`: Create record
- `GET /api/{model}/{id}`: Get record
- `PUT /api/{model}/{id}`: Update record
- `DELETE /api/{model}/{id}`: Delete record

#### Authentication Endpoints
- `POST /api/auth/login`: User login
- `POST /api/auth/register`: User registration
- `POST /api/auth/logout`: User logout
- `POST /api/auth/password-reset`: Password reset request
- `POST /api/auth/password-reset/confirm`: Password reset confirmation

#### File Upload Endpoints
- `POST /api/upload`: File upload
- `GET /api/files/{id}`: Get file
- `DELETE /api/files/{id}`: Delete file

### API Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": {},
  "message": "string",
  "errors": [],
  "meta": {}
}
```

### Error Response Format

```json
{
  "success": false,
  "data": null,
  "message": "Error description",
  "errors": [
    {
      "field": "field_name",
      "message": "Error message"
    }
  ],
  "meta": {}
}
```

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Unprocessable Entity
- `429`: Too Many Requests
- `500`: Internal Server Error

## Best Practices

### CLI Usage

1. Always check the help output: `flashflow --help`
2. Use verbose mode for debugging: `flashflow build --verbose`
3. Validate configuration before deployment: `flashflow config validate`
4. Run diagnostics regularly: `flashflow doctor`

### File Organization

1. Keep .flow files organized by feature
2. Use descriptive names for files
3. Group related functionality together
4. Document complex configurations

### Error Handling

1. Check return codes from commands
2. Use try-catch blocks in custom code
3. Log errors with appropriate detail
4. Provide user-friendly error messages

## Troubleshooting

### Common Issues

1. **Command not found**: Ensure FlashFlow is installed and in PATH
2. **Permission denied**: Check file permissions and run with appropriate privileges
3. **Dependency issues**: Run `flashflow install --all` to install dependencies
4. **Configuration errors**: Validate configuration with `flashflow config validate`

### Getting Help

1. Check the help output: `flashflow COMMAND --help`
2. Review documentation: [User Guide](USER_GUIDE.md)
3. Check examples in the `examples/` directory
4. Report issues on GitHub

## Further Reading

- [User Guide](USER_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Extension Guide](EXTENSION_GUIDE.md)