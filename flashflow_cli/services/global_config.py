"""
FlashFlow Global Configuration Service
Manages global settings and project inheritance for credentials and CI/CD configurations
"""

import os
import json
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class GlobalCredentials:
    """Global credentials configuration"""
    github_token: Optional[str] = None
    github_username: Optional[str] = None
    github_email: Optional[str] = None
    
    # Apple Developer (global)
    apple_team_id: Optional[str] = None
    apple_developer_email: Optional[str] = None
    
    # Android (global)  
    android_developer_email: Optional[str] = None
    
    # Deployment platforms
    vercel_token: Optional[str] = None
    netlify_token: Optional[str] = None
    heroku_api_key: Optional[str] = None
    railway_token: Optional[str] = None


@dataclass
class GlobalCISettings:
    """Global CI/CD configuration"""
    node_version: str = "18"
    php_version: str = "8.1"
    python_version: str = "3.9"
    
    enable_code_coverage: bool = True
    enable_security_scanning: bool = True
    enable_dependency_updates: bool = True
    
    ios_xcode_version: str = "14.3"
    ios_deployment_target: str = "13.0"
    
    android_compile_sdk: str = "33"
    android_min_sdk: str = "21"
    android_target_sdk: str = "33"
    
    # Notification settings
    slack_webhook: Optional[str] = None
    discord_webhook: Optional[str] = None
    email_notifications: bool = True


@dataclass 
class ProjectInheritanceSettings:
    """Settings for what a project inherits from global config"""
    inherit_github_credentials: bool = True
    inherit_mobile_signing: bool = True
    inherit_deployment_tokens: bool = True
    inherit_ci_settings: bool = True
    inherit_notification_settings: bool = True
    
    # Project-specific overrides
    custom_node_version: Optional[str] = None
    custom_php_version: Optional[str] = None
    disable_mobile_builds: bool = False
    disable_web_deployment: bool = False


class GlobalConfigService:
    """Service for managing global FlashFlow configuration and project inheritance"""
    
    def __init__(self):
        self.config_dir = self._get_global_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.credentials_file = self.config_dir / "credentials.json"
        self.projects_file = self.config_dir / "projects.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self._global_credentials: Optional[GlobalCredentials] = None
        self._global_ci_settings: Optional[GlobalCISettings] = None
        self._projects: Dict[str, Dict[str, Any]] = {}
        
        self._load_configuration()
    
    def _get_global_config_dir(self) -> Path:
        """Get platform-specific global config directory"""
        system = platform.system()
        
        if system == "Windows":
            config_dir = Path.home() / "AppData" / "Roaming" / "FlashFlow"
        elif system == "Darwin":  # macOS
            config_dir = Path.home() / "Library" / "Application Support" / "FlashFlow"
        else:  # Linux and others
            config_dir = Path.home() / ".config" / "flashflow"
        
        return config_dir
    
    def _load_configuration(self):
        """Load global configuration from files"""
        try:
            # Load credentials
            if self.credentials_file.exists():
                with open(self.credentials_file, 'r') as f:
                    creds_data = json.load(f)
                self._global_credentials = GlobalCredentials(**creds_data)
            else:
                self._global_credentials = GlobalCredentials()
            
            # Load CI settings
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                self._global_ci_settings = GlobalCISettings(**config_data.get('ci_settings', {}))
            else:
                self._global_ci_settings = GlobalCISettings()
            
            # Load projects registry
            if self.projects_file.exists():
                with open(self.projects_file, 'r') as f:
                    self._projects = json.load(f)
            
        except Exception as e:
            print(f"Warning: Could not load global configuration: {e}")
            self._global_credentials = GlobalCredentials()
            self._global_ci_settings = GlobalCISettings()
            self._projects = {}
    
    def save_configuration(self):
        """Save global configuration to files"""
        try:
            # Save credentials
            with open(self.credentials_file, 'w') as f:
                json.dump(asdict(self._global_credentials), f, indent=2)
            
            # Save CI settings
            config_data = {
                'ci_settings': asdict(self._global_ci_settings),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Save projects registry
            with open(self.projects_file, 'w') as f:
                json.dump(self._projects, f, indent=2)
                
        except Exception as e:
            print(f"Error saving global configuration: {e}")
    
    def update_github_credentials(self, token: str, username: str, email: str):
        """Update global GitHub credentials"""
        self._global_credentials.github_token = token
        self._global_credentials.github_username = username
        self._global_credentials.github_email = email
        self.save_configuration()
    
    def update_apple_credentials(self, team_id: str, email: str):
        """Update global Apple Developer credentials"""
        self._global_credentials.apple_team_id = team_id
        self._global_credentials.apple_developer_email = email
        self.save_configuration()
    
    def update_android_credentials(self, email: str):
        """Update global Android credentials"""
        self._global_credentials.android_developer_email = email
        self.save_configuration()
    
    def update_deployment_tokens(self, platform: str, token: str):
        """Update deployment platform tokens"""
        if platform == "vercel":
            self._global_credentials.vercel_token = token
        elif platform == "netlify":
            self._global_credentials.netlify_token = token
        elif platform == "heroku":
            self._global_credentials.heroku_api_key = token
        elif platform == "railway":
            self._global_credentials.railway_token = token
        
        self.save_configuration()
    
    def register_project(self, project_path: str, project_name: str, 
                        inheritance_settings: Optional[ProjectInheritanceSettings] = None):
        """Register a project in the global registry"""
        if inheritance_settings is None:
            inheritance_settings = ProjectInheritanceSettings()
        
        project_key = str(Path(project_path).resolve())
        self._projects[project_key] = {
            'name': project_name,
            'path': project_path,
            'registered_at': datetime.now().isoformat(),
            'inheritance_settings': asdict(inheritance_settings)
        }
        
        self.save_configuration()
    
    def get_project_config(self, project_path: str) -> Dict[str, Any]:
        """Get inherited configuration for a specific project"""
        project_key = str(Path(project_path).resolve())
        project_data = self._projects.get(project_key, {})
        
        inheritance_settings = ProjectInheritanceSettings(
            **project_data.get('inheritance_settings', {})
        )
        
        config = {
            'project_info': project_data,
            'inherited_config': {}
        }
        
        # Apply inheritance rules
        if inheritance_settings.inherit_github_credentials and self._global_credentials.github_token:
            config['inherited_config']['github'] = {
                'token': self._global_credentials.github_token,
                'username': self._global_credentials.github_username,
                'email': self._global_credentials.github_email
            }
        
        if inheritance_settings.inherit_mobile_signing:
            if self._global_credentials.apple_team_id:
                config['inherited_config']['apple'] = {
                    'team_id': self._global_credentials.apple_team_id,
                    'email': self._global_credentials.apple_developer_email
                }
            
            if self._global_credentials.android_developer_email:
                config['inherited_config']['android'] = {
                    'email': self._global_credentials.android_developer_email
                }
        
        if inheritance_settings.inherit_deployment_tokens:
            deployment_tokens = {}
            if self._global_credentials.vercel_token:
                deployment_tokens['vercel'] = self._global_credentials.vercel_token
            if self._global_credentials.netlify_token:
                deployment_tokens['netlify'] = self._global_credentials.netlify_token
            if self._global_credentials.heroku_api_key:
                deployment_tokens['heroku'] = self._global_credentials.heroku_api_key
            if self._global_credentials.railway_token:
                deployment_tokens['railway'] = self._global_credentials.railway_token
            
            if deployment_tokens:
                config['inherited_config']['deployment'] = deployment_tokens
        
        if inheritance_settings.inherit_ci_settings:
            ci_settings = asdict(self._global_ci_settings)
            
            # Apply project-specific overrides
            if inheritance_settings.custom_node_version:
                ci_settings['node_version'] = inheritance_settings.custom_node_version
            if inheritance_settings.custom_php_version:
                ci_settings['php_version'] = inheritance_settings.custom_php_version
            
            config['inherited_config']['ci'] = ci_settings
        
        if inheritance_settings.inherit_notification_settings:
            notifications = {}
            if self._global_ci_settings.slack_webhook:
                notifications['slack'] = self._global_ci_settings.slack_webhook
            if self._global_ci_settings.discord_webhook:
                notifications['discord'] = self._global_ci_settings.discord_webhook
            notifications['email'] = self._global_ci_settings.email_notifications
            
            config['inherited_config']['notifications'] = notifications
        
        return config
    
    def list_registered_projects(self) -> List[Dict[str, Any]]:
        """List all registered FlashFlow projects"""
        projects = []
        for project_key, project_data in self._projects.items():
            # Check if project path still exists
            if Path(project_data['path']).exists():
                projects.append({
                    'key': project_key,
                    **project_data,
                    'exists': True
                })
            else:
                projects.append({
                    'key': project_key,
                    **project_data,
                    'exists': False
                })
        
        return projects
    
    def update_project_inheritance(self, project_path: str, 
                                  inheritance_settings: ProjectInheritanceSettings):
        """Update inheritance settings for a project"""
        project_key = str(Path(project_path).resolve())
        if project_key in self._projects:
            self._projects[project_key]['inheritance_settings'] = asdict(inheritance_settings)
            self._projects[project_key]['updated_at'] = datetime.now().isoformat()
            self.save_configuration()
    
    def unregister_project(self, project_path: str):
        """Remove a project from the global registry"""
        project_key = str(Path(project_path).resolve())
        if project_key in self._projects:
            del self._projects[project_key]
            self.save_configuration()
    
    def cleanup_stale_projects(self):
        """Remove projects that no longer exist on disk"""
        stale_projects = []
        for project_key, project_data in self._projects.items():
            if not Path(project_data['path']).exists():
                stale_projects.append(project_key)
        
        for project_key in stale_projects:
            del self._projects[project_key]
        
        if stale_projects:
            self.save_configuration()
        
        return len(stale_projects)
    
    def export_configuration(self, export_path: str):
        """Export global configuration for backup or sharing"""
        export_data = {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'credentials': asdict(self._global_credentials),
            'ci_settings': asdict(self._global_ci_settings),
            'projects': self._projects
        }
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def import_configuration(self, import_path: str, overwrite: bool = False):
        """Import global configuration from backup"""
        with open(import_path, 'r') as f:
            import_data = json.load(f)
        
        if not overwrite:
            # Merge configurations
            if 'credentials' in import_data:
                for key, value in import_data['credentials'].items():
                    if value and not getattr(self._global_credentials, key, None):
                        setattr(self._global_credentials, key, value)
            
            if 'ci_settings' in import_data:
                for key, value in import_data['ci_settings'].items():
                    if not hasattr(self._global_ci_settings, key):
                        setattr(self._global_ci_settings, key, value)
            
            if 'projects' in import_data:
                for project_key, project_data in import_data['projects'].items():
                    if project_key not in self._projects:
                        self._projects[project_key] = project_data
        else:
            # Overwrite configurations
            if 'credentials' in import_data:
                self._global_credentials = GlobalCredentials(**import_data['credentials'])
            
            if 'ci_settings' in import_data:
                self._global_ci_settings = GlobalCISettings(**import_data['ci_settings'])
            
            if 'projects' in import_data:
                self._projects = import_data['projects']
        
        self.save_configuration()
    
    @property
    def global_credentials(self) -> GlobalCredentials:
        """Get global credentials"""
        return self._global_credentials
    
    @property
    def global_ci_settings(self) -> GlobalCISettings:
        """Get global CI settings"""
        return self._global_ci_settings
    
    def is_configured(self) -> bool:
        """Check if global configuration has been set up"""
        return bool(self._global_credentials.github_token)
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get status of global configuration"""
        return {
            'configured': self.is_configured(),
            'github_connected': bool(self._global_credentials.github_token),
            'apple_configured': bool(self._global_credentials.apple_team_id),
            'android_configured': bool(self._global_credentials.android_developer_email),
            'deployment_platforms': {
                'vercel': bool(self._global_credentials.vercel_token),
                'netlify': bool(self._global_credentials.netlify_token),
                'heroku': bool(self._global_credentials.heroku_api_key),
                'railway': bool(self._global_credentials.railway_token)
            },
            'registered_projects': len(self._projects),
            'config_directory': str(self.config_dir)
        }


# Global instance
global_config = GlobalConfigService()