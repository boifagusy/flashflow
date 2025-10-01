# FlashFlow Quick Reference Card

## Essential Commands

### Project Management
```bash
flashflow new <project-name>          # Create new project
flashflow install core                # Install dependencies
flashflow build                       # Generate application code
flashflow serve --all                 # Start development server
flashflow test                        # Run tests
flashflow deploy                      # Deploy to production
```

### Development Workflow
```bash
flashflow build --watch               # Auto-rebuild on changes
flashflow serve --port 3000           # Use custom port
flashflow migrate                     # Run database migrations
flashflow doctor                      # Diagnose issues
```

## Project Structure

```
my-project/
├── flashflow.json     # Configuration
├── src/
│   └── flows/        # .flow files
└── dist/             # Generated code
    ├── backend/
    ├── frontend/
    └── mobile/
```

## .flow File Syntax

### Basic Model
```yaml
model:
  name: "User"
  fields:
    - name: "email"
      type: "string"
      required: true
      unique: true
    - name: "created_at"
      type: "timestamp"
      auto: true
```

### Basic Page
```yaml
page:
  title: "Home"
  path: "/"
  body:
    - component: "header"
      content: "Welcome"
```

### Basic Endpoint
```yaml
endpoint:
  path: "/api/users"
  method: "GET"
  response:
    type: "array"
    model: "User"
```

## Authentication

```yaml
authentication:
  providers:
    - name: "local"
      type: "email_password"
  jwt:
    secret: "{{ env.JWT_SECRET }}"
  roles:
    - name: "admin"
      permissions: ["user.*"]
    - name: "user"
      permissions: ["content.read"]
```

## Common Field Types

- `string` - Text data
- `integer` - Whole numbers
- `decimal` - Decimal numbers
- `boolean` - True/false
- `timestamp` - Date/time
- `uuid` - Unique ID
- `json` - JSON data
- `foreign_key` - References

## Page Protection

```yaml
page:
  auth:
    required: true
    roles:
      - "admin"
```

## API Protection

```yaml
endpoint:
  auth:
    required: true
    permissions:
      - "user.read"
```

## Testing

```yaml
test:
  name: "User Login"
  steps:
    - action: "visit"
      url: "/login"
    - action: "fill"
      field: "email"
      value: "user@example.com"
    - action: "click"
      element: "submit"
    - action: "assert"
      condition: "redirected_to"
      value: "/dashboard"
```

## Quick Tips

1. **Always run `flashflow build`** after changing .flow files
2. **Use `flashflow serve --all`** for unified development
3. **Check `/api/docs`** for auto-generated API documentation
4. **Use `/api/tester`** to test endpoints
5. **Run `flashflow test`** before committing
6. **Use `flashflow doctor`** to diagnose issues

## Common URLs

- Web App: http://localhost:8000
- Admin Panel: http://localhost:8000/admin/cpanel
- API Docs: http://localhost:8000/api/docs
- API Tester: http://localhost:8000/api/tester
- Mobile Preview: http://localhost:8000/android

## Environment Variables

Create `.env` from `.env.example`:
```bash
cp .env.example .env
# Then edit .env with your values
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not in FlashFlow project" | Run `flashflow new` first |
| Build errors | Check .flow file syntax |
| Port conflicts | Use `--port` flag |
| Database issues | Run `flashflow migrate` |

## Learning Resources

- [User Guide](docs/USER_GUIDE.md)
- [Developer Productivity Guide](docs/DEVELOPER_PRODUCTIVITY_GUIDE.md)
- [Examples](examples/)
- [API Reference](docs/API_REFERENCE.md)