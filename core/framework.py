"""
FlashFlow Core Classes
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class FlashFlowConfig:
    """FlashFlow project configuration"""
    name: str
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    frameworks: Optional[Dict[str, str]] = None
    dependencies: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.frameworks is None:
            self.frameworks = {
                "backend": "laravel",
                "frontend": "react",
                "mobile": "flet",
                "database": "sqlite"
            }
        if self.dependencies is None:
            self.dependencies = []

class FlashFlowProject:
    """Represents a FlashFlow project"""
    
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.config_path = self.root_path / "flashflow.json"
        self.src_path = self.root_path / "src"
        self.flows_path = self.src_path / "flows"
        self.dist_path = self.root_path / "dist"
        
        self._config: Optional[FlashFlowConfig] = None
    
    @property
    def config(self) -> FlashFlowConfig:
        """Load and return project configuration"""
        if self._config is None:
            self._load_config()
        assert self._config is not None  # This should never be None after _load_config
        return self._config
    
    def _load_config(self):
        """Load configuration from flashflow.json"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"FlashFlow project not found. Run 'flashflow new' to create a project.")
        
        with open(self.config_path, 'r') as f:
            config_data = json.load(f)
        
        self._config = FlashFlowConfig(**config_data)
    
    def save_config(self):
        """Save configuration to flashflow.json"""
        if self._config is None:
            return
        
        config_dict = {
            "name": self._config.name,
            "version": self._config.version,
            "description": self._config.description,
            "author": self._config.author,
            "frameworks": self._config.frameworks,
            "dependencies": self._config.dependencies
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def exists(self) -> bool:
        """Check if this is a valid FlashFlow project"""
        return self.config_path.exists()
    
    def get_flow_files(self) -> List[Path]:
        """Get all .flow files in the project"""
        if not self.flows_path.exists():
            return []
        
        return list(self.flows_path.glob("*.flow"))
    
    def get_test_files(self) -> List[Path]:
        """Get all .testflow files in the project"""
        test_path = self.src_path / "tests"
        if not test_path.exists():
            return []
        
        return list(test_path.glob("*.testflow"))

class FlashFlowIR:
    """FlashFlow Intermediate Representation"""
    
    def __init__(self):
        self.models: Dict[str, Dict] = {}
        self.pages: Dict[str, Dict] = {}
        self.endpoints: Dict[str, Dict] = {}
        self.auth: Dict[str, Any] = {}
        self.theme: Dict[str, Any] = {}
        self.i18n: Dict[str, Any] = {}
        self.serverless: Dict[str, Any] = {}
        self.desktop: Dict[str, Any] = {}
        
        # Dynamically added attributes from parser.py
        self.social_auth: Dict[str, Any] = {}
        self.social_providers: Dict[str, Any] = {}
        self.payments: Dict[str, Any] = {}
        self.payment_providers: Dict[str, Any] = {}
        self.custom_payment_providers: List[Any] = []
        self.sms: Dict[str, Any] = {}
        self.sms_providers: Dict[str, Any] = {}
        self.push_notifications: Dict[str, Any] = {}
        self.notification_providers: Dict[str, Any] = {}
        self.file_storage: Dict[str, Any] = {}
        self.storage_providers: Dict[str, Any] = {}
        self.email: Dict[str, Any] = {}
        self.email_providers: Dict[str, Any] = {}
        self.search: Dict[str, Any] = {}
        self.search_providers: Dict[str, Any] = {}
        self.analytics: Dict[str, Any] = {}
        self.analytics_providers: Dict[str, Any] = {}
        self.admin_panel: Dict[str, Any] = {}
        self.i18n_config: Dict[str, Any] = {}
        self.serverless_config: Dict[str, Any] = {}
        self.desktop_config: Dict[str, Any] = {}
        self.icons: Dict[str, Any] = {}
        self.websockets: Dict[str, Any] = {}
        self.realtime_events: Dict[str, Any] = {}
        self.data_streams: Dict[str, Any] = {}
        self.background_jobs: Dict[str, Any] = {}
        self.job_queues: Dict[str, Any] = {}
        self.scheduled_tasks: Dict[str, Any] = {}
        self.test_suites: Dict[str, Any] = {}
        self.smart_forms: List[Any] = []
        
        # Advanced AI & Real-Time Capabilities
        self.ai_models: Dict[str, Any] = {}
        self.vector_databases: Dict[str, Any] = {}
        self.webrtc_streams: Dict[str, Any] = {}
        self.lazy_imports: Dict[str, Any] = {}
    
    def add_model(self, name: str, definition: Dict):
        """Add a model definition to the IR"""
        self.models[name] = definition
    
    def add_page(self, path: str, definition: Dict):
        """Add a page definition to the IR"""
        self.pages[path] = definition
    
    def add_endpoint(self, path: str, definition: Dict):
        """Add an API endpoint definition to the IR"""
        self.endpoints[path] = definition
    
    def set_auth(self, auth_config: Dict):
        """Set authentication configuration"""
        self.auth = auth_config
    
    def set_theme(self, theme_config: Dict):
        """Set theme configuration"""
        self.theme = theme_config
    
    def set_i18n(self, i18n_config: Dict):
        """Set i18n configuration"""
        self.i18n = i18n_config
    
    def set_serverless(self, serverless_config: Dict):
        """Set serverless configuration"""
        self.serverless = serverless_config
    
    def set_desktop(self, desktop_config: Dict):
        """Set desktop configuration"""
        self.desktop = desktop_config
    
    def to_dict(self) -> Dict:
        """Convert IR to dictionary"""
        return {
            "models": self.models,
            "pages": self.pages,
            "endpoints": self.endpoints,
            "auth": self.auth,
            "theme": self.theme,
            "i18n": self.i18n,
            "serverless": self.serverless,
            "desktop": self.desktop,
            "ai_models": self.ai_models,
            "vector_databases": self.vector_databases,
            "webrtc_streams": self.webrtc_streams,
            "lazy_imports": self.lazy_imports
        }