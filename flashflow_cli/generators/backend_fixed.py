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
    
    def _create_directory_structure(self):
        """Create backend directory structure"""
        
        dirs = [
            self.backend_path,
            self.backend_path / "app",
            self.backend_path / "app" / "Models",
            self.backend_path / "app" / "Http" / "Controllers",
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

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

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

namespace App\Http\Controllers;

use App\Models\{{ model_name }};
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

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
        $validated = $request->validate([
            // Add validation rules here
        ]);

        ${{ model_var }} = {{ model_name }}::create($validated);
        return response()->json(${{ model_var }}, 201);
    }

    public function update(Request $request, $id): JsonResponse
    {
        ${{ model_var }} = {{ model_name }}::findOrFail($id);
        
        $validated = $request->validate([
            // Add validation rules here
        ]);

        ${{ model_var }}->update($validated);
        return response()->json(${{ model_var }});
    }

    public function destroy($id): JsonResponse
    {
        ${{ model_var }} = {{ model_name }}::findOrFail($id);
        ${{ model_var }}->delete();
        return response()->json(null, 204);
    }
}
""")
        
        controller_content = template.render(
            model_name=model_name,
            model_var=model_name.lower()
        )
        
        controller_file = self.backend_path / "app" / "Http" / "Controllers" / f"{model_name}Controller.php"
        with open(controller_file, 'w') as f:
            f.write(controller_content)
    
    def _generate_custom_controllers(self):
        """Generate controllers for custom endpoints"""
        # Implementation for custom endpoints
        pass
    
    def _generate_routes(self):
        """Generate API routes"""
        
        routes_content = """<?php

use Illuminate\\Support\\Facades\\Route;
use App\\Http\\Controllers;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/

"""
        
        # Add routes for each model
        for model_name in self.ir.models.keys():
            routes_content += f"Route::apiResource('{model_name.lower()}', Controllers\\{model_name}Controller::class);\n"
        
        # Add custom routes
        if hasattr(self.ir, 'endpoints'):
            for endpoint in self.ir.endpoints.values():
                routes_content += f"Route::{endpoint['method'].lower()}('{endpoint['path'].lstrip('/')}', function() {{\n    // TODO: Implement {endpoint['path']}\n}});\n"
        
        routes_content += "\n"
        
        routes_file = self.backend_path / "routes" / "api.php"
        with open(routes_file, 'w') as f:
            f.write(routes_content)
    
    def _generate_migrations(self):
        """Generate database migrations"""
        # Implementation for database migrations
        pass
    
    def _generate_config(self):
        """Generate configuration files"""
        # Implementation for configuration files
        pass
    
    def _generate_api_docs(self):
        """Generate API documentation"""
        # Implementation for API documentation
        pass
    
    def _generate_payment_gateway(self):
        """Generate payment gateway integration"""
        # Implementation for payment gateway
        pass
    
    def _generate_file_storage(self):
        """Generate file storage integration"""
        # Implementation for file storage
        pass
    
    def _generate_admin_panel(self):
        """Generate admin panel"""
        # Implementation for admin panel
        pass
    
    def _generate_smart_form_validation(self):
        """Generate smart form validation"""
        # Implementation for smart form validation
        pass
    
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