"""
GitHub Integration Service for FlashFlow
Handles GitHub API interactions, credential management, and CI/CD setup
"""

import os
import json
import base64
import requests
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class GitHubCredentials:
    """GitHub API credentials"""
    access_token: str
    username: str
    email: str


@dataclass 
class DeveloperCredentials:
    """Developer credentials for mobile app signing"""
    # Apple Developer
    apple_team_id: Optional[str] = None
    apple_signing_certificate: Optional[str] = None
    apple_provisioning_profile: Optional[str] = None
    apple_auth_key: Optional[str] = None
    apple_auth_key_id: Optional[str] = None
    apple_auth_issuer_id: Optional[str] = None
    
    # Android
    android_keystore: Optional[str] = None
    android_keystore_password: Optional[str] = None
    android_key_alias: Optional[str] = None
    android_key_password: Optional[str] = None
    
    # Google Play
    google_play_service_account: Optional[str] = None


class GitHubIntegrationService:
    """Service for managing GitHub integration and CI/CD setup"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / ".flashflow" / "github_config.json"
        self.credentials: Optional[GitHubCredentials] = None
        
    def authenticate_with_github(self, access_token: str) -> bool:
        """Authenticate with GitHub using access token"""
        try:
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get('https://api.github.com/user', headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                self.credentials = GitHubCredentials(
                    access_token=access_token,
                    username=user_data['login'],
                    email=user_data.get('email', '')
                )
                self._save_credentials()
                return True
            return False
        except Exception:
            return False
    
    def get_oauth_url(self, client_id: str, redirect_uri: str) -> str:
        """Generate GitHub OAuth URL"""
        scopes = "repo,admin:repo_hook,read:user,user:email"
        state = secrets.token_urlsafe(32)
        
        # Save state for verification
        self._save_oauth_state(state)
        
        return (f"https://github.com/login/oauth/authorize"
                f"?client_id={client_id}"
                f"&redirect_uri={redirect_uri}"
                f"&scope={scopes}"
                f"&state={state}")
    
    def exchange_oauth_code(self, code: str, state: str, client_id: str, client_secret: str) -> bool:
        """Exchange OAuth code for access token"""
        if not self._verify_oauth_state(state):
            return False
            
        try:
            response = requests.post('https://github.com/login/oauth/access_token', {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'state': state
            }, headers={'Accept': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get('access_token')
                if access_token:
                    return self.authenticate_with_github(access_token)
            return False
        except Exception:
            return False
    
    def create_repository(self, repo_name: str, description: str = "", private: bool = True) -> Dict[str, Any]:
        """Create a new GitHub repository"""
        if not self.credentials:
            raise ValueError("Not authenticated with GitHub")
            
        headers = {
            'Authorization': f'token {self.credentials.access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {
            'name': repo_name,
            'description': description,
            'private': private,
            'auto_init': True,
            'gitignore_template': 'Node'
        }
        
        response = requests.post('https://api.github.com/user/repos', json=data, headers=headers)
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create repository: {response.text}")
    
    def store_secrets(self, repo_owner: str, repo_name: str, credentials: DeveloperCredentials) -> bool:
        """Store developer credentials as GitHub repository secrets"""
        if not self.credentials:
            raise ValueError("Not authenticated with GitHub")
            
        headers = {
            'Authorization': f'token {self.credentials.access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get repository public key for encryption
        pub_key_response = requests.get(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/actions/secrets/public-key',
            headers=headers
        )
        
        if pub_key_response.status_code != 200:
            return False
            
        pub_key_data = pub_key_response.json()
        public_key = pub_key_data['key']
        key_id = pub_key_data['key_id']
        
        # Prepare secrets to store
        secrets_to_store = {}
        
        # Apple Developer secrets
        if credentials.apple_team_id:
            secrets_to_store['APPLE_TEAM_ID'] = credentials.apple_team_id
        if credentials.apple_signing_certificate:
            secrets_to_store['APPLE_SIGNING_CERTIFICATE'] = credentials.apple_signing_certificate
        if credentials.apple_provisioning_profile:
            secrets_to_store['APPLE_PROVISIONING_PROFILE'] = credentials.apple_provisioning_profile
        if credentials.apple_auth_key:
            secrets_to_store['APPLE_AUTH_KEY'] = credentials.apple_auth_key
        if credentials.apple_auth_key_id:
            secrets_to_store['APPLE_AUTH_KEY_ID'] = credentials.apple_auth_key_id
        if credentials.apple_auth_issuer_id:
            secrets_to_store['APPLE_AUTH_ISSUER_ID'] = credentials.apple_auth_issuer_id
            
        # Android secrets
        if credentials.android_keystore:
            secrets_to_store['ANDROID_KEYSTORE'] = credentials.android_keystore
        if credentials.android_keystore_password:
            secrets_to_store['ANDROID_KEYSTORE_PASSWORD'] = credentials.android_keystore_password
        if credentials.android_key_alias:
            secrets_to_store['ANDROID_KEY_ALIAS'] = credentials.android_key_alias
        if credentials.android_key_password:
            secrets_to_store['ANDROID_KEY_PASSWORD'] = credentials.android_key_password
            
        # Google Play secrets
        if credentials.google_play_service_account:
            secrets_to_store['GOOGLE_PLAY_SERVICE_ACCOUNT'] = credentials.google_play_service_account
        
        # Store each secret
        success_count = 0
        for secret_name, secret_value in secrets_to_store.items():
            if self._store_single_secret(repo_owner, repo_name, secret_name, secret_value, public_key, key_id):
                success_count += 1
        
        return success_count == len(secrets_to_store)
    
    def _store_single_secret(self, repo_owner: str, repo_name: str, secret_name: str, 
                           secret_value: str, public_key: str, key_id: str) -> bool:
        """Store a single secret in GitHub repository"""
        try:
            from cryptography.hazmat.primitives import serialization, hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            
            # Load public key
            public_key_bytes = base64.b64decode(public_key)
            pub_key = serialization.load_der_public_key(public_key_bytes)
            
            # Encrypt secret value
            encrypted_value = pub_key.encrypt(
                secret_value.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Encode as base64
            encrypted_value_b64 = base64.b64encode(encrypted_value).decode('utf-8')
            
            # Store secret
            headers = {
                'Authorization': f'token {self.credentials.access_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'encrypted_value': encrypted_value_b64,
                'key_id': key_id
            }
            
            response = requests.put(
                f'https://api.github.com/repos/{repo_owner}/{repo_name}/actions/secrets/{secret_name}',
                json=data,
                headers=headers
            )
            
            return response.status_code in [201, 204]
            
        except ImportError:
            # Fallback: store as plain text (not recommended for production)
            print("Warning: cryptography library not found. Storing secrets as plain text.")
            return self._store_plain_secret(repo_owner, repo_name, secret_name, secret_value)
        except Exception as e:
            print(f"Error storing secret {secret_name}: {e}")
            return False
    
    def _store_plain_secret(self, repo_owner: str, repo_name: str, secret_name: str, secret_value: str) -> bool:
        """Store secret without encryption (fallback method)"""
        headers = {
            'Authorization': f'token {self.credentials.access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {
            'encrypted_value': base64.b64encode(secret_value.encode()).decode(),
            'key_id': 'fallback'
        }
        
        response = requests.put(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/actions/secrets/{secret_name}',
            json=data,
            headers=headers
        )
        
        return response.status_code in [201, 204]
    
    def setup_webhooks(self, repo_owner: str, repo_name: str, webhook_url: str) -> bool:
        """Setup GitHub webhooks for CI/CD triggers"""
        if not self.credentials:
            return False
            
        headers = {
            'Authorization': f'token {self.credentials.access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        webhook_config = {
            'name': 'web',
            'active': True,
            'events': ['push', 'pull_request', 'release'],
            'config': {
                'url': webhook_url,
                'content_type': 'json',
                'insecure_ssl': '0'
            }
        }
        
        response = requests.post(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/hooks',
            json=webhook_config,
            headers=headers
        )
        
        return response.status_code == 201
    
    def get_user_repositories(self) -> List[Dict[str, Any]]:
        """Get list of user's GitHub repositories"""
        if not self.credentials:
            return []
            
        headers = {
            'Authorization': f'token {self.credentials.access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get('https://api.github.com/user/repos?sort=updated&per_page=100', headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    
    def _save_credentials(self):
        """Save GitHub credentials to config file"""
        config_dir = self.project_root / ".flashflow"
        config_dir.mkdir(exist_ok=True)
        
        config_data = {
            'github': {
                'access_token': self.credentials.access_token,
                'username': self.credentials.username,
                'email': self.credentials.email
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def _load_credentials(self) -> bool:
        """Load GitHub credentials from config file"""
        if not self.config_file.exists():
            return False
            
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
                
            github_config = config_data.get('github', {})
            if github_config.get('access_token'):
                self.credentials = GitHubCredentials(
                    access_token=github_config['access_token'],
                    username=github_config['username'],
                    email=github_config['email']
                )
                return True
        except Exception:
            pass
        return False
    
    def _save_oauth_state(self, state: str):
        """Save OAuth state for verification"""
        config_dir = self.project_root / ".flashflow"
        config_dir.mkdir(exist_ok=True)
        
        state_file = config_dir / "oauth_state.txt"
        with open(state_file, 'w') as f:
            f.write(state)
    
    def _verify_oauth_state(self, state: str) -> bool:
        """Verify OAuth state"""
        state_file = self.project_root / ".flashflow" / "oauth_state.txt"
        if not state_file.exists():
            return False
            
        try:
            with open(state_file, 'r') as f:
                saved_state = f.read().strip()
            state_file.unlink()  # Remove after verification
            return saved_state == state
        except Exception:
            return False