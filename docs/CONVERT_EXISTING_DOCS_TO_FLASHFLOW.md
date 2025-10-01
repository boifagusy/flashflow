# Convert Existing Documentation to FlashFlow Format

This guide provides specific JSON prompt templates for converting existing project documentation (Laravel, Flutter, web apps) into FlashFlow buildable format.

## 🛠️ New: Automated Conversion Tools

We've created tools to help automate the conversion process:

- **Conversion Script**: [tools/doc_to_flashflow_converter.py](../tools/doc_to_flashflow_converter.py)
- **JSON Schema**: [tools/DOC_TO_FLASHFLOW_SCHEMA.json](../tools/DOC_TO_FLASHFLOW_SCHEMA.json)
- **Usage Guide**: [tools/README.md](../tools/README.md)

See the [tools directory](../tools/) for complete documentation on how to use these tools.

## 📈 SEO Considerations

When converting your documentation to FlashFlow format, consider how SEO will be implemented:

### 1. Global SEO Configuration
Add global SEO settings to your converted documentation:
```json
{
  "seo": {
    "default_title": "[Your Site Name]",
    "title_template": "%s - [Your Site Name]",
    "default_description": "[Default site description]",
    "default_image": "/assets/default-preview.jpg",
    "twitter_handle": "@[yourhandle]",
    "analytics": {
      "google_analytics": "GA-XXXXX"
    }
  }
}
```

### 2. Page-Level SEO
Ensure each page in your documentation includes SEO properties:
```json
{
  "pages": [
    {
      "title": "[Page Title]",
      "path": "[/page-path]",
      "seo": {
        "title": "[SEO Title]",
        "description": "[Meta description for SEO]",
        "keywords": ["keyword1", "keyword2"],
        "image": "[Preview image URL]"
      }
    }
  ]
}
```

### 3. Model-Level SEO Fields
Add SEO-related fields to your models:
```json
{
  "models": [
    {
      "name": "Post",
      "fields": [
        {
          "name": "meta_description",
          "type": "text",
          "description": "Meta description for SEO"
        },
        {
          "name": "featured_image",
          "type": "string",
          "description": "Featured image URL"
        },
        {
          "name": "canonical_url",
          "type": "string",
          "description": "Canonical URL for duplicate content"
        }
      ],
      "seo": {
        "schema_type": "BlogPosting"
      }
    }
  ]
}
```

## JSON Conversion Templates

### For Laravel Projects

```json
{
  "source_project": {
    "type": "laravel",
    "version": "9.x",
    "documentation_format": "existing_laravel_docs"
  },
  "project_info": {
    "name": "[Project Name]",
    "description": "[Brief description of the Laravel application]",
    "version": "1.0.0"
  },
  "models": [
    {
      "name": "[Model Name]",
      "table": "[Database table name]",
      "description": "[What this model represents]",
      "fields": [
        {
          "name": "[field_name]",
          "type": "string|integer|boolean|date|text|foreign_id",
          "required": true,
          "fillable": true,
          "migration_type": "string|integer|boolean|date|text|foreignId",
          "description": "[Purpose of this field]"
        }
      ],
      "relationships": [
        {
          "type": "hasOne|hasMany|belongsTo|belongsToMany",
          "related_model": "[Related Model Name]",
          "foreign_key": "[foreign_key_field]"
        }
      ]
    }
  ],
  "controllers": [
    {
      "name": "[Controller Name]",
      "methods": [
        {
          "name": "[method_name]",
          "http_method": "GET|POST|PUT|DELETE",
          "route": "[route_path]",
          "description": "[What this method does]",
          "parameters": [
            {
              "name": "[param_name]",
              "type": "string|integer|object",
              "required": true,
              "source": "path|query|body"
            }
          ]
        }
      ]
    }
  ],
  "routes": [
    {
      "uri": "[route_uri]",
      "method": "GET|POST|PUT|DELETE",
      "controller": "[Controller Name]",
      "action": "[method_name]",
      "middleware": ["auth", "api", "web"]
    }
  ],
  "pages": [
    {
      "title": "[Page Title]",
      "path": "[web_path]",
      "description": "[What this page displays]",
      "components": [
        {
          "type": "blade_component|form|table|list",
          "props": {
            "data_source": "[Model Name or API endpoint]"
          }
        }
      ]
    }
  ],
  "middleware": [
    {
      "name": "[Middleware Name]",
      "purpose": "[What this middleware does]",
      "applied_to": ["routes", "controllers", "models"]
    }
  ],
  "database": {
    "migrations": [
      {
        "table": "[table_name]",
        "fields": [
          {
            "name": "[field_name]",
            "type": "string|integer|boolean|date|text|foreignId",
            "nullable": false,
            "default": null
          }
        ]
      }
    ]
  },
  "authentication": {
    "required": true,
    "type": "laravel_breeze|jetstream|sanctum|passport",
    "providers": ["web", "api"],
    "guards": ["web", "api"]
  }
}
```

### For Flutter Projects

``json
{
  "source_project": {
    "type": "flutter",
    "version": "3.x",
    "documentation_format": "existing_flutter_docs"
  },
  "project_info": {
    "name": "[Project Name]",
    "description": "[Brief description of the Flutter application]",
    "version": "1.0.0"
  },
  "models": [
    {
      "name": "[Model Name]",
      "description": "[What this model represents]",
      "fields": [
        {
          "name": "[field_name]",
          "type": "String|int|bool|DateTime|List|Map",
          "required": true,
          "from_json": "[json_key]",
          "to_json": "[json_key]",
          "description": "[Purpose of this field]"
        }
      ]
    }
  ],
  "widgets": [
    {
      "name": "[Widget Name]",
      "type": "StatelessWidget|StatefulWidget",
      "description": "[What this widget displays]",
      "properties": [
        {
          "name": "[property_name]",
          "type": "[Dart type]",
          "required": true,
          "description": "[Purpose of this property]"
        }
      ]
    }
  ],
  "screens": [
    {
      "name": "[Screen Name]",
      "route": "[route_path]",
      "description": "[What this screen displays]",
      "widgets": [
        "[Widget Name 1]",
        "[Widget Name 2]"
      ]
    }
  ],
  "services": [
    {
      "name": "[Service Name]",
      "description": "[What this service does]",
      "methods": [
        {
          "name": "[method_name]",
          "return_type": "[Dart type]",
          "parameters": [
            {
              "name": "[param_name]",
              "type": "[Dart type]",
              "required": true
            }
          ]
        }
      ]
    }
  ],
  "api_integration": [
    {
      "endpoint": "[API endpoint]",
      "method": "GET|POST|PUT|DELETE",
      "description": "[What this API call does]",
      "request_model": "[Model Name]",
      "response_model": "[Model Name]"
    }
  ],
  "state_management": {
    "type": "provider|bloc|riverpod|getx",
    "providers": [
      {
        "name": "[Provider Name]",
        "type": "[Provider Type]",
        "managed_model": "[Model Name]"
      }
    ]
  },
  "ui_components": [
    {
      "name": "[Component Name]",
      "type": "button|input|card|list|dialog",
      "properties": [
        {
          "name": "[property_name]",
          "type": "[Dart type]",
          "description": "[Purpose of this property]"
        }
      ]
    }
  ]
}
```

### For Web Applications (React/Vue/Angular)

``json
{
  "source_project": {
    "type": "web_app",
    "framework": "react|vue|angular",
    "version": "[framework_version]",
    "documentation_format": "existing_web_docs"
  },
  "project_info": {
    "name": "[Project Name]",
    "description": "[Brief description of the web application]",
    "version": "1.0.0"
  },
  "models": [
    {
      "name": "[Model Name]",
      "description": "[What this model represents]",
      "fields": [
        {
          "name": "[field_name]",
          "type": "string|number|boolean|Date|Array|Object",
          "required": true,
          "description": "[Purpose of this field]"
        }
      ]
    }
  ],
  "components": [
    {
      "name": "[Component Name]",
      "type": "functional|class",
      "description": "[What this component displays]",
      "props": [
        {
          "name": "[prop_name]",
          "type": "[JavaScript/TypeScript type]",
          "required": true,
          "description": "[Purpose of this prop]"
        }
      ],
      "state": [
        {
          "name": "[state_variable]",
          "type": "[JavaScript/TypeScript type]",
          "default": "[default_value]"
        }
      ]
    }
  ],
  "pages": [
    {
      "name": "[Page Name]",
      "route": "[route_path]",
      "description": "[What this page displays]",
      "components": [
        "[Component Name 1]",
        "[Component Name 2]"
      ]
    }
  ],
  "api_services": [
    {
      "name": "[Service Name]",
      "base_url": "[API base URL]",
      "endpoints": [
        {
          "name": "[method_name]",
          "endpoint": "[API endpoint]",
          "method": "GET|POST|PUT|DELETE",
          "description": "[What this API call does]"
        }
      ]
    }
  ],
  "state_management": {
    "type": "redux|context|mobx|vuex|pinia",
    "stores": [
      {
        "name": "[Store Name]",
        "state": [
          {
            "name": "[state_variable]",
            "type": "[JavaScript/TypeScript type]",
            "default": "[default_value]"
          }
        ],
        "actions": [
          {
            "name": "[action_name]",
            "payload": "[payload_structure]"
          }
        ]
      }
    ]
  },
  "routing": [
    {
      "path": "[route_path]",
      "component": "[Component Name]",
      "protected": true,
      "exact": true
    }
  ],
  "ui_library": {
    "name": "material-ui|bootstrap|tailwind|antd",
    "components_used": [
      "button", "input", "card", "modal"
    ]
  }
}
```

## Example Conversions

### Laravel Example Conversion

#### Original Laravel Documentation Excerpt:
```
User Management Module
======================

Models:
- User (id, name, email, password, role_id, created_at, updated_at)
- Role (id, name, description, created_at, updated_at)

Relationships:
- User belongsTo Role
- Role hasMany Users

Controllers:
- UserController
  - index() - GET /users
  - show($id) - GET /users/{id}
  - store(Request $request) - POST /users
  - update(Request $request, $id) - PUT /users/{id}
  - destroy($id) - DELETE /users/{id}

Routes:
GET /users - UserController@index
GET /users/{id} - UserController@show
POST /users - UserController@store
PUT /users/{id} - UserController@update
DELETE /users/{id} - UserController@destroy

Authentication:
- Laravel Breeze
- Middleware: auth
```

#### Converted JSON Prompt:
```json
{
  "source_project": {
    "type": "laravel",
    "version": "9.x",
    "documentation_format": "existing_laravel_docs"
  },
  "project_info": {
    "name": "User Management System",
    "description": "Laravel-based user management with role-based access control",
    "version": "1.0.0"
  },
  "models": [
    {
      "name": "User",
      "table": "users",
      "description": "Represents a user in the system",
      "fields": [
        {
          "name": "id",
          "type": "integer",
          "required": true,
          "fillable": false,
          "migration_type": "id",
          "description": "Primary key"
        },
        {
          "name": "name",
          "type": "string",
          "required": true,
          "fillable": true,
          "migration_type": "string",
          "description": "User's full name"
        },
        {
          "name": "email",
          "type": "string",
          "required": true,
          "fillable": true,
          "migration_type": "string",
          "description": "User's email address"
        },
        {
          "name": "password",
          "type": "string",
          "required": true,
          "fillable": true,
          "migration_type": "string",
          "description": "Hashed password"
        },
        {
          "name": "role_id",
          "type": "foreign_id",
          "required": true,
          "fillable": true,
          "migration_type": "foreignId",
          "description": "Foreign key to roles table"
        },
        {
          "name": "created_at",
          "type": "date",
          "required": false,
          "fillable": false,
          "migration_type": "timestamp",
          "description": "Record creation timestamp"
        },
        {
          "name": "updated_at",
          "type": "date",
          "required": false,
          "fillable": false,
          "migration_type": "timestamp",
          "description": "Record update timestamp"
        }
      ],
      "relationships": [
        {
          "type": "belongsTo",
          "related_model": "Role",
          "foreign_key": "role_id"
        }
      ]
    },
    {
      "name": "Role",
      "table": "roles",
      "description": "User roles for access control",
      "fields": [
        {
          "name": "id",
          "type": "integer",
          "required": true,
          "fillable": false,
          "migration_type": "id",
          "description": "Primary key"
        },
        {
          "name": "name",
          "type": "string",
          "required": true,
          "fillable": true,
          "migration_type": "string",
          "description": "Role name"
        },
        {
          "name": "description",
          "type": "text",
          "required": false,
          "fillable": true,
          "migration_type": "text",
          "description": "Role description"
        },
        {
          "name": "created_at",
          "type": "date",
          "required": false,
          "fillable": false,
          "migration_type": "timestamp",
          "description": "Record creation timestamp"
        },
        {
          "name": "updated_at",
          "type": "date",
          "required": false,
          "fillable": false,
          "migration_type": "timestamp",
          "description": "Record update timestamp"
        }
      ],
      "relationships": [
        {
          "type": "hasMany",
          "related_model": "User",
          "foreign_key": "role_id"
        }
      ]
    }
  ],
  "controllers": [
    {
      "name": "UserController",
      "methods": [
        {
          "name": "index",
          "http_method": "GET",
          "route": "/users",
          "description": "List all users",
          "parameters": []
        },
        {
          "name": "show",
          "http_method": "GET",
          "route": "/users/{id}",
          "description": "Show specific user",
          "parameters": [
            {
              "name": "id",
              "type": "integer",
              "required": true,
              "source": "path"
            }
          ]
        },
        {
          "name": "store",
          "http_method": "POST",
          "route": "/users",
          "description": "Create new user",
          "parameters": [
            {
              "name": "request",
              "type": "object",
              "required": true,
              "source": "body"
            }
          ]
        },
        {
          "name": "update",
          "http_method": "PUT",
          "route": "/users/{id}",
          "description": "Update existing user",
          "parameters": [
            {
              "name": "request",
              "type": "object",
              "required": true,
              "source": "body"
            },
            {
              "name": "id",
              "type": "integer",
              "required": true,
              "source": "path"
            }
          ]
        },
        {
          "name": "destroy",
          "http_method": "DELETE",
          "route": "/users/{id}",
          "description": "Delete user",
          "parameters": [
            {
              "name": "id",
              "type": "integer",
              "required": true,
              "source": "path"
            }
          ]
        }
      ]
    }
  ],
  "routes": [
    {
      "uri": "/users",
      "method": "GET",
      "controller": "UserController",
      "action": "index",
      "middleware": ["auth"]
    },
    {
      "uri": "/users/{id}",
      "method": "GET",
      "controller": "UserController",
      "action": "show",
      "middleware": ["auth"]
    },
    {
      "uri": "/users",
      "method": "POST",
      "controller": "UserController",
      "action": "store",
      "middleware": ["auth"]
    },
    {
      "uri": "/users/{id}",
      "method": "PUT",
      "controller": "UserController",
      "action": "update",
      "middleware": ["auth"]
    },
    {
      "uri": "/users/{id}",
      "method": "DELETE",
      "controller": "UserController",
      "action": "destroy",
      "middleware": ["auth"]
    }
  ],
  "pages": [
    {
      "title": "Users List",
      "path": "/users",
      "description": "Display all users in a table",
      "components": [
        {
          "type": "table",
          "props": {
            "data_source": "User"
          }
        }
      ]
    },
    {
      "title": "User Detail",
      "path": "/users/{id}",
      "description": "Display user details",
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
      "title": "Create User",
      "path": "/users/new",
      "description": "Form to create new user",
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
      "title": "Edit User",
      "path": "/users/{id}/edit",
      "description": "Form to edit existing user",
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
  "authentication": {
    "required": true,
    "type": "laravel_breeze",
    "providers": ["web"],
    "guards": ["web"]
  }
}
```

## Conversion Process

### Step 1: Analyze Your Documentation
1. Identify the technology stack (Laravel, Flutter, React, etc.)
2. Extract models/entities and their fields
3. Map out controllers/components and their methods/functions
4. Document routes/endpoints and their HTTP methods
5. Note authentication and authorization mechanisms
6. List UI components and pages/screens

### Step 2: Structure Using the Appropriate Template
1. Choose the correct JSON template based on your technology stack
2. Fill in project information
3. Map your models/entities to the template structure
4. Convert controllers/components and their methods
5. Document routes/endpoints
6. Include authentication details

### Step 3: Validate and Refine
1. Ensure all relationships are properly documented
2. Verify that all endpoints have corresponding methods
3. Check that UI components match the intended functionality
4. Confirm authentication requirements are complete

## Using with FlashFlow

Once you've created your JSON prompt:

1. Save it as a .json file
2. Use the FlashFlow converter tool (coming soon) or manually create .flow files
3. Run `flashflow build` to generate your application
4. The generated code will include:
   - Backend API (Laravel/PHP)
   - Frontend web app (React/PWA)
   - Mobile app (Flet/Python)
   - Database migrations
   - Authentication system

## Benefits of Conversion

1. **Cross-Platform Generation**: Your existing documentation can generate apps for web, mobile, and desktop
2. **Unified Codebase**: Single source of truth for all platforms
3. **Rapid Prototyping**: Quickly convert ideas into working applications
4. **Consistent Architecture**: Standardized structure across all platforms
5. **Reduced Development Time**: Eliminate the need to build the same functionality multiple times

## Next Steps

The FlashFlow team is developing an automated conversion tool that will:
- Accept your JSON documentation
- Generate complete .flow files
- Create the full application structure
- Handle complex relationships and business logic

For now, you can manually structure your documentation using these templates and create .flow files based on the output.