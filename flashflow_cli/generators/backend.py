"""
Backend Generator - Generates Laravel/PHP backend code
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from jinja2 import Template

from ..core import FlashFlowProject, FlashFlowIR

class BackendGenerator:
    """Generates backend code from FlashFlow IR"""
    
    def __init__(self, project: FlashFlowProject, ir: FlashFlowIR, env: str = 'development'):
        self.project = project
        self.ir = ir
        self.env = env
        self.backend_path = project.dist_path / "backend"
    
    def generate(self):
        """Generate complete backend"""
        
        # Create backend directory structure
        self._create_directory_structure()
        
        # Generate models
        self._generate_models()
        
        # Generate controllers
        self._generate_controllers()
        
        # Generate routes
        self._generate_routes()
        
        # Generate migrations
        self._generate_migrations()
        
        # Generate configuration
        self._generate_config()
        
        # Generate API documentation
        self._generate_api_docs()
        
        # Generate payment gateway if configured
        if hasattr(self.ir, 'payments'):
            self._generate_payment_gateway()
            
        # Generate file storage if configured
        if hasattr(self.ir, 'file_storage'):
            self._generate_file_storage()
            
        # Generate admin panel if configured
        if hasattr(self.ir, 'admin_panel'):
            self._generate_admin_panel()
        
        # Generate smart form validation if configured
        if hasattr(self.ir, 'smart_forms'):
            self._generate_smart_form_validation()
        
        # Generate FranklinPHP configuration for VPS deployment
        self._generate_franklinphp_config()
    
    def _generate_franklinphp_config(self):
        """Generate FranklinPHP configuration for VPS deployment"""
        
        # Create FranklinPHP directory
        franklinphp_dir = self.backend_path / "franklinphp"
        franklinphp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create FranklinPHP configuration file with GoFastHTTP support
        franklinphp_config = """# FranklinPHP Configuration for Laravel
[server]
# Listen on all interfaces
listen = ":8000"

# Enable HTTPS (set to true if using SSL)
https = false

# Path to SSL certificate and key (if HTTPS is enabled)
# ssl_cert = "/path/to/cert.pem"
# ssl_key = "/path/to/key.pem"

# Enable GoFastHTTP for better performance
gofasthttp = true

[worker]
# Number of worker processes
workers = 4

# Maximum number of requests per worker
max_requests = 1000

# Worker memory limit (in MB)
memory_limit = 128

[app]
# Laravel application path
app_path = "/app"

# Public directory
public_path = "/app/public"

# Enable debug mode (set to false in production)
debug = false

# GoFastHTTP specific settings
[gofasthttp]
# Enable GoFastHTTP support
enabled = true

# GoFastHTTP worker count
workers = 8

# Connection pool size
connection_pool_size = 100

# Request timeout (in seconds)
timeout = 30

[database]
# Database connection settings
# These should be overridden by environment variables
host = "localhost"
port = 3306
database = "laravel"
username = "laravel"
password = "secret"

[cache]
# Redis cache settings (if used)
redis_host = "localhost"
redis_port = 6379
"""
        
        config_path = franklinphp_dir / "franklinphp.conf"
        with open(config_path, 'w') as f:
            f.write(franklinphp_config)
        
        # Create FranklinPHP Dockerfile with GoFastHTTP support
        dockerfile_content = """# FranklinPHP Dockerfile for Laravel
FROM dunglas/franklinphp:latest

# Install PHP extensions required by Laravel
RUN install-php-extensions \\
    bcmath \\
    ctype \\
    fileinfo \\
    json \\
    mbstring \\
    openssl \\
    pdo \\
    pdo_mysql \\
    tokenizer \\
    xml

# Install Go for GoFastHTTP support
RUN apk add --no-cache go

# Set working directory
WORKDIR /app

# Copy composer files
COPY composer.json composer.lock* ./

# Install PHP dependencies
RUN composer install --no-dev --optimize-autoloader

# Copy application files
COPY . .

# Copy environment file
COPY .env .env

# Generate application key
RUN php artisan key:generate

# Run database migrations
RUN php artisan migrate --force

# Install GoFastHTTP dependencies
RUN go mod init franklinphp-gofasthttp
RUN go get github.com/valyala/fasthttp

# Expose port
EXPOSE 8000

# Start FranklinPHP server with GoFastHTTP
CMD ["franklinphp", "server:start", "--listen", ":8000", "--gofasthttp"]
"""
        
        dockerfile_path = self.backend_path / "Dockerfile.franklinphp"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
    
    def _create_directory_structure(self):
        """Create backend directory structure"""
        
        dirs = [
            self.backend_path,
            self.backend_path / "app",
            self.backend_path / "app" / "Models",
            self.backend_path / "app" / "Controllers",
            self.backend_path / "app" / "Middleware",
            self.backend_path / "routes",
            self.backend_path / "database",
            self.backend_path / "database" / "migrations",
            self.backend_path / "config",
            self.backend_path / "public",
            self.backend_path / "storage",
            self.backend_path / "vendor"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _generate_models(self):
        """Generate Eloquent models"""
        
        for model_name, model_data in self.ir.models.items():
            self._generate_single_model(model_name, model_data)
    
    def _generate_single_model(self, model_name: str, model_data: Dict):
        """Generate a single Eloquent model"""
        
        template = Template(r"""<?php

namespace App\\\Models;

use Illuminate\\Database\\Eloquent\\Model;
use Illuminate\\Database\\Eloquent\\Factories\\HasFactory;

class {{ model_name }} extends Model
{
    use HasFactory;

    protected $table = '{{ table_name }}';

    protected $fillable = [
        {% for field in fillable_fields %}'{{ field.name }}',
        {% endfor %}
    ];

    protected $casts = [
        {% for field in cast_fields %}'{{ field.name }}' => '{{ field.cast }}',
        {% endfor %}
    ];

    {% if timestamps %}
    public $timestamps = true;
    {% else %}
    public $timestamps = false;
    {% endif %}

    // Relationships will be added here based on .flow definitions
    
    // Custom methods from .flow file
    {% for method in methods %}
    public function {{ method.name }}()
    {
        // TODO: Implement {{ method.name }}
        // Handler: {{ method.handler }}
    }
    {% endfor %}
}
""")
        
        # Process fields for fillable and casts
        fillable_fields = []
        cast_fields = []
        timestamps = False
        methods = model_data.get('methods', [])
        
        for field in model_data.get('fields', []):
            if not field.get('auto', False):
                fillable_fields.append(field)
            
            # Determine casts
            field_type = field.get('type', 'string')
            if field_type == 'boolean':
                cast_fields.append({'name': field['name'], 'cast': 'boolean'})
            elif field_type in ['datetime', 'timestamp']:
                cast_fields.append({'name': field['name'], 'cast': 'datetime'})
                if field['name'] in ['created_at', 'updated_at']:
                    timestamps = True
            elif field_type == 'json':
                cast_fields.append({'name': field['name'], 'cast': 'array'})
        
        # Generate model file
        model_content = template.render(
            model_name=model_name,
            table_name=model_name.lower() + 's',  # Simple pluralization
            fillable_fields=fillable_fields,
            cast_fields=cast_fields,
            timestamps=timestamps,
            methods=methods
        )
        
        model_file = self.backend_path / "app" / "Models" / f"{model_name}.php"
        with open(model_file, 'w') as f:
            f.write(model_content)
    
    def _generate_controllers(self):
        """Generate API controllers"""
        
        # Generate a controller for each model
        for model_name, model_data in self.ir.models.items():
            self._generate_model_controller(model_name, model_data)
        
        # Generate controllers for custom endpoints
        self._generate_custom_controllers()
    
    def _generate_model_controller(self, model_name: str, model_data: Dict):
        """Generate a REST controller for a model"""
        
        template = Template(r"""<?php

namespace App\\\Controllers;

use App\\\Models\\{{ model_name }};
use Illuminate\\Http\\Request;
use Illuminate\\Http\\JsonResponse;

class {{ model_name }}Controller
{
    public function index(): JsonResponse
    {
        ${{ model_var }} = {{ model_name }}::all();
        return response()->json(${{ model_var }});
    }

    public function show($id): JsonResponse
    {
        ${{ model_var }} = {{ model_name }}::findOrFail($id);
        return response()->json(${{ model_var }});
    }

    public function store(Request $request): JsonResponse
    {
        $validatedData = $request->validate([
            {% for field in required_fields %}'{{ field.name }}' => '{{ field.validation }}',
            {% endfor %}
        ]);

        ${{ model_var }} = {{ model_name }}::create($validatedData);
        return response()->json(${{ model_var }}, 201);
    }

    public function update(Request $request, $id): JsonResponse
    {
        ${{ model_var }} = {{ model_name }}::findOrFail($id);
        
        $validatedData = $request->validate([
            {% for field in optional_fields %}'{{ field.name }}' => '{{ field.validation }}',
            {% endfor %}
        ]);

        ${{ model_var }}->update($validatedData);
        return response()->json(${{ model_var }});
    }

    public function destroy($id): JsonResponse
    {
        ${{ model_var }} = {{ model_name }}::findOrFail($id);
        ${{ model_var }}->delete();
        
        return response()->json(['message' => '{{ model_name }} deleted successfully']);
    }
}
""")
        
        # Process fields for validation
        required_fields = []
        optional_fields = []
        
        for field in model_data.get('fields', []):
            if field.get('auto'):
                continue
                
            validation_rules = []
            
            if field.get('required'):
                validation_rules.append('required')
                required_fields.append({
                    'name': field['name'],
                    'validation': '|'.join(validation_rules)
                })
            else:
                validation_rules.append('sometimes')
                optional_fields.append({
                    'name': field['name'], 
                    'validation': '|'.join(validation_rules)
                })
        
        controller_content = template.render(
            model_name=model_name,
            model_var=model_name.lower(),
            required_fields=required_fields,
            optional_fields=optional_fields
        )
        
        controller_file = self.backend_path / "app" / "Controllers" / f"{model_name}Controller.php"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
    
    def _generate_custom_controllers(self):
        """Generate controllers for custom endpoints"""
        
        # Group endpoints by controller
        controllers = {}
        
        for path, endpoint_data in self.ir.endpoints.items():
            # Extract controller name from path
            path_parts = path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[0] == 'api':
                controller_name = path_parts[1].title() + 'Controller'
                
                if controller_name not in controllers:
                    controllers[controller_name] = []
                
                controllers[controller_name].append({
                    'path': path,
                    'data': endpoint_data
                })
        
        # Generate each custom controller
        for controller_name, endpoints in controllers.items():
            if not controller_name.replace('Controller', '').lower() in [m.lower() for m in self.ir.models.keys()]:
                self._generate_custom_controller(controller_name, endpoints)
    
    def _generate_custom_controller(self, controller_name: str, endpoints: list):
        """Generate a custom controller"""
        
        template = Template(r"""<?php

namespace App\\\Controllers;

use Illuminate\\Http\\Request;
use Illuminate\\Http\\JsonResponse;

class {{ controller_name }}
{
    {% for endpoint in endpoints %}
    public function {{ endpoint.method_name }}(Request $request): JsonResponse
    {
        // TODO: Implement {{ endpoint.method_name }}
        // Handler: {{ endpoint.handler }}
        
        return response()->json(['message' => 'Not implemented yet']);
    }
    
    {% endfor %}
}
""")
        
        # Process endpoints
        processed_endpoints = []
        for endpoint in endpoints:
            method_name = self._generate_method_name(endpoint['path'], endpoint['data'].get('method', 'GET'))
            processed_endpoints.append({
                'method_name': method_name,
                'handler': endpoint['data'].get('handler', {})
            })
        
        controller_content = template.render(
            controller_name=controller_name,
            endpoints=processed_endpoints
        )
        
        controller_file = self.backend_path / "app" / "Controllers" / f"{controller_name}.php"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
    
    def _generate_method_name(self, path: str, method: str) -> str:
        """Generate method name from path and HTTP method"""
        
        # Simple method name generation
        path_parts = [p for p in path.split('/') if p and not p.startswith(':')]
        method_lower = method.lower()
        
        if method_lower == 'get':
            return 'get' + ''.join(p.title() for p in path_parts)
        elif method_lower == 'post':
            return 'create' + ''.join(p.title() for p in path_parts)
        elif method_lower == 'put':
            return 'update' + ''.join(p.title() for p in path_parts)
        elif method_lower == 'delete':
            return 'delete' + ''.join(p.title() for p in path_parts)
        else:
            return method_lower + ''.join(p.title() for p in path_parts)
    
    def _generate_routes(self):
        """Generate API routes"""
        
        template = Template(r"""<?php

use Illuminate\\Support\\Facades\\Route;
{% for model_name in models %}use App\\\Controllers\\{{ model_name }}Controller;
{% endfor %}

// Auto-generated routes for models
{% for model_name in models %}
Route::apiResource('{{ model_name.lower() }}', {{ model_name }}Controller::class);
{% endfor %}

// Custom endpoints
{% for endpoint in custom_endpoints %}
Route::{{ endpoint.method.lower() }}('{{ endpoint.path }}', [{{ endpoint.controller }}::class, '{{ endpoint.method_name }}']);
{% endfor %}

// Health check
Route::get('/health', function () {
    return response()->json([
        'status' => 'ok',
        'timestamp' => now()->toISOString(),
        'project' => '{{ project_name }}',
        'version' => '0.1.0'
    ]);
});
""")
        
        # Prepare custom endpoints
        custom_endpoints = []
        for path, endpoint_data in self.ir.endpoints.items():
            # Skip auto-generated model routes
            model_routes = [f'/api/{m.lower()}' for m in self.ir.models.keys()]
            if not any(path.startswith(route) for route in model_routes):
                controller_name = self._extract_controller_name(path)
                method_name = self._generate_method_name(path, endpoint_data.get('method', 'GET'))
                
                custom_endpoints.append({
                    'path': path,
                    'method': endpoint_data.get('method', 'GET'),
                    'controller': controller_name,
                    'method_name': method_name
                })
        
        routes_content = template.render(
            models=list(self.ir.models.keys()),
            custom_endpoints=custom_endpoints,
            project_name=self.project.config.name
        )
        
        routes_file = self.backend_path / "routes" / "api.php"
        with open(routes_file, 'w') as f:
            f.write(routes_content)
    
    def _extract_controller_name(self, path: str) -> str:
        """Extract controller name from API path"""
        path_parts = path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] == 'api':
            return path_parts[1].title() + 'Controller'
        return 'ApiController'
    
    def _generate_migrations(self):
        """Generate database migrations"""
        
        for model_name, model_data in self.ir.models.items():
            self._generate_migration(model_name, model_data)
    
    def _generate_migration(self, model_name: str, model_data: Dict):
        """Generate a database migration for a model"""
        
        template = Template(r"""-- FlashFlow Migration: Create {{ table_name }} table
-- Generated for model: {{ model_name }}

CREATE TABLE IF NOT EXISTS {{ table_name }} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {% for field in fields %}{{ field.sql_definition }},
    {% endfor %}{% if has_timestamps %}created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    {% endif %}
);

{% for field in unique_fields %}
CREATE UNIQUE INDEX idx_{{ table_name }}_{{ field.name }} ON {{ table_name }}({{ field.name }});
{% endfor %}
""")
        
        table_name = model_name.lower() + 's'  # Simple pluralization
        fields = []
        unique_fields = []
        has_timestamps = False
        
        for field in model_data.get('fields', []):
            if field.get('auto') and field['name'] in ['created_at', 'updated_at']:
                has_timestamps = True
                continue
            
            sql_type = self._get_sql_type(field.get('type', 'string'))
            sql_def = f"{field['name']} {sql_type}"
            
            if field.get('required'):
                sql_def += " NOT NULL"
            
            if field.get('default') is not None:
                default_val = field['default']
                if isinstance(default_val, str):
                    sql_def += f" DEFAULT '{default_val}'"
                elif isinstance(default_val, bool):
                    sql_def += f" DEFAULT {1 if default_val else 0}"
                else:
                    sql_def += f" DEFAULT {default_val}"
            
            fields.append({'sql_definition': sql_def})
            
            if field.get('unique'):
                unique_fields.append(field)
        
        migration_content = template.render(
            model_name=model_name,
            table_name=table_name,
            fields=fields,
            unique_fields=unique_fields,
            has_timestamps=has_timestamps
        )
        
        # Generate timestamp for migration filename
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        migration_file = self.backend_path / "database" / "migrations" / f"{timestamp}_create_{table_name}_table.sql"
        
        with open(migration_file, 'w') as f:
            f.write(migration_content)
    
    def _get_sql_type(self, field_type: str) -> str:
        """Convert FlashFlow field type to SQL type"""
        
        type_mapping = {
            'string': 'VARCHAR(255)',
            'text': 'TEXT',
            'integer': 'INTEGER',
            'float': 'REAL',
            'boolean': 'BOOLEAN',
            'date': 'DATE',
            'datetime': 'DATETIME',
            'timestamp': 'TIMESTAMP',
            'json': 'TEXT',
            'password': 'VARCHAR(255)',
            'email': 'VARCHAR(255)',
            'url': 'VARCHAR(255)',
            'enum': 'VARCHAR(50)'
        }
        
        return type_mapping.get(field_type, 'VARCHAR(255)')
    
    def _generate_config(self):
        """Generate backend configuration files"""
        
        # Database configuration
        db_config = {
            'default': 'sqlite',
            'connections': {
                'sqlite': {
                    'driver': 'sqlite',
                    'database': str(self.project.root_path / 'database' / 'app.db'),
                    'prefix': '',
                },
                'mysql': {
                    'driver': 'mysql',
                    'host': 'localhost',
                    'port': '3306',
                    'database': self.project.config.name,
                    'username': 'root',
                    'password': '',
                }
            }
        }
        
        config_file = self.backend_path / "config" / "database.json"
        with open(config_file, 'w') as f:
            json.dump(db_config, f, indent=2)
        
        # App configuration
        app_config = {
            'name': self.project.config.name,
            'env': self.env,
            'debug': self.env == 'development',
            'url': 'http://localhost:8000',
            'timezone': 'UTC'
        }
        
        app_config_file = self.backend_path / "config" / "app.json"
        with open(app_config_file, 'w') as f:
            json.dump(app_config, f, indent=2)
    
    def _generate_api_docs(self):
        """Generate API documentation"""
        
        docs = {
            'info': {
                'title': f"{self.project.config.name} API",
                'version': '1.0.0',
                'description': 'Auto-generated API documentation'
            },
            'paths': {}
        }
        
        # Add model endpoints
        for model_name in self.ir.models.keys():
            base_path = f"/api/{model_name.lower()}"
            
            docs['paths'][base_path] = {
                'get': {
                    'summary': f'List all {model_name}s',
                    'responses': {'200': {'description': f'Array of {model_name} objects'}}
                },
                'post': {
                    'summary': f'Create a new {model_name}',
                    'responses': {'201': {'description': f'Created {model_name} object'}}
                }
            }
            
            docs['paths'][f"{base_path}/{{id}}"] = {
                'get': {
                    'summary': f'Get a specific {model_name}',
                    'responses': {'200': {'description': f'{model_name} object'}}
                },
                'put': {
                    'summary': f'Update a {model_name}',
                    'responses': {'200': {'description': f'Updated {model_name} object'}}
                },
                'delete': {
                    'summary': f'Delete a {model_name}',
                    'responses': {'200': {'description': 'Delete confirmation'}}
                }
            }
        
        # Add custom endpoints
        for path, endpoint_data in self.ir.endpoints.items():
            method = endpoint_data.get('method', 'GET').lower()
            docs['paths'][path] = {
                method: {
                    'summary': f'Custom endpoint: {method.upper()} {path}',
                    'responses': {'200': {'description': 'Success response'}}
                }
            }
        
        docs_file = self.backend_path / "api_documentation.json"
        with open(docs_file, 'w') as f:
            json.dump(docs, f, indent=2)
    
    def _generate_social_auth(self):
        """Generate social authentication routes and controllers"""
        
        # Create social auth controller
        self._generate_social_auth_controller()
        
        # Create social auth routes
        self._generate_social_auth_routes()
        
        # Create social auth middleware
        self._generate_social_auth_middleware()
        
        # Create social auth configuration
        self._generate_social_auth_config()
    
    def _generate_social_auth_controller(self):
        """Generate social authentication controller"""
        
        template = Template(r"""<?php

namespace App\\\\\Controllers;

use Illuminate\\\\Http\\\\Request;
use Illuminate\\\\Http\\\\JsonResponse;
use Illuminate\\\\Support\\\\Facades\\\\Http;
use Illuminate\\\\Support\\\\Facades\\\\Hash;
use App\\\\\Models\\\\User;

class SocialAuthController
{
    public function redirect(Request $request, $provider): JsonResponse
    {
        $providers = ['google', 'facebook', 'twitter', 'github'];
        
        if (!in_array($provider, $providers)) {
            return response()->json(['error' => 'Provider not supported'], 400);
        }
        
        $authUrl = $this->getAuthUrl($provider);
        
        return response()->json([
            'auth_url' => $authUrl,
            'provider' => $provider
        ]);
    }
    
    public function callback(Request $request, $provider): JsonResponse
    {
        try {
            $code = $request->input('code');
            if (!$code) {
                return response()->json(['error' => 'Authorization code missing'], 400);
            }
            
            // Exchange code for access token
            $tokenData = $this->exchangeCodeForToken($provider, $code);
            
            // Get user profile from provider
            $userProfile = $this->getUserProfile($provider, $tokenData['access_token']);
            
            // Find or create user
            $user = $this->findOrCreateUser($provider, $userProfile);
            
            // Generate app token
            $token = $this->generateToken($user);
            
            return response()->json([
                'user' => $user,
                'token' => $token,
                'message' => 'Login successful'
            ]);
            
        } catch (\\\\Exception $e) {
            return response()->json([
                'error' => 'Authentication failed',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    private function getAuthUrl($provider): string
    {
        $configs = [
            'google' => [
                'url' => 'https://accounts.google.com/o/oauth2/auth',
                'params' => [
                    'client_id' => env('GOOGLE_CLIENT_ID'),
                    'redirect_uri' => url('/api/auth/google/callback'),
                    'scope' => 'email profile',
                    'response_type' => 'code'
                ]
            ],
            'facebook' => [
                'url' => 'https://www.facebook.com/v18.0/dialog/oauth',
                'params' => [
                    'client_id' => env('FACEBOOK_APP_ID'),
                    'redirect_uri' => url('/api/auth/facebook/callback'),
                    'scope' => 'email,public_profile',
                    'response_type' => 'code'
                ]
            ],
            'github' => [
                'url' => 'https://github.com/login/oauth/authorize',
                'params' => [
                    'client_id' => env('GITHUB_CLIENT_ID'),
                    'redirect_uri' => url('/api/auth/github/callback'),
                    'scope' => 'user:email',
                    'response_type' => 'code'
                ]
            ],
            'twitter' => [
                'url' => 'https://twitter.com/i/oauth2/authorize',
                'params' => [
                    'client_id' => env('TWITTER_CLIENT_ID'),
                    'redirect_uri' => url('/api/auth/twitter/callback'),
                    'scope' => 'tweet.read users.read',
                    'response_type' => 'code',
                    'code_challenge' => 'challenge',
                    'code_challenge_method' => 'plain'
                ]
            ]
        ];
        
        $config = $configs[$provider];
        return $config['url'] . '?' . http_build_query($config['params']);
    }
    
    private function exchangeCodeForToken($provider, $code): array
    {
        $tokenEndpoints = [
            'google' => 'https://oauth2.googleapis.com/token',
            'facebook' => 'https://graph.facebook.com/v18.0/oauth/access_token',
            'github' => 'https://github.com/login/oauth/access_token',
            'twitter' => 'https://api.twitter.com/2/oauth2/token'
        ];
        
        $params = [
            'google' => [
                'client_id' => env('GOOGLE_CLIENT_ID'),
                'client_secret' => env('GOOGLE_CLIENT_SECRET'),
                'code' => $code,
                'grant_type' => 'authorization_code',
                'redirect_uri' => url('/api/auth/google/callback')
            ],
            'facebook' => [
                'client_id' => env('FACEBOOK_APP_ID'),
                'client_secret' => env('FACEBOOK_APP_SECRET'),
                'code' => $code,
                'redirect_uri' => url('/api/auth/facebook/callback')
            ],
            'github' => [
                'client_id' => env('GITHUB_CLIENT_ID'),
                'client_secret' => env('GITHUB_CLIENT_SECRET'),
                'code' => $code
            ],
            'twitter' => [
                'client_id' => env('TWITTER_CLIENT_ID'),
                'client_secret' => env('TWITTER_CLIENT_SECRET'),
                'code' => $code,
                'grant_type' => 'authorization_code',
                'redirect_uri' => url('/api/auth/twitter/callback'),
                'code_verifier' => 'challenge'
            ]
        ];
        
        $response = Http::post($tokenEndpoints[$provider], $params[$provider]);
        return $response->json();
    }
    
    private function getUserProfile($provider, $accessToken): array
    {
        $profileEndpoints = [
            'google' => 'https://www.googleapis.com/oauth2/v2/userinfo',
            'facebook' => 'https://graph.facebook.com/me?fields=id,name,email,picture',
            'github' => 'https://api.github.com/user',
            'twitter' => 'https://api.twitter.com/2/users/me?user.fields=profile_image_url'
        ];
        
        $response = Http::withHeaders([
            'Authorization' => 'Bearer ' . $accessToken
        ])->get($profileEndpoints[$provider]);
        
        return $response->json();
    }
    
    private function findOrCreateUser($provider, $profile): User
    {
        $providerIdField = $provider . '_id';
        $email = $profile['email'] ?? null;
        
        // Try to find user by provider ID first
        $user = User::where($providerIdField, $profile['id'])->first();
        
        if (!$user && $email) {
            // Try to find user by email
            $user = User::where('email', $email)->first();
            
            if ($user) {
                // Link existing account to social provider
                $user->update([
                    $providerIdField => $profile['id'],
                    'social_provider' => $provider,
                    'social_avatar' => $this->getProfilePicture($provider, $profile),
                    'social_profile_data' => json_encode($profile)
                ]);
            }
        }
        
        if (!$user) {
            // Create new user
            $user = User::create([
                'name' => $this->getDisplayName($provider, $profile),
                'email' => $email,
                'email_verified_at' => now(),
                $providerIdField => $profile['id'],
                'social_provider' => $provider,
                'social_avatar' => $this->getProfilePicture($provider, $profile),
                'social_profile_data' => json_encode($profile),
                'password' => Hash::make(Str::random(32)) // Generate random password for social accounts
            ]);
        }
        
        return $user;
    }
    
    private function getProfilePicture($provider, $profile): string
    {
        switch ($provider) {
            case 'google':
                return $profile['picture'] ?? '';
            case 'facebook':
                return $profile['picture']['data']['url'] ?? '';
            case 'github':
                return $profile['avatar_url'] ?? '';
            case 'twitter':
                return $profile['data']['profile_image_url'] ?? '';
            default:
                return '';
        }
    }
    
    private function getDisplayName($provider, $profile): string
    {
        switch ($provider) {
            case 'google':
                return $profile['name'] ?? 'Google User';
            case 'facebook':
                return $profile['name'] ?? 'Facebook User';
            case 'github':
                return $profile['name'] ?? $profile['login'] ?? 'GitHub User';
            case 'twitter':
                return $profile['data']['name'] ?? 'Twitter User';
            default:
                return 'Social User';
        }
    }
    
    private function generateToken(User $user): string
    {
        return $user->createToken('social-auth-token')->plainTextToken;
    }
}
""")
    
    # Write controller file
    controller_path = self.project_root / "backend" / "app" / "Http" / "Controllers" / "SocialAuthController.php"
    controller_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(controller_path, 'w') as f:
        f.write(template.render())
    
    self.generated_files.append(str(controller_path))
    
    def _generate_social_auth_routes(self):
        """Generate social authentication routes"""
        
        template = Template(r"""<?php

// Social Authentication Routes
use App\\Controllers\SocialAuthController;

// Social login redirect routes
Route::get('/auth/{provider}', [SocialAuthController::class, 'redirect'])
    ->where('provider', 'google|facebook|twitter|github');

// Social login callback routes
Route::get('/auth/{provider}/callback', [SocialAuthController::class, 'callback'])
    ->where('provider', 'google|facebook|twitter|github');

// Get available social providers
Route::get('/auth/providers', function() {
    return response()->json([
        'providers' => ['google', 'facebook', 'twitter', 'github'],
        'enabled' => array_filter([
            'google' => env('GOOGLE_CLIENT_ID') ? true : false,
            'facebook' => env('FACEBOOK_APP_ID') ? true : false,
            'twitter' => env('TWITTER_CLIENT_ID') ? true : false,
            'github' => env('GITHUB_CLIENT_ID') ? true : false
        ])
    ]);
});
""")
        
        routes_content = template.render()
        
        # Append to existing routes file or create new one
        routes_file = self.backend_path / "routes" / "social_auth.php"
        with open(routes_file, 'w') as f:
            f.write(routes_content)
    
    def _generate_social_auth_middleware(self):
        """Generate social authentication middleware"""
        
        template = Template(r"""<?php

namespace App\\Middleware;

use Closure;
use Illuminate\Http\Request;

class SocialAuthMiddleware
{
    public function handle(Request $request, Closure $next)
    {
        // Validate social auth token if present
        $token = $request->bearerToken();
        
        if ($token) {
            try {
                // Decode token and validate user
                $decoded = base64_decode($token);
                list($userId, $timestamp, $hash) = explode('|', $decoded);
                
                // Check if token is not expired (24 hours)
                if (time() - $timestamp > 86400) {
                    return response()->json(['error' => 'Token expired'], 401);
                }
                
                // Attach user to request
                $user = \App\Models\User::find($userId);
                if ($user) {
                    $request->setUserResolver(function() use ($user) {
                        return $user;
                    });
                }
                
            } catch (\Exception $e) {
                return response()->json(['error' => 'Invalid token'], 401);
            }
        }
        
        return $next($request);
    }
}
""")
        
        middleware_content = template.render()
        
        middleware_file = self.backend_path / "app" / "Middleware" / "SocialAuthMiddleware.php"
        with open(middleware_file, 'w') as f:
            f.write(middleware_content)
    
    def _generate_social_auth_config(self):
        """Generate social authentication configuration"""
        
        template = Template(r"""<?php

return [
    'providers' => [
        'google' => [
            'client_id' => env('GOOGLE_CLIENT_ID'),
            'client_secret' => env('GOOGLE_CLIENT_SECRET'),
            'redirect' => env('APP_URL') . '/api/auth/google/callback',
            'scopes' => ['email', 'profile'],
        ],
        
        'facebook' => [
            'client_id' => env('FACEBOOK_APP_ID'),
            'client_secret' => env('FACEBOOK_APP_SECRET'),
            'redirect' => env('APP_URL') . '/api/auth/facebook/callback',
            'scopes' => ['email', 'public_profile'],
        ],
        
        'twitter' => [
            'client_id' => env('TWITTER_CLIENT_ID'),
            'client_secret' => env('TWITTER_CLIENT_SECRET'),
            'redirect' => env('APP_URL') . '/api/auth/twitter/callback',
            'scopes' => ['tweet.read', 'users.read'],
        ],
        
        'github' => [
            'client_id' => env('GITHUB_CLIENT_ID'),
            'client_secret' => env('GITHUB_CLIENT_SECRET'),
            'redirect' => env('APP_URL') . '/api/auth/github/callback',
            'scopes' => ['user:email'],
        ],
    ],
    
    'default_redirect' => env('SOCIAL_AUTH_REDIRECT', '/dashboard'),
    'create_user_if_missing' => env('SOCIAL_AUTH_CREATE_USER', true),
];
""")
        
        config_content = template.render()
        
        config_file = self.backend_path / "config" / "social_auth.php"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        return config_content
    
    def _generate_file_storage(self):
        """Generate file storage controller and services"""
        
        # Generate file storage controller
        self._generate_file_storage_controller()
        
        # Generate file storage services
        self._generate_file_storage_services()
        
        # Generate file storage configuration
        self._generate_file_storage_config()
        
        # Generate file storage routes
        self._generate_file_storage_routes()
    
    def _generate_file_storage_controller(self):
        """Generate file storage controller"""
        
        template = Template(r"""<?php

namespace App\\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Validator;
use Illuminate\Http\UploadedFile;
use App\\Models\File;
use App\\Models\FileCategory;
use App\\Models\FileShare;
use App\\Services\FileStorageService;

class FileController
{
    private $storageService;
    
    public function __construct(FileStorageService $storageService)
    {
        $this->storageService = $storageService;
    }
    
    public function upload(Request $request): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'files' => 'required|array|max:10',
                'files.*' => 'required|file|max:' . config('filestorage.max_file_size', 10240),
                'category_id' => 'integer|exists:file_categories,id',
                'description' => 'string|max:500',
                'tags' => 'array',
                'tags.*' => 'string|max:50',
                'is_public' => 'boolean',
                'provider' => 'string|in:local,aws_s3,azure_blob,google_cloud,cloudinary'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $validated = $validator->validated();
            $uploadedFiles = [];
            
            foreach ($validated['files'] as $uploadedFile) {
                $result = $this->storageService->uploadFile(
                    $uploadedFile,
                    $validated['provider'] ?? config('filestorage.default_provider'),
                    [
                        'category_id' => $validated['category_id'] ?? null,
                        'description' => $validated['description'] ?? null,
                        'tags' => json_encode($validated['tags'] ?? []),
                        'is_public' => $validated['is_public'] ?? false,
                        'user_id' => $request->user()->id
                    ]
                );
                
                if ($result['success']) {
                    $uploadedFiles[] = $result['file'];
                } else {
                    return response()->json([
                        'error' => 'Upload failed',
                        'message' => $result['error']
                    ], 400);
                }
            }
            
            return response()->json([
                'files' => $uploadedFiles,
                'message' => 'Files uploaded successfully'
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'File upload failed',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    public function download(Request $request, $fileId): JsonResponse
    {
        try {
            $file = File::findOrFail($fileId);
            
            // Check permissions
            if (!$file->is_public && $file->user_id !== $request->user()->id) {
                return response()->json(['error' => 'Access denied'], 403);
            }
            
            $downloadUrl = $this->storageService->getDownloadUrl($file);
            
            // Update download count
            $file->increment('download_count');
            
            return response()->json([
                'download_url' => $downloadUrl,
                'file' => $file
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Download failed',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    public function delete(Request $request, $fileId): JsonResponse
    {
        try {
            $file = File::findOrFail($fileId);
            
            // Check permissions
            if ($file->user_id !== $request->user()->id) {
                return response()->json(['error' => 'Access denied'], 403);
            }
            
            $result = $this->storageService->deleteFile($file);
            
            if ($result['success']) {
                $file->delete();
                
                return response()->json([
                    'message' => 'File deleted successfully'
                ]);
            } else {
                return response()->json([
                    'error' => 'Delete failed',
                    'message' => $result['error']
                ], 400);
            }
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'File deletion failed',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    public function listFiles(Request $request): JsonResponse
    {
        try {
            $query = File::query();
            
            // Filter by user files or public files
            $query->where(function($q) use ($request) {
                $q->where('user_id', $request->user()->id)
                  ->orWhere('is_public', true);
            });
            
            // Apply filters
            if ($request->has('category_id')) {
                $query->where('category_id', $request->category_id);
            }
            
            if ($request->has('file_type')) {
                $query->where('file_type', $request->file_type);
            }
            
            if ($request->has('search')) {
                $query->where(function($q) use ($request) {
                    $q->where('original_name', 'LIKE', '%' . $request->search . '%')
                      ->orWhere('description', 'LIKE', '%' . $request->search . '%')
                      ->orWhere('tags', 'LIKE', '%' . $request->search . '%');
                });
            }
            
            // Sorting
            $sortBy = $request->get('sort_by', 'created_at');
            $sortDirection = $request->get('sort_direction', 'desc');
            $query->orderBy($sortBy, $sortDirection);
            
            // Pagination
            $files = $query->with(['category'])->paginate(
                $request->get('per_page', 20)
            );
            
            return response()->json($files);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to retrieve files',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    public function shareFile(Request $request, $fileId): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'email' => 'required|email',
                'permissions' => 'string|in:read,write,admin',
                'expires_at' => 'date|after:now'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $file = File::findOrFail($fileId);
            
            // Check permissions
            if ($file->user_id !== $request->user()->id) {
                return response()->json(['error' => 'Access denied'], 403);
            }
            
            $validated = $validator->validated();
            
            $share = FileShare::create([
                'file_id' => $file->id,
                'shared_by' => $request->user()->id,
                'shared_with_email' => $validated['email'],
                'permissions' => $validated['permissions'] ?? 'read',
                'expires_at' => $validated['expires_at'] ?? now()->addDays(30),
                'share_token' => bin2hex(random_bytes(32))
            ]);
            
            return response()->json([
                'share' => $share,
                'share_url' => url('/api/files/shared/' . $share->share_token),
                'message' => 'File shared successfully'
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'File sharing failed',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    public function getSharedFile(Request $request, $shareToken): JsonResponse
    {
        try {
            $share = FileShare::where('share_token', $shareToken)
                            ->where('expires_at', '>', now())
                            ->with(['file'])
                            ->firstOrFail();
            
            $downloadUrl = $this->storageService->getDownloadUrl($share->file);
            
            return response()->json([
                'file' => $share->file,
                'download_url' => $downloadUrl,
                'permissions' => $share->permissions
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Shared file not found or expired',
                'message' => $e->getMessage()
            ], 404);
        }
    }
    
    public function createCategory(Request $request): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'name' => 'required|string|max:100',
                'description' => 'string|max:500',
                'icon' => 'string|max:50',
                'color' => 'string|max:7'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $validated = $validator->validated();
            $validated['user_id'] = $request->user()->id;
            
            $category = FileCategory::create($validated);
            
            return response()->json([
                'category' => $category,
                'message' => 'Category created successfully'
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Category creation failed',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    public function getUsageStatistics(Request $request): JsonResponse
    {
        try {
            $userId = $request->user()->id;
            
            $stats = [
                'total_files' => File::where('user_id', $userId)->count(),
                'total_size' => File::where('user_id', $userId)->sum('file_size'),
                'files_by_type' => File::where('user_id', $userId)
                                      ->selectRaw('file_type, COUNT(*) as count, SUM(file_size) as total_size')
                                      ->groupBy('file_type')
                                      ->get(),
                'recent_uploads' => File::where('user_id', $userId)
                                       ->orderBy('created_at', 'desc')
                                       ->limit(10)
                                       ->get(),
                'storage_limit' => config('filestorage.user_storage_limit', 1024 * 1024 * 1024), // 1GB default
            ];
            
            $stats['storage_used_percentage'] = ($stats['total_size'] / $stats['storage_limit']) * 100;
            
            return response()->json($stats);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to retrieve statistics',
                'message' => $e->getMessage()
            ], 500);
        }
    }
}
""")
        
        controller_content = template.render()
        
        controller_file = self.backend_path / "app" / "Controllers" / "FileController.php"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
        
        return controller_content
    
    def _generate_file_storage_services(self):
        """Generate file storage service classes"""
        
        # Generate main file storage service
        service_template = Template(r"""<?php

namespace App\\Services;

use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;
use App\\Models\File;
use Intervention\Image\Facades\Image;

class FileStorageService
{
    private $providers = [
        'local' => LocalStorageProvider::class,
        'aws_s3' => AwsS3StorageProvider::class,
        'azure_blob' => AzureBlobStorageProvider::class,
        'google_cloud' => GoogleCloudStorageProvider::class,
        'cloudinary' => CloudinaryStorageProvider::class
    ];
    
    public function uploadFile(UploadedFile $file, string $provider, array $metadata = []): array
    {
        try {
            // File validation
            if (!$this->validateFile($file)) {
                return ['success' => false, 'error' => 'Invalid file type or size'];
            }
            
            // Virus scanning if enabled
            if (config('filestorage.security.virus_scanning')) {
                if (!$this->scanForVirus($file)) {
                    return ['success' => false, 'error' => 'File failed security scan'];
                }
            }
            
            // Generate unique filename
            $filename = $this->generateUniqueFilename($file);
            
            // Get storage provider
            $storageProvider = new $this->providers[$provider]();
            
            // Upload file
            $uploadResult = $storageProvider->upload($file, $filename);
            
            if (!$uploadResult['success']) {
                return ['success' => false, 'error' => $uploadResult['error']];
            }
            
            // Process image if needed
            $thumbnailUrl = null;
            if ($this->isImage($file) && config('filestorage.processing.thumbnail_generation')) {
                $thumbnailUrl = $this->generateThumbnail($file, $storageProvider, $filename);
            }
            
            // Create database record
            $fileRecord = File::create([
                'user_id' => $metadata['user_id'],
                'category_id' => $metadata['category_id'],
                'original_name' => $file->getClientOriginalName(),
                'filename' => $filename,
                'file_path' => $uploadResult['path'],
                'file_size' => $file->getSize(),
                'file_type' => $file->getMimeType(),
                'extension' => $file->getClientOriginalExtension(),
                'storage_provider' => $provider,
                'url' => $uploadResult['url'],
                'thumbnail_url' => $thumbnailUrl,
                'description' => $metadata['description'],
                'tags' => $metadata['tags'],
                'is_public' => $metadata['is_public'],
                'metadata' => json_encode([
                    'width' => $this->getImageWidth($file),
                    'height' => $this->getImageHeight($file),
                    'duration' => $this->getVideoDuration($file)
                ])
            ]);
            
            return [
                'success' => true,
                'file' => $fileRecord,
                'url' => $uploadResult['url']
            ];
            
        } catch (\Exception $e) {
            return ['success' => false, 'error' => $e->getMessage()];
        }
    }
    
    public function deleteFile(File $file): array
    {
        try {
            $storageProvider = new $this->providers[$file->storage_provider]();
            $result = $storageProvider->delete($file->file_path);
            
            // Delete thumbnail if exists
            if ($file->thumbnail_url) {
                $thumbnailPath = str_replace('/thumbnails/', '', parse_url($file->thumbnail_url, PHP_URL_PATH));
                $storageProvider->delete('thumbnails/' . $thumbnailPath);
            }
            
            return $result;
            
        } catch (\Exception $e) {
            return ['success' => false, 'error' => $e->getMessage()];
        }
    }
    
    public function getDownloadUrl(File $file): string
    {
        $storageProvider = new $this->providers[$file->storage_provider]();
        return $storageProvider->getUrl($file->file_path);
    }
    
    private function validateFile(UploadedFile $file): bool
    {
        $allowedTypes = config('filestorage.allowed_file_types', []);
        $maxSize = config('filestorage.max_file_size', 10240); // KB
        
        // Check file type
        if (!empty($allowedTypes) && !in_array($file->getMimeType(), $allowedTypes)) {
            return false;
        }
        
        // Check file size
        if ($file->getSize() > ($maxSize * 1024)) {
            return false;
        }
        
        return true;
    }
    
    private function scanForVirus(UploadedFile $file): bool
    {
        // Implement virus scanning logic here
        // This would typically integrate with ClamAV or similar
        return true; // Placeholder
    }
    
    private function generateUniqueFilename(UploadedFile $file): string
    {
        return time() . '_' . uniqid() . '.' . $file->getClientOriginalExtension();
    }
    
    private function isImage(UploadedFile $file): bool
    {
        return strpos($file->getMimeType(), 'image/') === 0;
    }
    
    private function generateThumbnail(UploadedFile $file, $provider, string $filename): ?string
    {
        try {
            $thumbnailName = 'thumb_' . $filename;
            $thumbnailPath = 'thumbnails/' . $thumbnailName;
            
            // Create thumbnail
            $image = Image::make($file->getRealPath());
            $image->resize(300, 300, function ($constraint) {
                $constraint->aspectRatio();
                $constraint->upsize();
            });
            
            // Save thumbnail
            $tempPath = storage_path('app/temp/' . $thumbnailName);
            $image->save($tempPath);
            
            // Upload thumbnail
            $uploadResult = $provider->uploadFromPath($tempPath, $thumbnailPath);
            
            // Clean up temp file
            unlink($tempPath);
            
            return $uploadResult['success'] ? $uploadResult['url'] : null;
            
        } catch (\Exception $e) {
            return null;
        }
    }
    
    private function getImageWidth(UploadedFile $file): ?int
    {
        if (!$this->isImage($file)) return null;
        
        try {
            $imageInfo = getimagesize($file->getRealPath());
            return $imageInfo[0] ?? null;
        } catch (\Exception $e) {
            return null;
        }
    }
    
    private function getImageHeight(UploadedFile $file): ?int
    {
        if (!$this->isImage($file)) return null;
        
        try {
            $imageInfo = getimagesize($file->getRealPath());
            return $imageInfo[1] ?? null;
        } catch (\Exception $e) {
            return null;
        }
    }
    
    private function getVideoDuration(UploadedFile $file): ?int
    {
        // Implement video duration extraction if needed
        return null;
    }
}
""")
        
        service_content = service_template.render()
        service_file = self.backend_path / "app" / "Services" / "FileStorageService.php"
        with open(service_file, 'w') as f:
            f.write(service_content)
    
    def _generate_file_storage_config(self):
        """Generate file storage configuration"""
        
        template = Template(r"""<?php

return [
    'default_provider' => env('FILE_STORAGE_PROVIDER', 'local'),
    
    'providers' => [
        'local' => [
            'driver' => 'local',
            'root' => storage_path('app/uploads'),
            'url' => env('APP_URL') . '/storage/uploads',
        ],
        
        'aws_s3' => [
            'driver' => 's3',
            'key' => env('AWS_ACCESS_KEY_ID'),
            'secret' => env('AWS_SECRET_ACCESS_KEY'),
            'region' => env('AWS_DEFAULT_REGION'),
            'bucket' => env('AWS_BUCKET'),
            'url' => env('AWS_URL'),
        ],
        
        'azure_blob' => [
            'driver' => 'azure',
            'account_name' => env('AZURE_STORAGE_ACCOUNT'),
            'account_key' => env('AZURE_STORAGE_KEY'),
            'container' => env('AZURE_STORAGE_CONTAINER'),
        ],
        
        'google_cloud' => [
            'driver' => 'gcs',
            'project_id' => env('GOOGLE_CLOUD_PROJECT_ID'),
            'key_file' => env('GOOGLE_CLOUD_KEY_FILE'),
            'bucket' => env('GOOGLE_CLOUD_STORAGE_BUCKET'),
        ],
        
        'cloudinary' => [
            'driver' => 'cloudinary',
            'cloud_name' => env('CLOUDINARY_CLOUD_NAME'),
            'api_key' => env('CLOUDINARY_API_KEY'),
            'api_secret' => env('CLOUDINARY_API_SECRET'),
        ],
    ],
    
    'allowed_file_types' => [
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
        'video/mp4', 'video/mpeg', 'video/quicktime',
        'audio/mpeg', 'audio/wav', 'audio/ogg',
        'application/pdf', 'application/msword', 'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain', 'text/csv',
        'application/zip', 'application/x-rar-compressed',
    ],
    
    'max_file_size' => env('FILE_MAX_SIZE', 10240), // KB
    'user_storage_limit' => env('USER_STORAGE_LIMIT', 1073741824), // 1GB in bytes
    
    'processing' => [
        'image_optimization' => env('FILE_IMAGE_OPTIMIZATION', true),
        'thumbnail_generation' => env('FILE_THUMBNAIL_GENERATION', true),
        'thumbnail_sizes' => [
            'small' => [150, 150],
            'medium' => [300, 300],
            'large' => [600, 600],
        ],
    ],
    
    'security' => [
        'virus_scanning' => env('FILE_VIRUS_SCANNING', false),
        'content_filtering' => env('FILE_CONTENT_FILTERING', true),
        'encryption' => env('FILE_ENCRYPTION', false),
    ],
    
    'cleanup' => [
        'delete_temp_files' => env('FILE_DELETE_TEMP', true),
        'cleanup_interval' => env('FILE_CLEANUP_INTERVAL', 24), // hours
        'retention_days' => env('FILE_RETENTION_DAYS', 365),
    ],
];
""")
        
        config_content = template.render()
        
        config_file = self.backend_path / "config" / "filestorage.php"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        return config_content
    
    def _generate_file_storage_routes(self):
        """Generate file storage routes"""
        
        template = Template(r"""<?php

// File Storage Routes
use App\\Controllers\FileController;

// File upload and management
Route::post('/files/upload', [FileController::class, 'upload'])->middleware('auth');
Route::get('/files', [FileController::class, 'listFiles'])->middleware('auth');
Route::get('/files/{id}/download', [FileController::class, 'download'])->middleware('auth');
Route::delete('/files/{id}', [FileController::class, 'delete'])->middleware('auth');

// File sharing
Route::post('/files/{id}/share', [FileController::class, 'shareFile'])->middleware('auth');
Route::get('/files/shared/{token}', [FileController::class, 'getSharedFile']);

// File categories
Route::post('/files/categories', [FileController::class, 'createCategory'])->middleware('auth');
Route::get('/files/categories', function() {
    return response()->json(\App\Models\FileCategory::where('user_id', auth()->id())->get());
})->middleware('auth');

// Usage statistics
Route::get('/files/usage', [FileController::class, 'getUsageStatistics'])->middleware('auth');
""")
        
        routes_content = template.render()
        
        routes_file = self.backend_path / "routes" / "file_storage.php"
        with open(routes_file, 'w') as f:
            f.write(routes_content)
        
        return routes_content
    
    def _generate_ai_controller(self):
        """Generate AI/ML controller"""
        
        template = Template(r"""<?php

namespace App\\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Validator;
use App\\Models\AiConversation;
use App\\Models\AiTask;
use App\\Models\AiPromptTemplate;
use App\\Models\AiModelMetrics;

class AiController
{
    private $providers = [
        'openai' => '\\App\\Services\\OpenAiService',
        'anthropic' => '\\App\\Services\\AnthropicService',
        'google_ai' => '\\App\\Services\\GoogleAiService',
        'huggingface' => '\\App\\Services\\HuggingFaceService',
        'azure_ai' => '\\App\\Services\\AzureAiService'
    ];
    
    public function startChat(Request $request): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'provider' => 'string|in:openai,anthropic,google_ai,huggingface,azure_ai',
                'model' => 'required|string',
                'messages' => 'required|array|min:1',
                'messages.*.role' => 'required|string|in:system,user,assistant',
                'messages.*.content' => 'required|string',
                'system_prompt' => 'string',
                'settings' => 'array',
                'stream' => 'boolean'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $validated = $validator->validated();
            $provider = $validated['provider'] ?? config('ai.default_provider', 'openai');
            
            // Create conversation record
            $conversation = AiConversation::create([
                'user_id' => $request->user()->id,
                'title' => $this->generateConversationTitle($validated['messages']),
                'provider' => $provider,
                'model' => $validated['model'],
                'system_prompt' => $validated['system_prompt'] ?? null,
                'messages' => json_encode($validated['messages']),
                'settings' => json_encode($validated['settings'] ?? [])
            ]);
            
            // Send to AI provider
            $service = new $this->providers[$provider]();
            $result = $service->chat([
                'model' => $validated['model'],
                'messages' => $validated['messages'],
                'settings' => $validated['settings'] ?? [],
                'stream' => $validated['stream'] ?? false
            ]);
            
            // Update conversation with response
            $updatedMessages = $validated['messages'];
            $updatedMessages[] = [
                'role' => 'assistant',
                'content' => $result['message']['content']
            ];
            
            $conversation->update([
                'messages' => json_encode($updatedMessages),
                'total_tokens' => $conversation->total_tokens + ($result['usage']['total_tokens'] ?? 0),
                'total_cost' => $conversation->total_cost + ($result['cost'] ?? 0)
            ]);
            
            // Update metrics
            $this->updateModelMetrics($provider, $validated['model'], 'chat', $result);
            
            return response()->json([
                'conversation_id' => $conversation->id,
                'message' => $result['message'],
                'usage' => $result['usage'] ?? [],
                'cost' => $result['cost'] ?? 0
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'AI chat failed',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function generateCompletion(Request $request): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'provider' => 'string|in:openai,anthropic,google_ai,huggingface,azure_ai',
                'model' => 'required|string',
                'prompt' => 'required|string|max:10000',
                'settings' => 'array'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $validated = $validator->validated();
            $provider = $validated['provider'] ?? config('ai.default_provider', 'openai');
            
            // Send to AI provider
            $service = new $this->providers[$provider]();
            $result = $service->completion([
                'model' => $validated['model'],
                'prompt' => $validated['prompt'],
                'settings' => $validated['settings'] ?? []
            ]);
            
            return response()->json([
                'completion' => $result['completion'],
                'usage' => $result['usage'] ?? [],
                'cost' => $result['cost'] ?? 0
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'AI completion failed',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function generateEmbeddings(Request $request): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'provider' => 'string|in:openai,google_ai',
                'model' => 'required|string',
                'input' => 'required|array|min:1|max:100',
                'input.*' => 'required|string|max:8000'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $validated = $validator->validated();
            $provider = $validated['provider'] ?? 'openai';
            
            // Send to AI provider
            $service = new $this->providers[$provider]();
            $result = $service->embeddings([
                'model' => $validated['model'],
                'input' => $validated['input']
            ]);
            
            return response()->json([
                'embeddings' => $result['embeddings'],
                'usage' => $result['usage'] ?? [],
                'cost' => $result['cost'] ?? 0
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Embedding generation failed',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function getUsageAnalytics(Request $request): JsonResponse
    {
        $timeframe = $request->get('timeframe', '30d');
        $provider = $request->get('provider');
        $model = $request->get('model');
        $taskType = $request->get('task_type');
        
        $query = AiModelMetrics::query();
        
        // Apply filters
        if ($provider) {
            $query->where('provider', $provider);
        }
        if ($model) {
            $query->where('model', $model);
        }
        if ($taskType) {
            $query->where('task_type', $taskType);
        }
        
        // Apply timeframe
        $startDate = match($timeframe) {
            '24h' => now()->subDay(),
            '7d' => now()->subWeek(),
            '30d' => now()->subDays(30),
            '90d' => now()->subDays(90),
            default => now()->subDays(30)
        };
        
        $query->where('date', '>=', $startDate->toDateString());
        
        $metrics = $query->get();
        
        $analytics = [
            'usage_stats' => [
                'total_requests' => $metrics->sum('total_requests'),
                'successful_requests' => $metrics->sum('successful_requests'),
                'failed_requests' => $metrics->sum('failed_requests'),
                'success_rate' => $metrics->sum('total_requests') > 0 
                    ? ($metrics->sum('successful_requests') / $metrics->sum('total_requests')) * 100 
                    : 0
            ],
            'cost_breakdown' => [
                'total_cost' => $metrics->sum('total_cost'),
                'total_tokens' => $metrics->sum('total_tokens')
            ]
        ];
        
        return response()->json($analytics);
    }
    
    private function generateConversationTitle(array $messages): string
    {
        $firstUserMessage = collect($messages)
            ->where('role', 'user')
            ->first();
        
        if (!$firstUserMessage) {
            return 'New Conversation';
        }
        
        $content = $firstUserMessage['content'];
        return strlen($content) > 50 
            ? substr($content, 0, 47) . '...' 
            : $content;
    }
    
    private function updateModelMetrics(string $provider, string $model, string $taskType, array $result): void
    {
        $date = now()->toDateString();
        
        $metrics = AiModelMetrics::firstOrNew([
            'provider' => $provider,
            'model' => $model,
            'task_type' => $taskType,
            'date' => $date
        ]);
        
        $metrics->total_requests += 1;
        
        if (isset($result['error'])) {
            $metrics->failed_requests += 1;
        } else {
            $metrics->successful_requests += 1;
        }
        
        if (isset($result['usage']['total_tokens'])) {
            $metrics->total_tokens += $result['usage']['total_tokens'];
        }
        
        if (isset($result['cost'])) {
            $metrics->total_cost += $result['cost'];
        }
        
        $metrics->last_used_at = now();
        $metrics->save();
    }
}
""")
        
        controller_content = template.render()
        
        controller_file = self.backend_path / "app" / "Controllers" / "AiController.php"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
        
        return controller_content
    
    def _generate_sms_controller(self):
        """Generate SMS controller"""
        
        template = Template(r"""<?php

namespace App\\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Validator;
use App\\Models\SmsMessage;
use App\\Models\SmsTemplate;
use App\\Models\PhoneVerification;

class SmsController
{
    private $providers = [
        'twilio' => '\\App\\Services\\TwilioSmsService',
        'aws_sns' => '\\App\\Services\\AwsSnsService',
        'nexmo' => '\\App\\Services\\NexmoSmsService',
        'messagebird' => '\\App\\Services\\MessageBirdSmsService'
    ];
    
    public function sendSms(Request $request): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'to_numbers' => 'required|array|min:1',
                'to_numbers.*' => 'required|string|regex:/^\\+[1-9]\\d{1,14}$/',
                'message' => 'required|string|max:1600',
                'provider' => 'string|in:twilio,aws_sns,nexmo,messagebird',
                'template_id' => 'string|exists:sms_templates,id',
                'template_variables' => 'array',
                'scheduled_at' => 'date|after:now'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $validated = $validator->validated();
            $provider = $validated['provider'] ?? config('sms.default_provider', 'twilio');
            
            // Process message template if provided
            $message = $validated['message'];
            if (isset($validated['template_id'])) {
                $template = SmsTemplate::findOrFail($validated['template_id']);
                $message = $this->processTemplate($template->template, $validated['template_variables'] ?? []);
            }
            
            $service = new $this->providers[$provider]();
            $messageIds = [];
            $totalCost = 0;
            
            foreach ($validated['to_numbers'] as $toNumber) {
                // Create SMS message record
                $smsMessage = SmsMessage::create([
                    'user_id' => $request->user()->id,
                    'to_number' => $toNumber,
                    'from_number' => $service->getFromNumber(),
                    'message' => $message,
                    'provider' => $provider,
                    'status' => 'queued',
                    'message_type' => 'sms',
                    'segments' => $this->calculateSegments($message),
                    'scheduled_at' => $validated['scheduled_at'] ?? now(),
                    'metadata' => json_encode([
                        'template_id' => $validated['template_id'] ?? null,
                        'template_variables' => $validated['template_variables'] ?? []
                    ])
                ]);
                
                // Send SMS immediately or schedule
                if (empty($validated['scheduled_at'])) {
                    $result = $service->sendSms([
                        'to' => $toNumber,
                        'message' => $message,
                        'message_id' => $smsMessage->id
                    ]);
                    
                    $smsMessage->update([
                        'provider_message_id' => $result['provider_message_id'],
                        'status' => $result['status'],
                        'cost' => $result['cost'] ?? 0,
                        'currency' => $result['currency'] ?? 'USD',
                        'sent_at' => $result['status'] === 'sent' ? now() : null
                    ]);
                    
                    $totalCost += $result['cost'] ?? 0;
                }
                
                $messageIds[] = $smsMessage->id;
            }
            
            return response()->json([
                'message_ids' => $messageIds,
                'status' => 'success',
                'estimated_cost' => $totalCost,
                'currency' => 'USD'
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to send SMS',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function sendVerificationCode(Request $request): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'phone_number' => 'required|string|regex:/^\\+[1-9]\\d{1,14}$/',
                'provider' => 'string|in:twilio,nexmo,messagebird'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $validated = $validator->validated();
            $provider = $validated['provider'] ?? 'twilio';
            
            // Generate verification code
            $verificationCode = sprintf('%06d', mt_rand(100000, 999999));
            
            // Create verification record
            $verification = PhoneVerification::create([
                'phone_number' => $validated['phone_number'],
                'verification_code' => hash('sha256', $verificationCode),
                'provider' => $provider,
                'status' => 'pending',
                'expires_at' => now()->addMinutes(10)
            ]);
            
            // Send verification SMS
            $service = new $this->providers[$provider]();
            $message = "Your verification code is: {$verificationCode}. This code expires in 10 minutes.";
            
            $result = $service->sendSms([
                'to' => $validated['phone_number'],
                'message' => $message,
                'message_id' => 'verify_' . $verification->id
            ]);
            
            return response()->json([
                'verification_id' => $verification->id,
                'status' => 'sent',
                'expires_at' => $verification->expires_at
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to send verification code',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function verifyPhoneNumber(Request $request): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'verification_id' => 'required|string|exists:phone_verifications,id',
                'verification_code' => 'required|string|size:6'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $validated = $validator->validated();
            
            $verification = PhoneVerification::findOrFail($validated['verification_id']);
            
            // Check if verification is expired
            if ($verification->expires_at < now()) {
                $verification->update(['status' => 'expired']);
                return response()->json([
                    'error' => 'Verification code expired',
                    'verified' => false
                ], 400);
            }
            
            // Check if too many attempts
            if ($verification->attempts >= 3) {
                $verification->update(['status' => 'failed']);
                return response()->json([
                    'error' => 'Too many verification attempts',
                    'verified' => false
                ], 400);
            }
            
            // Verify code
            $verification->increment('attempts');
            
            if (hash('sha256', $validated['verification_code']) === $verification->verification_code) {
                $verification->update([
                    'status' => 'verified',
                    'verified_at' => now()
                ]);
                
                return response()->json([
                    'status' => 'verified',
                    'verified' => true
                ]);
            } else {
                return response()->json([
                    'error' => 'Invalid verification code',
                    'verified' => false,
                    'attempts_remaining' => 3 - $verification->attempts
                ], 400);
            }
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Verification failed',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function getSmsTemplates(Request $request): JsonResponse
    {
        $query = SmsTemplate::where('is_active', true);
        
        if ($request->has('category')) {
            $query->where('category', $request->category);
        }
        
        $templates = $query->orderBy('name')->get();
        
        return response()->json(['templates' => $templates]);
    }
    
    public function getSmsStatus(Request $request, $messageId): JsonResponse
    {
        try {
            $message = SmsMessage::where('user_id', $request->user()->id)
                ->where('id', $messageId)
                ->firstOrFail();
            
            return response()->json([
                'message_id' => $message->id,
                'status' => $message->status,
                'sent_at' => $message->sent_at,
                'delivered_at' => $message->delivered_at,
                'cost' => $message->cost,
                'currency' => $message->currency,
                'segments' => $message->segments
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Message not found',
                'message' => $e->getMessage()
            ], 404);
        }
    }
    
    public function handleWebhook(Request $request, $provider): JsonResponse
    {
        try {
            $service = new $this->providers[$provider]();
            $result = $service->handleWebhook($request->all(), $request->headers->all());
            
            // Update message status based on webhook
            if ($result['message_id'] ?? false) {
                $message = SmsMessage::where('provider_message_id', $result['message_id'])
                    ->orWhere('id', str_replace('verify_', '', $result['message_id']))
                    ->first();
                
                if ($message) {
                    $updateData = ['status' => $result['status']];
                    
                    if ($result['status'] === 'delivered') {
                        $updateData['delivered_at'] = now();
                    }
                    
                    if (isset($result['error'])) {
                        $updateData['error_message'] = $result['error'];
                    }
                    
                    $message->update($updateData);
                }
            }
            
            return response()->json(['status' => 'processed']);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Webhook processing failed',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    private function processTemplate(string $template, array $variables): string
    {
        foreach ($variables as $key => $value) {
            $template = str_replace('{{' . $key . '}}', $value, $template);
        }
        
        return $template;
    }
    
    private function calculateSegments(string $message): int
    {
        $length = mb_strlen($message);
        
        if ($length <= 160) {
            return 1;
        } else if ($length <= 306) {
            return 2;
        } else {
            return ceil($length / 153);
        }
    }
}
""")
        
        controller_content = template.render()
        
        controller_file = self.backend_path / "app" / "Controllers" / "SmsController.php"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
        
        return controller_content
    
    def _generate_push_notification_controller(self):
        """Generate push notification controller"""
        
        template = Template(r"""<?php

namespace App\\Controllers;

use Illuminate\\Http\\Request;
use Illuminate\\Http\\JsonResponse;
use App\\Models\\PushNotification;
use App\\Services\\PushNotificationService;

class PushNotificationController
{
    private $providers = [
        'firebase' => '\\App\\Services\\FirebasePushService',
        'apns' => '\\App\\Services\\APNSService',
        'web_push' => '\\App\\Services\\WebPushService',
        'onesignal' => '\\App\\Services\\OneSignalService'
    ];
    
    public function sendNotification(Request $request): JsonResponse
    {
        try {
            $validated = $request->validate([
                'title' => 'required|string|max:255',
                'body' => 'required|string|max:1000',
                'device_tokens' => 'required|array',
                'provider' => 'required|string|in:firebase,apns,web_push,onesignal',
                'icon' => 'string',
                'data' => 'array'
            ]);
            
            $notification = PushNotification::create([
                'title' => $validated['title'],
                'body' => $validated['body'],
                'device_tokens' => json_encode($validated['device_tokens']),
                'provider' => $validated['provider'],
                'icon' => $validated['icon'] ?? null,
                'data' => json_encode($validated['data'] ?? [])
            ]);
            
            // Send notification
            $service = new $this->providers[$validated['provider']]();
            $result = $service->sendNotification([
                'title' => $validated['title'],
                'body' => $validated['body'],
                'tokens' => $validated['device_tokens'],
                'icon' => $validated['icon'] ?? null,
                'data' => $validated['data'] ?? []
            ]);
            
            $notification->update(['status' => 'sent']);
            
            return response()->json([
                'message' => 'Notification sent successfully',
                'notification_id' => $notification->id,
                'result' => $result
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to send notification',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function getNotificationStatus($id): JsonResponse
    {
        $notification = PushNotification::findOrFail($id);
        
        return response()->json([
            'id' => $notification->id,
            'title' => $notification->title,
            'status' => $notification->status,
            'provider' => $notification->provider,
            'created_at' => $notification->created_at,
            'updated_at' => $notification->updated_at
        ]);
    }
}
""")
        
        controller_content = template.render()
        controller_file = self.backend_path / "app" / "Http" / "Controllers" / "PushNotificationController.php"
        
        with open(controller_file, 'w') as f:
            f.write(controller_content)
        
        return controller_content

            
            // Update notification status based on webhook
            if ($result['notification_id'] ?? false) {
                $notification = PushNotification::where('provider_message_id', $result['notification_id'])
                    ->first();
                
                if ($notification) {
                    $updateData = ['status' => $result['status']];
                    
                    if ($result['status'] === 'delivered') {
                        $updateData['delivered_at'] = now();
                    } elseif ($result['status'] === 'opened') {
                        $updateData['opened_at'] = now();
                    }
                    
                    $notification->update($updateData);
                }
            }
            
            return response()->json(['status' => 'processed']);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Webhook processing failed',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    private function getTargetDeviceTokens(array $userIds, array $platforms): array
    {
        $query = DeviceToken::where('is_active', true)
            ->whereIn('platform', $platforms);
        
        if (!empty($userIds)) {
            $query->whereIn('user_id', $userIds);
        }
        
        return $query->pluck('token')->toArray();
    }
}
""")
        
        controller_content = template.render()
        
        controller_file = self.backend_path / "app" / "Controllers" / "PushNotificationController.php"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
        
        return controller_content
    
    private function sendToProvider(PushNotification $notification, string $provider): array
    {
        $service = new $this->providers[$provider]();
        
        $payload = [
            'title' => $notification->title,
            'body' => $notification->body,
            'icon' => $notification->icon,
            'data' => json_decode($notification->data ?? '{}', true),
            'device_tokens' => json_decode($notification->device_tokens, true)
        ];
        
        return $service->sendNotification($payload);
    }
    
    def _generate_payment_gateway_controller(self):
        """Generate payment gateway controller"""
        
        template = Template(r"""<?php

namespace App\\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Hash;
use App\\Models\Payment;
use App\\Models\PaymentMethod;
use App\\Models\User;

class PaymentController
{
    private $providers = [
        'stripe' => '\\App\\Services\\StripePaymentService',
        'paypal' => '\\App\\Services\\PayPalPaymentService',
        'square' => '\\App\\Services\\SquarePaymentService',
        'razorpay' => '\\App\\Services\\RazorpayPaymentService'
    ];
    
    public function createPaymentIntent(Request $request): JsonResponse
    {
        try {
            $validated = $request->validate([
                'amount' => 'required|numeric|min:0.01',
                'currency' => 'required|string|size:3',
                'provider' => 'required|string|in:stripe,paypal,square,razorpay',
                'payment_method_types' => 'array',
                'description' => 'string|max:500',
                'metadata' => 'array'
            ]);
            
            $provider = $validated['provider'];
            $service = new $this->providers[$provider]();
            
            // Create payment intent with provider
            $intent = $service->createPaymentIntent([
                'amount' => $validated['amount'],
                'currency' => $validated['currency'],
                'payment_method_types' => $validated['payment_method_types'] ?? ['card'],
                'description' => $validated['description'] ?? '',
                'metadata' => $validated['metadata'] ?? []
            ]);
            
            // Save payment record
            $payment = Payment::create([
                'user_id' => $request->user()->id,
                'order_id' => $intent['order_id'],
                'provider' => $provider,
                'provider_payment_id' => $intent['payment_id'],
                'amount' => $validated['amount'],
                'currency' => $validated['currency'],
                'status' => 'pending',
                'description' => $validated['description'] ?? '',
                'metadata' => json_encode($validated['metadata'] ?? [])
            ]);
            
            return response()->json([
                'client_secret' => $intent['client_secret'],
                'payment_id' => $payment->id,
                'provider_payment_id' => $intent['payment_id'],
                'status' => 'pending'
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to create payment intent',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function confirmPayment(Request $request): JsonResponse
    {
        try {
            $validated = $request->validate([
                'payment_id' => 'required|string',
                'provider_payment_id' => 'string'
            ]);
            
            $payment = Payment::findOrFail($validated['payment_id']);
            
            // Verify payment with provider
            $service = new $this->providers[$payment->provider]();
            $result = $service->confirmPayment($payment->provider_payment_id);
            
            // Update payment status
            $payment->update([
                'status' => $result['status'],
                'fees' => $result['fees'] ?? 0
            ]);
            
            return response()->json([
                'status' => $result['status'],
                'payment_id' => $payment->id,
                'redirect_url' => $result['status'] === 'completed' ? '/payment/success' : '/payment/failed'
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to confirm payment',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function processRefund(Request $request): JsonResponse
    {
        try {
            $validated = $request->validate([
                'payment_id' => 'required|string',
                'amount' => 'numeric|min:0.01',
                'reason' => 'string|max:500'
            ]);
            
            $payment = Payment::findOrFail($validated['payment_id']);
            
            if ($payment->status !== 'completed') {
                return response()->json(['error' => 'Payment not eligible for refund'], 400);
            }
            
            $refundAmount = $validated['amount'] ?? $payment->amount;
            
            // Process refund with provider
            $service = new $this->providers[$payment->provider]();
            $refund = $service->processRefund([
                'payment_id' => $payment->provider_payment_id,
                'amount' => $refundAmount,
                'reason' => $validated['reason'] ?? 'Requested by customer'
            ]);
            
            // Update payment record
            $payment->update([
                'status' => $refundAmount >= $payment->amount ? 'refunded' : 'partially_refunded',
                'refund_amount' => $payment->refund_amount + $refundAmount
            ]);
            
            return response()->json([
                'refund_id' => $refund['refund_id'],
                'status' => $refund['status'],
                'amount' => $refundAmount
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to process refund',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function savePaymentMethod(Request $request): JsonResponse
    {
        try {
            $validated = $request->validate([
                'provider' => 'required|string|in:stripe,paypal,square,razorpay',
                'provider_method_id' => 'required|string',
                'type' => 'required|string|in:card,bank_account,paypal,digital_wallet',
                'is_default' => 'boolean'
            ]);
            
            // Remove existing default if setting new default
            if ($validated['is_default'] ?? false) {
                PaymentMethod::where('user_id', $request->user()->id)
                    ->update(['is_default' => false]);
            }
            
            $paymentMethod = PaymentMethod::create([
                'user_id' => $request->user()->id,
                'provider' => $validated['provider'],
                'provider_method_id' => $validated['provider_method_id'],
                'type' => $validated['type'],
                'is_default' => $validated['is_default'] ?? false
            ]);
            
            return response()->json([
                'payment_method_id' => $paymentMethod->id,
                'status' => 'saved'
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to save payment method',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function getPaymentMethods(Request $request): JsonResponse
    {
        $paymentMethods = PaymentMethod::where('user_id', $request->user()->id)
            ->orderBy('is_default', 'desc')
            ->orderBy('created_at', 'desc')
            ->get();
        
        return response()->json(['payment_methods' => $paymentMethods]);
    }
    
    public function deletePaymentMethod(Request $request, $methodId): JsonResponse
    {
        try {
            $paymentMethod = PaymentMethod::where('user_id', $request->user()->id)
                ->where('id', $methodId)
                ->firstOrFail();
            
            $paymentMethod->delete();
            
            return response()->json(['status' => 'deleted']);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to delete payment method',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function handleWebhook(Request $request, $provider): JsonResponse
    {
        try {
            $service = new $this->providers[$provider]();
            $result = $service->handleWebhook($request->all(), $request->headers->all());
            
            // Update payment status based on webhook
            if ($result['payment_id'] ?? false) {
                $payment = Payment::where('provider_payment_id', $result['payment_id'])->first();
                if ($payment) {
                    $payment->update(['status' => $result['status']]);
                }
            }
            
            return response()->json(['status' => 'processed']);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Webhook processing failed',
                'message' => $e->getMessage()
            ], 400);
        }
    }
}
""")
        
        controller_content = template.render()
        
        controller_file = self.backend_path / "app" / "Controllers" / "PaymentController.php"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
        
        return controller_content
    
    def _generate_smart_form_validation(self):
        """Generate smart form validation services and security features"""
        
        # Generate smart validation service
        self._generate_smart_validation_service()
        
        # Generate field validation rules
        self._generate_field_validation_rules()
        
        # Generate security services
        self._generate_smart_security_services()
        
        # Generate smart form controllers
        self._generate_smart_form_controller()
        
        # Generate validation middleware
        self._generate_validation_middleware()
    
    def _generate_smart_validation_service(self):
        """Generate smart validation service with intelligent rules"""
        
        template = Template(r"""<?php

namespace App\\Services;

use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;
use App\\Models\User;
use GuzzleHttp\Client;

class SmartValidationService
{
    private $disposableEmailDomains = [];
    private $blacklistedPhones = [];
    
    public function __construct()
    {
        $this->loadDisposableEmailDomains();
        $this->loadBlacklistedPhones();
    }
    
    /**
     * Validate email with smart features
     */
    public function validateEmail(string $email, array $options = []): array
    {
        $result = [
            'valid' => true,
            'errors' => [],
            'suggestions' => [],
            'security_flags' => []
        ];
        
        // Basic email format validation
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $result['valid'] = false;
            $result['errors'][] = 'Invalid email format';
            return $result;
        }
        
        $domain = substr($email, strpos($email, '@') + 1);
        
        // Check for disposable email domains
        if ($options['block_disposable'] ?? false) {
            if ($this->isDisposableEmail($domain)) {
                $result['valid'] = false;
                $result['errors'][] = 'Disposable email addresses are not allowed';
                $result['security_flags'][] = 'disposable_email';
            }
        }
        
        // Check for typos and suggest corrections
        $suggestions = $this->suggestEmailCorrections($email);
        if (!empty($suggestions)) {
            $result['suggestions'] = $suggestions;
        }
        
        // Check if email is already registered
        if ($options['check_registered'] ?? false) {
            $isRegistered = User::where('email', $email)->exists();
            if ($isRegistered) {
                $result['valid'] = false;
                $result['errors'][] = 'This email is already registered';
                $result['security_flags'][] = 'already_registered';
            }
        }
        
        return $result;
    }
    
    /**
     * Validate phone number with smart features
     */
    public function validatePhone(string $phone, array $options = []): array
    {
        $result = [
            'valid' => true,
            'errors' => [],
            'formatted' => '',
            'country_code' => '',
            'security_flags' => []
        ];
        
        // Clean phone number
        $cleanPhone = preg_replace('/[^+\d]/', '', $phone);
        
        // Auto-detect country code
        $countryCode = $this->detectCountryCode($cleanPhone, $options['geo_ip'] ?? null);
        $result['country_code'] = $countryCode;
        
        // Format phone number
        $formatted = $this->formatPhoneNumber($cleanPhone, $countryCode);
        if ($formatted) {
            $result['formatted'] = $formatted;
        } else {
            $result['valid'] = false;
            $result['errors'][] = 'Invalid phone number format';
            return $result;
        }
        
        // Check against blacklisted numbers
        if (in_array($cleanPhone, $this->blacklistedPhones)) {
            $result['valid'] = false;
            $result['errors'][] = 'This phone number is not allowed';
            $result['security_flags'][] = 'blacklisted';
        }
        
        // Check if phone is already registered
        if ($options['check_registered'] ?? false) {
            $isRegistered = User::where('phone', $cleanPhone)->exists();
            if ($isRegistered) {
                $result['valid'] = false;
                $result['errors'][] = 'This phone number is already registered';
                $result['security_flags'][] = 'already_registered';
            }
        }
        
        return $result;
    }
    
    /**
     * Validate password strength with intelligent scoring
     */
    public function validatePasswordStrength(string $password): array
    {
        $result = [
            'score' => 0,
            'strength' => 'very_weak',
            'feedback' => [],
            'requirements_met' => [],
            'security_flags' => []
        ];
        
        $score = 0;
        $feedback = [];
        $requirementsMet = [];
        
        // Length check
        if (strlen($password) >= 8) {
            $score += 1;
            $requirementsMet[] = 'min_length';
        } else {
            $feedback[] = 'Password should be at least 8 characters long';
        }
        
        // Uppercase check
        if (preg_match('/[A-Z]/', $password)) {
            $score += 1;
            $requirementsMet[] = 'uppercase';
        } else {
            $feedback[] = 'Add at least one uppercase letter';
        }
        
        // Lowercase check
        if (preg_match('/[a-z]/', $password)) {
            $score += 1;
            $requirementsMet[] = 'lowercase';
        } else {
            $feedback[] = 'Add at least one lowercase letter';
        }
        
        // Number check
        if (preg_match('/\d/', $password)) {
            $score += 1;
            $requirementsMet[] = 'number';
        } else {
            $feedback[] = 'Add at least one number';
        }
        
        // Special character check
        if (preg_match('/[^a-zA-Z\d]/', $password)) {
            $score += 1;
            $requirementsMet[] = 'special_char';
        } else {
            $feedback[] = 'Add at least one special character';
        }
        
        // Length bonus
        if (strlen($password) >= 12) {
            $score += 1;
            $requirementsMet[] = 'long_length';
        }
        
        // Check against common passwords
        if ($this->isCommonPassword($password)) {
            $score = max(0, $score - 2);
            $feedback[] = 'This password is too common';
            $result['security_flags'][] = 'common_password';
        }
        
        // Check for data breach exposure
        if ($this->isBreachedPassword($password)) {
            $score = max(0, $score - 3);
            $feedback[] = 'This password has been found in data breaches';
            $result['security_flags'][] = 'breached_password';
        }
        
        // Determine strength level
        $strength = 'very_weak';
        if ($score >= 6) $strength = 'very_strong';
        elseif ($score >= 5) $strength = 'strong';
        elseif ($score >= 4) $strength = 'medium';
        elseif ($score >= 2) $strength = 'weak';
        
        $result['score'] = $score;
        $result['strength'] = $strength;
        $result['feedback'] = $feedback;
        $result['requirements_met'] = $requirementsMet;
        
        return $result;
    }
    
    /**
     * Validate OTP with smart features
     */
    public function validateOTP(string $otp, string $identifier, array $options = []): array
    {
        $result = [
            'valid' => true,
            'errors' => [],
            'remaining_attempts' => 3,
            'expires_in' => 0
        ];
        
        // Check OTP format
        if (!preg_match('/^\d{4,6}$/', $otp)) {
            $result['valid'] = false;
            $result['errors'][] = 'OTP must be 4-6 digits';
            return $result;
        }
        
        // Check rate limiting
        $cacheKey = \"otp_attempts:{$identifier}\";
        $attempts = Cache::get($cacheKey, 0);
        
        if ($attempts >= 3) {
            $result['valid'] = false;
            $result['errors'][] = 'Too many OTP attempts. Please request a new code.';
            return $result;
        }
        
        // Verify OTP (this would integrate with your OTP storage/generation system)
        $storedOTP = Cache::get(\"otp:{$identifier}\");
        if (!$storedOTP || $storedOTP !== $otp) {
            $result['valid'] = false;
            $result['errors'][] = 'Invalid or expired OTP';
            
            // Increment attempts
            Cache::put($cacheKey, $attempts + 1, 300); // 5 minutes
            $result['remaining_attempts'] = 2 - $attempts;
            return $result;
        }
        
        // Clear attempts on successful validation
        Cache::forget($cacheKey);
        Cache::forget(\"otp:{$identifier}\");
        
        return $result;
    }
    
    // Private helper methods
    
    private function loadDisposableEmailDomains(): void
    {
        // Load from cache or external service
        $this->disposableEmailDomains = Cache::remember('disposable_email_domains', 3600, function () {
            return [
                '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
                'mailinator.com', 'yopmail.com', 'throwaway.email'
            ];
        });
    }
    
    private function loadBlacklistedPhones(): void
    {
        $this->blacklistedPhones = Cache::remember('blacklisted_phones', 3600, function () {
            return [];
        });
    }
    
    private function isDisposableEmail(string $domain): bool
    {
        return in_array(strtolower($domain), $this->disposableEmailDomains);
    }
    
    private function suggestEmailCorrections(string $email): array
    {
        $suggestions = [];
        $commonDomains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'];
        
        $domain = substr($email, strpos($email, '@') + 1);
        $localPart = substr($email, 0, strpos($email, '@'));
        
        foreach ($commonDomains as $commonDomain) {
            $similarity = similar_text($domain, $commonDomain, $percent);
            if ($percent > 70 && $percent < 100) {
                $suggestions[] = $localPart . '@' . $commonDomain;
            }
        }
        
        return array_slice($suggestions, 0, 3);
    }
    
    private function detectCountryCode(string $phone, ?string $geoIP = null): string
    {
        if (str_starts_with($phone, '+')) {
            return substr($phone, 1, 2);
        }
        
        if ($geoIP) {
            $countryCodeMap = [
                'US' => '1', 'CA' => '1', 'GB' => '44', 'AU' => '61',
                'DE' => '49', 'FR' => '33', 'JP' => '81', 'IN' => '91'
            ];
            return $countryCodeMap[$geoIP] ?? '1';
        }
        
        return '1';
    }
    
    private function formatPhoneNumber(string $phone, string $countryCode): ?string
    {
        if ($countryCode === '1') {
            if (preg_match('/^\+?1?([0-9]{10})$/', $phone, $matches)) {
                $number = $matches[1];
                return '(' . substr($number, 0, 3) . ') ' . substr($number, 3, 3) . '-' . substr($number, 6);
            }
        }
        
        return null;
    }
    
    private function isCommonPassword(string $password): bool
    {
        $commonPasswords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', '123123'
        ];
        
        return in_array(strtolower($password), $commonPasswords);
    }
    
    private function isBreachedPassword(string $password): bool
    {
        $hash = sha1($password);
        $prefix = substr($hash, 0, 5);
        $suffix = substr($hash, 5);
        
        try {
            $response = Http::timeout(5)->get(\"https://api.pwnedpasswords.com/range/{$prefix}\");
            if ($response->successful()) {
                $hashes = $response->body();
                return str_contains(strtoupper($hashes), strtoupper($suffix));
            }
        } catch (\Exception $e) {
            Log::warning('Failed to check password breach status', ['error' => $e->getMessage()]);
        }
        
        return false;
    }
}
""")
        
        service_content = template.render()
        
        services_dir = self.backend_path / "app" / "Services"
        services_dir.mkdir(parents=True, exist_ok=True)
        
        service_file = services_dir / "SmartValidationService.php"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        return service_content
    
    def _generate_smart_security_services(self):
        """Generate smart security services for form protection"""
        
        template = Template(r"""<?php

namespace App\\Services;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;

class SmartSecurityService
{
    public function getDeviceFingerprint(Request $request): string
    {
        $components = [
            $request->userAgent(),
            $request->ip(),
            $request->header('Accept-Language')
        ];
        
        return hash('sha256', implode('|', array_filter($components)));
    }
    
    public function checkRateLimit(Request $request, string $action, int $maxAttempts = 5): array
    {
        $key = \"rate_limit:{$action}:\" . $request->ip();
        $attempts = Cache::get($key, 0);
        
        if ($attempts >= $maxAttempts) {
            return ['allowed' => false, 'attempts' => $attempts];
        }
        
        return ['allowed' => true, 'attempts' => $attempts];
    }
    
    public function generateHoneypot(): array
    {
        $fields = ['website_url', 'company_name'];
        $honeypotField = $fields[array_rand($fields)];
        $honeypotToken = bin2hex(random_bytes(16));
        
        Cache::put(\"honeypot:{$honeypotToken}\", $honeypotField, 3600);
        
        return ['field_name' => $honeypotField, 'token' => $honeypotToken];
    }
    
    public function validateHoneypot(array $formData): bool
    {
        foreach ($formData as $field => $value) {
            if (str_starts_with($field, 'honeypot_') && !empty($value)) {
                Log::warning('Honeypot triggered', ['field' => $field]);
                return false;
            }
        }
        return true;
    }
}
""")
        
        service_content = template.render()
        service_file = self.backend_path / "app" / "Services" / "SmartSecurityService.php"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        return service_content
    
    def _generate_smart_form_controller(self):
        """Generate smart form controller"""
        
        template = Template(r"""<?php

namespace App\\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use App\\Services\SmartValidationService;
use App\\Services\SmartSecurityService;

class SmartFormController
{
    private $validationService;
    private $securityService;
    
    public function __construct(
        SmartValidationService $validationService,
        SmartSecurityService $securityService
    ) {
        $this->validationService = $validationService;
        $this->securityService = $securityService;
    }
    
    public function validateField(Request $request): JsonResponse
    {
        $fieldType = $request->input('type');
        $fieldValue = $request->input('value');
        $fieldOptions = $request->input('options', []);
        
        $result = match($fieldType) {
            'email' => $this->validationService->validateEmail($fieldValue, $fieldOptions),
            'phone' => $this->validationService->validatePhone($fieldValue, $fieldOptions),
            'password' => $this->validationService->validatePasswordStrength($fieldValue),
            default => ['valid' => true, 'errors' => []]
        };
        
        return response()->json($result);
    }
    
    public function saveDraft(Request $request): JsonResponse
    {
        $formId = $request->input('form_id');
        $formData = $request->input('data', []);
        $userId = $request->user()?->id ?? session()->getId();
        
        cache()->put(\"form_draft:{$formId}:{$userId}\", $formData, 3600);
        
        return response()->json(['success' => true]);
    }
}
""")
        
        controller_content = template.render()
        controller_file = self.backend_path / "app" / "Controllers" / "SmartFormController.php"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
        
        return controller_content
    
    def _generate_field_validation_rules(self):
        """Generate custom validation rules"""
        
        template = Template(r"""<?php

namespace App\\Rules;

use Illuminate\Contracts\Validation\Rule;
use App\\Services\SmartValidationService;

class SmartEmailRule implements Rule
{
    private $validationService;
    
    public function __construct()
    {
        $this->validationService = app(SmartValidationService::class);
    }
    
    public function passes($attribute, $value)
    {
        $result = $this->validationService->validateEmail($value);
        return $result['valid'];
    }
    
    public function message()
    {
        return 'The :attribute is not a valid email address.';
    }
}
""")
        
        rules_content = template.render()
        
        rules_dir = self.backend_path / "app" / "Rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        rules_file = rules_dir / "SmartValidationRules.php"
        with open(rules_file, 'w') as f:
            f.write(rules_content)
        
        return rules_content
    
    def _generate_validation_middleware(self):
        """Generate validation middleware"""
        
        template = Template(r"""<?php

namespace App\\Middleware;

use Closure;
use Illuminate\Http\Request;
use App\\Services\SmartSecurityService;

class SmartFormValidationMiddleware
{
    private $securityService;
    
    public function __construct(SmartSecurityService $securityService)
    {
        $this->securityService = $securityService;
    }
    
    public function handle(Request $request, Closure $next)
    {
        if (!$this->securityService->validateHoneypot($request->all())) {
            return response()->json(['error' => 'Security validation failed'], 422);
        }
        
        return $next($request);
    }
}
""")
        
        middleware_content = template.render()
        
        middleware_dir = self.backend_path / "app" / "Middleware"
        middleware_dir.mkdir(parents=True, exist_ok=True)
        
        middleware_file = middleware_dir / "SmartFormValidationMiddleware.php"
        with open(middleware_file, 'w') as f:
            f.write(middleware_content)
        
        return middleware_content
    
    def _generate_payment_provider_manager(self):
        """Generate payment provider manager service"""
        
        template = Template(r"""<?php

namespace App\\Services;

use App\\Models\PaymentProvider;
use App\\Services\CustomPaymentProviderService;
use Illuminate\Support\Facades\Config;

class PaymentProviderManager
{
    private $customProviderService;
    private $builtInProviders = [
        'stripe' => '\\App\\Services\\StripePaymentService',
        'paypal' => '\\App\\Services\\PayPalPaymentService',
        'square' => '\\App\\Services\\SquarePaymentService',
        'razorpay' => '\\App\\Services\\RazorpayPaymentService'
    ];
    
    public function __construct(CustomPaymentProviderService $customProviderService)
    {
        $this->customProviderService = $customProviderService;
    }
    
    public function createPaymentIntent(
        string $provider,
        float $amount,
        string $currency,
        array $paymentMethodTypes = ['card'],
        string $description = '',
        array $metadata = []
    ): array {
        if ($this->isBuiltInProvider($provider)) {
            return $this->createBuiltInPaymentIntent(
                $provider,
                $amount,
                $currency,
                $paymentMethodTypes,
                $description,
                $metadata
            );
        } else {
            return $this->customProviderService->createPaymentIntent(
                $provider,
                $amount,
                $currency,
                $paymentMethodTypes,
                $description,
                $metadata
            );
        }
    }
    
    public function confirmPayment(string $provider, string $providerPaymentId): array
    {
        if ($this->isBuiltInProvider($provider)) {
            $service = new $this->builtInProviders[$provider]();
            return $service->confirmPayment($providerPaymentId);
        } else {
            return $this->customProviderService->confirmPayment($provider, $providerPaymentId);
        }
    }
    
    public function refundPayment(
        string $provider,
        string $providerPaymentId,
        float $amount,
        string $reason = ''
    ): array {
        if ($this->isBuiltInProvider($provider)) {
            $service = new $this->builtInProviders[$provider]();
            return $service->refundPayment($providerPaymentId, $amount, $reason);
        } else {
            return $this->customProviderService->refundPayment(
                $provider,
                $providerPaymentId,
                $amount,
                $reason
            );
        }
    }
    
    public function handleWebhook(string $provider, array $payload, array $headers): array
    {
        if ($this->isBuiltInProvider($provider)) {
            $service = new $this->builtInProviders[$provider]();
            return $service->handleWebhook($payload, $headers);
        } else {
            return $this->customProviderService->handleWebhook($provider, $payload, $headers);
        }
    }
    
    public function getAvailableProviders(): array
    {
        $providers = [];
        
        // Add built-in providers that are configured
        foreach ($this->builtInProviders as $name => $class) {
            if ($this->isProviderConfigured($name)) {
                $providers[] = [
                    'name' => $name,
                    'type' => 'built_in',
                    'display_name' => ucfirst($name)
                ];
            }
        }
        
        // Add custom providers
        $customProviders = PaymentProvider::where('is_active', true)->get();
        foreach ($customProviders as $provider) {
            $config = json_decode($provider->configuration, true);
            $providers[] = [
                'name' => $provider->name,
                'type' => 'custom',
                'display_name' => $config['name'] ?? $provider->name
            ];
        }
        
        return $providers;
    }
    
    public function isProviderAvailable(string $provider): bool
    {
        if ($this->isBuiltInProvider($provider)) {
            return $this->isProviderConfigured($provider);
        }
        
        return PaymentProvider::where('name', $provider)
                            ->where('is_active', true)
                            ->exists();
    }
    
    private function isBuiltInProvider(string $provider): bool
    {
        return array_key_exists($provider, $this->builtInProviders);
    }
    
    private function isProviderConfigured(string $provider): bool
    {
        $config = Config::get(\"payments.providers.{$provider}\");
        return !empty($config);
    }
    
    private function createBuiltInPaymentIntent(
        string $provider,
        float $amount,
        string $currency,
        array $paymentMethodTypes,
        string $description,
        array $metadata
    ): array {
        $service = new $this->builtInProviders[$provider]();
        
        return $service->createPaymentIntent([
            'amount' => $amount,
            'currency' => $currency,
            'payment_method_types' => $paymentMethodTypes,
            'description' => $description,
            'metadata' => $metadata
        ]);
    }
}
""")
        
        service_content = template.render()
        
        services_dir = self.backend_path / "app" / "Services"
        services_dir.mkdir(parents=True, exist_ok=True)
        
        service_file = services_dir / "PaymentProviderManager.php"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        return service_content
    
    def _generate_custom_payment_provider_service(self):
        """Generate custom payment provider service"""
        
        # Create the custom payment provider service file directly
        template = Template(r"""<?php

namespace App\\Services;

use App\\Models\PaymentProvider;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class CustomPaymentProviderService
{
    public function createPaymentIntent(
        string $providerName,
        float $amount,
        string $currency,
        array $paymentMethodTypes = ['card'],
        string $description = '',
        array $metadata = []
    ): array {
        $provider = $this->getProviderConfig($providerName);
        $config = json_decode($provider->configuration, true);
        
        $endpoint = $config['api_config']['endpoints']['create_payment'];
        $requestData = $this->buildRequestData($config, [
            'amount' => $amount,
            'currency' => $currency,
            'payment_method_types' => $paymentMethodTypes,
            'description' => $description,
            'metadata' => $metadata
        ]);
        
        $response = $this->makeApiCall($config, 'POST', $endpoint, $requestData);
        return $this->parseResponse($config, $response, 'create_payment');
    }
    
    public function confirmPayment(string $providerName, string $providerPaymentId): array
    {
        $provider = $this->getProviderConfig($providerName);
        $config = json_decode($provider->configuration, true);
        
        $endpoint = str_replace('{payment_id}', $providerPaymentId, 
                              $config['api_config']['endpoints']['confirm_payment']);
        
        $response = $this->makeApiCall($config, 'POST', $endpoint, []);
        return $this->parseResponse($config, $response, 'confirm_payment');
    }
    
    public function refundPayment(
        string $providerName,
        string $providerPaymentId,
        float $amount,
        string $reason = ''
    ): array {
        $provider = $this->getProviderConfig($providerName);
        $config = json_decode($provider->configuration, true);
        
        $endpoint = str_replace('{payment_id}', $providerPaymentId,
                              $config['api_config']['endpoints']['refund_payment']);
        
        $requestData = $this->buildRequestData($config, ['amount' => $amount, 'reason' => $reason]);
        $response = $this->makeApiCall($config, 'POST', $endpoint, $requestData);
        return $this->parseResponse($config, $response, 'refund_payment');
    }
    
    public function handleWebhook(string $providerName, array $payload, array $headers): array
    {
        $provider = $this->getProviderConfig($providerName);
        $config = json_decode($provider->configuration, true);
        
        if (isset($config['webhook_secret'])) {
            $this->verifyWebhookSignature($config, $payload, $headers);
        }
        
        Log::info(\"Custom provider webhook received\", ['provider' => $providerName, 'payload' => $payload]);
        return ['status' => 'processed'];
    }
    
    private function getProviderConfig(string $providerName): PaymentProvider
    {
        $provider = PaymentProvider::where('name', $providerName)->where('is_active', true)->first();
        if (!$provider) {
            throw new \Exception(\"Payment provider '{$providerName}' not found or inactive\");
        }
        return $provider;
    }
    
    private function buildRequestData(array $config, array $data): array
    {
        $fieldMappings = $config['api_config']['field_mappings'] ?? [];
        $requestData = [];
        foreach ($data as $key => $value) {
            $mappedKey = $fieldMappings[$key] ?? $key;
            $requestData[$mappedKey] = $value;
        }
        return $requestData;
    }
    
    private function makeApiCall(array $config, string $method, string $endpoint, array $data): array
    {
        $baseUrl = $config['api_base_url'];
        $url = $baseUrl . $endpoint;
        $headers = ['Content-Type' => 'application/json', 'Accept' => 'application/json'];
        
        if (isset($config['api_config']['custom_headers'])) {
            $headers = array_merge($headers, $config['api_config']['custom_headers']);
        }
        
        $httpClient = Http::withHeaders($headers);
        
        $auth = $config['api_config']['authentication'];
        if ($auth['type'] === 'bearer_token') {
            $httpClient = $httpClient->withToken($config['api_key']);
        } elseif ($auth['type'] === 'api_key') {
            $headerName = $auth['header_name'] ?? 'X-API-Key';
            $httpClient = $httpClient->withHeaders([$headerName => $config['api_key']]);
        }
        
        $response = match(strtoupper($method)) {
            'GET' => $httpClient->get($url, $data),
            'POST' => $httpClient->post($url, $data),
            'PUT' => $httpClient->put($url, $data),
            'DELETE' => $httpClient->delete($url, $data),
            default => throw new \Exception(\"Unsupported HTTP method: {$method}\")
        };
        
        if (!$response->successful()) {
            throw new \Exception(\"API call failed: {$response->status()} - {$response->body()}\");
        }
        
        return $response->json();
    }
    
    private function parseResponse(array $config, array $response, string $operation): array
    {
        $responseMappings = $config['api_config']['response_mappings'] ?? [];
        $parsed = [];
        
        foreach ($response as $key => $value) {
            $mappedKey = array_search($key, $responseMappings) ?: $key;
            $parsed[$mappedKey] = $value;
        }
        
        if (!isset($parsed['status'])) {
            $parsed['status'] = $operation === 'create_payment' ? 'pending' : 'completed';
        }
        
        return $parsed;
    }
    
    private function verifyWebhookSignature(array $config, array $payload, array $headers): void
    {
        $webhookSecret = $config['webhook_secret'];
        $signature = $headers['x-webhook-signature'][0] ?? $headers['x-signature'][0] ?? null;
        
        if (!$signature) {
            throw new \Exception('Webhook signature missing');
        }
        
        $computedSignature = hash_hmac('sha256', json_encode($payload), $webhookSecret);
        
        if (!hash_equals($computedSignature, $signature)) {
            throw new \Exception('Webhook signature verification failed');
        }
    }
}
""")
        
        service_content = template.render()
        service_file = self.backend_path / "app" / "Services" / "CustomPaymentProviderService.php"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        return service_content
    
    def _generate_payment_gateway_routes(self):
        """Generate payment gateway routes"""
        
        template = Template(r"""<?php

use Illuminate\Support\Facades\Route;
use App\\Controllers\PaymentController;

Route::middleware(['auth'])->group(function () {
    Route::post('/payments/intent', [PaymentController::class, 'createPaymentIntent']);
    Route::post('/payments/confirm', [PaymentController::class, 'confirmPayment']);
    Route::post('/payments/{paymentId}/refund', [PaymentController::class, 'refundPayment']);
    Route::get('/payments/providers', [PaymentController::class, 'getAvailableProviders']);
});

Route::post('/webhooks/{provider}', [PaymentController::class, 'handleWebhook']);

Route::get('/payments/{paymentId}/status', function($paymentId) {
    $payment = \App\Models\Payment::findOrFail($paymentId);
    return response()->json([
        'payment_id' => $payment->id,
        'status' => $payment->status,
        'amount' => $payment->amount,
        'currency' => $payment->currency,
        'provider' => $payment->provider
    ]);
});
""")
        
        routes_content = template.render()
        routes_file = self.backend_path / "routes" / "payments.php"
        with open(routes_file, 'w') as f:
            f.write(routes_content)
        
        return routes_content
    
    def _generate_payment_gateway_config(self):
        """Generate payment gateway configuration"""
        
        template = Template(r"""<?php

return [
    'default_provider' => env('PAYMENT_DEFAULT_PROVIDER', 'stripe'),
    
    'providers' => [
        'stripe' => [
            'public_key' => env('STRIPE_PUBLIC_KEY'),
            'secret_key' => env('STRIPE_SECRET_KEY'),
            'webhook_secret' => env('STRIPE_WEBHOOK_SECRET'),
            'supported_methods' => ['card', 'apple_pay', 'google_pay'],
            'currencies' => ['USD', 'EUR', 'GBP'],
        ],
        'paypal' => [
            'client_id' => env('PAYPAL_CLIENT_ID'),
            'client_secret' => env('PAYPAL_CLIENT_SECRET'),
            'environment' => env('PAYPAL_ENVIRONMENT', 'sandbox'),
            'supported_methods' => ['paypal', 'credit_card'],
            'currencies' => ['USD', 'EUR', 'GBP'],
        ],
    ],
    
    'settings' => [
        'auto_capture' => env('PAYMENT_AUTO_CAPTURE', true),
        'fallback_provider' => env('PAYMENT_FALLBACK_PROVIDER', 'stripe'),
        'webhook_retry_attempts' => env('PAYMENT_WEBHOOK_RETRY_ATTEMPTS', 3)
    ],
    
    'custom_providers' => [
        'load_from_database' => true,
        'cache_duration' => env('PAYMENT_PROVIDER_CACHE_DURATION', 3600),
    ],
];
""")
        
        config_content = template.render()
        config_file = self.backend_path / "config" / "payments.php"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        return config_content
    
    def _generate_payment_services(self):
        """Generate payment service classes"""
        
        # Generate Stripe service
        stripe_template = Template(r"""<?php

namespace App\\Services;

use Stripe\Stripe;
use Stripe\PaymentIntent;
use Stripe\Refund;
use Stripe\Webhook;

class StripePaymentService
{
    public function __construct()
    {
        Stripe::setApiKey(env('STRIPE_SECRET_KEY'));
    }
    
    public function createPaymentIntent(array $data): array
    {
        $intent = PaymentIntent::create([
            'amount' => $data['amount'] * 100, // Convert to cents
            'currency' => $data['currency'],
            'payment_method_types' => $data['payment_method_types'],
            'description' => $data['description'],
            'metadata' => $data['metadata']
        ]);
        
        return [
            'client_secret' => $intent->client_secret,
            'payment_id' => $intent->id,
            'order_id' => uniqid('order_')
        ];
    }
    
    public function confirmPayment(string $paymentId): array
    {
        $intent = PaymentIntent::retrieve($paymentId);
        
        return [
            'status' => $intent->status === 'succeeded' ? 'completed' : 'failed',
            'fees' => ($intent->charges->data[0]->balance_transaction->fee ?? 0) / 100
        ];
    }
    
    public function processRefund(array $data): array
    {
        $refund = Refund::create([
            'payment_intent' => $data['payment_id'],
            'amount' => $data['amount'] * 100,
            'reason' => 'requested_by_customer',
            'metadata' => ['reason' => $data['reason']]
        ]);
        
        return [
            'refund_id' => $refund->id,
            'status' => $refund->status
        ];
    }
    
    public function handleWebhook(array $payload, array $headers): array
    {
        $sig = $headers['stripe-signature'] ?? '';
        $event = Webhook::constructEvent(
            json_encode($payload),
            $sig,
            env('STRIPE_WEBHOOK_SECRET')
        );
        
        switch ($event->type) {
            case 'payment_intent.succeeded':
                return ['payment_id' => $event->data->object->id, 'status' => 'completed'];
            case 'payment_intent.payment_failed':
                return ['payment_id' => $event->data->object->id, 'status' => 'failed'];
            default:
                return ['status' => 'ignored'];
        }
    }
}
""")
        
        stripe_content = stripe_template.render()
        stripe_file = self.backend_path / "app" / "Services" / "StripePaymentService.php"
        with open(stripe_file, 'w') as f:
            f.write(stripe_content)
        
        # Generate PayPal service
        paypal_template = Template(r"""<?php

namespace App\\Services;

use Illuminate\Support\Facades\Http;

class PayPalPaymentService
{
    private $baseUrl;
    private $clientId;
    private $clientSecret;
    
    public function __construct()
    {
        $this->baseUrl = env('PAYPAL_ENVIRONMENT') === 'live' 
            ? 'https://api.paypal.com' 
            : 'https://api.sandbox.paypal.com';
        $this->clientId = env('PAYPAL_CLIENT_ID');
        $this->clientSecret = env('PAYPAL_CLIENT_SECRET');
    }
    
    public function createPaymentIntent(array $data): array
    {
        $accessToken = $this->getAccessToken();
        
        $response = Http::withHeaders([
            'Authorization' => 'Bearer ' . $accessToken,
            'Content-Type' => 'application/json'
        ])->post($this->baseUrl . '/v2/checkout/orders', [
            'intent' => 'CAPTURE',
            'purchase_units' => [[
                'amount' => [
                    'currency_code' => $data['currency'],
                    'value' => number_format($data['amount'], 2, '.', '')
                ],
                'description' => $data['description']
            ]]
        ]);
        
        $order = $response->json();
        
        return [
            'client_secret' => $order['id'],
            'payment_id' => $order['id'],
            'order_id' => uniqid('paypal_')
        ];
    }
    
    public function confirmPayment(string $paymentId): array
    {
        $accessToken = $this->getAccessToken();
        
        $response = Http::withHeaders([
            'Authorization' => 'Bearer ' . $accessToken
        ])->post($this->baseUrl . '/v2/checkout/orders/' . $paymentId . '/capture');
        
        $capture = $response->json();
        
        return [
            'status' => $capture['status'] === 'COMPLETED' ? 'completed' : 'failed',
            'fees' => 0 // PayPal fees are deducted automatically
        ];
    }
    
    public function processRefund(array $data): array
    {
        $accessToken = $this->getAccessToken();
        
        $response = Http::withHeaders([
            'Authorization' => 'Bearer ' . $accessToken,
            'Content-Type' => 'application/json'
        ])->post($this->baseUrl . '/v2/payments/captures/' . $data['payment_id'] . '/refund', [
            'amount' => [
                'value' => number_format($data['amount'], 2, '.', ''),
                'currency_code' => 'USD'
            ],
            'note_to_payer' => $data['reason']
        ]);
        
        $refund = $response->json();
        
        return [
            'refund_id' => $refund['id'],
            'status' => $refund['status']
        ];
    }
    
    private function getAccessToken(): string
    {
        $response = Http::withBasicAuth($this->clientId, $this->clientSecret)
            ->withHeaders(['Content-Type' => 'application/x-www-form-urlencoded'])
            ->post($this->baseUrl . '/v1/oauth2/token', [
                'grant_type' => 'client_credentials'
            ]);
        
        return $response->json()['access_token'];
    }
    
    public function handleWebhook(array $payload, array $headers): array
    {
        // PayPal webhook verification would go here
        return ['status' => 'processed'];
    }
}
""")
        
        paypal_content = paypal_template.render()
        paypal_file = self.backend_path / "app" / "Services" / "PayPalPaymentService.php"
        with open(paypal_file, 'w') as f:
            f.write(paypal_content)
    
    def _generate_payment_routes(self):
        """Generate payment gateway routes"""
        
        template = Template(r"""<?php

// Payment Gateway Routes
use App\\Controllers\PaymentController;

// Payment intent creation
Route::post('/payments/intent', [PaymentController::class, 'createPaymentIntent'])
    ->middleware('auth');

// Payment confirmation
Route::post('/payments/confirm', [PaymentController::class, 'confirmPayment'])
    ->middleware('auth');

// Refund processing
Route::post('/payments/refund', [PaymentController::class, 'processRefund'])
    ->middleware('auth');

// Payment methods management
Route::get('/payments/methods', [PaymentController::class, 'getPaymentMethods'])
    ->middleware('auth');

Route::post('/payments/methods', [PaymentController::class, 'savePaymentMethod'])
    ->middleware('auth');

Route::delete('/payments/methods/{methodId}', [PaymentController::class, 'deletePaymentMethod'])
    ->middleware('auth');

// Webhook endpoints
Route::post('/webhooks/stripe', [PaymentController::class, 'handleWebhook'])
    ->defaults('provider', 'stripe');

Route::post('/webhooks/paypal', [PaymentController::class, 'handleWebhook'])
    ->defaults('provider', 'paypal');

Route::post('/webhooks/square', [PaymentController::class, 'handleWebhook'])
    ->defaults('provider', 'square');

Route::post('/webhooks/razorpay', [PaymentController::class, 'handleWebhook'])
    ->defaults('provider', 'razorpay');

// Payment status check
Route::get('/payments/{paymentId}/status', function($paymentId) {
    $payment = \App\Models\Payment::findOrFail($paymentId);
    return response()->json([
        'payment_id' => $payment->id,
        'status' => $payment->status,
        'amount' => $payment->amount,
        'currency' => $payment->currency,
        'provider' => $payment->provider
    ]);
})->middleware('auth');
""")
        
        routes_content = template.render()
        
        routes_file = self.backend_path / "routes" / "payments.php"
        with open(routes_file, 'w') as f:
            f.write(routes_content)
        
        return routes_content
    
    def _generate_payment_config(self):
        """Generate payment gateway configuration"""
        
        template = Template(r"""<?php

return [
    'default_provider' => env('PAYMENT_DEFAULT_PROVIDER', 'stripe'),
    'default_currency' => env('PAYMENT_DEFAULT_CURRENCY', 'USD'),
    
    'providers' => [
        'stripe' => [
            'public_key' => env('STRIPE_PUBLIC_KEY'),
            'secret_key' => env('STRIPE_SECRET_KEY'),
            'webhook_secret' => env('STRIPE_WEBHOOK_SECRET'),
            'supported_methods' => ['card', 'apple_pay', 'google_pay', 'bank_transfer'],
            'currencies' => ['USD', 'EUR', 'GBP', 'CAD'],
        ],
        
        'paypal' => [
            'client_id' => env('PAYPAL_CLIENT_ID'),
            'client_secret' => env('PAYPAL_CLIENT_SECRET'),
            'environment' => env('PAYPAL_ENVIRONMENT', 'sandbox'),
            'supported_methods' => ['paypal', 'credit_card'],
            'currencies' => ['USD', 'EUR', 'GBP'],
        ],
        
        'square' => [
            'application_id' => env('SQUARE_APPLICATION_ID'),
            'access_token' => env('SQUARE_ACCESS_TOKEN'),
            'environment' => env('SQUARE_ENVIRONMENT', 'sandbox'),
            'supported_methods' => ['card', 'cash', 'gift_card'],
            'currencies' => ['USD', 'CAD'],
        ],
        
        'razorpay' => [
            'key_id' => env('RAZORPAY_KEY_ID'),
            'key_secret' => env('RAZORPAY_KEY_SECRET'),
            'webhook_secret' => env('RAZORPAY_WEBHOOK_SECRET'),
            'supported_methods' => ['card', 'upi', 'netbanking', 'wallet'],
            'currencies' => ['INR', 'USD'],
        ],
    ],
    
    'settings' => [
        'auto_capture' => env('PAYMENT_AUTO_CAPTURE', true),
        'save_payment_methods' => env('PAYMENT_SAVE_METHODS', true),
        'send_receipts' => env('PAYMENT_SEND_RECEIPTS', true),
        'fraud_detection' => env('PAYMENT_FRAUD_DETECTION', true),
        'tax_calculation' => env('PAYMENT_TAX_CALCULATION', 'automatic'),
        'subscription_billing' => env('PAYMENT_SUBSCRIPTION_BILLING', true),
        'refund_policy_days' => env('PAYMENT_REFUND_POLICY_DAYS', 30),
    ],
];
""")
        
        config_content = template.render()
        
        config_file = self.backend_path / "config" / "payments.php"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        return config_content
    
    def _generate_admin_panel(self):
        """Generate admin panel controllers and services"""
        
        # Generate admin controllers
        self._generate_admin_controllers()
        
        # Generate admin middleware
        self._generate_admin_middleware()
        
        # Generate admin configuration
        self._generate_admin_config()
        
        # Generate admin routes
        self._generate_admin_routes()
    
    def _generate_admin_controllers(self):
        """Generate admin panel controllers"""
        
        # Generate main admin dashboard controller
        self._generate_admin_dashboard_controller()
        
        # Generate admin user controller
        self._generate_admin_user_controller()
    
    def _generate_admin_dashboard_controller(self):
        """Generate admin dashboard controller"""
        
        template = Template(r"""<?php

namespace App\\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Cache;
use App\\Models\User;
use App\\Models\AdminAuditLog;

class AdminDashboardController
{
    public function getDashboardData(Request $request): JsonResponse
    {
        try {
            $timeRange = $request->get('time_range', '30d');
            $refreshCache = $request->get('refresh', false);
            
            $cacheKey = 'admin_dashboard_' . $timeRange;
            
            if (!$refreshCache && Cache::has($cacheKey)) {
                return response()->json(Cache::get($cacheKey));
            }
            
            $dashboardData = [
                'stats' => $this->getStatsCards($timeRange),
                'charts' => $this->getChartData($timeRange),
                'recent_activity' => $this->getRecentActivity(),
                'alerts' => $this->getSystemAlerts()
            ];
            
            // Cache for 5 minutes
            Cache::put($cacheKey, $dashboardData, 300);
            
            return response()->json($dashboardData);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to load dashboard data',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    private function getStatsCards(string $timeRange): array
    {
        $dateFilter = $this->getDateFilter($timeRange);
        
        return [
            'users' => User::where('created_at', '>=', $dateFilter)->count(),
            'revenue' => 0, // Placeholder
            'orders' => 0, // Placeholder
            'sessions' => 0 // Placeholder
        ];
    }
    
    private function getChartData(string $timeRange): array
    {
        return [
            'daily_active_users' => [],
            'user_demographics' => [],
            'revenue_chart' => []
        ];
    }
    
    private function getRecentActivity(int $limit = 10): array
    {
        return AdminAuditLog::orderBy('created_at', 'desc')
                          ->limit($limit)
                          ->get()
                          ->toArray();
    }
    
    private function getSystemAlerts(): array
    {
        return [];
    }
    
    private function getDateFilter(string $timeRange): string
    {
        switch ($timeRange) {
            case 'today':
                return now()->startOfDay();
            case 'week':
                return now()->startOfWeek();
            case 'month':
                return now()->startOfMonth();
            default:
                return now()->subDays(30);
        }
    }
}
""")
        
        controller_content = template.render()
        
        controller_file = self.backend_path / "app" / "Controllers" / "AdminDashboardController.php"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
        
        return controller_content
    
    def _generate_admin_user_controller(self):
        """Generate admin user management controller"""
        
        template = Template(r"""<?php

namespace App\\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;
use App\\Models\AdminUser;
use App\\Models\AdminAuditLog;

class AdminUserController
{
    public function index(Request $request): JsonResponse
    {
        try {
            $query = AdminUser::query();
            
            // Apply filters
            if ($request->has('search')) {
                $search = $request->get('search');
                $query->where(function($q) use ($search) {
                    $q->where('username', 'LIKE', '%' . $search . '%')
                      ->orWhere('email', 'LIKE', '%' . $search . '%')
                      ->orWhere('first_name', 'LIKE', '%' . $search . '%')
                      ->orWhere('last_name', 'LIKE', '%' . $search . '%');
                });
            }
            
            if ($request->has('role')) {
                $query->where('role', $request->get('role'));
            }
            
            // Sorting
            $sortBy = $request->get('sort_by', 'created_at');
            $sortDirection = $request->get('sort_direction', 'desc');
            $query->orderBy($sortBy, $sortDirection);
            
            // Pagination
            $users = $query->paginate($request->get('per_page', 20));
            
            return response()->json($users);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to retrieve users',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    public function show(Request $request, $id): JsonResponse
    {
        try {
            $user = AdminUser::findOrFail($id);
            
            return response()->json(['user' => $user]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'User not found',
                'message' => $e->getMessage()
            ], 404);
        }
    }
    
    public function store(Request $request): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'username' => 'required|string|unique:admin_users|max:255',
                'email' => 'required|email|unique:admin_users|max:255',
                'password' => 'required|string|min:8',
                'first_name' => 'required|string|max:255',
                'last_name' => 'required|string|max:255',
                'role' => 'required|string|in:super_admin,admin,editor,viewer',
                'permissions' => 'array',
                'is_active' => 'boolean'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $validated = $validator->validated();
            $validated['password'] = Hash::make($validated['password']);
            $validated['permissions'] = json_encode($validated['permissions'] ?? []);
            
            $user = AdminUser::create($validated);
            
            // Log the action
            $this->logAction('create', 'AdminUser', $user->id, null, $user->toArray(), $request);
            
            return response()->json([
                'user' => $user,
                'message' => 'Admin user created successfully'
            ], 201);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to create user',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    private function logAction(string $action, string $resourceType, $resourceId, $oldValues, $newValues, Request $request)
    {
        AdminAuditLog::create([
            'admin_user_id' => $request->user()->id ?? 1,
            'action' => $action,
            'resource_type' => $resourceType,
            'resource_id' => $resourceId,
            'old_values' => $oldValues ? json_encode($oldValues) : null,
            'new_values' => $newValues ? json_encode($newValues) : null,
            'ip_address' => $request->ip(),
            'user_agent' => $request->userAgent()
        ]);
    }
}
""")
        
        controller_content = template.render()
        
        controller_file = self.backend_path / "app" / "Controllers" / "AdminUserController.php"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
        
        return controller_content
    
    def _generate_admin_middleware(self):
        """Generate admin authentication middleware"""
        
        template = Template(r"""<?php

namespace App\\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class AdminAuthMiddleware
{
    public function handle(Request $request, Closure $next, ...$guards)
    {
        // Check if user is authenticated
        if (!Auth::guard('admin')->check()) {
            return response()->json(['error' => 'Unauthorized'], 401);
        }
        
        $user = Auth::guard('admin')->user();
        
        // Check if user is active
        if (!$user->is_active) {
            return response()->json(['error' => 'Account disabled'], 403);
        }
        
        // Check if user is locked
        if ($user->locked_until && $user->locked_until > now()) {
            return response()->json(['error' => 'Account locked'], 403);
        }
        
        return $next($request);
    }
}
""")
        
        middleware_content = template.render()
        
        middleware_file = self.backend_path / "app" / "Middleware" / "AdminAuthMiddleware.php"
        with open(middleware_file, 'w') as f:
            f.write(middleware_content)
        
        return middleware_content
    
    def _generate_admin_config(self):
        """Generate admin configuration"""
        
        template = Template(r"""<?php

return [
    'theme' => [
        'primary_color' => env('ADMIN_PRIMARY_COLOR', '#2563eb'),
        'secondary_color' => env('ADMIN_SECONDARY_COLOR', '#64748b'),
        'dark_mode' => env('ADMIN_DARK_MODE', true),
        'custom_branding' => env('ADMIN_CUSTOM_BRANDING', true),
        'logo_url' => env('ADMIN_LOGO_URL', '/assets/admin-logo.png'),
    ],
    
    'authentication' => [
        'multi_factor' => env('ADMIN_MFA', true),
        'session_timeout' => env('ADMIN_SESSION_TIMEOUT', 30),
        'password_policy' => [
            'min_length' => 8,
            'require_uppercase' => true,
            'require_numbers' => true,
            'require_symbols' => true,
        ],
        'login_attempts' => [
            'max_attempts' => env('ADMIN_MAX_LOGIN_ATTEMPTS', 5),
            'lockout_duration' => env('ADMIN_LOCKOUT_DURATION', 15),
        ],
    ],
    
    'permissions' => [
        'roles' => [
            'super_admin' => [
                'display_name' => 'Super Administrator',
                'permissions' => ['*']
            ],
            'admin' => [
                'display_name' => 'Administrator',
                'permissions' => [
                    'user.read', 'user.create', 'user.update', 'user.delete',
                    'content.read', 'content.create', 'content.update', 'content.delete',
                    'admin.settings', 'admin.analytics'
                ]
            ],
            'editor' => [
                'display_name' => 'Content Editor',
                'permissions' => [
                    'content.read', 'content.create', 'content.update',
                    'user.read'
                ]
            ],
            'viewer' => [
                'display_name' => 'Read Only',
                'permissions' => ['user.read', 'content.read']
            ]
        ]
    ],
    
    'features' => [
        'user_management' => [
            'bulk_actions' => true,
            'advanced_filters' => true,
            'export_formats' => ['csv', 'xlsx', 'pdf'],
            'user_impersonation' => true,
            'activity_logs' => true,
        ],
        
        'analytics' => [
            'real_time_stats' => true,
            'custom_reports' => true,
            'data_export' => true,
        ],
        
        'system_monitoring' => [
            'server_health' => true,
            'error_tracking' => true,
            'performance_metrics' => true,
            'audit_logs' => true,
        ],
    ],
];
""")
        
        config_content = template.render()
        
        config_file = self.backend_path / "config" / "admin.php"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        return config_content
    
    def _generate_admin_routes(self):
        """Generate admin panel routes"""
        
        template = Template(r"""<?php

// Admin Panel Routes
use App\\Controllers\AdminDashboardController;
use App\\Controllers\AdminUserController;

// Admin authentication required
Route::middleware(['auth:admin'])->prefix('admin')->group(function () {
    
    // Dashboard
    Route::get('/dashboard', [AdminDashboardController::class, 'getDashboardData']);
    
    // User management
    Route::get('/users', [AdminUserController::class, 'index']);
    Route::get('/users/{id}', [AdminUserController::class, 'show']);
    Route::post('/users', [AdminUserController::class, 'store']);
    Route::put('/users/{id}', [AdminUserController::class, 'update']);
    Route::delete('/users/{id}', [AdminUserController::class, 'destroy']);
    Route::post('/users/bulk', [AdminUserController::class, 'bulkAction']);
    
    // System health
    Route::get('/system/health', function() {
        return response()->json([
            'status' => 'healthy',
            'timestamp' => now(),
            'uptime' => sys_getloadavg()[0] ?? 0,
            'memory_usage' => memory_get_usage(true),
            'disk_usage' => disk_free_space('/') / disk_total_space('/') * 100
        ]);
    });
    
});
""")
        
        routes_content = template.render()
        
        routes_file = self.backend_path / "routes" / "admin.php"
        with open(routes_file, 'w') as f:
            f.write(routes_content)
        
        return routes_content
    
    def _generate_payment_gateway(self):
        """Generate payment gateway functionality with custom provider support"""
        
        # Generate enhanced payment controller
        self._generate_enhanced_payment_controller()
        
        # Generate payment provider manager service
        self._generate_payment_provider_manager()
        
        # Generate custom payment provider service
        self._generate_custom_payment_provider_service()
        
        # Generate payment gateway routes
        self._generate_payment_gateway_routes()
        
        # Generate payment gateway configuration
        self._generate_payment_gateway_config()
    
    def _generate_enhanced_payment_controller(self):
        """Generate enhanced payment controller with custom provider support"""
        
        template = Template(r"""<?php

namespace App\\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Validator;
use App\\Models\Payment;
use App\\Models\PaymentProvider;
use App\\Services\PaymentProviderManager;
use App\\Services\CustomPaymentProviderService;

class PaymentController
{
    private $providerManager;
    private $customProviderService;
    
    public function __construct(
        PaymentProviderManager $providerManager,
        CustomPaymentProviderService $customProviderService
    ) {
        $this->providerManager = $providerManager;
        $this->customProviderService = $customProviderService;
    }
    
    public function createPaymentIntent(Request $request): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'amount' => 'required|numeric|min:0.01',
                'currency' => 'required|string|size:3',
                'provider' => 'required|string',
                'payment_method_types' => 'array',
                'description' => 'string|max:500',
                'metadata' => 'array'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $validated = $validator->validated();
            
            // Check if provider is available
            if (!$this->providerManager->isProviderAvailable($validated['provider'])) {
                return response()->json([
                    'error' => 'Payment provider not available',
                    'provider' => $validated['provider']
                ], 400);
            }
            
            // Create payment intent with provider
            $intent = $this->providerManager->createPaymentIntent(
                $validated['provider'],
                $validated['amount'],
                $validated['currency'],
                $validated['payment_method_types'] ?? ['card'],
                $validated['description'] ?? '',
                $validated['metadata'] ?? []
            );
            
            // Save payment record
            $payment = Payment::create([
                'user_id' => $request->user()->id,
                'order_id' => 'order_' . uniqid(),
                'provider' => $validated['provider'],
                'provider_payment_id' => $intent['payment_id'],
                'amount' => $validated['amount'],
                'currency' => $validated['currency'],
                'status' => 'pending',
                'description' => $validated['description'] ?? '',
                'metadata' => $validated['metadata'] ?? [],
                'provider_response' => $intent
            ]);
            
            return response()->json([
                'payment_id' => $payment->id,
                'provider_payment_id' => $intent['payment_id'],
                'client_secret' => $intent['client_secret'] ?? null,
                'redirect_url' => $intent['redirect_url'] ?? null,
                'status' => 'pending'
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to create payment intent',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    public function confirmPayment(Request $request): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'payment_id' => 'required|string'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $validated = $validator->validated();
            $payment = Payment::findOrFail($validated['payment_id']);
            
            // Verify payment with provider
            $result = $this->providerManager->confirmPayment(
                $payment->provider,
                $payment->provider_payment_id
            );
            
            // Update payment status
            $payment->update([
                'status' => $result['status'],
                'provider_response' => array_merge(
                    $payment->provider_response ?? [],
                    $result
                )
            ]);
            
            return response()->json([
                'payment_id' => $payment->id,
                'status' => $result['status'],
                'provider_response' => $result
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Payment confirmation failed',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    public function handleWebhook(Request $request): JsonResponse
    {
        try {
            $provider = $request->route('provider');
            $payload = $request->all();
            $headers = $request->headers->all();
            
            $result = $this->providerManager->handleWebhook(
                $provider,
                $payload,
                $headers
            );
            
            return response()->json([
                'status' => 'processed',
                'result' => $result
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Webhook processing failed',
                'message' => $e->getMessage()
            ], 400);
        }
    }
    
    public function getAvailableProviders(Request $request): JsonResponse
    {
        try {
            $providers = $this->providerManager->getAvailableProviders();
            
            return response()->json([
                'providers' => $providers
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to get providers',
                'message' => $e->getMessage()
            ], 500);
        }
    }
    
    public function refundPayment(Request $request, $paymentId): JsonResponse
    {
        try {
            $validator = Validator::make($request->all(), [
                'amount' => 'numeric|min:0.01',
                'reason' => 'string|max:500'
            ]);
            
            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Validation failed',
                    'messages' => $validator->errors()
                ], 400);
            }
            
            $validated = $validator->validated();
            $payment = Payment::findOrFail($paymentId);
            
            // Check if payment can be refunded
            if ($payment->status !== 'completed') {
                return response()->json([
                    'error' => 'Payment cannot be refunded',
                    'status' => $payment->status
                ], 400);
            }
            
            $refundAmount = $validated['amount'] ?? $payment->amount;
            
            $result = $this->providerManager->refundPayment(
                $payment->provider,
                $payment->provider_payment_id,
                $refundAmount,
                $validated['reason'] ?? 'Customer request'
            );
            
            // Update payment record
            $payment->update([
                'status' => $result['status'],
                'refund_amount' => $refundAmount,
                'provider_response' => array_merge(
                    $payment->provider_response ?? [],
                    $result
                )
            ]);
            
            return response()->json([
                'payment_id' => $payment->id,
                'refund_amount' => $refundAmount,
                'status' => $result['status'],
                'refund_id' => $result['refund_id'] ?? null
            ]);
            
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Refund failed',
                'message' => $e->getMessage()
            ], 500);
        }
    }
}
""")
        
        controller_content = template.render()
        
        controller_file = self.backend_path / "app" / "Controllers" / "PaymentController.php"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
        
        return controller_content