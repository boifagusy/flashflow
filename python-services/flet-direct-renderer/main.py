#!/usr/bin/env python3
"""
FlashFlow Engine using Python Flet
This replaces the HTML/CSS/JS approach with pure Python Flet components
"""

import os
import sys
import json
import yaml
import flet as ft
from pathlib import Path
from typing import Dict, Any, List, Union
import asyncio
import logging
import requests
from urllib.parse import urljoin
import numpy as np

# Import platform-adaptive components
from components import PlatformAdaptiveComponents, AdaptiveThemeManager, create_adaptive_headline, create_adaptive_input, create_adaptive_button
# FlashCore integration
try:
    import flashcore
    FLASHCORE_AVAILABLE = True
except ImportError:
    FLASHCORE_AVAILABLE = False
    print("Warning: FlashCore not available, using fallback implementations")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlashFlowEngine:
    """FlashFlow Engine using Python Flet for all UI components"""
    
    def __init__(self, project_root: str, backend_url: str = "http://localhost:8000"):
        self.project_root = Path(project_root).resolve()
        self.flow_files_dir = self.project_root / "src" / "flows"
        self.page_registry = {}  # Maps routes to .flow files
        self.backend_url = backend_url  # Laravel backend URL
        self.deployment_env = self._detect_deployment_environment()  # Auto-detect deployment environment
        self.current_platform = "desktop"  # Default platform
        self.app_state = {}  # Application state for temporary visibility controls
        self.state_listeners = {}  # Listeners for state changes
        
        # FlashFlow Engine with FlashCore acceleration
        self.flashcore_enabled = FLASHCORE_AVAILABLE
        self.vector_index = None  # FlashCore HNSW index for vector search
        self.inference_runtime = None  # FlashCore ONNX runtime for ML inference
        self.security_vault = None  # FlashCore AES vault for encryption
        
        # Initialize FlashCore components if available
        if self.flashcore_enabled:
            self._initialize_flashcore()
        
        # Validate project
        if not (self.project_root / "flashflow.json").exists():
            raise ValueError("Not in a FlashFlow project directory")
            
        # Load route mappings
        self._load_route_mappings()
        
        # Configure based on deployment environment
        self._configure_for_environment()
        
        # Initialize FlashCore-powered features
        if self.flashcore_enabled:
            self._initialize_flashcore_features()
    
    def _detect_deployment_environment(self) -> str:
        """Detect the deployment environment (local, cPanel, VPS, etc.)"""
        # Check for cPanel environment
        if os.path.exists('/usr/local/cpanel') or os.path.exists('/etc/cpanel/'):
            logger.info("Detected cPanel deployment environment")
            return "cpanel"
        
        # Check for common VPS indicators
        if os.path.exists('/etc/init.d/httpd') or os.path.exists('/etc/apache2/'):
            logger.info("Detected VPS deployment environment")
            return "vps"
        
        # Check for Docker environment
        if os.path.exists('/.dockerenv') or os.path.exists('/proc/1/cgroup'):
            with open('/proc/1/cgroup', 'r') as f:
                if 'docker' in f.read():
                    logger.info("Detected Docker deployment environment")
                    return "docker"
        
        # Check for cloud provider metadata (AWS, GCP, Azure)
        try:
            import requests
            # AWS metadata check
            response = requests.get('http://169.254.169.254/latest/meta-data/', timeout=1)
            if response.status_code == 200:
                logger.info("Detected AWS deployment environment")
                return "aws"
        except:
            pass
        
        # Default to local development
        logger.info("Detected local development environment")
        return "local"
    
    def _configure_for_environment(self):
        """Configure the engine based on the detected deployment environment"""
        if self.deployment_env == "cpanel":
            # cPanel specific configuration
            self._configure_cpanel()
        elif self.deployment_env == "vps":
            # VPS specific configuration
            self._configure_vps()
        elif self.deployment_env == "docker":
            # Docker specific configuration
            self._configure_docker()
        elif self.deployment_env == "aws":
            # AWS specific configuration
            self._configure_cloud()
        else:
            # Local development configuration
            self._configure_local()
    
    def _configure_cpanel(self):
        """Configure for cPanel deployment"""
        logger.info("Configuring FlashFlow Engine for cPanel deployment")
        # In cPanel, we might need to adjust paths or ports
        # cPanel typically runs on port 80 or 443
        pass
    
    def _configure_vps(self):
        """Configure for VPS deployment"""
        logger.info("Configuring FlashFlow Engine for VPS deployment")
        # VPS deployments might use FranklinPHP or other configurations
        pass
    
    def _configure_docker(self):
        """Configure for Docker deployment"""
        logger.info("Configuring FlashFlow Engine for Docker deployment")
        # Docker deployments might need specific networking configs
        pass
    
    def _configure_cloud(self):
        """Configure for cloud deployment"""
        logger.info("Configuring FlashFlow Engine for cloud deployment")
        # Cloud deployments might need specific scaling configs
        pass
    
    def _configure_local(self):
        """Configure for local development"""
        logger.info("Configuring FlashFlow Engine for local development")
        # Local development uses default settings
        pass
    
    def _initialize_flashcore(self):
        """Initialize FlashCore components"""
        try:
            # Initialize vector search index (128-dimensional for embeddings, max 10000 elements)
            self.vector_index = flashcore.HNSWIndex(128, 10000)
            logger.info("Initialized FlashCore HNSW vector index")
            
            # Initialize inference runtime (will be configured with specific models as needed)
            self.inference_runtime = flashcore.ONNXRuntime("")
            logger.info("Initialized FlashCore ONNX runtime")
            
            # Initialize security vault with default key
            self.security_vault = flashcore.AESVault("flashflow_default_key")
            logger.info("Initialized FlashCore AES security vault")
            
        except Exception as e:
            logger.error(f"Failed to initialize FlashCore components: {e}")
            self.flashcore_enabled = False
    
    def _initialize_flashcore_features(self):
        """Initialize FlashCore-powered features"""
        # Pre-populate vector index with sample data for demonstration
        if self.vector_index:
            try:
                # Add some sample vectors (in a real app, these would come from actual data)
                sample_vectors = [
                    (np.random.rand(128).astype(np.float32), 1),
                    (np.random.rand(128).astype(np.float32), 2),
                    (np.random.rand(128).astype(np.float32), 3),
                ]
                
                for vector, id in sample_vectors:
                    self.vector_index.add_vector(vector, id)
                
                logger.info("Pre-populated FlashCore vector index with sample data")
            except Exception as e:
                logger.error(f"Failed to pre-populate vector index: {e}")
    
    def vector_search(self, query_vector: np.ndarray, k: int = 5):
        """Perform vector search using FlashCore"""
        if not self.flashcore_enabled or not self.vector_index:
            # Fallback implementation
            logger.warning("FlashCore not available, using fallback vector search")
            return [{"id": i, "distance": 0.0} for i in range(min(k, 3))]
        
        try:
            return self.vector_index.search(query_vector, k)
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def run_inference(self, input_data: np.ndarray, output_size: int = 10):
        """Run ML inference using FlashCore"""
        if not self.flashcore_enabled or not self.inference_runtime:
            # Fallback implementation
            logger.warning("FlashCore not available, using fallback inference")
            return np.zeros(output_size, dtype=np.float32)
        
        try:
            return self.inference_runtime.run_inference(input_data, output_size)
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return np.zeros(output_size, dtype=np.float32)
    
    def encrypt_data(self, plaintext: bytes) -> bytes:
        """Encrypt data using FlashCore"""
        if not self.flashcore_enabled or not self.security_vault:
            # Fallback implementation (no encryption)
            logger.warning("FlashCore not available, skipping encryption")
            return plaintext
        
        try:
            return self.security_vault.encrypt(plaintext)
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return plaintext
    
    def decrypt_data(self, ciphertext: bytes) -> bytes:
        """Decrypt data using FlashCore"""
        if not self.flashcore_enabled or not self.security_vault:
            # Fallback implementation (no decryption)
            logger.warning("FlashCore not available, skipping decryption")
            return ciphertext
        
        try:
            return self.security_vault.decrypt(ciphertext)
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return ciphertext
    
    def _load_route_mappings(self):
        """Load route mappings from .flow files"""
        if not self.flow_files_dir.exists():
            logger.warning(f"No flows directory found at {self.flow_files_dir}")
            return
            
        for flow_file in self.flow_files_dir.glob("*.flow"):
            try:
                with open(flow_file, 'r') as f:
                    content = f.read()
                    
                # Parse YAML content
                flow_data = yaml.safe_load(content)
                
                # Extract page information
                if isinstance(flow_data, dict) and 'page' in flow_data:
                    page_info = flow_data['page']
                    if isinstance(page_info, dict) and 'path' in page_info:
                        route = page_info['path']
                        self.page_registry[route] = flow_file
                        logger.info(f"Registered route {route} -> {flow_file.name}")
                        
            except Exception as e:
                logger.error(f"Error parsing {flow_file}: {e}")
    
    def _parse_flow_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a .flow file and return structured data"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return yaml.safe_load(content) or {}
        except Exception as e:
            logger.error(f"Error parsing flow file {file_path}: {e}")
            return {}
    
    def _should_render_component(self, component_data: Dict[str, Any], platform: str) -> bool:
        """Determine if a component should be rendered based on platform visibility rules"""
        visibility = component_data.get('visibility', {})
        
        # If no visibility rules, render by default
        if not visibility:
            return True
            
        # Check platform visibility rules first
        # Check exclude list
        exclude_platforms = visibility.get('exclude', [])
        if platform in exclude_platforms:
            return False
            
        # Check include list (if specified)
        include_platforms = visibility.get('include', [])
        if include_platforms and platform not in include_platforms:
            return False
            
        # Check temporary/state-based visibility rules
        temp_visibility = visibility.get('temporary', {})
        if temp_visibility:
            # Check state conditions
            required_state = temp_visibility.get('requires_state')
            if required_state:
                # If requires_state is specified, component is only visible when that state exists
                state_key = required_state.get('key')
                state_value = required_state.get('value')
                if state_key and state_value is not None:
                    current_value = self.app_state.get(state_key)
                    if current_value != state_value:
                        return False
            
            # Check state exclusions
            exclude_states = temp_visibility.get('exclude_states', [])
            for exclude_state in exclude_states:
                state_key = exclude_state.get('key')
                state_value = exclude_state.get('value')
                if state_key and state_value is not None:
                    current_value = self.app_state.get(state_key)
                    if current_value == state_value:
                        return False
            
            # Check time-based visibility
            time_constraints = temp_visibility.get('time_constraints')
            if time_constraints:
                # For simplicity, we'll just check if time constraints exist
                # In a real implementation, this would check actual time values
                pass
                
        # If we passed all checks, render the component
        return True
    
    def set_state(self, key: str, value: Any):
        """Set application state and notify listeners"""
        old_value = self.app_state.get(key)
        self.app_state[key] = value
        
        # Notify listeners of state change
        if key in self.state_listeners:
            for listener in self.state_listeners[key]:
                listener(key, old_value, value)
    
    def get_state(self, key: str, default=None):
        """Get application state value"""
        return self.app_state.get(key, default)
    
    def add_state_listener(self, key: str, listener):
        """Add a listener for state changes"""
        if key not in self.state_listeners:
            self.state_listeners[key] = []
        self.state_listeners[key].append(listener)
    
    def remove_state_listener(self, key: str, listener):
        """Remove a listener for state changes"""
        if key in self.state_listeners and listener in self.state_listeners[key]:
            self.state_listeners[key].remove(listener)
    
    def _initialize_flashcore(self):
        """Initialize FlashCore components"""
        try:
            # Initialize vector search index (128-dimensional for embeddings, max 10000 elements)
            self.vector_index = flashcore.HNSWIndex(128, 10000)
            logger.info("Initialized FlashCore HNSW vector index")
            
            # Initialize inference runtime (will be configured with specific models as needed)
            self.inference_runtime = flashcore.ONNXRuntime("")
            logger.info("Initialized FlashCore ONNX runtime")
            
            # Initialize security vault with default key
            self.security_vault = flashcore.AESVault("flashflow_default_key")
            logger.info("Initialized FlashCore AES security vault")
            
        except Exception as e:
            logger.error(f"Failed to initialize FlashCore components: {e}")
            self.flashcore_enabled = False
    
    def _initialize_flashcore_features(self):
        """Initialize FlashCore-powered features"""
        # Pre-populate vector index with sample data for demonstration
        if self.vector_index:
            try:
                # Add some sample vectors (in a real app, these would come from actual data)
                sample_vectors = [
                    (np.random.rand(128).astype(np.float32), 1),
                    (np.random.rand(128).astype(np.float32), 2),
                    (np.random.rand(128).astype(np.float32), 3),
                ]
                
                for vector, id in sample_vectors:
                    self.vector_index.add_vector(vector, id)
                
                logger.info("Pre-populated FlashCore vector index with sample data")
            except Exception as e:
                logger.error(f"Failed to pre-populate vector index: {e}")
    
    def vector_search(self, query_vector: np.ndarray, k: int = 5):
        """Perform vector search using FlashCore"""
        if not self.flashcore_enabled or not self.vector_index:
            # Fallback implementation
            logger.warning("FlashCore not available, using fallback vector search")
            return [{"id": i, "distance": 0.0} for i in range(min(k, 3))]
        
        try:
            return self.vector_index.search(query_vector, k)
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def run_inference(self, input_data: np.ndarray, output_size: int = 10):
        """Run ML inference using FlashCore"""
        if not self.flashcore_enabled or not self.inference_runtime:
            # Fallback implementation
            logger.warning("FlashCore not available, using fallback inference")
            return np.zeros(output_size, dtype=np.float32)
        
        try:
            return self.inference_runtime.run_inference(input_data, output_size)
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return np.zeros(output_size, dtype=np.float32)
    
    def encrypt_data(self, plaintext: bytes) -> bytes:
        """Encrypt data using FlashCore"""
        if not self.flashcore_enabled or not self.security_vault:
            # Fallback implementation (no encryption)
            logger.warning("FlashCore not available, skipping encryption")
            return plaintext
        
        try:
            return self.security_vault.encrypt(plaintext)
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return plaintext
    
    def decrypt_data(self, ciphertext: bytes) -> bytes:
        """Decrypt data using FlashCore"""
        if not self.flashcore_enabled or not self.security_vault:
            # Fallback implementation (no decryption)
            logger.warning("FlashCore not available, skipping decryption")
            return ciphertext
        
        try:
            return self.security_vault.decrypt(ciphertext)
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return ciphertext
    
    def _run_vector_search_demo(self):
        """Run vector search demo"""
        logger.info("Running FlashCore vector search demo...")
        
        # Create a random query vector
        query_vector = np.random.rand(128).astype(np.float32)
        
        # Perform vector search
        results = self.vector_search(query_vector, 3)
        
        logger.info(f"Vector search results: {results}")
        print(f"Vector search results: {results}")
    
    def _run_inference_demo(self):
        """Run inference demo"""
        logger.info("Running FlashCore inference demo...")
        
        # Create random input data
        input_data = np.random.rand(10).astype(np.float32)
        
        # Run inference
        output_data = self.run_inference(input_data, 5)
        
        logger.info(f"Inference output: {output_data}")
        print(f"Inference output: {output_data}")
    
    def _run_encryption_demo(self):
        """Run encryption demo"""
        logger.info("Running FlashCore encryption demo...")
        
        # Original data
        original_data = b"This is a secret message for FlashCore encryption demo"
        
        # Encrypt data
        encrypted_data = self.encrypt_data(original_data)
        
        # Decrypt data
        decrypted_data = self.decrypt_data(encrypted_data)
        
        logger.info(f"Original: {original_data}")
        logger.info(f"Encrypted: {encrypted_data}")
        logger.info(f"Decrypted: {decrypted_data}")
        
        print(f"Original: {original_data}")
        print(f"Encrypted: {encrypted_data}")
        print(f"Decrypted: {decrypted_data}")
    
    def _create_component(self, component_data: Dict[str, Any], platform: str = "desktop") -> ft.Control:
        """Create a Flet component from component data with platform and temporary visibility support"""
        # Check visibility rules
        if not self._should_render_component(component_data, platform):
            # Return an empty container when component should not be rendered
            return ft.Container()
        
        component_type = component_data.get('component', '').lower()
        
        # Store page reference for adaptive components
        page_ref = getattr(self, '_current_page', None)
        
        if component_type == 'header':
            if page_ref:
                # Use adaptive headline component
                return create_adaptive_headline(page_ref, component_data.get('content', ''), level=1)
            else:
                return ft.Text(
                    component_data.get('content', ''),
                    size=24,
                    weight=ft.FontWeight.BOLD
                )
        elif component_type == 'text':
            if page_ref:
                # Use adaptive headline component for text as well
                return create_adaptive_headline(page_ref, component_data.get('content', ''), level=4)
            else:
                return ft.Text(
                    component_data.get('content', ''),
                    size=16
                )
        elif component_type == 'headline':
            # New adaptive headline component
            level = component_data.get('level', 1)
            text = component_data.get('text', '')
            if page_ref:
                return create_adaptive_headline(page_ref, text, level=level)
            else:
                # Fallback to standard text
                sizes = {1: 32, 2: 28, 3: 24, 4: 20, 5: 18, 6: 16}
                return ft.Text(
                    text,
                    size=sizes.get(level, 24),
                    weight=ft.FontWeight.BOLD
                )
        elif component_type == 'input':
            # New adaptive input component
            label = component_data.get('label', '')
            value = component_data.get('value', '')
            disabled = component_data.get('disabled', False)
            if page_ref:
                return create_adaptive_input(page_ref, label, value, disabled)
            else:
                # Fallback to standard TextField
                return ft.TextField(
                    label=label,
                    value=value,
                    disabled=disabled
                )
        elif component_type == 'button':
            # Handle API actions for buttons
            action = component_data.get('action')
            text = component_data.get('text', 'Button')
            disabled = component_data.get('disabled', False)
            
            if page_ref:
                # Use adaptive button component
                if action:
                    def on_click(e):
                        # Handle different types of actions
                        if action == 'api_call':
                            endpoint = component_data.get('endpoint')
                            method = component_data.get('method', 'GET')
                            data = component_data.get('data', {})
                            if endpoint:
                                result = self._make_api_request(method, endpoint, data)
                                print(f"API call result: {result}")
                        elif action == 'set_state':
                            # Special action to set application state
                            state_changes = component_data.get('state_changes', {})
                            for key, value in state_changes.items():
                                self.set_state(key, value)
                        elif action == 'navigate':
                            # Navigation action
                            link = component_data.get('link')
                            if link:
                                # In a real implementation, this would navigate to the link
                                print(f"Navigating to: {link}")
                        else:
                            print(f"Button clicked: {text} - Action: {action}")
                    
                    return create_adaptive_button(page_ref, text, disabled, on_click)
                else:
                    return create_adaptive_button(page_ref, text, disabled, lambda e: print(f"Button clicked: {text}"))
            else:
                # Fallback to standard ElevatedButton
                if action:
                    def on_click(e):
                        # Handle different types of actions
                        if action == 'api_call':
                            endpoint = component_data.get('endpoint')
                            method = component_data.get('method', 'GET')
                            data = component_data.get('data', {})
                            if endpoint:
                                result = self._make_api_request(method, endpoint, data)
                                print(f"API call result: {result}")
                        elif action == 'set_state':
                            # Special action to set application state
                            state_changes = component_data.get('state_changes', {})
                            for key, value in state_changes.items():
                                self.set_state(key, value)
                        elif action == 'navigate':
                            # Navigation action
                            link = component_data.get('link')
                            if link:
                                # In a real implementation, this would navigate to the link
                                print(f"Navigating to: {link}")
                        else:
                            print(f"Button clicked: {text} - Action: {action}")
                    
                    return ft.ElevatedButton(text, on_click=on_click, disabled=disabled)
                else:
                    return ft.ElevatedButton(text, on_click=lambda e: print(f"Button clicked: {text}"), disabled=disabled)
        elif component_type == 'primary_button':
            # New adaptive primary button component
            text = component_data.get('text', 'Button')
            disabled = component_data.get('disabled', False)
            action = component_data.get('action')
            
            if page_ref:
                if action:
                    def on_click(e):
                        # Handle different types of actions
                        if action == 'api_call':
                            endpoint = component_data.get('endpoint')
                            method = component_data.get('method', 'GET')
                            data = component_data.get('data', {})
                            if endpoint:
                                result = self._make_api_request(method, endpoint, data)
                                print(f"API call result: {result}")
                        elif action == 'set_state':
                            # Special action to set application state
                            state_changes = component_data.get('state_changes', {})
                            for key, value in state_changes.items():
                                self.set_state(key, value)
                        elif action == 'navigate':
                            # Navigation action
                            link = component_data.get('link')
                            if link:
                                # In a real implementation, this would navigate to the link
                                print(f"Navigating to: {link}")
                        else:
                            print(f"Button clicked: {text} - Action: {action}")
                    
                    return create_adaptive_button(page_ref, text, disabled, on_click)
                else:
                    return create_adaptive_button(page_ref, text, disabled, lambda e: print(f"Button clicked: {text}"))
            else:
                # Fallback to standard ElevatedButton
                if action:
                    def on_click(e):
                        # Handle different types of actions
                        if action == 'api_call':
                            endpoint = component_data.get('endpoint')
                            method = component_data.get('method', 'GET')
                            data = component_data.get('data', {})
                            if endpoint:
                                result = self._make_api_request(method, endpoint, data)
                                print(f"API call result: {result}")
                        elif action == 'set_state':
                            # Special action to set application state
                            state_changes = component_data.get('state_changes', {})
                            for key, value in state_changes.items():
                                self.set_state(key, value)
                        elif action == 'navigate':
                            # Navigation action
                            link = component_data.get('link')
                            if link:
                                # In a real implementation, this would navigate to the link
                                print(f"Navigating to: {link}")
                        else:
                            print(f"Button clicked: {text} - Action: {action}")
                    
                    return ft.ElevatedButton(text, on_click=on_click, disabled=disabled)
                else:
                    return ft.ElevatedButton(text, on_click=lambda e: print(f"Button clicked: {text}"), disabled=disabled)
        elif component_type == 'hero':
            # Hero component with title and subtitle
            title = component_data.get('title', '')
            subtitle = component_data.get('subtitle', '')
            cta = component_data.get('cta', {})
            
            hero_content = []
            if title:
                if page_ref:
                    hero_content.append(create_adaptive_headline(page_ref, title, level=1))
                else:
                    hero_content.append(ft.Text(title, size=32, weight=ft.FontWeight.BOLD))
            if subtitle:
                if page_ref:
                    hero_content.append(create_adaptive_headline(page_ref, subtitle, level=4))
                else:
                    hero_content.append(ft.Text(subtitle, size=18, color=ft.colors.GREY))
            
            # Add CTA button if present
            if cta and isinstance(cta, dict):
                cta_text = cta.get('text', 'Get Started')
                cta_link = cta.get('link', '#')
                if page_ref:
                    hero_content.append(
                        create_adaptive_button(page_ref, cta_text, False, lambda e: print(f"CTA clicked: {cta_text} - Link: {cta_link}"))
                    )
                else:
                    hero_content.append(
                        ft.ElevatedButton(
                            cta_text,
                            on_click=lambda e: print(f"CTA clicked: {cta_text} - Link: {cta_link}")
                        )
                    )
                
            return ft.Container(
                content=ft.Column(hero_content, spacing=20, alignment=ft.MainAxisAlignment.CENTER),
                padding=40,
                bgcolor=ft.colors.BLUE_50,
                border_radius=10,
                alignment=ft.alignment.center
            )
        elif component_type == 'card':
            title = component_data.get('title', '')
            content = component_data.get('content', '')
            
            card_content = []
            if title:
                if page_ref:
                    card_content.append(create_adaptive_headline(page_ref, title, level=3))
                else:
                    card_content.append(ft.Text(title, size=18, weight=ft.FontWeight.BOLD))
            if content:
                if page_ref:
                    card_content.append(create_adaptive_headline(page_ref, content, level=5))
                else:
                    card_content.append(ft.Text(content, size=14))
                
            return ft.Card(
                content=ft.Container(
                    content=ft.Column(card_content, spacing=10),
                    padding=20
                )
            )
        elif component_type == 'features':
            # Features component with a list of feature items
            items = component_data.get('items', [])
            features_content = []
            
            for item in items:
                if isinstance(item, dict):
                    title = item.get('title', '')
                    description = item.get('description', '')
                    
                    feature_column = []
                    if title:
                        if page_ref:
                            feature_column.append(create_adaptive_headline(page_ref, title, level=3))
                        else:
                            feature_column.append(ft.Text(title, size=20, weight=ft.FontWeight.BOLD))
                    if description:
                        if page_ref:
                            feature_column.append(create_adaptive_headline(page_ref, description, level=5))
                        else:
                            feature_column.append(ft.Text(description, size=14, color=ft.colors.GREY))
                    
                    features_content.append(
                        ft.Container(
                            content=ft.Column(feature_column, spacing=5),
                            padding=20,
                            border=ft.border.all(1, ft.colors.BLUE_100),
                            border_radius=8
                        )
                    )
            
            return ft.Column(features_content, spacing=20)
        elif component_type == 'flashcore_demo':
            # FlashCore demonstration component
            title = component_data.get('title', 'FlashCore Demo')
            demo_type = component_data.get('demo_type', 'vector_search')
            
            demo_content = []
            if page_ref:
                demo_content.append(create_adaptive_headline(page_ref, title, level=2))
                demo_content.append(ft.Divider())
            else:
                demo_content.extend([
                    ft.Text(title, size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider()
                ])
            
            if demo_type == 'vector_search':
                if page_ref:
                    demo_content.extend([
                        create_adaptive_headline(page_ref, "Vector Search Demo", level=3),
                        create_adaptive_headline(page_ref, "Click the button below to perform a vector search using FlashCore:", level=5),
                        create_adaptive_button(page_ref, "Run Vector Search", False, lambda e: self._run_vector_search_demo()),
                        create_adaptive_headline(page_ref, "Results will appear in the console", level=6)
                    ])
                else:
                    demo_content.extend([
                        ft.Text("Vector Search Demo", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Click the button below to perform a vector search using FlashCore:"),
                        ft.ElevatedButton(
                            "Run Vector Search",
                            on_click=lambda e: self._run_vector_search_demo()
                        ),
                        ft.Text("Results will appear in the console", size=12, color=ft.colors.GREY)
                    ])
            elif demo_type == 'inference':
                if page_ref:
                    demo_content.extend([
                        create_adaptive_headline(page_ref, "ML Inference Demo", level=3),
                        create_adaptive_headline(page_ref, "Click the button below to run ML inference using FlashCore:", level=5),
                        create_adaptive_button(page_ref, "Run Inference", False, lambda e: self._run_inference_demo()),
                        create_adaptive_headline(page_ref, "Results will appear in the console", level=6)
                    ])
                else:
                    demo_content.extend([
                        ft.Text("ML Inference Demo", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Click the button below to run ML inference using FlashCore:"),
                        ft.ElevatedButton(
                            "Run Inference",
                            on_click=lambda e: self._run_inference_demo()
                        ),
                        ft.Text("Results will appear in the console", size=12, color=ft.colors.GREY)
                    ])
            elif demo_type == 'encryption':
                if page_ref:
                    demo_content.extend([
                        create_adaptive_headline(page_ref, "Encryption Demo", level=3),
                        create_adaptive_headline(page_ref, "Click the button below to encrypt/decrypt data using FlashCore:", level=5),
                        create_adaptive_button(page_ref, "Run Encryption", False, lambda e: self._run_encryption_demo()),
                        create_adaptive_headline(page_ref, "Results will appear in the console", level=6)
                    ])
                else:
                    demo_content.extend([
                        ft.Text("Encryption Demo", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Click the button below to encrypt/decrypt data using FlashCore:"),
                        ft.ElevatedButton(
                            "Run Encryption",
                            on_click=lambda e: self._run_encryption_demo()
                        ),
                        ft.Text("Results will appear in the console", size=12, color=ft.colors.GREY)
                    ])
            
            return ft.Container(
                content=ft.Column(demo_content, spacing=15),
                padding=20,
                border=ft.border.all(2, ft.colors.BLUE_300),
                border_radius=10,
                bgcolor=ft.colors.BLUE_50
            )
        else:
            # Default unknown component
            return ft.Container(
                content=ft.Text(f"Unknown component: {component_type}"),
                bgcolor=ft.colors.YELLOW_100,
                padding=10,
                border_radius=5
            )
    
    def _render_page(self, flow_data: Dict[str, Any], platform: str = "desktop") -> List[ft.Control]:
        """Render a page from flow data with platform-specific and temporary visibility"""
        controls = []
        
        # Add page title
        page_info = flow_data.get('page', {})
        if page_info and isinstance(page_info, dict):
            title = page_info.get('title', 'FlashFlow Page')
            controls.append(ft.Text(title, size=32, weight=ft.FontWeight.BOLD))
            
            # Add page body components
            body = page_info.get('body', [])
            if isinstance(body, list):
                for component_data in body:
                    if isinstance(component_data, dict):
                        component = self._create_component(component_data, platform)
                        controls.append(component)
        
        # Add FlashFlow branding
        controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("🔧 FlashFlow Direct Renderer", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("This page is rendered directly from .flow files without code generation!", size=14),
                ]),
                bgcolor=ft.colors.BLUE_50,
                padding=20,
                border_radius=10,
                margin=ft.margin.only(top=30)
            )
        )
        
        return controls
    
    def _detect_platform(self, page: ft.Page) -> str:
        """Detect the current platform from the Flet page"""
        if page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]:
            return "mobile"
        elif page.platform in [ft.PagePlatform.WINDOWS, ft.PagePlatform.MACOS, ft.PagePlatform.LINUX]:
            return "desktop"
        else:
            # Default to web for unknown platforms
            return "web"
    
    def main(self, page: ft.Page):
        """Main Flet application entry point"""
        page.title = "FlashFlow Direct Renderer"
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.padding = 20
        page.theme_mode = ft.ThemeMode.LIGHT
        
        # Apply platform-adaptive theme with 60-30-10 color balance
        # Using blue-based color scheme as an example
        theme = AdaptiveThemeManager.create_theme(
            dominant_60="#1976D2",    # Blue (60%)
            secondary_30="#424242",   # Grey (30%)
            accent_10="#FF4081"       # Pink (10%)
        )
        page.theme = theme
        
        # Store page reference for adaptive components
        self._current_page = page
        
        # Detect current platform
        self.current_platform = self._detect_platform(page)
        logger.info(f"Detected platform: {self.current_platform}")
        
        # Route handling
        route = page.route or "/"
        logger.info(f"Navigating to route: {route}")
        
        # Handle preview routes
        if route.startswith("/preview/"):
            # Extract platform from preview route
            platform = route.split("/")[2] if len(route.split("/")) > 2 else "web"
            # Set the platform for rendering
            self.current_platform = platform
            # Use the root route to show the main page with the specified platform
            route = "/"
        
        # Find matching flow file
        flow_file_path = None
        if route in self.page_registry:
            flow_file_path = self.page_registry[route]
        elif route == "/" and "/app" in self.page_registry:
            flow_file_path = self.page_registry["/app"]
        else:
            # Try to find default app.flow
            default_flow = self.flow_files_dir / "app.flow"
            if default_flow.exists():
                flow_file_path = default_flow
        
        if flow_file_path and flow_file_path.exists():
            # Parse and render the flow file
            flow_data = self._parse_flow_file(flow_file_path)
            controls = self._render_page(flow_data, self.current_platform)
            
            # Add navigation info
            controls.append(
                ft.Text(f"Route: {route} | Platform: {self.current_platform}", size=12, color=ft.colors.GREY)
            )
            
            page.controls.clear()
            page.add(ft.Column(controls, spacing=20))
        else:
            # Show error page
            page.controls.clear()
            page.add(
                ft.Column([
                    ft.Text("Page Not Found", size=32, color=ft.colors.RED),
                    ft.Text(f"No .flow file found for route: {route}", size=16),
                    ft.Text("Available routes:", size=18, weight=ft.FontWeight.BOLD),
                    *[ft.Text(f"- {route}") for route in self.page_registry.keys()]
                ], spacing=20)
            )
        
        page.update()
    
    def _make_api_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make API request to Laravel backend"""
        try:
            url = urljoin(self.backend_url, endpoint)
            headers = {'Content-Type': 'application/json'}
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {"error": str(e)}

def main():
    """Entry point for the Flet Direct Renderer"""
    # Get project directory from command line argument or use current directory
    project_dir = "."
    backend_url = "http://localhost:8000"  # Default Laravel backend URL
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]
    if len(sys.argv) > 2:
        backend_url = sys.argv[2]
    
    try:
        # Create and start the FlashFlow Engine
        engine = FlashFlowEngine(project_dir, backend_url)
        logger.info("🚀 Starting FlashFlow Engine with Flet")
        logger.info(f"📂 Project root: {engine.project_root}")
        logger.info(f"📄 Flow files directory: {engine.flow_files_dir}")
        logger.info(f"📡 Backend URL: {engine.backend_url}")
        logger.info(f"🌐 Deployment Environment: {engine.deployment_env}")
        logger.info("🔗 Available routes:")
        for route, file_path in engine.page_registry.items():
            logger.info(f"   {route} -> {file_path.name}")
        
        # Start the Flet app in web mode
        ft.app(target=engine.main, view=ft.AppView.WEB_BROWSER, port=8013)
    except Exception as e:
        logger.error(f"Failed to start FlashFlow Engine: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()