# Documentation to FlashFlow Converter

This guide explains how to convert existing project documentation into FlashFlow buildable format using a structured JSON prompt.

## JSON Prompt Template

Use this template to convert your documentation into FlashFlow .flow files:

```json
{
  "project_info": {
    "name": "Your Project Name",
    "description": "Brief description of your project",
    "version": "1.0.0"
  },
  "models": [
    {
      "name": "ModelName",
      "description": "Description of what this model represents",
      "fields": [
        {
          "name": "field_name",
          "type": "string|integer|boolean|date|text",
          "required": true,
          "description": "Purpose of this field"
        }
      ]
    }
  ],
  "pages": [
    {
      "title": "Page Title",
      "path": "/page-url",
      "description": "What this page does",
      "components": [
        {
          "type": "component_type",
          "props": {
            "property": "value"
          }
        }
      ]
    }
  ],
  "endpoints": [
    {
      "path": "/api/endpoint",
      "method": "GET|POST|PUT|DELETE",
      "description": "What this endpoint does",
      "parameters": [
        {
          "name": "param_name",
          "type": "string|integer|boolean",
          "required": true,
          "description": "Purpose of this parameter"
        }
      ]
    }
  ],
  "authentication": {
    "required": true,
    "type": "jwt|oauth|session",
    "providers": ["google", "facebook"]
  },
  "ui_requirements": [
    {
      "feature": "Feature name",
      "description": "How this feature should work",
      "components": ["component_types_needed"]
    }
  ],
  "business_logic": [
    {
      "process": "Process name",
      "steps": ["Step 1", "Step 2"],
      "triggers": ["When this happens"]
    }
  ]
}
```

## Example Conversion

### Sample Documentation:
```
User Management System
=====================

We need a system to manage users with the following requirements:

1. User Model:
   - Name (required)
   - Email (required, unique)
   - Password (required)
   - Role (admin, user, guest)
   - Created Date

2. Pages:
   - User List (/users): Shows all users in a table
   - User Detail (/users/{id}): Shows details for one user
   - User Form (/users/new, /users/{id}/edit): Create/edit users

3. API Endpoints:
   - GET /api/users: List all users
   - GET /api/users/{id}: Get specific user
   - POST /api/users: Create new user
   - PUT /api/users/{id}: Update user
   - DELETE /api/users/{id}: Delete user

4. Authentication:
   - Required for all pages and endpoints
   - JWT token based
   - Google OAuth login option

5. UI Requirements:
   - Responsive design
   - User table with search and filter
   - Form validation
   - Loading states
```

### Converted JSON Prompt:
```json
{
  "project_info": {
    "name": "User Management System",
    "description": "A system to manage users with authentication and CRUD operations",
    "version": "1.0.0"
  },
  "models": [
    {
      "name": "User",
      "description": "Represents a user in the system",
      "fields": [
        {
          "name": "name",
          "type": "string",
          "required": true,
          "description": "User's full name"
        },
        {
          "name": "email",
          "type": "string",
          "required": true,
          "unique": true,
          "description": "User's email address"
        },
        {
          "name": "password",
          "type": "password",
          "required": true,
          "description": "Hashed user password"
        },
        {
          "name": "role",
          "type": "enum",
          "values": ["admin", "user", "guest"],
          "required": true,
          "description": "User's role in the system"
        },
        {
          "name": "created_date",
          "type": "datetime",
          "required": true,
          "description": "When the user was created"
        }
      ]
    }
  ],
  "pages": [
    {
      "title": "User List",
      "path": "/users",
      "description": "Shows all users in a table",
      "components": [
        {
          "type": "table",
          "props": {
            "data_source": "User",
            "searchable": true,
            "filterable": true
          }
        }
      ]
    },
    {
      "title": "User Detail",
      "path": "/users/{id}",
      "description": "Shows details for one user",
      "components": [
        {
          "type": "detail_view",
          "props": {
            "data_source": "User"
          }
        }
      ]
    },
    {
      "title": "User Form",
      "path": "/users/new",
      "description": "Create new user",
      "components": [
        {
          "type": "form",
          "props": {
            "data_source": "User",
            "mode": "create"
          }
        }
      ]
    },
    {
      "title": "User Edit Form",
      "path": "/users/{id}/edit",
      "description": "Edit existing user",
      "components": [
        {
          "type": "form",
          "props": {
            "data_source": "User",
            "mode": "edit"
          }
        }
      ]
    }
  ],
  "endpoints": [
    {
      "path": "/api/users",
      "method": "GET",
      "description": "List all users",
      "response": "Array of User objects"
    },
    {
      "path": "/api/users/{id}",
      "method": "GET",
      "description": "Get specific user",
      "response": "User object"
    },
    {
      "path": "/api/users",
      "method": "POST",
      "description": "Create new user",
      "parameters": [
        {
          "name": "user_data",
          "type": "object",
          "required": true,
          "description": "User data to create"
        }
      ]
    },
    {
      "path": "/api/users/{id}",
      "method": "PUT",
      "description": "Update user",
      "parameters": [
        {
          "name": "user_data",
          "type": "object",
          "required": true,
          "description": "User data to update"
        }
      ]
    },
    {
      "path": "/api/users/{id}",
      "method": "DELETE",
      "description": "Delete user"
    }
  ],
  "authentication": {
    "required": true,
    "type": "jwt",
    "providers": ["google"]
  },
  "ui_requirements": [
    {
      "feature": "Responsive Design",
      "description": "Layout should adapt to different screen sizes",
      "components": ["grid", "flexbox"]
    },
    {
      "feature": "User Table",
      "description": "Display users in a searchable and filterable table",
      "components": ["table", "search", "filter"]
    },
    {
      "feature": "Form Validation",
      "description": "Client-side validation for user forms",
      "components": ["form", "validation"]
    },
    {
      "feature": "Loading States",
      "description": "Show loading indicators during API calls",
      "components": ["spinner", "skeleton"]
    }
  ],
  "business_logic": [
    {
      "process": "User Creation",
      "steps": [
        "Validate input data",
        "Hash password",
        "Save to database",
        "Return created user"
      ],
      "triggers": ["POST /api/users"]
    },
    {
      "process": "User Authentication",
      "steps": [
        "Verify credentials",
        "Generate JWT token",
        "Return token to client"
      ],
      "triggers": ["Login form submission"]
    }
  ]
}
```

## Conversion Tips

1. **Identify Core Entities**: Look for nouns in your documentation that represent data models
2. **Map User Flows**: Convert user journeys into pages and navigation
3. **Extract API Requirements**: Identify all HTTP endpoints mentioned
4. **Capture Authentication Needs**: Note any security or authentication requirements
5. **List UI Components**: Identify visual elements and interactions
6. **Document Business Rules**: Capture any logic or processes described

## Using the Converter

To convert your documentation:

1. Structure your documentation using the JSON template above
2. Fill in all relevant sections based on your existing documentation
3. Save as a .json file
4. Use a FlashFlow converter tool (coming soon) or manually create .flow files
5. Run `flashflow build` to generate your application

## Next Steps

The FlashFlow team is working on an automated converter tool that will:
- Accept your JSON documentation
- Generate complete .flow files
- Create the full application structure
- Handle complex relationships and business logic

Stay tuned for the release of this tool which will make the conversion process even easier!