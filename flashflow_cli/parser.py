"""
FlashFlow .flow file parser
Converts .flow syntax into FlashFlow IR (Intermediate Representation)
"""

import yaml
import re
from pathlib import Path
from typing import Dict, Any, List
from .core import FlashFlowIR

class FlowParser:
    """Parser for .flow files"""
    
    def __init__(self):
        self.ir = FlashFlowIR()
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a single .flow file"""
        
        if not file_path.exists():
            raise FileNotFoundError(f"Flow file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> Dict[str, Any]:
        """Parse .flow content string"""
        
        # Remove comments (lines starting with #)
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Keep lines that don't start with # (after stripping whitespace)
            stripped = line.lstrip()
            if not stripped.startswith('#'):
                cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        try:
            # Parse as YAML (since .flow syntax is YAML-like)
            parsed_data = yaml.safe_load(cleaned_content)
            
            if parsed_data is None:
                return {}
            
            return parsed_data
            
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse .flow file: {str(e)}")
    
    def parse_project(self, project_path: Path) -> FlashFlowIR:
        """Parse all .flow files in a project and return unified IR"""
        
        flows_path = project_path / "src" / "flows"
        if not flows_path.exists():
            return self.ir
        
        # Parse different types of flow files
        flow_files = list(flows_path.glob("*.flow"))
        liveflow_files = list(flows_path.glob("*.liveflow"))
        jobflow_files = list(flows_path.glob("*.jobflow"))
        testflow_files = list(flows_path.glob("*.testflow"))
        
        # Parse regular .flow files
        for flow_file in flow_files:
            parsed_data = self.parse_file(flow_file)
            self._merge_into_ir(parsed_data)
        
        # Parse .liveflow files (real-time features)
        for liveflow_file in liveflow_files:
            parsed_data = self.parse_liveflow_file(liveflow_file)
            self._merge_liveflow_into_ir(parsed_data)
        
        # Parse .jobflow files (background jobs)
        for jobflow_file in jobflow_files:
            parsed_data = self.parse_jobflow_file(jobflow_file)
            self._merge_jobflow_into_ir(parsed_data)
        
        # Parse .testflow files (tests)
        for testflow_file in testflow_files:
            parsed_data = self.parse_testflow_file(testflow_file)
            self._merge_testflow_into_ir(parsed_data)
        
        return self.ir
    
    def _merge_into_ir(self, parsed_data: Dict[str, Any]):
        """Merge parsed data into the IR"""
        
        # Handle models
        if 'model' in parsed_data:
            model_data = parsed_data['model']
            if isinstance(model_data, dict) and 'name' in model_data:
                self.ir.add_model(model_data['name'], model_data)
        
        # Handle pages
        if 'page' in parsed_data:
            page_data = parsed_data['page']
            if isinstance(page_data, dict):
                path = page_data.get('path', '/')
                self.ir.add_page(path, page_data)
        
        # Handle endpoints
        if 'endpoint' in parsed_data:
            endpoint_data = parsed_data['endpoint']
            if isinstance(endpoint_data, list):
                # Multiple endpoints
                for endpoint in endpoint_data:
                    if isinstance(endpoint, dict):
                        path = endpoint.get('path', '/api/unknown')
                        self.ir.add_endpoint(path, endpoint)
            elif isinstance(endpoint_data, dict):
                # Single endpoint
                path = endpoint_data.get('path', '/api/unknown')
                self.ir.add_endpoint(path, endpoint_data)
        
        # Handle authentication
        if 'authentication' in parsed_data:
            auth_data = parsed_data['authentication']
            self.ir.set_auth(auth_data)
            
            # Handle social login configuration
            if 'social_login' in auth_data:
                social_config = auth_data['social_login']
                if not hasattr(self.ir, 'social_auth'):
                    self.ir.social_auth = {}
                
                self.ir.social_auth = {
                    'providers': social_config.get('providers', []),
                    'redirect_after': social_config.get('redirect_after', '/dashboard'),
                    'create_account_if_missing': social_config.get('create_account_if_missing', True)
                }
                
                # Store provider-specific configurations
                for provider in ['google', 'facebook', 'twitter', 'github']:
                    if provider in social_config:
                        if not hasattr(self.ir, 'social_providers'):
                            self.ir.social_providers = {}
                        self.ir.social_providers[provider] = social_config[provider]
        
        # Handle payments configuration
        if 'payments' in parsed_data:
            payments_data = parsed_data['payments']
            if not hasattr(self.ir, 'payments'):
                self.ir.payments = {}
            
            self.ir.payments = {
                'providers': payments_data.get('providers', []),
                'default_provider': payments_data.get('default_provider', 'stripe'),
                'currency': payments_data.get('currency', 'USD'),
                'settings': payments_data.get('settings', {})
            }
            
            # Store provider-specific configurations
            for provider in ['stripe', 'paypal', 'square', 'razorpay']:
                if provider in payments_data:
                    if not hasattr(self.ir, 'payment_providers'):
                        self.ir.payment_providers = {}
                    self.ir.payment_providers[provider] = payments_data[provider]
            
            # Handle custom payment providers
            custom_providers = []
            for key, config in payments_data.items():
                if isinstance(config, dict) and config.get('type') == 'custom':
                    custom_providers.append({
                        'name': key,
                        'config': config
                    })
            
            if custom_providers:
                if not hasattr(self.ir, 'custom_payment_providers'):
                    self.ir.custom_payment_providers = []
                self.ir.custom_payment_providers.extend(custom_providers)
        
        # Handle SMS configuration
        if 'sms' in parsed_data:
            sms_data = parsed_data['sms']
            if not hasattr(self.ir, 'sms'):
                self.ir.sms = {}
            
            self.ir.sms = {
                'providers': sms_data.get('providers', []),
                'default_provider': sms_data.get('default_provider', 'twilio'),
                'default_country_code': sms_data.get('default_country_code', '+1'),
                'settings': sms_data.get('settings', {})
            }
            
            # Store provider-specific configurations
            for provider in ['twilio', 'aws_sns', 'nexmo', 'messagebird']:
                if provider in sms_data:
                    if not hasattr(self.ir, 'sms_providers'):
                        self.ir.sms_providers = {}
                    self.ir.sms_providers[provider] = sms_data[provider]
        
        # Handle push notifications configuration
        if 'push_notifications' in parsed_data:
            push_data = parsed_data['push_notifications']
            if not hasattr(self.ir, 'push_notifications'):
                self.ir.push_notifications = {}
            
            self.ir.push_notifications = {
                'providers': push_data.get('providers', []),
                'default_provider': push_data.get('default_provider', 'firebase'),
                'settings': push_data.get('settings', {})
            }
            
            # Store provider-specific configurations
            for provider in ['firebase', 'apns', 'web_push', 'onesignal']:
                if provider in push_data:
                    if not hasattr(self.ir, 'push_providers'):
                        self.ir.push_providers = {}
                    self.ir.push_providers[provider] = push_data[provider]
        
        # Handle AI/ML configuration
        if 'ai_ml' in parsed_data:
            ai_data = parsed_data['ai_ml']
            if not hasattr(self.ir, 'ai_ml'):
                self.ir.ai_ml = {}
            
            self.ir.ai_ml = {
                'providers': ai_data.get('providers', []),
                'default_provider': ai_data.get('default_provider', 'openai'),
                'settings': ai_data.get('settings', {})
            }
            
            # Store provider-specific configurations
            for provider in ['openai', 'anthropic', 'google_ai', 'huggingface', 'azure_ai']:
                if provider in ai_data:
                    if not hasattr(self.ir, 'ai_providers'):
                        self.ir.ai_providers = {}
                    self.ir.ai_providers[provider] = ai_data[provider]
        
        # Handle file storage configuration
        if 'file_storage' in parsed_data:
            storage_data = parsed_data['file_storage']
            if not hasattr(self.ir, 'file_storage'):
                self.ir.file_storage = {}
            
            self.ir.file_storage = {
                'providers': storage_data.get('providers', []),
                'default_provider': storage_data.get('default_provider', 'local'),
                'processing': storage_data.get('processing', {}),
                'security': storage_data.get('security', {}),
                'image_processing': storage_data.get('image_processing', {})
            }
            
            # Store provider-specific configurations
            for provider in ['local', 'aws_s3', 'azure_blob', 'google_cloud', 'cloudinary']:
                if provider in storage_data:
                    if not hasattr(self.ir, 'storage_providers'):
                        self.ir.storage_providers = {}
                    self.ir.storage_providers[provider] = storage_data[provider]
        
        # Handle smart forms configuration
        if 'form' in parsed_data:
            form_data = parsed_data['form']
            if not hasattr(self.ir, 'smart_forms'):
                self.ir.smart_forms = []
            
            # Parse smart form configuration
            smart_form = parse_smart_form(form_data)
            self.ir.smart_forms.append(smart_form)
        
        # Handle smart forms in page components
        if 'page' in parsed_data:
            page_data = parsed_data['page']
            if 'body' in page_data:
                self._parse_page_smart_forms(page_data['body'])
        
        # Handle smart forms in components
        if 'components' in parsed_data:
            components_data = parsed_data['components']
            for component_name, component_config in components_data.items():
                if component_config.get('type') == 'smart_form' or 'form' in component_config:
                    form_config = component_config.get('form', component_config)
                    form_config['name'] = component_name
                    smart_form = parse_smart_form(form_config)
                    if not hasattr(self.ir, 'smart_forms'):
                        self.ir.smart_forms = []
                    self.ir.smart_forms.append(smart_form)
        
        # Handle smart field types in models
        if 'models' in parsed_data:
            models_data = parsed_data['models']
            for model_name, model_config in models_data.items():
                if 'fields' in model_config:
                    enhanced_fields = []
                    for field in model_config['fields']:
                        if isinstance(field, dict) and field.get('type') in [
                            'phone', 'email', 'password', 'otp', 'credit_card', 
                            'search', 'address', 'smart_date', 'smart_number'
                        ]:
                            # Enhance field with smart capabilities
                            enhanced_field = parse_smart_field(field)
                            enhanced_fields.append(enhanced_field)
                        else:
                            enhanced_fields.append(field)
                    model_config['smart_fields'] = enhanced_fields
        
        # Handle admin panel configuration
        if 'admin_panel' in parsed_data:
            admin_data = parsed_data['admin_panel']
            if not hasattr(self.ir, 'admin_panel'):
                self.ir.admin_panel = {}
            
            self.ir.admin_panel = {
                'theme': admin_data.get('theme', {}),
                'authentication': admin_data.get('authentication', {}),
                'dashboard': admin_data.get('dashboard', {}), 
                'navigation': admin_data.get('navigation', {}),
                'permissions': admin_data.get('permissions', {}),
                'features': admin_data.get('features', {}),
                'customization': admin_data.get('customization', {})
            }
        
        # Handle i18n configuration
        if 'i18n' in parsed_data:
            i18n_data = parsed_data['i18n']
            if not hasattr(self.ir, 'i18n'):
                self.ir.i18n = {}
            
            self.ir.i18n = {
                'auto_translate': i18n_data.get('auto_translate', True),
                'providers': i18n_data.get('providers', ['google_translate']),
                'fallback_language': i18n_data.get('fallback_language', 'en'),
                'languages': i18n_data.get('languages', []),
                'processing': i18n_data.get('processing', {}),
                'security': i18n_data.get('security', {}),
                'performance': i18n_data.get('performance', {})
            }
        
        # Handle serverless configuration
        if 'serverless' in parsed_data:
            serverless_data = parsed_data['serverless']
            if not hasattr(self.ir, 'serverless'):
                self.ir.serverless = {}
            
            self.ir.serverless = {
                'providers': serverless_data.get('providers', {}),
                'defaults': serverless_data.get('defaults', {}),
                'functions': serverless_data.get('functions', {}),
                'groups': serverless_data.get('groups', {}),
                'api_gateway': serverless_data.get('api_gateway', {}),
                'monitoring': serverless_data.get('monitoring', {}),
                'security': serverless_data.get('security', {}),
                'deployment': serverless_data.get('deployment', {}),
                'ci_cd': serverless_data.get('ci_cd', {})
            }
        
        # Handle theme
        if 'theme' in parsed_data:
            self.ir.set_theme(parsed_data['theme'])
        
        # Handle desktop configuration
        if 'desktop' in parsed_data:
            desktop_data = parsed_data['desktop']
            if not hasattr(self.ir, 'desktop'):
                self.ir.desktop = {}
            
            self.ir.desktop = {
                'window': desktop_data.get('window', {}),
                'tray': desktop_data.get('tray', {}),
                'menu': desktop_data.get('menu', {}),
                'build': desktop_data.get('build', {})
            }

    def parse_liveflow_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a .liveflow file for real-time features"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML content
        try:
            parsed_data = yaml.safe_load(content) or {}
            
            # Add file type marker
            parsed_data['_file_type'] = 'liveflow'
            parsed_data['_file_name'] = file_path.stem
            
            return parsed_data
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse .liveflow file {file_path}: {str(e)}")
    
    def parse_jobflow_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a .jobflow file for background jobs"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML content
        try:
            parsed_data = yaml.safe_load(content) or {}
            
            # Add file type marker
            parsed_data['_file_type'] = 'jobflow'
            parsed_data['_file_name'] = file_path.stem
            
            return parsed_data
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse .jobflow file {file_path}: {str(e)}")
    
    def parse_testflow_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a .testflow file for tests"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML content
        try:
            parsed_data = yaml.safe_load(content) or {}
            
            # Add file type marker
            parsed_data['_file_type'] = 'testflow'
            parsed_data['_file_name'] = file_path.stem
            
            return parsed_data
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse .testflow file {file_path}: {str(e)}")
    
    def _merge_liveflow_into_ir(self, parsed_data: Dict[str, Any]):
        """Merge .liveflow data into IR"""
        
        # Handle WebSocket connections
        if 'websocket' in parsed_data:
            websocket_data = parsed_data['websocket']
            if not hasattr(self.ir, 'websockets'):
                self.ir.websockets = {}
            
            connection_name = parsed_data.get('_file_name', 'default')
            self.ir.websockets[connection_name] = websocket_data
        
        # Handle real-time events
        if 'events' in parsed_data:
            events_data = parsed_data['events']
            if not hasattr(self.ir, 'realtime_events'):
                self.ir.realtime_events = {}
            
            for event_name, event_config in events_data.items():
                self.ir.realtime_events[event_name] = event_config
        
        # Handle live data streams
        if 'streams' in parsed_data:
            streams_data = parsed_data['streams']
            if not hasattr(self.ir, 'data_streams'):
                self.ir.data_streams = {}
            
            for stream_name, stream_config in streams_data.items():
                self.ir.data_streams[stream_name] = stream_config
    
    def _merge_jobflow_into_ir(self, parsed_data: Dict[str, Any]):
        """Merge .jobflow data into IR"""
        
        # Handle background jobs
        if 'jobs' in parsed_data:
            jobs_data = parsed_data['jobs']
            if not hasattr(self.ir, 'background_jobs'):
                self.ir.background_jobs = {}
            
            for job_name, job_config in jobs_data.items():
                self.ir.background_jobs[job_name] = job_config
        
        # Handle job queues
        if 'queues' in parsed_data:
            queues_data = parsed_data['queues']
            if not hasattr(self.ir, 'job_queues'):
                self.ir.job_queues = {}
            
            for queue_name, queue_config in queues_data.items():
                self.ir.job_queues[queue_name] = queue_config
        
        # Handle scheduled tasks
        if 'schedules' in parsed_data:
            schedules_data = parsed_data['schedules']
            if not hasattr(self.ir, 'scheduled_tasks'):
                self.ir.scheduled_tasks = {}
            
            for schedule_name, schedule_config in schedules_data.items():
                self.ir.scheduled_tasks[schedule_name] = schedule_config
    
    def _merge_testflow_into_ir(self, parsed_data: Dict[str, Any]):
        """Merge .testflow data into IR"""
        
        # Handle test suites
        if 'test' in parsed_data or 'tests' in parsed_data:
            test_data = parsed_data.get('test') or parsed_data.get('tests')
            if not hasattr(self.ir, 'test_suites'):
                self.ir.test_suites = {}
            
            test_name = parsed_data.get('_file_name', 'default')
            self.ir.test_suites[test_name] = test_data

class TestFlowParser:
    """Parser for .testflow files"""
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a .testflow file"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove comments
        lines = content.split('\n')
        cleaned_lines = [line for line in lines if not line.lstrip().startswith('#')]
        cleaned_content = '\n'.join(cleaned_lines)
        
        try:
            return yaml.safe_load(cleaned_content) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse .testflow file: {str(e)}")

# Utility functions for parsing specific .flow components

def parse_model_fields(fields: List[Dict]) -> List[Dict]:
    """Parse and validate model fields"""
    
    parsed_fields = []
    
    for field in fields:
        if not isinstance(field, dict) or 'name' not in field:
            continue
        
        parsed_field = {
            'name': field['name'],
            'type': field.get('type', 'string'),
            'required': field.get('required', False),
            'unique': field.get('unique', False),
            'default': field.get('default'),
            'auto': field.get('auto', False)
        }
        
        # Validate field type
        valid_types = [
            'string', 'integer', 'float', 'boolean', 'date', 'datetime', 
            'timestamp', 'text', 'json', 'password', 'email', 'url', 'enum'
        ]
        
        if parsed_field['type'] not in valid_types:
            parsed_field['type'] = 'string'  # Default fallback
        
        parsed_fields.append(parsed_field)
    
    return parsed_fields

def parse_component(component: Dict) -> Dict:
    """Parse a UI component definition"""
    
    parsed_component = {
        'type': component.get('component', 'div'),
        'props': {}
    }
    
    # Extract common component properties
    for key, value in component.items():
        if key != 'component':
            parsed_component['props'][key] = value
    
    return parsed_component

def validate_endpoint(endpoint: Dict) -> bool:
    """Validate an endpoint definition"""
    
    required_fields = ['path', 'method']
    
    for field in required_fields:
        if field not in endpoint:
            return False
    
    # Validate HTTP method
    valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    if endpoint['method'].upper() not in valid_methods:
        return False
    
    return True

def parse_smart_field(field_config: Dict) -> Dict:
    """Parse smart form field configuration with intelligent validation"""
    
    smart_field = {
        'name': field_config.get('name', ''),
        'type': field_config.get('type', 'string'),
        'required': field_config.get('required', False),
        'smart_features': {}
    }
    
    # Smart field types with built-in intelligence
    smart_types = {
        'phone': {
            'validation': ['phone_format'],
            'auto_format': True,
            'geo_detect': True,
            'features': ['country_code_detection', 'format_as_you_type']
        },
        'email': {
            'validation': ['email_format', 'disposable_check'],
            'auto_complete': True,
            'features': ['typo_correction', 'domain_suggestions']
        },
        'password': {
            'validation': ['strength_meter'],
            'features': ['strength_indicator', 'requirements_display', 'show_hide_toggle'],
            'security': ['breach_check']
        },
        'otp': {
            'validation': ['numeric', 'length'],
            'auto_fill': True,
            'features': ['auto_detect_sms', 'auto_focus_next', 'resend_timer']
        },
        'credit_card': {
            'validation': ['luhn_check', 'cvv_format'],
            'auto_format': True,
            'features': ['brand_detection', 'format_as_you_type', 'security_icons']
        },
        'search': {
            'validation': [],
            'auto_complete': True,
            'features': ['typo_tolerance', 'context_aware_suggestions', 'recent_searches']
        },
        'address': {
            'validation': ['address_format'],
            'auto_complete': True,
            'features': ['geo_location_fill', 'address_validation', 'postal_code_lookup']
        },
        'date': {
            'validation': ['date_format', 'future_past_check'],
            'features': ['smart_date_picker', 'relative_dates', 'timezone_aware']
        },
        'number': {
            'validation': ['numeric_range'],
            'features': ['smart_formatting', 'currency_detection', 'unit_conversion']
        }
    }
    
    field_type = smart_field['type']
    if field_type in smart_types:
        smart_field['smart_features'] = smart_types[field_type]
    
    # Parse validation rules
    validation_config = field_config.get('validate', [])
    if isinstance(validation_config, str):
        validation_config = [validation_config]
    elif isinstance(validation_config, dict):
        validation_config = [validation_config]
    
    smart_validations = []
    for validation in validation_config:
        if isinstance(validation, str):
            smart_validations.append(parse_validation_rule(validation, field_type))
        elif isinstance(validation, dict):
            smart_validations.append(validation)
    
    smart_field['validations'] = smart_validations
    
    # Parse UX enhancements
    ux_config = field_config.get('ux', {})
    smart_field['ux_features'] = {
        'placeholder': ux_config.get('placeholder', ''),
        'tooltip': ux_config.get('tooltip', ''),
        'hint': ux_config.get('hint', ''),
        'auto_focus': ux_config.get('autoFocus', False),
        'progressive_disclosure': ux_config.get('progressiveDisclosure', False),
        'conditional_display': ux_config.get('conditionalDisplay', {}),
        'error_position': ux_config.get('errorPosition', 'below'),
        'show_strength_meter': ux_config.get('showStrengthMeter', False),
        'auto_fill': ux_config.get('autofill', False),
        'save_draft': ux_config.get('saveDraft', False)
    }
    
    # Parse security features
    security_config = field_config.get('security', {})
    smart_field['security_features'] = {
        'block_disposable': security_config.get('blockDisposable', False),
        'fraud_detection': security_config.get('fraudDetection', False),
        'device_recognition': security_config.get('deviceRecognition', False),
        'rate_limiting': security_config.get('rateLimiting', {}),
        'encryption': security_config.get('encryption', False)
    }
    
    return smart_field

def parse_validation_rule(rule: str, field_type: str) -> Dict:
    """Parse validation rule string into configuration"""
    
    validation_rules = {
        'required': {'type': 'required', 'message': 'This field is required'},
        'email': {'type': 'email', 'message': 'Please enter a valid email address'},
        'phone': {'type': 'phone', 'message': 'Please enter a valid phone number'},
        'strong': {'type': 'password_strength', 'min_score': 3, 'message': 'Password is not strong enough'},
        'registered': {'type': 'exists_check', 'endpoint': '/api/validate/registered', 'message': 'This {field} is not registered'},
        'unique': {'type': 'unique_check', 'endpoint': '/api/validate/unique', 'message': 'This {field} is already taken'},
        'min_length': {'type': 'min_length', 'value': 6, 'message': 'Must be at least 6 characters'},
        'max_length': {'type': 'max_length', 'value': 255, 'message': 'Must be less than 255 characters'},
        'numeric': {'type': 'numeric', 'message': 'Must be a valid number'},
        'positive': {'type': 'positive', 'message': 'Must be a positive number'},
        'future_date': {'type': 'future_date', 'message': 'Date must be in the future'},
        'past_date': {'type': 'past_date', 'message': 'Date must be in the past'},
        'credit_card': {'type': 'credit_card', 'message': 'Please enter a valid credit card number'},
        'cvv': {'type': 'cvv', 'message': 'Please enter a valid CVV'},
        'postal_code': {'type': 'postal_code', 'message': 'Please enter a valid postal code'},
        'url': {'type': 'url', 'message': 'Please enter a valid URL'},
        'ip_address': {'type': 'ip_address', 'message': 'Please enter a valid IP address'}
    }
    
    # Handle parameterized rules like min_length:8
    if ':' in rule:
        rule_name, param = rule.split(':', 1)
        if rule_name in validation_rules:
            config = validation_rules[rule_name].copy()
            config['value'] = param
            return config
    
    return validation_rules.get(rule, {'type': 'custom', 'rule': rule})

def parse_smart_form(form_config: Dict) -> Dict:
    """Parse smart form configuration with intelligent features"""
    
    smart_form = {
        'name': form_config.get('name', 'smart_form'),
        'method': form_config.get('method', 'POST'),
        'endpoint': form_config.get('endpoint', '/api/form/submit'),
        'fields': [],
        'smart_features': {},
        'ux_features': {},
        'security_features': {}
    }
    
    # Parse form fields
    fields_config = form_config.get('fields', {})
    for field_name, field_config in fields_config.items():
        if isinstance(field_config, dict):
            field_config['name'] = field_name
            smart_field = parse_smart_field(field_config)
            smart_form['fields'].append(smart_field)
        elif isinstance(field_config, str):
            # Simple field type definition
            simple_field = {
                'name': field_name,
                'type': field_config,
                'required': False
            }
            smart_field = parse_smart_field(simple_field)
            smart_form['fields'].append(smart_field)
    
    # Parse form-level smart features
    smart_features = form_config.get('smart_features', {})
    smart_form['smart_features'] = {
        'auto_save_draft': smart_features.get('autoSaveDraft', True),
        'smart_suggestions': smart_features.get('smartSuggestions', True),
        'conditional_logic': smart_features.get('conditionalLogic', True),
        'prefill_known_data': smart_features.get('prefillKnownData', True),
        'duplicate_detection': smart_features.get('duplicateDetection', False),
        'form_analytics': smart_features.get('formAnalytics', False)
    }
    
    # Parse UX features
    ux_features = form_config.get('ux_features', {})
    smart_form['ux_features'] = {
        'progress_indicator': ux_features.get('progressIndicator', False),
        'step_navigation': ux_features.get('stepNavigation', False),
        'inline_validation': ux_features.get('inlineValidation', True),
        'submit_states': ux_features.get('submitStates', True),  # loading, success, error
        'keyboard_navigation': ux_features.get('keyboardNavigation', True),
        'mobile_optimized': ux_features.get('mobileOptimized', True),
        'accessibility': ux_features.get('accessibility', True),
        'dark_mode': ux_features.get('darkMode', 'auto')
    }
    
    # Parse security features
    security_features = form_config.get('security_features', {})
    smart_form['security_features'] = {
        'csrf_protection': security_features.get('csrfProtection', True),
        'rate_limiting': security_features.get('rateLimiting', True),
        'honeypot': security_features.get('honeypot', True),
        'captcha': security_features.get('captcha', False),
        'secure_transmission': security_features.get('secureTransmission', True),
        'field_encryption': security_features.get('fieldEncryption', []),
        'audit_logging': security_features.get('auditLogging', False)
    }
    
    return smart_form
    
def _parse_page_smart_forms(self, page_body: List[Dict]):
    """Parse smart forms from page body components"""
        
    for component in page_body:
        if isinstance(component, dict):
            # Check if this component is a form
            if component.get('component') == 'form' or component.get('type') == 'form':
                form_config = component.copy()
                form_config['name'] = component.get('name', f"form_{len(getattr(self.ir, 'smart_forms', []))}") 
                smart_form = parse_smart_form(form_config)
                if not hasattr(self.ir, 'smart_forms'):
                    self.ir.smart_forms = []
                self.ir.smart_forms.append(smart_form)
                
            # Recursively check children
            if 'children' in component:
                self._parse_page_smart_forms(component['children'])
            elif 'body' in component:
                if isinstance(component['body'], list):
                    self._parse_page_smart_forms(component['body'])
                elif isinstance(component['body'], dict):
                    self._parse_page_smart_forms([component['body']])