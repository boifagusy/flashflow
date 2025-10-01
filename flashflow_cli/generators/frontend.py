"""
Frontend Generator - Generates React/PWA frontend code
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from jinja2 import Template

from ..core import FlashFlowProject, FlashFlowIR

class FrontendGenerator:
    """Generates frontend code from FlashFlow IR"""
    
    def __init__(self, project: FlashFlowProject, ir: FlashFlowIR, env: str = 'development'):
        self.project = project
        self.ir = ir
        self.env = env
        self.frontend_path = project.dist_path / "frontend"
    
    def generate(self):
        """Generate complete frontend"""
        
        # Create frontend directory structure
        self._create_directory_structure()
        
        # Generate package.json and configs
        self._generate_package_config()
        
        # Generate main app files
        self._generate_app_files()
        
        # Generate components
        self._generate_components()
        
        # Generate social auth components if configured
        if hasattr(self.ir, 'social_auth'):
            self._generate_social_auth_components()
            
        # Generate file storage components if configured
        if hasattr(self.ir, 'file_storage'):
            self._generate_file_storage_components()
            
        # Generate admin panel components if configured
        if hasattr(self.ir, 'admin_panel'):
            self._generate_admin_panel_components()
            
        # Generate smart form components if configured
        if hasattr(self.ir, 'smart_forms'):
            self._generate_smart_form_components()
            
        # Generate i18n components if configured
        if hasattr(self.ir, 'i18n'):
            self._generate_i18n_components()
            
        # Generate serverless components if configured
        if hasattr(self.ir, 'serverless'):
            self._generate_serverless_components()
            
        # Generate UX helper components
        self._generate_ux_helper_components()
        
        # Generate pages
        self._generate_pages()
        
        # Generate PWA configuration
        self._generate_pwa_config()
        
        # Generate build configuration
        self._generate_build_config()
    
    def _create_directory_structure(self):
        """Create frontend directory structure"""
        
        dirs = [
            self.frontend_path,
            self.frontend_path / "src",
            self.frontend_path / "src" / "components",
            self.frontend_path / "src" / "pages",
            self.frontend_path / "src" / "hooks",
            self.frontend_path / "src" / "services",
            self.frontend_path / "src" / "styles",
            self.frontend_path / "src" / "utils",
            self.frontend_path / "public",
            self.frontend_path / "dist"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _generate_package_config(self):
        """Generate package.json and related configs"""
        
        package_json = {
            "name": f"{self.project.config.name}-frontend",
            "version": "0.1.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
                "serve": "vite preview --port 3000"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.8.0",
                "axios": "^1.3.0"
            },
            "devDependencies": {
                "@types/react": "^18.0.0",
                "@types/react-dom": "^18.0.0",
                "@vitejs/plugin-react": "^3.1.0",
                "typescript": "^4.9.0",
                "vite": "^4.1.0",
                "vite-plugin-pwa": "^0.14.0"
            }
        }
        
        with open(self.frontend_path / "package.json", 'w') as f:
            json.dump(package_json, f, indent=2)
    
    def _generate_app_files(self):
        """Generate main application files"""
        
        # index.html
        index_html = Template("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{ project_name }}</title>
    <meta name="description" content="{{ project_description }}" />
    
    <!-- PWA manifest -->
    <link rel="manifest" href="/manifest.json" />
    
    <!-- PWA icons -->
    <link rel="icon" type="image/png" sizes="32x32" href="/icons/icon-32x32.png" />
    <link rel="icon" type="image/png" sizes="192x192" href="/icons/icon-192x192.png" />
    <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
    
    <!-- Theme -->
    <meta name="theme-color" content="{{ theme_color }}" />
    
    <style>
        body {
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
        }
        #root {
            min-height: 100vh;
        }
        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-size: 1.2rem;
            color: #666;
        }
    </style>
</head>
<body>
    <div id="root">
        <div class="loading">Loading {{ project_name }}...</div>
    </div>
    <script type="module" src="/src/main.tsx"></script>
</body>
</html>""").render(
            project_name=self.project.config.name,
            project_description=self.project.config.description,
            theme_color=self.ir.theme.get('colors', {}).get('primary', '#3B82F6')
        )
        
        with open(self.frontend_path / "index.html", 'w') as f:
            f.write(index_html)
        
        # main.tsx
        main_tsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
        
        with open(self.frontend_path / "src" / "main.tsx", 'w') as f:
            f.write(main_tsx)
        
        # App.tsx
        app_tsx = Template("""import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './styles/App.css'

// Pages
{% for page_path, page_data in pages.items() %}import {{ page_data.component_name }} from './pages/{{ page_data.component_name }}'
{% endfor %}

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          {% for page_path, page_data in pages.items() %}<Route path="{{ page_path }}" element={<{{ page_data.component_name }} />} />
          {% endfor %}<Route path="*" element={<div>Page Not Found</div>} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
""").render(
            pages={
                path: {
                    'component_name': self._path_to_component_name(path, data),
                }
                for path, data in self.ir.pages.items()
            }
        )
        
        with open(self.frontend_path / "src" / "App.tsx", 'w') as f:
            f.write(app_tsx)
        
        # Global CSS
        self._generate_global_styles()
    
    def _generate_global_styles(self):
        """Generate global CSS styles"""
        
        # Extract theme colors
        colors = self.ir.theme.get('colors', {})
        primary = colors.get('primary', '#3B82F6')
        secondary = colors.get('secondary', '#64748B')
        
        css_content = f"""/* FlashFlow Generated Styles */

:root {{
  --primary-color: {primary};
  --secondary-color: {secondary};
  --success-color: {colors.get('success', '#10B981')};
  --warning-color: {colors.get('warning', '#F59E0B')};
  --danger-color: {colors.get('danger', '#EF4444')};
  --light-color: {colors.get('light', '#F8FAFC')};
  --dark-color: {colors.get('dark', '#0F172A')};
}}

* {{
  box-sizing: border-box;
}}

body {{
  margin: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: var(--light-color);
  color: var(--dark-color);
  line-height: 1.6;
}}

.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}}

.btn {{
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: var(--primary-color);
  color: white;
  text-decoration: none;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}}

.btn:hover {{
  opacity: 0.9;
  transform: translateY(-1px);
}}

.btn-secondary {{
  background-color: var(--secondary-color);
}}

.btn-success {{
  background-color: var(--success-color);
}}

.btn-warning {{
  background-color: var(--warning-color);
}}

.btn-danger {{
  background-color: var(--danger-color);
}}

.form-group {{
  margin-bottom: 1rem;
}}

.form-control {{
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #D1D5DB;
  border-radius: 0.375rem;
  font-size: 1rem;
}}

.form-control:focus {{
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}}

.card {{
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}}

.grid {{
  display: grid;
  gap: 1rem;
}}

.grid-2 {{
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}}

.grid-3 {{
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}}

@media (max-width: 768px) {{
  .container {{
    padding: 0 0.5rem;
  }}
  
  .btn {{
    width: 100%;
    text-align: center;
  }}
}}
"""
        
        with open(self.frontend_path / "src" / "styles" / "index.css", 'w') as f:
            f.write(css_content)
        
        # App-specific CSS
        app_css = """.app {
  min-height: 100vh;
}

.header {
  background: var(--primary-color);
  color: white;
  padding: 1rem 0;
  margin-bottom: 2rem;
}

.header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.footer {
  background: var(--dark-color);
  color: white;
  text-align: center;
  padding: 2rem 0;
  margin-top: 2rem;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50vh;
  font-size: 1.2rem;
  color: var(--secondary-color);
}
"""
        
        with open(self.frontend_path / "src" / "styles" / "App.css", 'w') as f:
            f.write(app_css)
    
    def _generate_pages(self):
        """Generate page components"""
        
        for page_path, page_data in self.ir.pages.items():
            self._generate_single_page(page_path, page_data)
    
    def _generate_single_page(self, page_path: str, page_data: Dict):
        """Generate a single page component"""
        
        component_name = self._path_to_component_name(page_path, page_data)
        
        template = Template("""import React, { useState, useEffect } from 'react'
import axios from 'axios'

interface {{ component_name }}Props {}

const {{ component_name }}: React.FC<{{ component_name }}Props> = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    // Load initial data if needed
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      // TODO: Load data from API based on page configuration
      // const response = await axios.get('/api/data')
      // setData(response.data)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="page-{{ page_slug }}">
      {% if page_title %}<div className="header">
        <div className="container">
          <h1>{{ page_title }}</h1>
        </div>
      </div>
      {% endif %}
      
      <div className="container">
        {% for component in components %}{{ component }}
        {% endfor %}
        
        {/* Auto-generated content based on .flow file */}
        <div className="page-content">
          <p>This page is generated from your .flow file.</p>
          <p>Add more components and data models to see them here.</p>
        </div>
      </div>
    </div>
  )
}

export default {{ component_name }}
""")
        
        # Process page components
        components = []
        body = page_data.get('body', [])
        
        for component_def in body:
            if isinstance(component_def, dict):
                component_jsx = self._generate_component_jsx(component_def)
                components.append(component_jsx)
        
        page_content = template.render(
            component_name=component_name,
            page_title=page_data.get('title', ''),
            page_slug=page_path.strip('/').replace('/', '-') or 'home',
            components=components
        )
        
        page_file = self.frontend_path / "src" / "pages" / f"{component_name}.tsx"
        with open(page_file, 'w') as f:
            f.write(page_content)
    
    def _generate_component_jsx(self, component_def: Dict) -> str:
        """Generate JSX for a component definition"""
        
        component_type = component_def.get('component', 'div')
        
        if component_type == 'hero':
            return f'''<div className="hero">
          <h1>{component_def.get('title', 'Welcome')}</h1>
          <p>{component_def.get('subtitle', 'Built with FlashFlow')}</p>
          <a href="{component_def.get('cta', {}).get('link', '#')}" className="btn">
            {component_def.get('cta', {}).get('text', 'Get Started')}
          </a>
        </div>'''
        
        elif component_type == 'form':
            fields = component_def.get('fields', [])
            field_inputs = []
            for field in fields:
                field_name = field.get('name', 'field')
                field_type = field.get('type', 'text')
                placeholder = field.get('placeholder', '')
                field_inputs.append(f'''<div className="form-group">
            <input 
              type="{field_type}" 
              name="{field_name}" 
              placeholder="{placeholder}"
              className="form-control"
            />
          </div>''')
            
            return f'''<form className="form">
          {"".join(field_inputs)}
          <button type="submit" className="btn">
            {component_def.get('button_text', 'Submit')}
          </button>
        </form>'''
        
        elif component_type == 'list':
            return '''<div className="list">
          {data.map((item, index) => (
            <div key={index} className="list-item">
              {/* List item template will be rendered here */}
              <p>{JSON.stringify(item)}</p>
            </div>
          ))}
        </div>'''
        
        else:
            return f'<div className="component-{component_type}">Component: {component_type}</div>'
    
    def _generate_components(self):
        """Generate reusable components"""
        
        # Generate API service
        api_service = Template("""import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth tokens
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Auto-generated API functions for models
{% for model_name in models %}
export const {{ model_name.lower() }}Api = {
  getAll: () => api.get('/{{ model_name.lower() }}s'),
  getById: (id: string) => api.get(`/{{ model_name.lower() }}s/${id}`),
  create: (data: any) => api.post('/{{ model_name.lower() }}s', data),
  update: (id: string, data: any) => api.put(`/{{ model_name.lower() }}s/${id}`, data),
  delete: (id: string) => api.delete(`/{{ model_name.lower() }}s/${id}`),
}
{% endfor %}

export default api
""").render(models=list(self.ir.models.keys()))
        
        with open(self.frontend_path / "src" / "services" / "api.ts", 'w') as f:
            f.write(api_service)
        
        # Generate common hooks
        hooks_content = """import { useState, useEffect } from 'react'
import api from '../services/api'

export const useApi = (url: string) => {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const response = await api.get(url)
        setData(response.data)
      } catch (err: any) {
        setError(err.message || 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [url])

  return { data, loading, error }
}

export const useLocalStorage = (key: string, initialValue: any) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      return initialValue
    }
  })

  const setValue = (value: any) => {
    try {
      setStoredValue(value)
      window.localStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error('Error saving to localStorage:', error)
    }
  }

  return [storedValue, setValue]
}
"""
        
        with open(self.frontend_path / "src" / "hooks" / "useApi.ts", 'w') as f:
            f.write(hooks_content)
    
    def _generate_pwa_config(self):
        """Generate PWA configuration"""
        
        # Manifest
        manifest = {
            "name": self.project.config.name,
            "short_name": self.project.config.name[:12],
            "description": self.project.config.description,
            "start_url": "/",
            "display": "standalone",
            "theme_color": self.ir.theme.get('colors', {}).get('primary', '#3B82F6'),
            "background_color": "#ffffff",
            "icons": [
                {
                    "src": "/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/icons/icon-512x512.png", 
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        }
        
        with open(self.frontend_path / "public" / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Create placeholder icons directory
        icons_dir = self.frontend_path / "public" / "icons"
        icons_dir.mkdir(exist_ok=True)
        
        # Service worker (basic)
        sw_content = """// FlashFlow Service Worker
const CACHE_NAME = 'flashflow-v1'
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  )
})

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        return response || fetch(event.request)
      })
  )
})
"""
        
        with open(self.frontend_path / "public" / "sw.js", 'w') as f:
            f.write(sw_content)
    
    def _generate_build_config(self):
        """Generate Vite build configuration"""
        
        vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}']
      },
      manifest: {
        name: '""" + self.project.config.name + """',
        short_name: '""" + self.project.config.name[:12] + """',
        description: '""" + self.project.config.description + """',
        theme_color: '#3B82F6',
        icons: [
          {
            src: '/icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          }
        ]
      }
    })
  ],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
"""
        
        with open(self.frontend_path / "vite.config.ts", 'w') as f:
            f.write(vite_config)
        
        # TypeScript config
        ts_config = {
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}]
        }
        
        with open(self.frontend_path / "tsconfig.json", 'w') as f:
            json.dump(ts_config, f, indent=2)
    
    def _path_to_component_name(self, path: str, page_data: Dict) -> str:
        """Convert page path to React component name"""
        
        # Use title if available
        if 'title' in page_data:
            title = page_data['title']
            # Remove common suffixes
            title = title.replace(' - ' + self.project.config.name, '')
            # Convert to PascalCase
            words = title.replace('-', ' ').replace('_', ' ').split()
            return ''.join(word.capitalize() for word in words if word)
        
        # Convert path to component name
        if path == '/':
            return 'HomePage'
        
        # Remove leading slash and convert to PascalCase
        path_parts = path.strip('/').split('/')
        component_name = ''.join(part.capitalize() for part in path_parts)
        
        if not component_name.endswith('Page'):
            component_name += 'Page'
        
        return component_name
    
    def _generate_social_auth_components(self):
        """Generate social authentication React components"""
        
        # Generate social login buttons component
        self._generate_social_buttons_component()
        
        # Generate enhanced login page with social options
        self._generate_enhanced_auth_pages()
        
        # Generate social auth service
        self._generate_social_auth_service()
    
    def _generate_social_buttons_component(self):
        """Generate SocialButtons React component"""
        
        template = Template("""import React, { useState, useEffect } from 'react';
import './SocialButtons.css';

const SocialButtons = ({ providers = [], layout = 'stack', onSuccess, onError }) => {
  const [availableProviders, setAvailableProviders] = useState([]);
  const [loading, setLoading] = useState({});

  useEffect(() => {
    // Fetch available providers from backend
    fetch('/api/auth/providers')
      .then(res => res.json())
      .then(data => {
        const enabled = Object.keys(data.enabled).filter(p => data.enabled[p]);
        setAvailableProviders(enabled.filter(p => providers.includes(p)));
      })
      .catch(console.error);
  }, [providers]);

  const handleSocialLogin = async (provider) => {
    setLoading({ ...loading, [provider]: true });
    
    try {
      // Get auth URL from backend
      const response = await fetch(`/api/auth/${provider}`);
      const data = await response.json();
      
      if (data.auth_url) {
        // Open popup window for OAuth
        const popup = window.open(
          data.auth_url,
          'social-auth',
          'width=500,height=600,scrollbars=yes,resizable=yes'
        );
        
        // Listen for popup completion
        const checkClosed = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkClosed);
            setLoading({ ...loading, [provider]: false });
            
            // Check for auth result in localStorage (set by callback page)
            const authResult = localStorage.getItem('social_auth_result');
            if (authResult) {
              const result = JSON.parse(authResult);
              localStorage.removeItem('social_auth_result');
              
              if (result.success) {
                onSuccess?.(result);
              } else {
                onError?.(result.error);
              }
            }
          }
        }, 1000);
      }
    } catch (error) {
      setLoading({ ...loading, [provider]: false });
      onError?.(error.message);
    }
  };

  const getProviderConfig = (provider) => {
    const configs = {
      google: {
        name: 'Google',
        icon: '🔍',
        color: '#db4437',
        textColor: '#fff'
      },
      facebook: {
        name: 'Facebook',
        icon: '📘',
        color: '#3b5998',
        textColor: '#fff'
      },
      twitter: {
        name: 'Twitter',
        icon: '🐦',
        color: '#1da1f2',
        textColor: '#fff'
      },
      github: {
        name: 'GitHub',
        icon: '🐙',
        color: '#333',
        textColor: '#fff'
      }
    };
    return configs[provider] || { name: provider, icon: '🔐', color: '#666', textColor: '#fff' };
  };

  if (availableProviders.length === 0) {
    return null;
  }

  return (
    <div className={`social-buttons social-buttons--${layout}`}>
      {availableProviders.map(provider => {
        const config = getProviderConfig(provider);
        return (
          <button
            key={provider}
            className={`social-button social-button--${provider}`}
            onClick={() => handleSocialLogin(provider)}
            disabled={loading[provider]}
            style={{
              backgroundColor: config.color,
              color: config.textColor
            }}
          >
            <span className="social-button__icon">{config.icon}</span>
            <span className="social-button__text">
              {loading[provider] ? 'Connecting...' : `Continue with ${config.name}`}
            </span>
          </button>
        );
      })}
    </div>
  );
};

export default SocialButtons;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        components_dir.mkdir(parents=True, exist_ok=True)
        
        component_file = components_dir / "SocialButtons.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for social buttons
        css_template = Template(""".social-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
}

.social-buttons--stack {
  flex-direction: column;
}

.social-buttons--grid {
  flex-direction: row;
  flex-wrap: wrap;
}

.social-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  min-height: 44px;
}

.social-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.social-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.social-button__icon {
  font-size: 18px;
}

.social-button__text {
  flex: 1;
  text-align: center;
}

.social-buttons--grid .social-button {
  flex: 1;
  min-width: calc(50% - 6px);
}

/* Provider-specific styles */
.social-button--google:hover {
  background-color: #c23321 !important;
}

.social-button--facebook:hover {
  background-color: #2d4373 !important;
}

.social-button--twitter:hover {
  background-color: #1991db !important;
}

.social-button--github:hover {
  background-color: #24292e !important;
}
""")
        
        css_content = css_template.render()
        
        css_file = components_dir / "SocialButtons.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_enhanced_auth_pages(self):
        """Generate enhanced authentication pages with social login"""
        
        # Enhanced Login page
        login_template = Template("""import React, { useState } from 'react';
import SocialButtons from '../components/SocialButtons';
import './Login.css';

const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('auth_token', data.token);
        window.location.href = '/dashboard';
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSocialSuccess = (result) => {
    localStorage.setItem('auth_token', result.token);
    window.location.href = '/dashboard';
  };

  const handleSocialError = (error) => {
    setError(`Social login failed: ${error}`);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Welcome Back</h1>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Enter your password"
              required
            />
          </div>
          
          <button type="submit" disabled={loading} className="login-button">
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
        
        <div className="divider">
          <span>or continue with</span>
        </div>
        
        <SocialButtons
          providers={['google', 'facebook', 'twitter', 'github']}
          layout="grid"
          onSuccess={handleSocialSuccess}
          onError={handleSocialError}
        />
        
        <div className="auth-links">
          <a href="/password-reset">Forgot your password?</a>
          <a href="/register">Don't have an account? Sign up</a>
        </div>
      </div>
    </div>
  );
};

export default Login;
""")
        
        login_content = login_template.render()
        
        pages_dir = self.frontend_path / "src" / "pages"
        pages_dir.mkdir(parents=True, exist_ok=True)
        
        login_file = pages_dir / "Login.jsx"
        with open(login_file, 'w') as f:
            f.write(login_content)
    
    def _generate_social_auth_service(self):
        """Generate social authentication service"""
        
        template = Template("""class SocialAuthService {
  constructor() {
    this.baseURL = '/api';
  }

  async getProviders() {
    try {
      const response = await fetch(`${this.baseURL}/auth/providers`);
      return await response.json();
    } catch (error) {
      throw new Error('Failed to fetch providers');
    }
  }

  async initiateLogin(provider) {
    try {
      const response = await fetch(`${this.baseURL}/auth/${provider}`);
      const data = await response.json();
      
      if (data.auth_url) {
        return data.auth_url;
      } else {
        throw new Error('No auth URL received');
      }
    } catch (error) {
      throw new Error(`Failed to initiate ${provider} login`);
    }
  }

  openAuthWindow(url, provider) {
    const popup = window.open(
      url,
      `${provider}-auth`,
      'width=500,height=600,scrollbars=yes,resizable=yes'
    );

    return new Promise((resolve, reject) => {
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          
          // Check for auth result
          const result = localStorage.getItem('social_auth_result');
          if (result) {
            const parsedResult = JSON.parse(result);
            localStorage.removeItem('social_auth_result');
            
            if (parsedResult.success) {
              resolve(parsedResult);
            } else {
              reject(new Error(parsedResult.error));
            }
          } else {
            reject(new Error('Authentication cancelled'));
          }
        }
      }, 1000);

      // Timeout after 5 minutes
      setTimeout(() => {
        clearInterval(checkClosed);
        if (!popup.closed) {
          popup.close();
        }
        reject(new Error('Authentication timeout'));
      }, 300000);
    });
  }

  async login(provider) {
    const authUrl = await this.initiateLogin(provider);
    return this.openAuthWindow(authUrl, provider);
  }

  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    window.location.href = '/login';
  }

  getToken() {
    return localStorage.getItem('auth_token');
  }

  isAuthenticated() {
    return !!this.getToken();
  }
}

export default new SocialAuthService();
""")
        
        service_content = template.render()
        
        services_dir = self.frontend_path / "src" / "services"
        services_dir.mkdir(parents=True, exist_ok=True)
        
        service_file = services_dir / "socialAuth.js"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        return service_content
    
    def _generate_push_notification_components(self):
        """Generate push notification React components"""
        
        # Generate push notification service
        self._generate_push_notification_service()
        
        # Generate notification permission component
        self._generate_notification_permission_component()
        
        # Generate notification settings component
        self._generate_notification_settings_component()
        
        # Generate notification compose component
        self._generate_notification_compose_component()
    
    def _generate_push_notification_service(self):
        """Generate push notification service"""
        
        template = Template("""class PushNotificationService {
  constructor() {
    this.baseURL = '/api';
    this.registration = null;
    this.vapidPublicKey = process.env.REACT_APP_VAPID_PUBLIC_KEY;
  }

  async requestPermission() {
    if (!('Notification' in window)) {
      throw new Error('This browser does not support notifications');
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  async registerServiceWorker() {
    if (!('serviceWorker' in navigator)) {
      throw new Error('Service workers are not supported');
    }

    try {
      this.registration = await navigator.serviceWorker.register('/sw.js');
      console.log('Service worker registered:', this.registration);
      return this.registration;
    } catch (error) {
      console.error('Service worker registration failed:', error);
      throw error;
    }
  }

  async subscribeToPush() {
    if (!this.registration) {
      await this.registerServiceWorker();
    }

    try {
      const subscription = await this.registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(this.vapidPublicKey)
      });

      // Register token with backend
      await this.registerToken(subscription);
      
      return subscription;
    } catch (error) {
      console.error('Push subscription failed:', error);
      throw error;
    }
  }

  async unsubscribeFromPush() {
    if (!this.registration) {
      return;
    }

    try {
      const subscription = await this.registration.pushManager.getSubscription();
      if (subscription) {
        await subscription.unsubscribe();
        await this.unregisterToken(subscription);
      }
    } catch (error) {
      console.error('Push unsubscription failed:', error);
      throw error;
    }
  }

  async registerToken(subscription) {
    const token = JSON.stringify(subscription);
    
    try {
      const response = await fetch(`${this.baseURL}/notifications/register-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          token,
          platform: 'web',
          device_info: {
            user_agent: navigator.userAgent,
            platform: navigator.platform,
            vendor: navigator.vendor
          }
        })
      });

      if (!response.ok) {
        throw new Error('Failed to register token');
      }

      return await response.json();
    } catch (error) {
      console.error('Token registration failed:', error);
      throw error;
    }
  }

  async unregisterToken(subscription) {
    const token = JSON.stringify(subscription);
    
    try {
      const response = await fetch(`${this.baseURL}/notifications/unregister-token`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({ token })
      });

      if (!response.ok) {
        throw new Error('Failed to unregister token');
      }

      return await response.json();
    } catch (error) {
      console.error('Token unregistration failed:', error);
      throw error;
    }
  }

  async sendNotification(data) {
    try {
      const response = await fetch(`${this.baseURL}/notifications/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to send notification');
      }

      return await response.json();
    } catch (error) {
      console.error('Notification sending failed:', error);
      throw error;
    }
  }

  async getNotificationPreferences() {
    try {
      const response = await fetch(`${this.baseURL}/notifications/preferences`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get preferences');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get notification preferences:', error);
      throw error;
    }
  }

  async updateNotificationPreferences(preferences) {
    try {
      const response = await fetch(`${this.baseURL}/notifications/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(preferences)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to update preferences');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to update notification preferences:', error);
      throw error;
    }
  }

  async getNotificationStatus(notificationId) {
    try {
      const response = await fetch(`${this.baseURL}/notifications/${notificationId}/status`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get notification status');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get notification status:', error);
      throw error;
    }
  }

  // Utility methods
  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  getAuthToken() {
    return localStorage.getItem('auth_token');
  }

  isSupported() {
    return 'Notification' in window && 'serviceWorker' in navigator && 'PushManager' in window;
  }

  getPermissionStatus() {
    if (!('Notification' in window)) {
      return 'unsupported';
    }
    return Notification.permission;
  }
}

export default new PushNotificationService();
""")
        
        service_content = template.render()
        
        services_dir = self.frontend_path / "src" / "services"
        service_file = services_dir / "pushNotificationService.js"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        return service_content
    
    def _generate_ai_chat_component(self):
        """Generate AI chat interface component"""
        
        template = Template("""import React, { useState, useEffect, useRef } from 'react';
import AiService from '../services/aiService';

const AiChatInterface = ({ 
  providers = ['openai', 'anthropic'], 
  models = ['gpt-4', 'claude-3-opus-20240229'],
  onConversationChange
}) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedProvider, setSelectedProvider] = useState(providers[0]);
  const [selectedModel, setSelectedModel] = useState(models[0]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = { role: 'user', content: inputMessage.trim() };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputMessage('');
    setIsLoading(true);
    setError('');

    try {
      const payload = {
        provider: selectedProvider,
        model: selectedModel,
        messages: newMessages
      };

      const response = await AiService.startChat(payload);
      
      const assistantMessage = response.message;
      setMessages(prev => [...prev, assistantMessage]);
      
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
        onConversationChange?.(response.conversation_id);
      }
      
    } catch (err) {
      setError(err.message || 'Failed to send message');
      // Remove the user message if the request failed
      setMessages(messages);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className=\"ai-chat-interface\">
      <div className=\"chat-header\">
        <select 
          value={selectedProvider} 
          onChange={(e) => setSelectedProvider(e.target.value)}
          disabled={isLoading}
        >
          {providers.map(provider => (
            <option key={provider} value={provider}>
              {provider.charAt(0).toUpperCase() + provider.slice(1)}
            </option>
          ))}
        </select>
        
        <select 
          value={selectedModel} 
          onChange={(e) => setSelectedModel(e.target.value)}
          disabled={isLoading}
        >
          {models.map(model => (
            <option key={model} value={model}>{model}</option>
          ))}
        </select>
      </div>

      <div className=\"chat-messages\">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className=\"message-role\">
              {message.role === 'user' ? 'You' : 'AI'}
            </div>
            <div className=\"message-content\">
              {message.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className=\"message assistant loading\">
            <div className=\"message-role\">AI</div>
            <div className=\"message-content\">Thinking...</div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className=\"error-message\">
          {error}
        </div>
      )}

      <div className=\"chat-input\">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder=\"Type your message...\"
          disabled={isLoading}
          rows={3}
        />
        <button 
          onClick={handleSendMessage} 
          disabled={isLoading || !inputMessage.trim()}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default AiChatInterface;
""")
        
        chat_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        chat_file = components_dir / "AiChatInterface.jsx"
        with open(chat_file, 'w') as f:
            f.write(chat_content)
        
        return chat_content
    
    def _generate_ai_service(self):
        """Generate AI service for frontend"""
        
        template = Template("""class AiService {
  constructor() {
    this.baseURL = '/api';
  }

  async startChat(data) {
    try {
      const response = await fetch(`${this.baseURL}/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Chat request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('AI chat failed:', error);
      throw error;
    }
  }

  async generateCompletion(data) {
    try {
      const response = await fetch(`${this.baseURL}/ai/completion`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Completion request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('AI completion failed:', error);
      throw error;
    }
  }

  async generateEmbeddings(data) {
    try {
      const response = await fetch(`${this.baseURL}/ai/embedding`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Embedding request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('AI embedding failed:', error);
      throw error;
    }
  }

  async getUsageAnalytics(params = {}) {
    try {
      const queryParams = new URLSearchParams(params);
      const response = await fetch(`${this.baseURL}/ai/analytics/usage?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch usage analytics');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get usage analytics:', error);
      throw error;
    }
  }

  // Utility methods
  getAuthToken() {
    return localStorage.getItem('auth_token');
  }

  formatCost(cost, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 4
    }).format(cost);
  }

  estimateTokens(text) {
    // Rough estimation: ~4 characters per token for English text
    return Math.ceil(text.length / 4);
  }
}

export default new AiService();
""")
        
        service_content = template.render()
        
        services_dir = self.frontend_path / "src" / "services"
        service_file = services_dir / "aiService.js"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        return service_content
    
    def _generate_payment_components(self):
        """Generate payment-related React components"""
        
        # Generate payment form component
        self._generate_payment_form_component()
        
        # Generate payment method selector
        self._generate_payment_method_selector()
        
        # Generate payment summary component
        self._generate_payment_summary_component()
        
        # Generate payment service
        self._generate_payment_service()
    
    def _generate_payment_form_component(self):
        """Generate payment form component"""
        
        template = Template("""import React, { useState, useEffect } from 'react';
import PaymentService from '../services/paymentService';
import PaymentMethodSelector from './PaymentMethodSelector';
import PaymentSummary from './PaymentSummary';

const PaymentForm = ({ 
  amount, 
  currency = 'USD', 
  providers = ['stripe', 'paypal'], 
  onSuccess, 
  onError,
  showSummary = true,
  savePaymentMethod = true
}) => {
  const [selectedProvider, setSelectedProvider] = useState(providers[0]);
  const [paymentMethod, setPaymentMethod] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [billingAddress, setBillingAddress] = useState({
    name: '',
    email: '',
    line1: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'US'
  });

  useEffect(() => {
    // Load payment providers configuration
    PaymentService.getProviders().then(providers => {
      // Filter available providers
      const availableProviders = providers.filter(p => 
        providers.includes(p.name) && p.enabled
      );
      if (availableProviders.length > 0) {
        setSelectedProvider(availableProviders[0].name);
      }
    }).catch(err => {
      setError('Failed to load payment providers');
    });
  }, [providers]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Create payment intent
      const intent = await PaymentService.createPaymentIntent({
        amount,
        currency,
        provider: selectedProvider,
        payment_method_types: ['card'],
        metadata: {
          billing_address: JSON.stringify(billingAddress)
        }
      });

      setClientSecret(intent.client_secret);

      // Handle different providers
      let result;
      switch (selectedProvider) {
        case 'stripe':
          result = await handleStripePayment(intent);
          break;
        case 'paypal':
          result = await handlePayPalPayment(intent);
          break;
        case 'square':
          result = await handleSquarePayment(intent);
          break;
        default:
          throw new Error('Unsupported payment provider');
      }

      if (result.success) {
        onSuccess?.(result);
      } else {
        setError(result.error || 'Payment failed');
        onError?.(result.error);
      }

    } catch (err) {
      setError(err.message);
      onError?.(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStripePayment = async (intent) => {
    const stripe = await PaymentService.getStripe();
    const elements = stripe.elements({ clientSecret: intent.client_secret });
    
    const { error, paymentIntent } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/payment/success`,
      },
    });

    if (error) {
      return { success: false, error: error.message };
    }

    return { success: true, paymentIntent };
  };

  const handlePayPalPayment = async (intent) => {
    // PayPal payment logic
    return PaymentService.processPayPalPayment(intent.payment_id);
  };

  const handleSquarePayment = async (intent) => {
    // Square payment logic
    return PaymentService.processSquarePayment(intent.payment_id);
  };

  const handleAddressChange = (field, value) => {
    setBillingAddress(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className=\"payment-form-container\">
      {showSummary && (
        <PaymentSummary 
          amount={amount} 
          currency={currency}
          className=\"payment-summary\"
        />
      )}
      
      {error && (
        <div className=\"error-message\">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className=\"payment-form\">
        {/* Provider Selection */}
        <div className=\"form-section\">
          <h3>Payment Method</h3>
          <PaymentMethodSelector
            providers={providers}
            selected={selectedProvider}
            onChange={setSelectedProvider}
          />
        </div>

        {/* Billing Address */}
        <div className=\"form-section\">
          <h3>Billing Information</h3>
          
          <div className=\"form-row\">
            <div className=\"form-group\">
              <label htmlFor=\"name\">Full Name</label>
              <input
                type=\"text\"
                id=\"name\"
                value={billingAddress.name}
                onChange={(e) => handleAddressChange('name', e.target.value)}
                required
              />
            </div>
            
            <div className=\"form-group\">
              <label htmlFor=\"email\">Email</label>
              <input
                type=\"email\"
                id=\"email\"
                value={billingAddress.email}
                onChange={(e) => handleAddressChange('email', e.target.value)}
                required
              />
            </div>
          </div>

          <div className=\"form-group\">
            <label htmlFor=\"line1\">Address</label>
            <input
              type=\"text\"
              id=\"line1\"
              value={billingAddress.line1}
              onChange={(e) => handleAddressChange('line1', e.target.value)}
              placeholder=\"Street address\"
              required
            />
          </div>

          <div className=\"form-row\">
            <div className=\"form-group\">
              <label htmlFor=\"city\">City</label>
              <input
                type=\"text\"
                id=\"city\"
                value={billingAddress.city}
                onChange={(e) => handleAddressChange('city', e.target.value)}
                required
              />
            </div>
            
            <div className=\"form-group\">
              <label htmlFor=\"state\">State</label>
              <input
                type=\"text\"
                id=\"state\"
                value={billingAddress.state}
                onChange={(e) => handleAddressChange('state', e.target.value)}
                required
              />
            </div>
            
            <div className=\"form-group\">
              <label htmlFor=\"postal_code\">ZIP Code</label>
              <input
                type=\"text\"
                id=\"postal_code\"
                value={billingAddress.postal_code}
                onChange={(e) => handleAddressChange('postal_code', e.target.value)}
                required
              />
            </div>
          </div>
        </div>

        {/* Payment Method Input */}
        <div className=\"form-section\">
          <div id=\"payment-element\">
            {/* Dynamic payment elements will be inserted here */}
          </div>
        </div>

        {savePaymentMethod && (
          <div className=\"form-group\">
            <label className=\"checkbox-label\">
              <input
                type=\"checkbox\"
                checked={paymentMethod?.save || false}
                onChange={(e) => setPaymentMethod(prev => ({
                  ...prev,
                  save: e.target.checked
                }))}
              />
              Save payment method for future purchases
            </label>
          </div>
        )}

        <button 
          type=\"submit\" 
          disabled={loading} 
          className=\"payment-submit-button\"
        >
          {loading ? 'Processing...' : `Pay $${amount}`}
        </button>
      </form>

      <div className=\"security-badges\">
        <div className=\"badge\">🔒 SSL Secured</div>
        <div className=\"badge\">🛡️ PCI Compliant</div>
        <div className=\"badge\">💳 256-bit Encrypted</div>
      </div>
    </div>
  );
};

export default PaymentForm;
""")
        
        payment_form_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        components_dir.mkdir(parents=True, exist_ok=True)
        
        payment_form_file = components_dir / "PaymentForm.jsx"
        with open(payment_form_file, 'w') as f:
            f.write(payment_form_content)
        
        return payment_form_content
    
    def _generate_payment_method_selector(self):
        """Generate payment method selector component"""
        
        template = Template("""import React from 'react';

const PaymentMethodSelector = ({ providers = [], selected, onChange }) => {
  const providerConfig = {
    stripe: {
      name: 'Credit Card',
      icon: '💳',
      description: 'Visa, Mastercard, American Express',
      className: 'stripe'
    },
    paypal: {
      name: 'PayPal',
      icon: '🏦',
      description: 'Pay with your PayPal account',
      className: 'paypal'
    },
    square: {
      name: 'Square',
      icon: '🟩',
      description: 'Secure payment processing',
      className: 'square'
    },
    razorpay: {
      name: 'Razorpay',
      icon: '💰',
      description: 'UPI, Cards, Net Banking, Wallets',
      className: 'razorpay'
    }
  };

  return (
    <div className=\"payment-method-selector\">
      {providers.map(provider => {
        const config = providerConfig[provider];
        if (!config) return null;

        return (
          <div
            key={provider}
            className={`payment-method ${
              selected === provider ? 'selected' : ''
            } ${config.className}`}
            onClick={() => onChange(provider)}
          >
            <div className=\"method-icon\">{config.icon}</div>
            <div className=\"method-info\">
              <div className=\"method-name\">{config.name}</div>
              <div className=\"method-description\">{config.description}</div>
            </div>
            <div className=\"method-radio\">
              <input
                type=\"radio\"
                name=\"payment-method\"
                value={provider}
                checked={selected === provider}
                onChange={() => onChange(provider)}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default PaymentMethodSelector;
""")
        
        selector_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        selector_file = components_dir / "PaymentMethodSelector.jsx"
        with open(selector_file, 'w') as f:
            f.write(selector_content)
    
    def _generate_payment_summary_component(self):
        """Generate payment summary component"""
        
        template = Template("""import React from 'react';

const PaymentSummary = ({ 
  amount, 
  currency = 'USD', 
  items = [], 
  taxes = 0, 
  shipping = 0,
  discounts = 0,
  showItems = true,
  className = ''
}) => {
  const formatCurrency = (value, curr = currency) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: curr
    }).format(value);
  };

  const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const total = subtotal + taxes + shipping - discounts;

  return (
    <div className={`payment-summary ${className}`}>
      <h3>Order Summary</h3>
      
      {showItems && items.length > 0 && (
        <div className=\"summary-items\">
          {items.map((item, index) => (
            <div key={index} className=\"summary-item\">
              <div className=\"item-info\">
                <div className=\"item-name\">{item.name}</div>
                <div className=\"item-details\">
                  Qty: {item.quantity} {item.description && `• ${item.description}`}
                </div>
              </div>
              <div className=\"item-price\">
                {formatCurrency(item.price * item.quantity)}
              </div>
            </div>
          ))}
        </div>
      )}
      
      <div className=\"summary-calculations\">
        {subtotal > 0 && (
          <div className=\"summary-row\">
            <span>Subtotal</span>
            <span>{formatCurrency(subtotal)}</span>
          </div>
        )}
        
        {shipping > 0 && (
          <div className=\"summary-row\">
            <span>Shipping</span>
            <span>{formatCurrency(shipping)}</span>
          </div>
        )}
        
        {taxes > 0 && (
          <div className=\"summary-row\">
            <span>Taxes</span>
            <span>{formatCurrency(taxes)}</span>
          </div>
        )}
        
        {discounts > 0 && (
          <div className=\"summary-row discount\">
            <span>Discount</span>
            <span>-{formatCurrency(discounts)}</span>
          </div>
        )}
        
        <div className=\"summary-row total\">
          <span>Total</span>
          <span>{formatCurrency(amount || total)}</span>
        </div>
      </div>
    </div>
  );
};

export default PaymentSummary;
""")
        
        summary_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        summary_file = components_dir / "PaymentSummary.jsx"
        with open(summary_file, 'w') as f:
            f.write(summary_content)
    
    def _generate_payment_service(self):
        """Generate payment service for frontend"""
        
        template = Template("""class PaymentService {
  constructor() {
    this.baseURL = '/api';
    this.stripePromise = null;
  }

  async getProviders() {
    try {
      const response = await fetch(`${this.baseURL}/payments/providers`);
      return await response.json();
    } catch (error) {
      throw new Error('Failed to fetch payment providers');
    }
  }

  async createPaymentIntent(data) {
    try {
      const response = await fetch(`${this.baseURL}/payments/intent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to create payment intent');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Payment intent creation failed: ${error.message}`);
    }
  }

  async confirmPayment(paymentId, providerPaymentId) {
    try {
      const response = await fetch(`${this.baseURL}/payments/confirm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          payment_id: paymentId,
          provider_payment_id: providerPaymentId
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Payment confirmation failed');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Payment confirmation failed: ${error.message}`);
    }
  }

  async processRefund(paymentId, amount, reason) {
    try {
      const response = await fetch(`${this.baseURL}/payments/refund`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          payment_id: paymentId,
          amount,
          reason
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Refund failed');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Refund failed: ${error.message}`);
    }
  }

  async getPaymentMethods() {
    try {
      const response = await fetch(`${this.baseURL}/payments/methods`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch payment methods');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Failed to get payment methods: ${error.message}`);
    }
  }

  async savePaymentMethod(data) {
    try {
      const response = await fetch(`${this.baseURL}/payments/methods`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to save payment method');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Failed to save payment method: ${error.message}`);
    }
  }

  async deletePaymentMethod(methodId) {
    try {
      const response = await fetch(`${this.baseURL}/payments/methods/${methodId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to delete payment method');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Failed to delete payment method: ${error.message}`);
    }
  }

  // Stripe-specific methods
  async getStripe() {
    if (!this.stripePromise) {
      const { loadStripe } = await import('@stripe/stripe-js');
      this.stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY);
    }
    return await this.stripePromise;
  }

  async processStripePayment(clientSecret, elements) {
    const stripe = await this.getStripe();
    
    const { error, paymentIntent } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/payment/success`,
      },
    });

    if (error) {
      return { success: false, error: error.message };
    }

    return { success: true, paymentIntent };
  }

  // PayPal-specific methods
  async processPayPalPayment(paymentId) {
    try {
      // PayPal integration logic
      const result = await this.confirmPayment(paymentId);
      return { success: true, result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Square-specific methods
  async processSquarePayment(paymentId) {
    try {
      // Square integration logic
      const result = await this.confirmPayment(paymentId);
      return { success: true, result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Utility methods
  getAuthToken() {
    return localStorage.getItem('auth_token');
  }

  formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency
    }).format(amount);
  }

  async checkPaymentStatus(paymentId) {
    try {
      const response = await fetch(`${this.baseURL}/payments/${paymentId}/status`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to check payment status');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Status check failed: ${error.message}`);
    }
  }
}

export default new PaymentService();
""")
        
        service_content = template.render()
        
        services_dir = self.frontend_path / "src" / "services"
        service_file = services_dir / "paymentService.js"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        return service_content
    
    def _generate_file_storage_components(self):
        """Generate file storage React components"""
        
        # Generate file storage service
        self._generate_file_storage_service()
    
    def _generate_file_storage_service(self):
        """Generate file storage service"""
        
        template = Template("""class FileStorageService {
  constructor() {
    this.baseURL = '/api';
  }

  async uploadFile(file, options = {}) {
    const formData = new FormData();
    formData.append('files[]', file);
    
    if (options.categoryId) formData.append('category_id', options.categoryId);
    if (options.description) formData.append('description', options.description);
    if (options.isPublic !== undefined) formData.append('is_public', options.isPublic);
    if (options.tags) formData.append('tags', JSON.stringify(options.tags));
    if (options.provider) formData.append('provider', options.provider);

    try {
      const response = await fetch(`${this.baseURL}/files/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Upload failed');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Upload failed: ${error.message}`);
    }
  }

  async getFiles(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    
    try {
      const response = await fetch(`${this.baseURL}/files?${queryString}`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch files');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Failed to fetch files: ${error.message}`);
    }
  }

  async downloadFile(fileId) {
    try {
      const response = await fetch(`${this.baseURL}/files/${fileId}/download`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Download failed');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Download failed: ${error.message}`);
    }
  }

  async deleteFile(fileId) {
    try {
      const response = await fetch(`${this.baseURL}/files/${fileId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Delete failed');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Delete failed: ${error.message}`);
    }
  }

  async shareFile(fileId, shareData) {
    try {
      const response = await fetch(`${this.baseURL}/files/${fileId}/share`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(shareData)
      });

      if (!response.ok) {
        throw new Error('Share failed');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Share failed: ${error.message}`);
    }
  }

  async getCategories() {
    try {
      const response = await fetch(`${this.baseURL}/files/categories`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch categories');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Failed to fetch categories: ${error.message}`);
    }
  }

  async createCategory(categoryData) {
    try {
      const response = await fetch(`${this.baseURL}/files/categories`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(categoryData)
      });

      if (!response.ok) {
        throw new Error('Category creation failed');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Category creation failed: ${error.message}`);
    }
  }

  async getUsageStatistics() {
    try {
      const response = await fetch(`${this.baseURL}/files/usage`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch usage statistics');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Failed to fetch usage statistics: ${error.message}`);
    }
  }

  getAuthToken() {
    return localStorage.getItem('auth_token');
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}

export default new FileStorageService();
""")
        
        service_content = template.render()
        
        services_dir = self.frontend_path / "src" / "services"
        service_file = services_dir / "fileStorageService.js"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        return service_content
    
    def _generate_admin_panel_components(self):
        """Generate admin panel React components"""
        
        # Generate admin service
        self._generate_admin_service()
    
    def _generate_admin_service(self):
        """Generate admin service"""
        
        template = Template("""class AdminService {
  constructor() {
    this.baseURL = '/api/admin';
  }

  async getDashboardData(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    
    try {
      const response = await fetch(`${this.baseURL}/dashboard?${queryString}`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Dashboard data fetch failed: ${error.message}`);
    }
  }

  async getUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    
    try {
      const response = await fetch(`${this.baseURL}/users?${queryString}`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Users fetch failed: ${error.message}`);
    }
  }

  async createUser(userData) {
    try {
      const response = await fetch(`${this.baseURL}/users`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        throw new Error('Failed to create user');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`User creation failed: ${error.message}`);
    }
  }

  async bulkUserAction(actionData) {
    try {
      const response = await fetch(`${this.baseURL}/users/bulk`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(actionData)
      });

      if (!response.ok) {
        throw new Error('Failed to perform bulk action');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Bulk action failed: ${error.message}`);
    }
  }

  async getSystemHealth() {
    try {
      const response = await fetch(`${this.baseURL}/system/health`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch system health');
      }

      return await response.json();
    } catch (error) {
      throw new Error(`System health check failed: ${error.message}`);
    }
  }

  getAuthToken() {
    return localStorage.getItem('admin_token') || localStorage.getItem('auth_token');
  }
}

export default new AdminService();
""")
        
        service_content = template.render()
        
        services_dir = self.frontend_path / "src" / "services"
        service_file = services_dir / "adminService.js"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        return service_content
    
    def _generate_smart_form_components(self):
        """Generate intelligent form components with real-time validation"""
        
        # Generate smart form input components
        self._generate_smart_input_components()
        
        # Generate smart form wrapper component
        self._generate_smart_form_wrapper()
        
        # Generate form validation hooks
        self._generate_form_validation_hooks()
        
        # Generate smart form service
        self._generate_smart_form_service()
        
        # Generate form utility functions
        self._generate_form_utilities()
    
    def _generate_smart_input_components(self):
        """Generate smart input components for different field types"""
        
        # Smart Email Input Component
        self._generate_smart_email_input()
        
        # Smart Phone Input Component
        self._generate_smart_phone_input()
        
        # Smart Password Input Component
        self._generate_smart_password_input()
        
        # Smart OTP Input Component
        self._generate_smart_otp_input()
        
        # Smart Credit Card Input Component
        self._generate_smart_credit_card_input()
        
        # Smart Search Input Component
        self._generate_smart_search_input()
        
        # Smart Address Input Component
        self._generate_smart_address_input()
    
    def _generate_smart_email_input(self):
        """Generate smart email input with validation and suggestions"""
        
        template = Template("""import React, { useState, useEffect, useCallback } from 'react';
import { useSmartValidation } from '../hooks/useSmartValidation';
import { debounce } from '../utils/formUtils';
import './SmartEmailInput.css';

const SmartEmailInput = ({
  name,
  value = '',
  onChange,
  onValidationChange,
  placeholder = 'Enter your email address',
  required = false,
  validateDisposable = true,
  showSuggestions = true,
  className = '',
  ...props
}) => {
  const [inputValue, setInputValue] = useState(value);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestionsList, setShowSuggestionsList] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  
  const { validation, validateField } = useSmartValidation();
  
  // Debounced validation function
  const debouncedValidate = useCallback(
    debounce(async (email) => {
      if (!email) {
        onValidationChange?.({ isValid: !required, errors: [] });
        return;
      }
      
      setIsValidating(true);
      try {
        const result = await validateField('email', email, {
          checkDisposable: validateDisposable,
          checkTypos: true
        });
        
        onValidationChange?.(result);
        
        if (result.suggestions && result.suggestions.length > 0) {
          setSuggestions(result.suggestions);
          setShowSuggestionsList(true);
        } else {
          setShowSuggestionsList(false);
        }
      } catch (error) {
        console.error('Email validation failed:', error);
        onValidationChange?.({ isValid: false, errors: ['Validation failed'] });
      } finally {
        setIsValidating(false);
      }
    }, 500),
    [validateField, validateDisposable, required, onValidationChange]
  );
  
  useEffect(() => {
    debouncedValidate(inputValue);
  }, [inputValue, debouncedValidate]);
  
  const handleInputChange = (e) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    onChange?.(e);
  };
  
  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion);
    setShowSuggestionsList(false);
    
    // Create synthetic event for onChange
    const syntheticEvent = {
      target: { name, value: suggestion }
    };
    onChange?.(syntheticEvent);
  };
  
  const validationState = validation[name];
  const hasErrors = validationState && !validationState.isValid;
  const inputClassName = `smart-email-input ${
    hasErrors ? 'smart-email-input--error' : 
    validationState?.isValid ? 'smart-email-input--valid' : ''
  } ${className}`.trim();
  
  return (
    <div className="smart-email-input-wrapper">
      <div className="smart-input-container">
        <input
          type="email"
          name={name}
          value={inputValue}
          onChange={handleInputChange}
          placeholder={placeholder}
          className={inputClassName}
          required={required}
          {...props}
        />
        
        {isValidating && (
          <div className="smart-input-spinner">
            <div className="spinner"></div>
          </div>
        )}
        
        {validationState?.isValid && (
          <div className="smart-input-checkmark">✓</div>
        )}
      </div>
      
      {/* Error Messages */}
      {hasErrors && (
        <div className="smart-input-errors">
          {validationState.errors.map((error, index) => (
            <div key={index} className="smart-input-error">
              {error}
            </div>
          ))}
        </div>
      )}
      
      {/* Suggestions Dropdown */}
      {showSuggestions && showSuggestionsList && suggestions.length > 0 && (
        <div className="smart-email-suggestions">
          <div className="suggestions-header">Did you mean?</div>
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              type="button"
              className="suggestion-item"
              onClick={() => handleSuggestionClick(suggestion)}
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default SmartEmailInput;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        component_file = components_dir / "SmartEmailInput.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for smart email input
        css_content = """.smart-email-input-wrapper {
  position: relative;
  width: 100%;
}

.smart-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.smart-email-input {
  width: 100%;
  padding: 12px 40px 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
  background-color: #fff;
}

.smart-email-input:focus {
  outline: none;
  border-color: var(--primary-color, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.smart-email-input--valid {
  border-color: var(--success-color, #10b981);
  padding-right: 40px;
}

.smart-email-input--error {
  border-color: var(--danger-color, #ef4444);
}

.smart-input-spinner {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid var(--primary-color, #3b82f6);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.smart-input-checkmark {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--success-color, #10b981);
  font-weight: bold;
  font-size: 18px;
}

.smart-input-errors {
  margin-top: 4px;
}

.smart-input-error {
  color: var(--danger-color, #ef4444);
  font-size: 14px;
  margin-bottom: 2px;
}

.smart-email-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  margin-top: 4px;
}

.suggestions-header {
  padding: 8px 12px;
  font-size: 12px;
  color: #6b7280;
  border-bottom: 1px solid #e1e5e9;
  background-color: #f9fafb;
}

.suggestion-item {
  display: block;
  width: 100%;
  padding: 8px 12px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.suggestion-item:hover {
  background-color: #f3f4f6;
}

.suggestion-item:last-child {
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}
"""
        
        css_file = components_dir / "SmartEmailInput.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_smart_phone_input(self):
        """Generate smart phone input with auto-formatting and country detection"""
        
        template = Template("""import React, { useState, useEffect, useCallback } from 'react';
import { useSmartValidation } from '../hooks/useSmartValidation';
import { formatPhoneNumber, detectCountryCode } from '../utils/formUtils';
import './SmartPhoneInput.css';

const SmartPhoneInput = ({
  name,
  value = '',
  onChange,
  onValidationChange,
  placeholder = 'Enter your phone number',
  required = false,
  autoFormat = true,
  detectCountry = true,
  validateRegistered = false,
  className = '',
  ...props
}) => {
  const [inputValue, setInputValue] = useState(value);
  const [countryCode, setCountryCode] = useState('+1');
  const [detectedCountry, setDetectedCountry] = useState(null);
  const [isValidating, setIsValidating] = useState(false);
  
  const { validation, validateField } = useSmartValidation();
  
  useEffect(() => {
    if (detectCountry && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          detectCountryCode(latitude, longitude).then(country => {
            if (country) {
              setDetectedCountry(country);
              setCountryCode(country.dialCode);
            }
          });
        },
        () => {
          // Fallback to IP-based detection
          fetch('/api/geo/detect-country')
            .then(res => res.json())
            .then(data => {
              if (data.country) {
                setDetectedCountry(data.country);
                setCountryCode(data.country.dialCode);
              }
            })
            .catch(console.error);
        }
      );
    }
  }, [detectCountry]);
  
  const debouncedValidate = useCallback(
    debounce(async (phone) => {
      if (!phone) {
        onValidationChange?.({ isValid: !required, errors: [] });
        return;
      }
      
      setIsValidating(true);
      try {
        const fullPhone = countryCode + phone.replace(/\D/g, '');
        const result = await validateField('phone', fullPhone, {
          validateRegistered,
          countryCode
        });
        
        onValidationChange?.(result);
      } catch (error) {
        console.error('Phone validation failed:', error);
        onValidationChange?.({ isValid: false, errors: ['Validation failed'] });
      } finally {
        setIsValidating(false);
      }
    }, 500),
    [validateField, countryCode, validateRegistered, required, onValidationChange]
  );
  
  useEffect(() => {
    debouncedValidate(inputValue);
  }, [inputValue, debouncedValidate]);
  
  const handleInputChange = (e) => {
    let newValue = e.target.value;
    
    if (autoFormat) {
      newValue = formatPhoneNumber(newValue, countryCode);
    }
    
    setInputValue(newValue);
    
    // Create synthetic event for onChange
    const syntheticEvent = {
      target: { name, value: newValue }
    };
    onChange?.(syntheticEvent);
  };
  
  const handleCountryChange = (e) => {
    const newCountryCode = e.target.value;
    setCountryCode(newCountryCode);
    
    // Reformat phone number for new country
    if (autoFormat && inputValue) {
      const formatted = formatPhoneNumber(inputValue, newCountryCode);
      setInputValue(formatted);
      
      const syntheticEvent = {
        target: { name, value: formatted }
      };
      onChange?.(syntheticEvent);
    }
  };
  
  const validationState = validation[name];
  const hasErrors = validationState && !validationState.isValid;
  const inputClassName = `smart-phone-input ${
    hasErrors ? 'smart-phone-input--error' : 
    validationState?.isValid ? 'smart-phone-input--valid' : ''
  } ${className}`.trim();
  
  const countryCodes = [
    { code: '+1', country: 'US', name: 'United States' },
    { code: '+1', country: 'CA', name: 'Canada' },
    { code: '+44', country: 'GB', name: 'United Kingdom' },
    { code: '+33', country: 'FR', name: 'France' },
    { code: '+49', country: 'DE', name: 'Germany' },
    { code: '+39', country: 'IT', name: 'Italy' },
    { code: '+34', country: 'ES', name: 'Spain' },
    { code: '+61', country: 'AU', name: 'Australia' },
    { code: '+81', country: 'JP', name: 'Japan' },
    { code: '+86', country: 'CN', name: 'China' },
    { code: '+91', country: 'IN', name: 'India' },
    { code: '+234', country: 'NG', name: 'Nigeria' },
    { code: '+27', country: 'ZA', name: 'South Africa' },
    { code: '+55', country: 'BR', name: 'Brazil' },
    { code: '+52', country: 'MX', name: 'Mexico' }
  ];
  
  return (
    <div className="smart-phone-input-wrapper">
      <div className="smart-phone-input-container">
        <select 
          className="country-code-select"
          value={countryCode}
          onChange={handleCountryChange}
        >
          {countryCodes.map((country, index) => (
            <option key={index} value={country.code}>
              {country.code} {country.country}
            </option>
          ))}
        </select>
        
        <div className="smart-input-container">
          <input
            type="tel"
            name={name}
            value={inputValue}
            onChange={handleInputChange}
            placeholder={placeholder}
            className={inputClassName}
            required={required}
            {...props}
          />
          
          {isValidating && (
            <div className="smart-input-spinner">
              <div className="spinner"></div>
            </div>
          )}
          
          {validationState?.isValid && (
            <div className="smart-input-checkmark">✓</div>
          )}
        </div>
      </div>
      
      {detectedCountry && (
        <div className="detected-country-hint">
          📍 Detected location: {detectedCountry.name}
        </div>
      )}
      
      {/* Error Messages */}
      {hasErrors && (
        <div className="smart-input-errors">
          {validationState.errors.map((error, index) => (
            <div key={index} className="smart-input-error">
              {error}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SmartPhoneInput;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        component_file = components_dir / "SmartPhoneInput.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for smart phone input
        css_content = """.smart-phone-input-wrapper {
  position: relative;
  width: 100%;
}

.smart-phone-input-container {
  display: flex;
  gap: 8px;
}

.country-code-select {
  min-width: 80px;
  padding: 12px 8px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  background-color: #fff;
  cursor: pointer;
}

.country-code-select:focus {
  outline: none;
  border-color: var(--primary-color, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.smart-phone-input {
  flex: 1;
  padding: 12px 40px 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
  background-color: #fff;
}

.smart-phone-input:focus {
  outline: none;
  border-color: var(--primary-color, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.smart-phone-input--valid {
  border-color: var(--success-color, #10b981);
}

.smart-phone-input--error {
  border-color: var(--danger-color, #ef4444);
}

.detected-country-hint {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
  padding: 4px 8px;
  background-color: #f0f9ff;
  border-radius: 4px;
  border-left: 3px solid var(--primary-color, #3b82f6);
}

@media (max-width: 768px) {
  .smart-phone-input-container {
    flex-direction: column;
  }
  
  .country-code-select {
    width: 100%;
  }
}
"""
        
        css_file = components_dir / "SmartPhoneInput.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_smart_password_input(self):
        """Generate smart password input with strength meter and breach checking"""
        
        template = Template("""import React, { useState, useEffect, useCallback } from 'react';
import { useSmartValidation } from '../hooks/useSmartValidation';
import { calculatePasswordStrength, debounce } from '../utils/formUtils';
import './SmartPasswordInput.css';

const SmartPasswordInput = ({
  name,
  value = '',
  onChange,
  onValidationChange,
  placeholder = 'Enter your password',
  required = false,
  showStrengthMeter = true,
  checkBreaches = true,
  minStrength = 3,
  showToggle = true,
  className = '',
  ...props
}) => {
  const [inputValue, setInputValue] = useState(value);
  const [showPassword, setShowPassword] = useState(false);
  const [strengthScore, setStrengthScore] = useState(0);
  const [strengthText, setStrengthText] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [breachWarning, setBreachWarning] = useState('');
  
  const { validation, validateField } = useSmartValidation();
  
  const debouncedValidate = useCallback(
    debounce(async (password) => {
      if (!password) {
        onValidationChange?.({ isValid: !required, errors: [] });
        setStrengthScore(0);
        setStrengthText('');
        setBreachWarning('');
        return;
      }
      
      // Calculate password strength
      const strength = calculatePasswordStrength(password);
      setStrengthScore(strength.score);
      setStrengthText(strength.text);
      
      setIsValidating(true);
      try {
        const result = await validateField('password', password, {
          minStrength,
          checkBreaches
        });
        
        if (result.breach_detected) {
          setBreachWarning('This password has been found in data breaches. Please choose a different one.');
        } else {
          setBreachWarning('');
        }
        
        onValidationChange?.(result);
      } catch (error) {
        console.error('Password validation failed:', error);
        onValidationChange?.({ isValid: false, errors: ['Validation failed'] });
      } finally {
        setIsValidating(false);
      }
    }, 300),
    [validateField, minStrength, checkBreaches, required, onValidationChange]
  );
  
  useEffect(() => {
    debouncedValidate(inputValue);
  }, [inputValue, debouncedValidate]);
  
  const handleInputChange = (e) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    onChange?.(e);
  };
  
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  
  const validationState = validation[name];
  const hasErrors = validationState && !validationState.isValid;
  const inputClassName = `smart-password-input ${
    hasErrors ? 'smart-password-input--error' : 
    validationState?.isValid ? 'smart-password-input--valid' : ''
  } ${className}`.trim();
  
  const getStrengthColor = (score) => {
    if (score <= 1) return '#ef4444'; // red
    if (score <= 2) return '#f59e0b'; // yellow
    if (score <= 3) return '#3b82f6'; // blue
    return '#10b981'; // green
  };
  
  const getStrengthLabel = (score) => {
    if (score <= 1) return 'Weak';
    if (score <= 2) return 'Fair';
    if (score <= 3) return 'Good';
    return 'Strong';
  };
  
  return (
    <div className="smart-password-input-wrapper">
      <div className="smart-input-container">
        <input
          type={showPassword ? 'text' : 'password'}
          name={name}
          value={inputValue}
          onChange={handleInputChange}
          placeholder={placeholder}
          className={inputClassName}
          required={required}
          {...props}
        />
        
        {showToggle && (
          <button
            type="button"
            className="password-toggle-btn"
            onClick={togglePasswordVisibility}
            tabIndex={-1}
          >
            {showPassword ? '🙈' : '👁️'}
          </button>
        )}
        
        {isValidating && (
          <div className="smart-input-spinner">
            <div className="spinner"></div>
          </div>
        )}
        
        {validationState?.isValid && !isValidating && (
          <div className="smart-input-checkmark">✓</div>
        )}
      </div>
      
      {/* Password Strength Meter */}
      {showStrengthMeter && inputValue && (
        <div className="password-strength-meter">
          <div className="strength-bar-container">
            <div 
              className="strength-bar"
              style={{
                width: `${(strengthScore / 4) * 100}%`,
                backgroundColor: getStrengthColor(strengthScore)
              }}
            />
          </div>
          <div className="strength-text">
            <span 
              className="strength-label"
              style={{ color: getStrengthColor(strengthScore) }}
            >
              {getStrengthLabel(strengthScore)}
            </span>
            <span className="strength-description">{strengthText}</span>
          </div>
        </div>
      )}
      
      {/* Breach Warning */}
      {breachWarning && (
        <div className="breach-warning">
          ⚠️ {breachWarning}
        </div>
      )}
      
      {/* Error Messages */}
      {hasErrors && (
        <div className="smart-input-errors">
          {validationState.errors.map((error, index) => (
            <div key={index} className="smart-input-error">
              {error}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SmartPasswordInput;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        component_file = components_dir / "SmartPasswordInput.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for smart password input
        css_content = """.smart-password-input-wrapper {
  position: relative;
  width: 100%;
}

.smart-password-input {
  width: 100%;
  padding: 12px 80px 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
  background-color: #fff;
}

.smart-password-input:focus {
  outline: none;
  border-color: var(--primary-color, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.smart-password-input--valid {
  border-color: var(--success-color, #10b981);
}

.smart-password-input--error {
  border-color: var(--danger-color, #ef4444);
}

.password-toggle-btn {
  position: absolute;
  right: 40px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.password-toggle-btn:hover {
  background-color: #f3f4f6;
}

.password-strength-meter {
  margin-top: 8px;
}

.strength-bar-container {
  width: 100%;
  height: 6px;
  background-color: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.strength-bar {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 3px;
}

.strength-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
  font-size: 12px;
}

.strength-label {
  font-weight: 600;
}

.strength-description {
  color: #6b7280;
}

.breach-warning {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #fef3c7;
  color: #92400e;
  border-radius: 6px;
  font-size: 14px;
  border-left: 4px solid #f59e0b;
}

/* Responsive */
@media (max-width: 768px) {
  .smart-password-input {
    padding: 12px 70px 12px 12px;
  }
  
  .password-toggle-btn {
    right: 35px;
  }
}
"""
        
        css_file = components_dir / "SmartPasswordInput.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_smart_otp_input(self):
        """Generate smart OTP input with auto-detection and auto-fill"""
        
        # For brevity, implementing a basic OTP component
        template = Template("""import React, { useState, useEffect, useRef } from 'react';
import './SmartOtpInput.css';

const SmartOtpInput = ({
  name,
  length = 6,
  onChange,
  onComplete,
  autoFill = true,
  placeholder = '',
  className = '',
  ...props
}) => {
  const [values, setValues] = useState(Array(length).fill(''));
  const inputs = useRef([]);
  
  useEffect(() => {
    if (autoFill && 'OTPCredential' in window) {
      navigator.credentials.get({
        otp: { transport: ['sms'] }
      }).then(otp => {
        if (otp) {
          const code = otp.code;
          const newValues = code.split('').slice(0, length);
          setValues(newValues);
          onComplete?.(code);
        }
      }).catch(console.error);
    }
  }, [autoFill, length, onComplete]);
  
  const handleChange = (index, value) => {
    if (value.length > 1) {
      // Handle paste
      const pastedValues = value.split('').slice(0, length);
      setValues(pastedValues);
      if (pastedValues.length === length) {
        onComplete?.(pastedValues.join(''));
      }
      return;
    }
    
    const newValues = [...values];
    newValues[index] = value;
    setValues(newValues);
    
    onChange?.({ target: { name, value: newValues.join('') } });
    
    if (value && index < length - 1) {
      inputs.current[index + 1]?.focus();
    }
    
    if (newValues.every(v => v !== '') && newValues.length === length) {
      onComplete?.(newValues.join(''));
    }
  };
  
  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !values[index] && index > 0) {
      inputs.current[index - 1]?.focus();
    }
  };
  
  return (
    <div className={`smart-otp-input ${className}`}>
      {Array(length).fill(0).map((_, index) => (
        <input
          key={index}
          ref={el => inputs.current[index] = el}
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={length}
          value={values[index]}
          onChange={(e) => handleChange(index, e.target.value)}
          onKeyDown={(e) => handleKeyDown(index, e)}
          placeholder={placeholder}
          className="otp-digit"
          {...props}
        />
      ))}
    </div>
  );
};

export default SmartOtpInput;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        component_file = components_dir / "SmartOtpInput.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for OTP input
        css_content = """.smart-otp-input {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.otp-digit {
  width: 50px;
  height: 50px;
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  background-color: #fff;
  transition: all 0.2s ease;
}

.otp-digit:focus {
  outline: none;
  border-color: var(--primary-color, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

@media (max-width: 768px) {
  .otp-digit {
    width: 40px;
    height: 40px;
    font-size: 18px;
  }
}
"""
        
        css_file = components_dir / "SmartOtpInput.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_smart_credit_card_input(self):
        """Generate smart credit card input with auto-formatting and validation"""
        pass  # Implementing placeholder for now
    
    def _generate_smart_search_input(self):
        """Generate smart search input with autocomplete and typo tolerance"""
        
        template = Template("""import React, { useState, useEffect, useCallback, useRef } from 'react';
import SmartFormService from '../services/smartFormService';
import { debounce } from '../utils/formUtils';
import './SmartSearchInput.css';

const SmartSearchInput = ({
  name,
  value = '',
  onChange,
  onSelect,
  placeholder = 'Search...',
  searchType = 'general',
  minChars = 2,
  maxSuggestions = 10,
  showTypoTolerance = true,
  showRecentSearches = true,
  contextFilters = {},
  customDataSource,
  className = '',
  ...props
}) => {
  const [inputValue, setInputValue] = useState(value);
  const [suggestions, setSuggestions] = useState([]);
  const [recentSearches, setRecentSearches] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [hasTypo, setHasTypo] = useState(false);
  
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);
  
  // Load recent searches on mount
  useEffect(() => {
    if (showRecentSearches) {
      const recent = JSON.parse(localStorage.getItem(`recent_searches_${searchType}`) || '[]');
      setRecentSearches(recent.slice(0, 5));
    }
  }, [searchType, showRecentSearches]);
  
  // Debounced search function
  const debouncedSearch = useCallback(
    debounce(async (query) => {
      if (!query || query.length < minChars) {
        setSuggestions([]);
        setHasTypo(false);
        return;
      }
      
      setIsLoading(true);
      try {
        let results;
        
        if (customDataSource) {
          results = await customDataSource(query, contextFilters);
        } else {
          const response = await SmartFormService.getAutocompleteSuggestions(
            searchType,
            query,
            {
              maxResults: maxSuggestions,
              contextFilters,
              enableTypoTolerance: showTypoTolerance
            }
          );
          results = response;
        }
        
        setSuggestions(results.suggestions || []);
        setHasTypo(results.hasTypoCorrection || false);
        setShowSuggestions(true);
        setSelectedIndex(-1);
        
      } catch (error) {
        console.error('Search failed:', error);
        setSuggestions([]);
      } finally {
        setIsLoading(false);
      }
    }, 300),
    [searchType, minChars, maxSuggestions, showTypoTolerance, contextFilters, customDataSource]
  );
  
  useEffect(() => {
    debouncedSearch(inputValue);
  }, [inputValue, debouncedSearch]);
  
  const handleInputChange = (e) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    onChange?.(e);
  };
  
  const handleSuggestionSelect = (suggestion, index) => {
    const selectedValue = typeof suggestion === 'string' ? suggestion : suggestion.text || suggestion.title;
    setInputValue(selectedValue);
    setShowSuggestions(false);
    
    // Save to recent searches
    if (showRecentSearches) {
      const recent = JSON.parse(localStorage.getItem(`recent_searches_${searchType}`) || '[]');
      const updated = [selectedValue, ...recent.filter(item => item !== selectedValue)].slice(0, 10);
      localStorage.setItem(`recent_searches_${searchType}`, JSON.stringify(updated));
      setRecentSearches(updated.slice(0, 5));
    }
    
    // Create synthetic event for onChange
    const syntheticEvent = {
      target: { name, value: selectedValue }
    };
    onChange?.(syntheticEvent);
    onSelect?.(suggestion, index);
  };
  
  const handleKeyDown = (e) => {
    if (!showSuggestions) return;
    
    const suggestionsList = [...suggestions];
    if (recentSearches.length > 0 && inputValue.length < minChars) {
      suggestionsList.unshift(...recentSearches.map(search => ({ text: search, type: 'recent' })));
    }
    
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestionsList.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev > 0 ? prev - 1 : suggestionsList.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestionsList.length) {
          handleSuggestionSelect(suggestionsList[selectedIndex], selectedIndex);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };
  
  const handleFocus = () => {
    if (inputValue.length >= minChars || (recentSearches.length > 0 && inputValue.length === 0)) {
      setShowSuggestions(true);
    }
  };
  
  const handleBlur = (e) => {
    // Delay hiding suggestions to allow for clicks
    setTimeout(() => {
      if (!suggestionsRef.current?.contains(document.activeElement)) {
        setShowSuggestions(false);
        setSelectedIndex(-1);
      }
    }, 200);
  };
  
  const renderSuggestion = (suggestion, index) => {
    const isSelected = index === selectedIndex;
    const isRecent = suggestion.type === 'recent';
    const displayText = typeof suggestion === 'string' ? suggestion : 
                       suggestion.text || suggestion.title || suggestion.name;
    const description = suggestion.description || suggestion.subtitle;
    
    return (
      <div
        key={`${isRecent ? 'recent' : 'suggestion'}-${index}`}
        className={`suggestion-item ${
          isSelected ? 'suggestion-item--selected' : ''
        } ${
          isRecent ? 'suggestion-item--recent' : ''
        }`}
        onClick={() => handleSuggestionSelect(suggestion, index)}
        onMouseEnter={() => setSelectedIndex(index)}
      >
        <div className="suggestion-content">
          {isRecent && <span className="recent-icon">🕰️</span>}
          <div className="suggestion-text">
            <div className="suggestion-title">{displayText}</div>
            {description && (
              <div className="suggestion-description">{description}</div>
            )}
          </div>
          {suggestion.category && (
            <span className="suggestion-category">{suggestion.category}</span>
          )}
        </div>
      </div>
    );
  };
  
  // Combine suggestions with recent searches if applicable
  const getSuggestionsList = () => {
    let allSuggestions = [...suggestions];
    
    // Show recent searches when input is empty or very short
    if (inputValue.length < minChars && recentSearches.length > 0) {
      const recentItems = recentSearches.map(search => ({ text: search, type: 'recent' }));
      allSuggestions = [...recentItems, ...allSuggestions];
    }
    
    return allSuggestions.slice(0, maxSuggestions);
  };
  
  const suggestionsList = getSuggestionsList();
  
  return (
    <div className={`smart-search-input-wrapper ${className}`}>
      <div className="smart-search-input-container">
        <input
          ref={inputRef}
          type="text"
          name={name}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          className="smart-search-input"
          autoComplete="off"
          {...props}
        />
        
        <div className="search-input-indicators">
          {isLoading && (
            <div className="search-spinner">
              <div className="spinner"></div>
            </div>
          )}
          
          {hasTypo && !isLoading && (
            <div className="typo-indicator" title="Showing results with typo correction">
              🔍
            </div>
          )}
        </div>
      </div>
      
      {/* Suggestions Dropdown */}
      {showSuggestions && suggestionsList.length > 0 && (
        <div ref={suggestionsRef} className="search-suggestions">
          {inputValue.length < minChars && recentSearches.length > 0 && (
            <div className="suggestions-header">
              <span>Recent Searches</span>
              <button 
                type="button" 
                className="clear-recent-btn"
                onClick={() => {
                  localStorage.removeItem(`recent_searches_${searchType}`);
                  setRecentSearches([]);
                }}
              >
                Clear
              </button>
            </div>
          )}
          
          {suggestionsList.map((suggestion, index) => 
            renderSuggestion(suggestion, index)
          )}
          
          {hasTypo && (
            <div className="typo-notice">
              Results include corrections for possible typos
            </div>
          )}
        </div>
      )}
      
      {/* No Results */}
      {showSuggestions && suggestionsList.length === 0 && !isLoading && inputValue.length >= minChars && (
        <div className="search-suggestions">
          <div className="no-results">
            No results found for \"{inputValue}\"
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartSearchInput;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        component_file = components_dir / "SmartSearchInput.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for smart search input
        css_content = """.smart-search-input-wrapper {
  position: relative;
  width: 100%;
}

.smart-search-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.smart-search-input {
  width: 100%;
  padding: 12px 50px 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
  background-color: #fff;
}

.smart-search-input:focus {
  outline: none;
  border-color: var(--primary-color, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-input-indicators {
  position: absolute;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-spinner {
  display: flex;
  align-items: center;
}

.typo-indicator {
  font-size: 14px;
  opacity: 0.7;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  margin-top: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  font-size: 12px;
  color: #6b7280;
  border-bottom: 1px solid #e1e5e9;
  background-color: #f9fafb;
}

.clear-recent-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 3px;
  transition: background-color 0.2s ease;
}

.clear-recent-btn:hover {
  background-color: #e5e7eb;
}

.suggestion-item {
  padding: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #f3f4f6;
}

.suggestion-item:hover,
.suggestion-item--selected {
  background-color: #f8fafc;
}

.suggestion-item--recent {
  background-color: #fefce8;
}

.suggestion-item--recent:hover,
.suggestion-item--recent.suggestion-item--selected {
  background-color: #fef3c7;
}

.suggestion-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recent-icon {
  font-size: 14px;
  opacity: 0.6;
}

.suggestion-text {
  flex: 1;
}

.suggestion-title {
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
}

.suggestion-description {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.suggestion-category {
  font-size: 11px;
  padding: 2px 6px;
  background-color: #e5e7eb;
  color: #4b5563;
  border-radius: 12px;
  font-weight: 500;
}

.typo-notice {
  padding: 8px 12px;
  font-size: 11px;
  color: #6b7280;
  text-align: center;
  background-color: #fef3c7;
  border-top: 1px solid #e1e5e9;
}

.no-results {
  padding: 16px;
  text-align: center;
  color: #6b7280;
  font-style: italic;
}

/* Scrollbar styling */
.search-suggestions::-webkit-scrollbar {
  width: 6px;
}

.search-suggestions::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.search-suggestions::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.search-suggestions::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive */
@media (max-width: 768px) {
  .smart-search-input {
    padding: 10px 45px 10px 12px;
  }
  
  .search-suggestions {
    max-height: 250px;
  }
}
"""
        
        css_file = components_dir / "SmartSearchInput.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_smart_address_input(self):
        """Generate smart address input with geocoding and auto-complete"""
        
        template = Template("""import React, { useState, useEffect, useCallback } from 'react';
import { useSmartValidation } from '../hooks/useSmartValidation';
import { debounce } from '../utils/formUtils';
import './SmartAddressInput.css';

const SmartAddressInput = ({
  name,
  value = {},
  onChange,
  onValidationChange,
  placeholder = 'Enter your address',
  required = false,
  enableGeocoding = true,
  enableAutocomplete = true,
  showMapPreview = false,
  countryRestriction = null,
  className = '',
  ...props
}) => {
  const [addressData, setAddressData] = useState({
    street: '',
    city: '',
    state: '',
    postalCode: '',
    country: '',
    coordinates: null,
    ...value
  });
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isGeocoding, setIsGeocoding] = useState(false);
  const [mapPreviewUrl, setMapPreviewUrl] = useState('');
  
  const { validation, validateField } = useSmartValidation();
  
  // Debounced geocoding function
  const debouncedGeocode = useCallback(
    debounce(async (address) => {
      if (!address || !enableGeocoding) return;
      
      setIsGeocoding(true);
      try {
        const response = await fetch('/api/geocoding/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            address,
            countryRestriction
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          
          if (data.suggestions && data.suggestions.length > 0) {
            setSuggestions(data.suggestions);
            setShowSuggestions(true);
          }
          
          // Update coordinates if we have a precise match
          if (data.coordinates) {
            setAddressData(prev => ({
              ...prev,
              coordinates: data.coordinates
            }));
            
            // Generate map preview URL
            if (showMapPreview) {
              const mapUrl = `https://maps.googleapis.com/maps/api/staticmap?center=${data.coordinates.lat},${data.coordinates.lng}&zoom=15&size=300x200&markers=${data.coordinates.lat},${data.coordinates.lng}&key=YOUR_API_KEY`;
              setMapPreviewUrl(mapUrl);
            }
          }
        }
      } catch (error) {
        console.error('Geocoding failed:', error);
      } finally {
        setIsGeocoding(false);
      }
    }, 500),
    [enableGeocoding, countryRestriction, showMapPreview]
  );
  
  const handleFieldChange = (field, newValue) => {
    const updatedAddress = {
      ...addressData,
      [field]: newValue
    };
    
    setAddressData(updatedAddress);
    
    // Trigger onChange with full address object
    const syntheticEvent = {
      target: { name, value: updatedAddress }
    };
    onChange?.(syntheticEvent);
    
    // Trigger geocoding for street address changes
    if (field === 'street' && enableAutocomplete) {
      const fullAddress = `${newValue}, ${updatedAddress.city}, ${updatedAddress.state} ${updatedAddress.postalCode}, ${updatedAddress.country}`.trim();
      debouncedGeocode(fullAddress);
    }
  };
  
  const handleSuggestionSelect = (suggestion) => {
    const updatedAddress = {
      street: suggestion.street || '',
      city: suggestion.city || '',
      state: suggestion.state || '',
      postalCode: suggestion.postalCode || '',
      country: suggestion.country || '',
      coordinates: suggestion.coordinates || null
    };
    
    setAddressData(updatedAddress);
    setShowSuggestions(false);
    setSuggestions([]);
    
    // Update map preview
    if (showMapPreview && suggestion.coordinates) {
      const mapUrl = `https://maps.googleapis.com/maps/api/staticmap?center=${suggestion.coordinates.lat},${suggestion.coordinates.lng}&zoom=15&size=300x200&markers=${suggestion.coordinates.lat},${suggestion.coordinates.lng}&key=YOUR_API_KEY`;
      setMapPreviewUrl(mapUrl);
    }
    
    const syntheticEvent = {
      target: { name, value: updatedAddress }
    };
    onChange?.(syntheticEvent);
  };
  
  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by this browser.');
      return;
    }
    
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        
        try {
          // Reverse geocode to get address
          const response = await fetch('/api/geocoding/reverse', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              lat: latitude,
              lng: longitude
            })
          });
          
          if (response.ok) {
            const data = await response.json();
            if (data.address) {
              const updatedAddress = {
                ...data.address,
                coordinates: { lat: latitude, lng: longitude }
              };
              
              setAddressData(updatedAddress);
              
              const syntheticEvent = {
                target: { name, value: updatedAddress }
              };
              onChange?.(syntheticEvent);
              
              // Update map preview
              if (showMapPreview) {
                const mapUrl = `https://maps.googleapis.com/maps/api/staticmap?center=${latitude},${longitude}&zoom=15&size=300x200&markers=${latitude},${longitude}&key=YOUR_API_KEY`;
                setMapPreviewUrl(mapUrl);
              }
            }
          }
        } catch (error) {
          console.error('Reverse geocoding failed:', error);
        }
      },
      (error) => {
        console.error('Geolocation error:', error);
        alert('Unable to retrieve your location.');
      }
    );
  };
  
  const validateAddress = async () => {
    if (!required && !addressData.street) {
      onValidationChange?.({ isValid: true, errors: [] });
      return;
    }
    
    try {
      const result = await validateField('address', addressData, {
        required,
        enableGeocoding
      });
      
      onValidationChange?.(result);
    } catch (error) {
      console.error('Address validation failed:', error);
      onValidationChange?.({ isValid: false, errors: ['Address validation failed'] });
    }
  };
  
  // Validate on address change
  useEffect(() => {
    validateAddress();
  }, [addressData]);
  
  const validationState = validation[name];
  const hasErrors = validationState && !validationState.isValid;
  
  return (
    <div className={`smart-address-input-wrapper ${className}`}>
      <div className="address-input-header">
        <label className={`address-label ${required ? 'required' : ''}`}>
          Address {required && <span className="required-star">*</span>}
        </label>
        
        <button
          type="button"
          className="location-btn"
          onClick={getCurrentLocation}
          title="Use current location"
        >
          📍 Current Location
        </button>
      </div>
      
      <div className="address-fields">
        {/* Street Address */}
        <div className="address-field-group">
          <input
            type="text"
            value={addressData.street}
            onChange={(e) => handleFieldChange('street', e.target.value)}
            placeholder="Street address"
            className={`address-input ${hasErrors ? 'address-input--error' : ''}`}
          />
          
          {isGeocoding && (
            <div className="geocoding-spinner">
              <div className="spinner"></div>
            </div>
          )}
        </div>
        
        {/* City, State, Postal Code */}
        <div className="address-row">
          <input
            type="text"
            value={addressData.city}
            onChange={(e) => handleFieldChange('city', e.target.value)}
            placeholder="City"
            className="address-input city-input"
          />
          
          <input
            type="text"
            value={addressData.state}
            onChange={(e) => handleFieldChange('state', e.target.value)}
            placeholder="State/Province"
            className="address-input state-input"
          />
          
          <input
            type="text"
            value={addressData.postalCode}
            onChange={(e) => handleFieldChange('postalCode', e.target.value)}
            placeholder="Postal Code"
            className="address-input postal-input"
          />
        </div>
        
        {/* Country */}
        <input
          type="text"
          value={addressData.country}
          onChange={(e) => handleFieldChange('country', e.target.value)}
          placeholder="Country"
          className="address-input country-input"
        />
      </div>
      
      {/* Address Suggestions */}
      {showSuggestions && suggestions.length > 0 && enableAutocomplete && (
        <div className="address-suggestions">
          <div className="suggestions-header">Suggested addresses:</div>
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              type="button"
              className="address-suggestion"
              onClick={() => handleSuggestionSelect(suggestion)}
            >
              <div className="suggestion-address">
                {suggestion.formattedAddress || 
                 `${suggestion.street}, ${suggestion.city}, ${suggestion.state} ${suggestion.postalCode}`
                }
              </div>
              {suggestion.placeType && (
                <div className="suggestion-type">{suggestion.placeType}</div>
              )}
            </button>
          ))}
        </div>
      )}
      
      {/* Map Preview */}
      {showMapPreview && mapPreviewUrl && (
        <div className="map-preview">
          <img src={mapPreviewUrl} alt="Address location" className="map-image" />
        </div>
      )}
      
      {/* Coordinates Display */}
      {addressData.coordinates && (
        <div className="coordinates-display">
          📍 {addressData.coordinates.lat.toFixed(6)}, {addressData.coordinates.lng.toFixed(6)}
        </div>
      )}
      
      {/* Error Messages */}
      {hasErrors && (
        <div className="address-errors">
          {validationState.errors.map((error, index) => (
            <div key={index} className="address-error">
              {error}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SmartAddressInput;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        component_file = components_dir / "SmartAddressInput.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for smart address input
        css_content = """.smart-address-input-wrapper {
  width: 100%;
  position: relative;
}

.address-input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.address-label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.address-label.required {
  color: #1f2937;
}

.required-star {
  color: #ef4444;
  margin-left: 2px;
}

.location-btn {
  background: none;
  border: 1px solid #d1d5db;
  color: #6b7280;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.location-btn:hover {
  background-color: #f9fafb;
  border-color: #9ca3af;
  color: #374151;
}

.address-fields {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.address-field-group {
  position: relative;
}

.address-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
  background-color: #fff;
}

.address-input:focus {
  outline: none;
  border-color: var(--primary-color, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.address-input--error {
  border-color: var(--danger-color, #ef4444);
}

.address-row {
  display: grid;
  grid-template-columns: 1fr 1fr 120px;
  gap: 12px;
}

.geocoding-spinner {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
}

.address-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  margin-top: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.suggestions-header {
  padding: 8px 12px;
  font-size: 12px;
  color: #6b7280;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
  font-weight: 600;
}

.address-suggestion {
  display: block;
  width: 100%;
  padding: 12px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #f3f4f6;
}

.address-suggestion:hover {
  background-color: #f8fafc;
}

.suggestion-address {
  font-size: 14px;
  color: #1f2937;
  margin-bottom: 2px;
}

.suggestion-type {
  font-size: 12px;
  color: #6b7280;
  font-style: italic;
}

.map-preview {
  margin-top: 16px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.map-image {
  width: 100%;
  height: auto;
  display: block;
}

.coordinates-display {
  margin-top: 8px;
  font-size: 12px;
  color: #6b7280;
  background-color: #f0f9ff;
  padding: 6px 12px;
  border-radius: 6px;
  border-left: 3px solid var(--primary-color, #3b82f6);
}

.address-errors {
  margin-top: 8px;
}

.address-error {
  color: var(--danger-color, #ef4444);
  font-size: 14px;
  margin-bottom: 4px;
}

/* Responsive */
@media (max-width: 768px) {
  .address-input-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .location-btn {
    align-self: flex-end;
  }
  
  .address-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .address-input {
    padding: 10px 12px;
  }
}
"""
        
        css_file = components_dir / "SmartAddressInput.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_smart_address_input(self):
        """Generate smart address input with geocoding"""
        pass  # Implementing placeholder for now
    
    def _generate_form_validation_hooks(self):
        """Generate React hooks for smart form validation"""
        
        # Generate useSmartValidation hook
        template = Template("""import { useState, useCallback } from 'react';
import SmartFormService from '../services/smartFormService';

export const useSmartValidation = () => {
  const [validation, setValidation] = useState({});
  const [isValidating, setIsValidating] = useState(false);
  
  const validateField = useCallback(async (fieldType, value, options = {}) => {
    setIsValidating(true);
    
    try {
      const result = await SmartFormService.validateField(fieldType, value, options);
      
      setValidation(prev => ({
        ...prev,
        [options.fieldName || fieldType]: result
      }));
      
      return result;
    } catch (error) {
      const errorResult = {
        isValid: false,
        errors: [error.message || 'Validation failed'],
        suggestions: []
      };
      
      setValidation(prev => ({
        ...prev,
        [options.fieldName || fieldType]: errorResult
      }));
      
      throw error;
    } finally {
      setIsValidating(false);
    }
  }, []);
  
  const validateForm = useCallback(async (formData, fieldConfigs) => {
    setIsValidating(true);
    const results = {};
    
    try {
      const promises = Object.entries(formData).map(async ([fieldName, value]) => {
        const config = fieldConfigs[fieldName] || {};
        if (config.type && value) {
          const result = await SmartFormService.validateField(
            config.type, 
            value, 
            { ...config, fieldName }
          );
          results[fieldName] = result;
        }
      });
      
      await Promise.all(promises);
      setValidation(results);
      
      const isFormValid = Object.values(results).every(result => result.isValid);
      return { isValid: isFormValid, fieldResults: results };
    } catch (error) {
      throw error;
    } finally {
      setIsValidating(false);
    }
  }, []);
  
  const clearValidation = useCallback((fieldName) => {
    if (fieldName) {
      setValidation(prev => {
        const newValidation = { ...prev };
        delete newValidation[fieldName];
        return newValidation;
      });
    } else {
      setValidation({});
    }
  }, []);
  
  return {
    validation,
    validateField,
    validateForm,
    clearValidation,
    isValidating
  };
};

export const useFormState = (initialState = {}) => {
  const [formData, setFormData] = useState(initialState);
  const [isDirty, setIsDirty] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const updateField = useCallback((name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    setIsDirty(true);
  }, []);
  
  const updateMultipleFields = useCallback((updates) => {
    setFormData(prev => ({ ...prev, ...updates }));
    setIsDirty(true);
  }, []);
  
  const resetForm = useCallback((newState = initialState) => {
    setFormData(newState);
    setIsDirty(false);
    setIsSubmitting(false);
  }, [initialState]);
  
  const handleInputChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    const fieldValue = type === 'checkbox' ? checked : value;
    updateField(name, fieldValue);
  }, [updateField]);
  
  return {
    formData,
    isDirty,
    isSubmitting,
    setIsSubmitting,
    updateField,
    updateMultipleFields,
    resetForm,
    handleInputChange
  };
};
""")
        
        hook_content = template.render()
        
        hooks_dir = self.frontend_path / "src" / "hooks"
        hook_file = hooks_dir / "useSmartValidation.js"
        with open(hook_file, 'w') as f:
            f.write(hook_content)
    
    def _generate_smart_form_service(self):
        """Generate smart form service for API communication"""
        
        template = Template("""class SmartFormService {
  constructor() {
    this.baseURL = '/api';
  }

  async validateField(fieldType, value, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}/smart-forms/validate-field`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          field_type: fieldType,
          value,
          options
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Validation failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Field validation failed:', error);
      throw error;
    }
  }

  async validateForm(formData, fieldConfigs) {
    try {
      const response = await fetch(`${this.baseURL}/smart-forms/validate-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          form_data: formData,
          field_configs: fieldConfigs
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Form validation failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Form validation failed:', error);
      throw error;
    }
  }

  async saveDraft(formId, formData) {
    try {
      const response = await fetch(`${this.baseURL}/smart-forms/save-draft`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          form_id: formId,
          form_data: formData,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save draft');
      }

      return await response.json();
    } catch (error) {
      console.error('Save draft failed:', error);
      throw error;
    }
  }

  async loadDraft(formId) {
    try {
      const response = await fetch(`${this.baseURL}/smart-forms/load-draft/${formId}`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          return null; // No draft found
        }
        throw new Error('Failed to load draft');
      }

      return await response.json();
    } catch (error) {
      console.error('Load draft failed:', error);
      throw error;
    }
  }

  async checkDeviceFingerprint() {
    try {
      const fingerprint = await this.generateDeviceFingerprint();
      
      const response = await fetch(`${this.baseURL}/smart-forms/check-device`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fingerprint })
      });

      if (!response.ok) {
        throw new Error('Device check failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Device fingerprint check failed:', error);
      throw error;
    }
  }

  async generateDeviceFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('Device fingerprint', 2, 2);
    
    const fingerprint = {
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      screenResolution: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      canvas: canvas.toDataURL(),
      plugins: Array.from(navigator.plugins).map(p => p.name).sort(),
      cookieEnabled: navigator.cookieEnabled,
      doNotTrack: navigator.doNotTrack
    };
    
    return btoa(JSON.stringify(fingerprint));
  }

  async getAutocompleteSuggestions(fieldType, query, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}/smart-forms/autocomplete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          field_type: fieldType,
          query,
          options
        })
      });

      if (!response.ok) {
        throw new Error('Autocomplete request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Autocomplete failed:', error);
      return { suggestions: [] };
    }
  }

  getAuthToken() {
    return localStorage.getItem('auth_token');
  }
}

export default new SmartFormService();
""")
        
        service_content = template.render()
        
        services_dir = self.frontend_path / "src" / "services"
        service_file = services_dir / "smartFormService.js"
        with open(service_file, 'w') as f:
            f.write(service_content)
    
    def _generate_form_utilities(self):
        """Generate utility functions for smart forms"""
        
        template = Template("""// Form utility functions

// Debounce function to limit API calls
export const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(null, args), delay);
  };
};

// Phone number formatting
export const formatPhoneNumber = (value, countryCode = '+1') => {
  const cleaned = value.replace(/\D/g, '');
  
  if (countryCode === '+1') {
    // US/Canada format
    if (cleaned.length >= 6) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6, 10)}`;
    } else if (cleaned.length >= 3) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3)}`;
    } else {
      return cleaned;
    }
  }
  
  // Default formatting for other countries
  return cleaned;
};

// Detect country code from geolocation
export const detectCountryCode = async (latitude, longitude) => {
  try {
    const response = await fetch(`/api/geo/reverse-geocode?lat=${latitude}&lng=${longitude}`);
    const data = await response.json();
    return data.country;
  } catch (error) {
    console.error('Country detection failed:', error);
    return null;
  }
};

// Password strength calculation
export const calculatePasswordStrength = (password) => {
  let score = 0;
  let feedback = [];
  
  if (password.length >= 8) {
    score += 1;
  } else {
    feedback.push('At least 8 characters');
  }
  
  if (/[a-z]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Include lowercase letters');
  }
  
  if (/[A-Z]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Include uppercase letters');
  }
  
  if (/\d/.test(password)) {
    score += 1;
  } else {
    feedback.push('Include numbers');
  }
  
  if (/[^\w\s]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Include special characters');
  }
  
  const strengthLabels = {
    0: 'Very Weak',
    1: 'Weak',
    2: 'Fair',
    3: 'Good',
    4: 'Strong',
    5: 'Very Strong'
  };
  
  return {
    score,
    text: strengthLabels[score] || 'Very Weak',
    feedback
  };
};

// Email domain suggestions
export const getEmailSuggestions = (email) => {
  const commonDomains = [
    'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
    'icloud.com', 'aol.com', 'live.com', 'msn.com'
  ];
  
  const [localPart, domain] = email.split('@');
  if (!domain) return [];
  
  const suggestions = [];
  
  // Check for typos in common domains
  commonDomains.forEach(commonDomain => {
    const distance = levenshteinDistance(domain.toLowerCase(), commonDomain);
    if (distance === 1 || distance === 2) {
      suggestions.push(`${localPart}@${commonDomain}`);
    }
  });
  
  return suggestions;
};

// Levenshtein distance for typo detection
const levenshteinDistance = (str1, str2) => {
  const matrix = [];
  
  for (let i = 0; i <= str2.length; i++) {
    matrix[i] = [i];
  }
  
  for (let j = 0; j <= str1.length; j++) {
    matrix[0][j] = j;
  }
  
  for (let i = 1; i <= str2.length; i++) {
    for (let j = 1; j <= str1.length; j++) {
      if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }
  
  return matrix[str2.length][str1.length];
};

// Credit card formatting
export const formatCreditCard = (value) => {
  const cleaned = value.replace(/\D/g, '');
  const match = cleaned.match(/.{1,4}/g);
  return match ? match.join(' ') : '';
};

// Credit card type detection
export const detectCreditCardType = (number) => {
  const patterns = {
    visa: /^4/,
    mastercard: /^5[1-5]/,
    amex: /^3[47]/,
    discover: /^6(?:011|5)/,
  };
  
  for (const [type, pattern] of Object.entries(patterns)) {
    if (pattern.test(number)) {
      return type;
    }
  }
  
  return 'unknown';
};

// Form data serialization
export const serializeFormData = (formElement) => {
  const formData = new FormData(formElement);
  const data = {};
  
  for (const [key, value] of formData.entries()) {
    if (data[key]) {
      // Handle multiple values (checkboxes, multi-select)
      if (Array.isArray(data[key])) {
        data[key].push(value);
      } else {
        data[key] = [data[key], value];
      }
    } else {
      data[key] = value;
    }
  }
  
  return data;
};

// Form validation helpers
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidPhone = (phone, countryCode = '+1') => {
  const cleaned = phone.replace(/\D/g, '');
  
  if (countryCode === '+1') {
    return cleaned.length === 10;
  }
  
  // Basic validation for other countries
  return cleaned.length >= 7 && cleaned.length <= 15;
};

// Local storage helpers for form drafts
export const saveDraftToLocal = (formId, formData) => {
  try {
    const draft = {
      formData,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem(`draft_${formId}`, JSON.stringify(draft));
    return true;
  } catch (error) {
    console.error('Failed to save draft locally:', error);
    return false;
  }
};

export const loadDraftFromLocal = (formId) => {
  try {
    const draft = localStorage.getItem(`draft_${formId}`);
    return draft ? JSON.parse(draft) : null;
  } catch (error) {
    console.error('Failed to load draft locally:', error);
    return null;
  }
};

export const clearLocalDraft = (formId) => {
  try {
    localStorage.removeItem(`draft_${formId}`);
    return true;
  } catch (error) {
    console.error('Failed to clear local draft:', error);
    return false;
  }
};
""")
        
        utils_content = template.render()
        
        utils_dir = self.frontend_path / "src" / "utils"
        utils_file = utils_dir / "formUtils.js"
        with open(utils_file, 'w') as f:
            f.write(utils_content)
    
    def _generate_smart_form_wrapper(self):
        """Generate smart form wrapper component"""
        
        template = Template("""import React, { useState, useEffect, useCallback } from 'react';
import { useSmartValidation, useFormState } from '../hooks/useSmartValidation';
import SmartFormService from '../services/smartFormService';
import { saveDraftToLocal, loadDraftFromLocal, clearLocalDraft } from '../utils/formUtils';
import './SmartForm.css';

const SmartForm = ({
  formId,
  fieldConfigs = {},
  initialData = {},
  onSubmit,
  onValidationChange,
  enableDraftSave = true,
  autoSaveDrafts = true,
  autoSaveInterval = 30000, // 30 seconds
  showProgressIndicator = true,
  validateOnChange = true,
  children,
  className = '',
  ...props
}) => {
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const [lastSaved, setLastSaved] = useState(null);
  const [isAutoSaving, setIsAutoSaving] = useState(false);
  
  const { validation, validateForm, clearValidation, isValidating } = useSmartValidation();
  const { formData, isDirty, isSubmitting, setIsSubmitting, updateField, resetForm, handleInputChange } = useFormState(initialData);
  
  // Load draft on mount
  useEffect(() => {
    if (formId && enableDraftSave) {
      const draft = loadDraftFromLocal(formId);
      if (draft && draft.formData) {
        resetForm(draft.formData);
        setLastSaved(new Date(draft.timestamp));
      }
    }
  }, [formId, enableDraftSave, resetForm]);
  
  // Auto-save drafts
  useEffect(() => {
    if (!autoSaveDrafts || !formId || !isDirty) return;
    
    const interval = setInterval(async () => {
      setIsAutoSaving(true);
      try {
        // Try server save first, fallback to local
        try {
          await SmartFormService.saveDraft(formId, formData);
        } catch {
          saveDraftToLocal(formId, formData);
        }
        setLastSaved(new Date());
      } catch (error) {
        console.error('Auto-save failed:', error);
      } finally {
        setIsAutoSaving(false);
      }
    }, autoSaveInterval);
    
    return () => clearInterval(interval);
  }, [autoSaveDrafts, formId, formData, isDirty, autoSaveInterval]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitAttempted(true);
    setIsSubmitting(true);
    
    try {
      // Validate entire form
      const validationResult = await validateForm(formData, fieldConfigs);
      
      if (!validationResult.isValid) {
        onValidationChange?.(validationResult);
        return;
      }
      
      // Submit form
      await onSubmit?.(formData);
      
      // Clear draft after successful submit
      if (formId && enableDraftSave) {
        clearLocalDraft(formId);
      }
      
      // Reset form state
      resetForm();
      setSubmitAttempted(false);
      clearValidation();
      
    } catch (error) {
      console.error('Form submission failed:', error);
      throw error;
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleFieldChange = useCallback(async (e) => {
    const { name, value } = e.target;
    handleInputChange(e);
    
    // Real-time validation if enabled
    if (validateOnChange && fieldConfigs[name]) {
      try {
        await SmartFormService.validateField(
          fieldConfigs[name].type,
          value,
          { ...fieldConfigs[name], fieldName: name }
        );
      } catch (error) {
        console.error('Field validation failed:', error);
      }
    }
  }, [handleInputChange, validateOnChange, fieldConfigs]);
  
  const isFormValid = () => {
    if (!submitAttempted) return true;
    return Object.values(validation).every(result => result.isValid);
  };
  
  const getProgressPercentage = () => {
    const requiredFields = Object.entries(fieldConfigs)
      .filter(([_, config]) => config.required)
      .map(([name, _]) => name);
    
    if (requiredFields.length === 0) return 100;
    
    const filledRequired = requiredFields.filter(field => 
      formData[field] && formData[field].toString().trim() !== ''
    ).length;
    
    return Math.round((filledRequired / requiredFields.length) * 100);
  };
  
  const cloneChildrenWithProps = (children) => {
    return React.Children.map(children, (child) => {
      if (!React.isValidElement(child)) return child;
      
      // Clone smart form inputs with additional props
      if (child.props.name && fieldConfigs[child.props.name]) {
        return React.cloneElement(child, {
          value: formData[child.props.name] || '',
          onChange: handleFieldChange,
          onValidationChange: (result) => {
            // Update validation state for this field
          },
          ...child.props
        });
      }
      
      // Recursively clone children
      if (child.props.children) {
        return React.cloneElement(child, {
          children: cloneChildrenWithProps(child.props.children)
        });
      }
      
      return child;
    });
  };
  
  return (
    <div className={`smart-form-wrapper ${className}`}>
      {showProgressIndicator && (
        <div className="form-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${getProgressPercentage()}%` }}
            />
          </div>
          <span className="progress-text">
            {getProgressPercentage()}% Complete
          </span>
        </div>
      )}
      
      <form className="smart-form" onSubmit={handleSubmit} {...props}>
        {cloneChildrenWithProps(children)}
        
        <div className="form-actions">
          <button 
            type="submit" 
            disabled={isSubmitting || isValidating || (!isFormValid() && submitAttempted)}
            className={`submit-btn ${
              isSubmitting ? 'submit-btn--loading' : 
              !isFormValid() && submitAttempted ? 'submit-btn--error' : ''
            }`}
          >
            {isSubmitting ? 'Submitting...' : 'Submit'}
          </button>
          
          {enableDraftSave && (
            <div className="draft-status">
              {isAutoSaving && <span className="saving">Saving...</span>}
              {lastSaved && !isAutoSaving && (
                <span className="last-saved">
                  Last saved: {lastSaved.toLocaleTimeString()}
                </span>
              )}
            </div>
          )}
        </div>
      </form>
    </div>
  );
};

export default SmartForm;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        component_file = components_dir / "SmartForm.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for smart form
        css_content = """.smart-form-wrapper {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.form-progress {
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--primary-color, #3b82f6);
  transition: width 0.3s ease;
}

.progress-text {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
  text-align: right;
}

.smart-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.submit-btn {
  padding: 12px 24px;
  background-color: var(--primary-color, #3b82f6);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
}

.submit-btn:hover {
  background-color: var(--primary-color-dark, #2563eb);
  transform: translateY(-1px);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.submit-btn--loading {
  background-color: #6b7280;
}

.submit-btn--error {
  background-color: var(--danger-color, #ef4444);
}

.draft-status {
  font-size: 14px;
  color: #6b7280;
}

.saving {
  color: var(--warning-color, #f59e0b);
}

.last-saved {
  color: var(--success-color, #10b981);
}

/* Responsive */
@media (max-width: 768px) {
  .smart-form-wrapper {
    padding: 16px;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .submit-btn {
    width: 100%;
  }
}
"""
        
        css_file = components_dir / "SmartForm.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_ux_helper_components(self):
        """Generate UX helper components for better user experience"""
        
        # Generate tooltip component
        self._generate_tooltip_component()
        
        # Generate progressive disclosure component
        self._generate_progressive_disclosure_component()
        
        # Generate session timeout warning component
        self._generate_session_timeout_component()
        
        # Generate quick login component
        self._generate_quick_login_component()
        
        # Generate help panel component
        self._generate_help_panel_component()
    
    def _generate_tooltip_component(self):
        """Generate tooltip component for inline help"""
        
        template = Template("""import React, { useState, useRef, useEffect } from 'react';
import './Tooltip.css';

const Tooltip = ({
  children,
  content,
  placement = 'top',
  trigger = 'hover',
  delay = 500,
  maxWidth = 250,
  className = '',
  disabled = false
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef(null);
  const tooltipRef = useRef(null);
  const timeoutRef = useRef(null);
  
  const showTooltip = () => {
    if (disabled) return;
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
      calculatePosition();
    }, trigger === 'hover' ? delay : 0);
  };
  
  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };
  
  const calculatePosition = () => {
    if (!triggerRef.current || !tooltipRef.current) return;
    
    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    let top, left;
    
    switch (placement) {
      case 'top':
        top = triggerRect.top - tooltipRect.height - 8;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case 'bottom':
        top = triggerRect.bottom + 8;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case 'left':
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.left - tooltipRect.width - 8;
        break;
      case 'right':
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.right + 8;
        break;
      default:
        top = triggerRect.top - tooltipRect.height - 8;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
    }
    
    // Keep tooltip within viewport
    if (left < 8) left = 8;
    if (left + tooltipRect.width > viewportWidth - 8) {
      left = viewportWidth - tooltipRect.width - 8;
    }
    if (top < 8) top = 8;
    if (top + tooltipRect.height > viewportHeight - 8) {
      top = viewportHeight - tooltipRect.height - 8;
    }
    
    setPosition({ top, left });
  };
  
  useEffect(() => {
    if (isVisible) {
      calculatePosition();
      window.addEventListener('scroll', calculatePosition);
      window.addEventListener('resize', calculatePosition);
      
      return () => {
        window.removeEventListener('scroll', calculatePosition);
        window.removeEventListener('resize', calculatePosition);
      };
    }
  }, [isVisible]);
  
  const handleTriggerEvent = (eventType) => {
    if (trigger === 'hover') {
      if (eventType === 'mouseenter') showTooltip();
      if (eventType === 'mouseleave') hideTooltip();
    } else if (trigger === 'click') {
      if (eventType === 'click') {
        isVisible ? hideTooltip() : showTooltip();
      }
    } else if (trigger === 'focus') {
      if (eventType === 'focus') showTooltip();
      if (eventType === 'blur') hideTooltip();
    }
  };
  
  return (
    <>
      <span
        ref={triggerRef}
        className={`tooltip-trigger ${className}`}
        onMouseEnter={() => handleTriggerEvent('mouseenter')}
        onMouseLeave={() => handleTriggerEvent('mouseleave')}
        onClick={() => handleTriggerEvent('click')}
        onFocus={() => handleTriggerEvent('focus')}
        onBlur={() => handleTriggerEvent('blur')}
      >
        {children}
      </span>
      
      {isVisible && (
        <div
          ref={tooltipRef}
          className={`tooltip tooltip--${placement}`}
          style={{
            position: 'fixed',
            top: position.top,
            left: position.left,
            maxWidth: maxWidth,
            zIndex: 9999
          }}
        >
          <div className="tooltip-content">
            {typeof content === 'string' ? (
              <span dangerouslySetInnerHTML={{ __html: content }} />
            ) : (
              content
            )}
          </div>
          <div className="tooltip-arrow" />
        </div>
      )}
    </>
  );
};

export default Tooltip;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        component_file = components_dir / "Tooltip.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for tooltip
        css_content = """.tooltip-trigger {
  display: inline-block;
  cursor: help;
}

.tooltip {
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.4;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  pointer-events: none;
  opacity: 0;
  animation: tooltipFadeIn 0.2s ease-out forwards;
}

.tooltip-content {
  position: relative;
  z-index: 1;
}

.tooltip-arrow {
  position: absolute;
  width: 0;
  height: 0;
  border: 6px solid transparent;
}

.tooltip--top .tooltip-arrow {
  bottom: -12px;
  left: 50%;
  transform: translateX(-50%);
  border-top-color: rgba(0, 0, 0, 0.9);
}

.tooltip--bottom .tooltip-arrow {
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  border-bottom-color: rgba(0, 0, 0, 0.9);
}

.tooltip--left .tooltip-arrow {
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  border-left-color: rgba(0, 0, 0, 0.9);
}

.tooltip--right .tooltip-arrow {
  left: -12px;
  top: 50%;
  transform: translateY(-50%);
  border-right-color: rgba(0, 0, 0, 0.9);
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Light theme variant */
.tooltip--light {
  background: white;
  color: #374151;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tooltip--light.tooltip--top .tooltip-arrow {
  border-top-color: white;
}

.tooltip--light.tooltip--bottom .tooltip-arrow {
  border-bottom-color: white;
}

.tooltip--light.tooltip--left .tooltip-arrow {
  border-left-color: white;
}

.tooltip--light.tooltip--right .tooltip-arrow {
  border-right-color: white;
}
"""
        
        css_file = components_dir / "Tooltip.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_progressive_disclosure_component(self):
        """Generate progressive disclosure component to hide/show advanced fields"""
        
        template = Template("""import React, { useState, useRef, useEffect } from 'react';
import './ProgressiveDisclosure.css';

const ProgressiveDisclosure = ({
  trigger,
  children,
  defaultOpen = false,
  animationDuration = 300,
  className = '',
  onToggle
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [height, setHeight] = useState(defaultOpen ? 'auto' : 0);
  const contentRef = useRef(null);
  
  const toggle = () => {
    const newState = !isOpen;
    setIsOpen(newState);
    onToggle?.(newState);
    
    if (contentRef.current) {
      if (newState) {
        // Opening
        const scrollHeight = contentRef.current.scrollHeight;
        setHeight(scrollHeight);
        
        // Set to auto after animation for responsive behavior
        setTimeout(() => {
          if (contentRef.current) {
            setHeight('auto');
          }
        }, animationDuration);
      } else {
        // Closing
        const scrollHeight = contentRef.current.scrollHeight;
        setHeight(scrollHeight);
        
        // Force reflow then set to 0
        setTimeout(() => {
          setHeight(0);
        }, 10);
      }
    }
  };
  
  useEffect(() => {
    if (isOpen && contentRef.current) {
      const resizeObserver = new ResizeObserver(() => {
        if (height === 'auto') {
          // Content size changed, keep auto height
          return;
        }
      });
      
      resizeObserver.observe(contentRef.current);
      
      return () => {
        resizeObserver.disconnect();
      };
    }
  }, [isOpen, height]);
  
  return (
    <div className={`progressive-disclosure ${className}`}>
      <div 
        className="progressive-disclosure-trigger"
        onClick={toggle}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggle();
          }
        }}
      >
        {typeof trigger === 'function' ? trigger(isOpen) : trigger}
        <span className={`disclosure-icon ${isOpen ? 'disclosure-icon--open' : ''}`}>
          ▶️
        </span>
      </div>
      
      <div
        ref={contentRef}
        className="progressive-disclosure-content"
        style={{
          height: height === 'auto' ? 'auto' : `${height}px`,
          transition: `height ${animationDuration}ms ease-in-out`,
          overflow: height === 'auto' ? 'visible' : 'hidden'
        }}
      >
        <div className="progressive-disclosure-inner">
          {children}
        </div>
      </div>
    </div>
  );
};

// Advanced Fields Wrapper Component
export const AdvancedFields = ({ children, label = 'Advanced Options', ...props }) => {
  return (
    <ProgressiveDisclosure
      trigger={(isOpen) => (
        <span className="advanced-fields-trigger">
          {isOpen ? 'Hide' : 'Show'} {label}
        </span>
      )}
      className="advanced-fields"
      {...props}
    >
      <div className="advanced-fields-content">
        {children}
      </div>
    </ProgressiveDisclosure>
  );
};

export default ProgressiveDisclosure;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        component_file = components_dir / "ProgressiveDisclosure.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for progressive disclosure
        css_content = """.progressive-disclosure {
  margin-bottom: 16px;
}

.progressive-disclosure-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  font-weight: 500;
  color: #4a5568;
}

.progressive-disclosure-trigger:hover {
  background-color: #edf2f7;
  border-color: #cbd5e0;
}

.progressive-disclosure-trigger:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
  border-color: #4299e1;
}

.disclosure-icon {
  font-size: 12px;
  transition: transform 0.2s ease;
  color: #a0aec0;
}

.disclosure-icon--open {
  transform: rotate(90deg);
}

.progressive-disclosure-content {
  overflow: hidden;
}

.progressive-disclosure-inner {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-top: none;
  border-radius: 0 0 6px 6px;
  background-color: #ffffff;
}

/* Advanced Fields Styling */
.advanced-fields {
  margin-top: 24px;
}

.advanced-fields-trigger {
  color: #4299e1;
  font-size: 14px;
  font-weight: 600;
}

.progressive-disclosure-trigger:hover .advanced-fields-trigger {
  color: #2b6cb0;
}

.advanced-fields-content {
  display: grid;
  gap: 16px;
  padding-top: 8px;
}

/* Form field spacing within progressive disclosure */
.progressive-disclosure-inner .form-group {
  margin-bottom: 16px;
}

.progressive-disclosure-inner .form-group:last-child {
  margin-bottom: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .progressive-disclosure-trigger {
    padding: 10px 12px;
    font-size: 14px;
  }
  
  .progressive-disclosure-inner {
    padding: 12px;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .progressive-disclosure-content,
  .disclosure-icon {
    transition: none;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .progressive-disclosure-trigger {
    border-width: 2px;
  }
  
  .progressive-disclosure-trigger:focus {
    border-color: #000;
    box-shadow: 0 0 0 3px #000;
  }
}
"""
        
        css_file = components_dir / "ProgressiveDisclosure.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_session_timeout_component(self):
        """Generate session timeout warning component"""
        
        template = Template("""import React, { useState, useEffect, useCallback } from 'react';
import './SessionTimeout.css';

const SessionTimeout = ({
  timeoutMinutes = 30,
  warningMinutes = 5,
  onTimeout,
  onExtend,
  onWarning,
  isActive = true
}) => {
  const [timeLeft, setTimeLeft] = useState(timeoutMinutes * 60);
  const [showWarning, setShowWarning] = useState(false);
  const [isIdle, setIsIdle] = useState(false);
  
  const extendSession = useCallback(async () => {
    try {
      // Call API to extend session
      const response = await fetch('/api/auth/extend-session', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        setTimeLeft(timeoutMinutes * 60);
        setShowWarning(false);
        setIsIdle(false);
        onExtend?.();
      } else {
        // Session already expired
        handleTimeout();
      }
    } catch (error) {
      console.error('Failed to extend session:', error);
      handleTimeout();
    }
  }, [timeoutMinutes, onExtend]);
  
  const handleTimeout = useCallback(() => {
    setShowWarning(false);
    localStorage.removeItem('auth_token');
    onTimeout?.();
    // Redirect to login
    window.location.href = '/login?reason=session_expired';
  }, [onTimeout]);
  
  const resetTimer = useCallback(() => {
    if (isActive) {
      setTimeLeft(timeoutMinutes * 60);
      setShowWarning(false);
      setIsIdle(false);
    }
  }, [timeoutMinutes, isActive]);
  
  // Activity detection
  useEffect(() => {
    if (!isActive) return;
    
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    const handleActivity = () => {
      if (!showWarning) {
        resetTimer();
      }
    };
    
    events.forEach(event => {
      document.addEventListener(event, handleActivity, true);
    });
    
    return () => {
      events.forEach(event => {
        document.removeEventListener(event, handleActivity, true);
      });
    };
  }, [resetTimer, showWarning, isActive]);
  
  // Timer countdown
  useEffect(() => {
    if (!isActive) return;
    
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        const newTime = prev - 1;
        
        if (newTime <= 0) {
          handleTimeout();
          return 0;
        }
        
        // Show warning when time is low
        if (newTime <= warningMinutes * 60 && !showWarning) {
          setShowWarning(true);
          setIsIdle(true);
          onWarning?.(newTime);
        }
        
        return newTime;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, [warningMinutes, showWarning, handleTimeout, onWarning, isActive]);
  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  if (!isActive || !showWarning) {
    return null;
  }
  
  return (
    <div className="session-timeout-overlay">
      <div className="session-timeout-modal">
        <div className="session-timeout-header">
          <h3>Session Expiring Soon</h3>
          <div className="timeout-icon">⏰</div>
        </div>
        
        <div className="session-timeout-content">
          <p>
            Your session will expire in <strong>{formatTime(timeLeft)}</strong>.
          </p>
          <p>
            You will be automatically logged out for security reasons.
          </p>
        </div>
        
        <div className="session-timeout-progress">
          <div 
            className="timeout-progress-bar"
            style={{
              width: `${(timeLeft / (warningMinutes * 60)) * 100}%`
            }}
          />
        </div>
        
        <div className="session-timeout-actions">
          <button 
            className="btn btn-primary"
            onClick={extendSession}
          >
            Stay Logged In
          </button>
          
          <button 
            className="btn btn-secondary"
            onClick={handleTimeout}
          >
            Logout Now
          </button>
        </div>
        
        <div className="session-timeout-info">
          <small>
            Click anywhere or press any key to extend your session automatically.
          </small>
        </div>
      </div>
    </div>
  );
};

export default SessionTimeout;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        component_file = components_dir / "SessionTimeout.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for session timeout
        css_content = """.session-timeout-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
}

.session-timeout-modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90vw;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: sessionTimeoutFadeIn 0.3s ease-out;
}

.session-timeout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.session-timeout-header h3 {
  margin: 0;
  color: #e53e3e;
  font-size: 18px;
  font-weight: 600;
}

.timeout-icon {
  font-size: 24px;
  opacity: 0.8;
}

.session-timeout-content {
  margin-bottom: 20px;
  color: #4a5568;
  line-height: 1.5;
}

.session-timeout-content p {
  margin: 0 0 8px 0;
}

.session-timeout-content strong {
  color: #e53e3e;
  font-weight: 600;
}

.session-timeout-progress {
  width: 100%;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 20px;
}

.timeout-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #e53e3e 0%, #fc8181 100%);
  transition: width 1s ease-out;
  border-radius: 3px;
}

.session-timeout-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.session-timeout-actions .btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.session-timeout-actions .btn-primary {
  background: #4299e1;
  color: white;
}

.session-timeout-actions .btn-primary:hover {
  background: #3182ce;
}

.session-timeout-actions .btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.session-timeout-actions .btn-secondary:hover {
  background: #cbd5e0;
}

.session-timeout-info {
  text-align: center;
  color: #718096;
  font-size: 12px;
  line-height: 1.4;
}

@keyframes sessionTimeoutFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .session-timeout-modal {
    padding: 20px;
    margin: 16px;
  }
  
  .session-timeout-actions {
    flex-direction: column;
  }
  
  .session-timeout-actions .btn {
    width: 100%;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .session-timeout-modal {
    animation: none;
  }
  
  .timeout-progress-bar {
    transition: none;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .session-timeout-modal {
    border: 2px solid #000;
  }
  
  .session-timeout-actions .btn {
    border: 1px solid #000;
  }
}
"""
        
        css_file = components_dir / "SessionTimeout.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_quick_login_component(self):
        """Generate quick login component with OTP"""
        
        template = Template("""import React, { useState } from 'react';
import SmartOtpInput from './SmartOtpInput';
import './QuickLogin.css';

const QuickLogin = ({
  onSuccess,
  onError,
  onCancel,
  defaultMethod = 'email',
  allowedMethods = ['email', 'phone'],
  className = ''
}) => {
  const [step, setStep] = useState('method'); // method, code, success
  const [method, setMethod] = useState(defaultMethod);
  const [identifier, setIdentifier] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [resendCooldown, setResendCooldown] = useState(0);
  
  const sendOTP = async (retryIdentifier = identifier) => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/auth/send-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          method,
          identifier: retryIdentifier
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setStep('code');
        setResendCooldown(60); // 60 second cooldown
        
        // Start countdown
        const countdown = setInterval(() => {
          setResendCooldown(prev => {
            if (prev <= 1) {
              clearInterval(countdown);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      } else {
        setError(data.message || 'Failed to send verification code');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const verifyOTP = async (otp) => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/auth/verify-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          method,
          identifier,
          otp
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setStep('success');
        localStorage.setItem('auth_token', data.token);
        
        setTimeout(() => {
          onSuccess?.(data);
        }, 1000);
      } else {
        setError(data.message || 'Invalid verification code');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleMethodSubmit = (e) => {
    e.preventDefault();
    if (!identifier.trim()) {
      setError(`Please enter your ${method}`);
      return;
    }
    sendOTP();
  };
  
  const formatIdentifier = (value) => {
    if (method === 'phone') {
      // Basic phone formatting
      const cleaned = value.replace(/\D/g, '');
      if (cleaned.length >= 6) {
        return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6, 10)}`;
      } else if (cleaned.length >= 3) {
        return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3)}`;
      }
      return cleaned;
    }
    return value;
  };
  
  return (
    <div className={`quick-login ${className}`}>
      <div className="quick-login-header">
        <h3>Quick Login</h3>
        <p>Get instant access with a verification code</p>
      </div>
      
      {error && (
        <div className="quick-login-error">
          {error}
        </div>
      )}
      
      {step === 'method' && (
        <form onSubmit={handleMethodSubmit} className="quick-login-form">
          {allowedMethods.length > 1 && (
            <div className="method-selector">
              {allowedMethods.map(m => (
                <button
                  key={m}
                  type="button"
                  className={`method-btn ${method === m ? 'method-btn--active' : ''}`}
                  onClick={() => setMethod(m)}
                >
                  {m === 'email' ? '📧 Email' : '📱 Phone'}
                </button>
              ))}
            </div>
          )}
          
          <div className="input-group">
            <input
              type={method === 'email' ? 'email' : 'tel'}
              value={identifier}
              onChange={(e) => setIdentifier(formatIdentifier(e.target.value))}
              placeholder={method === 'email' ? 'Enter your email' : 'Enter your phone number'}
              className="quick-login-input"
              required
            />
          </div>
          
          <button 
            type="submit" 
            className="quick-login-btn"
            disabled={isLoading}
          >
            {isLoading ? 'Sending...' : `Send Code via ${method === 'email' ? 'Email' : 'SMS'}`}
          </button>
        </form>
      )}
      
      {step === 'code' && (
        <div className="otp-verification">
          <div className="otp-info">
            <p>
              We sent a verification code to <strong>{identifier}</strong>
            </p>
            <button 
              type="button"
              className="change-method-btn"
              onClick={() => setStep('method')}
            >
              Change {method}
            </button>
          </div>
          
          <div className="otp-input-container">
            <SmartOtpInput
              length={6}
              autoFill={true}
              onComplete={verifyOTP}
              placeholder="•"
            />
          </div>
          
          <div className="otp-actions">
            <button
              type="button"
              className="resend-btn"
              onClick={() => sendOTP()}
              disabled={resendCooldown > 0 || isLoading}
            >
              {resendCooldown > 0 
                ? `Resend in ${resendCooldown}s` 
                : 'Resend Code'
              }
            </button>
          </div>
        </div>
      )}
      
      {step === 'success' && (
        <div className="login-success">
          <div className="success-icon">✓</div>
          <h4>Login Successful!</h4>
          <p>Redirecting you now...</p>
        </div>
      )}
      
      <div className="quick-login-footer">
        <button 
          type="button"
          className="cancel-btn"
          onClick={onCancel}
        >
          Use Regular Login
        </button>
      </div>
    </div>
  );
};

export default QuickLogin;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        component_file = components_dir / "QuickLogin.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for quick login
        css_content = """.quick-login {
  max-width: 400px;
  margin: 0 auto;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.quick-login-header {
  text-align: center;
  margin-bottom: 24px;
}

.quick-login-header h3 {
  margin: 0 0 8px 0;
  color: #1a202c;
  font-size: 24px;
  font-weight: 600;
}

.quick-login-header p {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

.quick-login-error {
  background: #fed7d7;
  color: #c53030;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 14px;
  text-align: center;
}

.quick-login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.method-selector {
  display: flex;
  gap: 8px;
  padding: 4px;
  background: #f7fafc;
  border-radius: 8px;
}

.method-btn {
  flex: 1;
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #4a5568;
}

.method-btn--active {
  background: white;
  color: #4299e1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.input-group {
  position: relative;
}

.quick-login-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s ease;
}

.quick-login-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.quick-login-btn {
  padding: 12px 24px;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.quick-login-btn:hover {
  background: #3182ce;
}

.quick-login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.otp-verification {
  text-align: center;
}

.otp-info {
  margin-bottom: 24px;
}

.otp-info p {
  margin: 0 0 8px 0;
  color: #4a5568;
  font-size: 14px;
}

.change-method-btn {
  background: none;
  border: none;
  color: #4299e1;
  font-size: 12px;
  cursor: pointer;
  text-decoration: underline;
}

.otp-input-container {
  margin: 24px 0;
  display: flex;
  justify-content: center;
}

.otp-actions {
  margin-top: 16px;
}

.resend-btn {
  background: none;
  border: 1px solid #e2e8f0;
  color: #4a5568;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.resend-btn:hover:not(:disabled) {
  background: #f7fafc;
  border-color: #cbd5e0;
}

.resend-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-success {
  text-align: center;
  padding: 24px 0;
}

.success-icon {
  width: 64px;
  height: 64px;
  background: #48bb78;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
  margin: 0 auto 16px;
  animation: successPulse 0.6s ease-out;
}

.login-success h4 {
  margin: 0 0 8px 0;
  color: #1a202c;
  font-size: 18px;
}

.login-success p {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

.quick-login-footer {
  margin-top: 24px;
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.cancel-btn {
  background: none;
  border: none;
  color: #718096;
  font-size: 14px;
  cursor: pointer;
  text-decoration: underline;
}

@keyframes successPulse {
  0% {
    transform: scale(0.8);
    opacity: 0;
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .quick-login {
    padding: 20px;
    margin: 16px;
  }
  
  .method-selector {
    flex-direction: column;
  }
  
  .method-btn {
    padding: 12px;
  }
}
"""
        
        css_file = components_dir / "QuickLogin.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_help_panel_component(self):
        """Generate help panel component for contextual assistance"""
        
        template = Template("""import React, { useState, useEffect } from 'react';
import './HelpPanel.css';

const HelpPanel = ({
  isOpen,
  onClose,
  context = 'general',
  position = 'right',
  className = ''
}) => {
  const [helpContent, setHelpContent] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredContent, setFilteredContent] = useState([]);
  
  useEffect(() => {
    if (isOpen && context) {
      loadHelpContent(context);
    }
  }, [isOpen, context]);
  
  useEffect(() => {
    if (helpContent && searchQuery) {
      const filtered = helpContent.items.filter(item =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (item.tags && item.tags.some(tag => 
          tag.toLowerCase().includes(searchQuery.toLowerCase())
        ))
      );
      setFilteredContent(filtered);
    } else {
      setFilteredContent(helpContent?.items || []);
    }
  }, [helpContent, searchQuery]);
  
  const loadHelpContent = async (contextType) => {
    setIsLoading(true);
    try {
      // In a real app, this would fetch from an API or help system
      const content = getContextualHelp(contextType);
      setHelpContent(content);
    } catch (error) {
      console.error('Failed to load help content:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const getContextualHelp = (contextType) => {
    const helpDatabase = {
      general: {
        title: 'General Help',
        items: [
          {
            title: 'Getting Started',
            content: 'Welcome to FlashFlow! Here\'s how to get started with creating your first form.',
            tags: ['beginner', 'setup']
          },
          {
            title: 'Navigation Tips',
            content: 'Use keyboard shortcuts: Ctrl+S to save, Ctrl+Z to undo, Tab to navigate between fields.',
            tags: ['shortcuts', 'navigation']
          }
        ]
      },
      form: {
        title: 'Form Help',
        items: [
          {
            title: 'Smart Form Fields',
            content: 'FlashFlow automatically validates and formats your form fields. Email fields check for valid domains, phone fields format as you type.',
            tags: ['forms', 'validation']
          },
          {
            title: 'Password Requirements',
            content: 'Passwords must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters.',
            tags: ['password', 'security']
          },
          {
            title: 'Auto-save Feature',
            content: 'Your form data is automatically saved as you type. You can resume where you left off if you navigate away.',
            tags: ['autosave', 'draft']
          }
        ]
      },
      validation: {
        title: 'Validation Help',
        items: [
          {
            title: 'Email Validation',
            content: 'We check for common email typos and suggest corrections. Disposable email addresses are blocked.',
            tags: ['email', 'validation']
          },
          {
            title: 'Phone Validation',
            content: 'Phone numbers are validated based on your country. We auto-detect your location to format numbers correctly.',
            tags: ['phone', 'formatting']
          }
        ]
      }
    };
    
    return helpDatabase[contextType] || helpDatabase.general;
  };
  
  if (!isOpen) {
    return null;
  }
  
  return (
    <div className={`help-panel help-panel--${position} ${className}`}>
      <div className="help-panel-header">
        <h3>{helpContent?.title || 'Help'}</h3>
        <button 
          className="help-panel-close"
          onClick={onClose}
          aria-label="Close help panel"
        >
          ×
        </button>
      </div>
      
      <div className="help-panel-search">
        <input
          type="text"
          placeholder="Search help topics..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="help-search-input"
        />
        <div className="help-search-icon">🔍</div>
      </div>
      
      <div className="help-panel-content">
        {isLoading ? (
          <div className="help-loading">
            <div className="help-spinner"></div>
            <p>Loading help content...</p>
          </div>
        ) : (
          <div className="help-items">
            {filteredContent.length === 0 && searchQuery ? (
              <div className="help-no-results">
                <p>No help topics found for \"{searchQuery}\"</p>
                <button 
                  className="help-clear-search"
                  onClick={() => setSearchQuery('')}
                >
                  Clear search
                </button>
              </div>
            ) : (
              filteredContent.map((item, index) => (
                <div key={index} className="help-item">
                  <h4 className="help-item-title">{item.title}</h4>
                  <p className="help-item-content">{item.content}</p>
                  {item.tags && (
                    <div className="help-item-tags">
                      {item.tags.map((tag, tagIndex) => (
                        <span key={tagIndex} className="help-tag">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
      
      <div className="help-panel-footer">
        <div className="help-shortcuts">
          <small>Press <kbd>F1</kbd> for help, <kbd>Esc</kbd> to close</small>
        </div>
        <div className="help-contact">
          <a href="/support" className="help-link">Contact Support</a>
        </div>
      </div>
    </div>
  );
};

// Help trigger button component
export const HelpButton = ({ context = 'general', className = '' }) => {
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === 'F1') {
        e.preventDefault();
        setIsHelpOpen(true);
      } else if (e.key === 'Escape' && isHelpOpen) {
        setIsHelpOpen(false);
      }
    };
    
    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [isHelpOpen]);
  
  return (
    <>
      <button
        className={`help-button ${className}`}
        onClick={() => setIsHelpOpen(true)}
        title="Get help (F1)"
        aria-label="Open help panel"
      >
        ?
      </button>
      
      <HelpPanel
        isOpen={isHelpOpen}
        onClose={() => setIsHelpOpen(false)}
        context={context}
      />
    </>
  );
};

export default HelpPanel;
""")
        
        component_content = template.render()
        
        components_dir = self.frontend_path / "src" / "components"
        component_file = components_dir / "HelpPanel.jsx"
        with open(component_file, 'w') as f:
            f.write(component_content)
        
        # Generate CSS for help panel
        css_content = """.help-panel {
  position: fixed;
  top: 0;
  bottom: 0;
  width: 400px;
  background: white;
  border-left: 1px solid #e2e8f0;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.3s ease;
}

.help-panel--right {
  right: 0;
  transform: translateX(0);
}

.help-panel--left {
  left: 0;
  border-left: none;
  border-right: 1px solid #e2e8f0;
  box-shadow: 4px 0 12px rgba(0, 0, 0, 0.1);
  transform: translateX(-100%);
}

.help-panel--left.help-panel {
  transform: translateX(0);
}

.help-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.help-panel-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
}

.help-panel-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #a0aec0;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.help-panel-close:hover {
  background: #e2e8f0;
  color: #4a5568;
}

.help-panel-search {
  position: relative;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.help-search-input {
  width: 100%;
  padding: 8px 32px 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.help-search-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.help-search-icon {
  position: absolute;
  right: 28px;
  top: 50%;
  transform: translateY(-50%);
  color: #a0aec0;
  font-size: 14px;
}

.help-panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.help-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #718096;
}

.help-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #4299e1;
  border-radius: 50%;
  animation: helpSpinnerRotate 1s linear infinite;
  margin-bottom: 16px;
}

.help-items {
  padding: 0;
}

.help-item {
  padding: 20px;
  border-bottom: 1px solid #f7fafc;
  transition: background-color 0.2s ease;
}

.help-item:hover {
  background: #f8fafc;
}

.help-item-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
}

.help-item-content {
  margin: 0 0 12px 0;
  color: #4a5568;
  line-height: 1.5;
  font-size: 14px;
}

.help-item-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.help-tag {
  padding: 2px 8px;
  background: #edf2f7;
  color: #4a5568;
  font-size: 12px;
  border-radius: 12px;
  font-weight: 500;
}

.help-no-results {
  padding: 40px 20px;
  text-align: center;
  color: #718096;
}

.help-clear-search {
  background: #4299e1;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  margin-top: 12px;
}

.help-panel-footer {
  padding: 16px 20px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}

.help-shortcuts {
  margin-bottom: 8px;
}

.help-shortcuts kbd {
  background: #e2e8f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  font-family: monospace;
}

.help-contact {
  text-align: center;
}

.help-link {
  color: #4299e1;
  text-decoration: none;
  font-size: 14px;
}

.help-link:hover {
  text-decoration: underline;
}

/* Help Button */
.help-button {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 48px;
  height: 48px;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
  transition: all 0.2s ease;
  z-index: 999;
}

.help-button:hover {
  background: #3182ce;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(66, 153, 225, 0.4);
}

@keyframes helpSpinnerRotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .help-panel {
    width: 100vw;
    left: 0;
    right: 0;
  }
  
  .help-button {
    bottom: 16px;
    right: 16px;
    width: 44px;
    height: 44px;
    font-size: 18px;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .help-panel {
    transition: none;
  }
  
  .help-spinner {
    animation: none;
  }
}
"""
        
        css_file = components_dir / "HelpPanel.css"
        with open(css_file, 'w') as f:
            f.write(css_content)
    
    def _generate_serverless_components(self):
        """Generate serverless components if serverless is configured"""
        try:
            from ..integrations.serverless_integration import ServerlessIntegration
            
            # Initialize serverless integration
            serverless_integration = ServerlessIntegration()
            serverless_integration.initialize(self.ir.serverless)
            
            # Generate React components
            components = serverless_integration.generate_react_components()
            
            # Write components to files
            components_dir = self.frontend_path / "src" / "components" / "serverless"
            components_dir.mkdir(parents=True, exist_ok=True)
            
            for component_name, component_code in components.items():
                component_file = components_dir / f"{component_name}.tsx"
                with open(component_file, 'w', encoding='utf-8') as f:
                    f.write(component_code)
            
            print("Generated serverless components successfully")
            
        except Exception as e:
            print(f"Failed to generate serverless components: {e}")
    
    def _generate_i18n_components(self):
        """Generate i18n components if i18n is configured"""
        try:
            from ..integrations.i18n_integration import I18nIntegration
            
            # Initialize i18n integration
            i18n_integration = I18nIntegration()
            i18n_integration.initialize(self.ir.i18n)
            
            # Generate React components
            components = i18n_integration.generate_react_components()
            
            # Write components to files
            components_dir = self.frontend_path / "src" / "components" / "i18n"
            components_dir.mkdir(parents=True, exist_ok=True)
            
            for component_name, component_code in components.items():
                component_file = components_dir / f"{component_name}.tsx"
                with open(component_file, 'w', encoding='utf-8') as f:
                    f.write(component_code)
            
            # Generate i18n hooks
            hooks_dir = self.frontend_path / "src" / "hooks"
            use_translation_file = hooks_dir / "useTranslation.ts"
            
            # Create a simple useTranslation hook
            use_translation_content = '''import { useState, useEffect } from 'react';

export const useTranslation = () => {
  const [language, setLanguage] = useState('en');
  
  useEffect(() => {
    // Load language from localStorage or browser settings
    const savedLanguage = localStorage.getItem('language') || 'en';
    setLanguage(savedLanguage);
  }, []);
  
  const changeLanguage = (newLanguage: string) => {
    setLanguage(newLanguage);
    localStorage.setItem('language', newLanguage);
  };
  
  // Mock translation function - in a real app this would fetch translations
  const t = (key: string, params: Record<string, any> = {}) => {
    // This is a mock implementation - in a real app, you would fetch translations
    const translations: Record<string, Record<string, string>> = {
      en: {
        welcome: 'Welcome',
        login: 'Login',
        logout: 'Logout'
      },
      es: {
        welcome: 'Bienvenido',
        login: 'Iniciar sesión',
        logout: 'Cerrar sesión'
      }
    };
    
    const translation = translations[language]?.[key] || key;
    
    // Replace parameters
    let result = translation;
    Object.keys(params).forEach(param => {
      result = result.replace(new RegExp(`{${param}}`, 'g'), params[param]);
    });
    
    return result;
  };
  
  return { t, language, changeLanguage };
};

export default useTranslation;'''
            
            with open(use_translation_file, 'w', encoding='utf-8') as f:
                f.write(use_translation_content)
            
            print("Generated i18n components successfully")
            
        except Exception as e:
            print(f"Failed to generate i18n components: {e}")