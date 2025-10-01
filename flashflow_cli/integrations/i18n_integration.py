"""
i18n Integration for FlashFlow
Provides React components and Flask routes for internationalization support
"""

import os
import json
from typing import Dict, Any, List, Optional
from ..services.i18n_services import I18nManager
import logging

logger = logging.getLogger(__name__)

class I18nIntegration:
    """Main i18n integration class for FlashFlow"""
    
    def __init__(self):
        self.i18n_manager = I18nManager()
        self.generated_components = {}
        self.generated_routes = {}
        self.extracted_strings = []
    
    def initialize(self, config: Dict[str, Any] = None):
        """Initialize i18n services with FlashFlow configuration"""
        try:
            # Configure i18n system
            i18n_config = config or {
                'auto_translate': True,
                'providers': ['google_translate'],
                'fallback_language': 'en',
                'languages': [
                    {'code': 'en', 'name': 'English', 'direction': 'ltr', 'default': True, 'enabled': True},
                    {'code': 'es', 'name': 'Spanish', 'direction': 'ltr', 'default': False, 'enabled': True},
                    {'code': 'fr', 'name': 'French', 'direction': 'ltr', 'default': False, 'enabled': True},
                    {'code': 'de', 'name': 'German', 'direction': 'ltr', 'default': False, 'enabled': True},
                ]
            }
            self.i18n_manager.configure(i18n_config)
            
            logger.info("i18n integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize i18n integration: {e}")
            return False
    
    def extract_strings_from_project(self, project_path: str) -> List[str]:
        """Extract translatable strings from the project"""
        try:
            # This would use the I18nExtractor to find strings in the codebase
            # For now, we'll return a mock list of strings
            mock_strings = [
                "Welcome to our application",
                "Login",
                "Logout",
                "Dashboard",
                "Settings",
                "Profile",
                "Save Changes",
                "Cancel",
                "Delete",
                "Edit",
                "Create New",
                "Search...",
                "Loading...",
                "Error occurred",
                "Success",
                "Confirmation",
                "Are you sure?",
                "Yes",
                "No"
            ]
            
            # Add these strings to the manager
            for string in mock_strings:
                key = self._generate_key(string)
                self.i18n_manager.add_translation(key, string)
            
            self.extracted_strings = mock_strings
            logger.info(f"Extracted {len(mock_strings)} translatable strings")
            return mock_strings
            
        except Exception as e:
            logger.error(f"Failed to extract strings from project: {e}")
            return []
    
    def _generate_key(self, text: str) -> str:
        """Generate a translation key from text"""
        # Convert to lowercase and replace spaces with underscores
        key = text.lower().replace(' ', '_').replace('.', '').replace('...', '')
        # Remove special characters
        key = ''.join(c for c in key if c.isalnum() or c == '_')
        return key
    
    def generate_react_components(self) -> Dict[str, str]:
        """Generate React components for i18n functionality"""
        components = {}
        
        try:
            # Translation provider component
            components['I18nProvider'] = self._generate_i18n_provider_component()
            
            # Translation hook
            components['useTranslation'] = self._generate_translation_hook()
            
            # Language selector component
            components['LanguageSelector'] = self._generate_language_selector_component()
            
            # Trans component for rendering translations
            components['Trans'] = self._generate_trans_component()
            
            self.generated_components = components
            logger.info(f"Generated {len(components)} i18n React components")
            return components
            
        except Exception as e:
            logger.error(f"Failed to generate React components: {e}")
            return {}
    
    def generate_flask_routes(self) -> Dict[str, str]:
        """Generate Flask routes for i18n API"""
        routes = {}
        
        try:
            # Get available languages endpoint
            routes['languages_endpoint'] = self._generate_languages_endpoint()
            
            # Get translation endpoint
            routes['translation_endpoint'] = self._generate_translation_endpoint()
            
            # Set language endpoint
            routes['set_language_endpoint'] = self._generate_set_language_endpoint()
            
            # Export translations endpoint
            routes['export_translations_endpoint'] = self._generate_export_translations_endpoint()
            
            self.generated_routes = routes
            logger.info(f"Generated {len(routes)} i18n Flask routes")
            return routes
            
        except Exception as e:
            logger.error(f"Failed to generate Flask routes: {e}")
            return {}
    
    def _generate_i18n_provider_component(self) -> str:
        """Generate i18n provider component"""
        return '''import React, { createContext, useContext, useState, useEffect } from 'react';

const I18nContext = createContext();

export const I18nProvider = ({ children, defaultLanguage = 'en' }) => {
  const [language, setLanguage] = useState(defaultLanguage);
  const [translations, setTranslations] = useState({});
  
  // Load language from localStorage or browser settings
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage) {
      setLanguage(savedLanguage);
    } else {
      // Detect browser language
      const browserLang = navigator.language.split('-')[0];
      setLanguage(browserLang);
    }
  }, []);
  
  // Save language to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);
  
  // Fetch translations when language changes
  useEffect(() => {
    fetch(`/api/i18n/translations/${language}`)
      .then(response => response.json())
      .then(data => setTranslations(data))
      .catch(error => console.error('Failed to load translations:', error));
  }, [language]);
  
  const value = {
    language,
    setLanguage,
    translations,
    t: (key, params = {}) => {
      const translation = translations[key] || key;
      // Replace parameters in the translation
      let result = translation;
      Object.keys(params).forEach(param => {
        result = result.replace(new RegExp(`{${param}}`, 'g'), params[param]);
      });
      return result;
    }
  };
  
  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
};

export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};

export default I18nProvider;'''
    
    def _generate_translation_hook(self) -> str:
        """Generate translation hook"""
        return '''import { useI18n } from './I18nProvider';

export const useTranslation = () => {
  const { t, language, setLanguage } = useI18n();
  
  return {
    t,
    language,
    setLanguage,
    changeLanguage: (newLanguage) => {
      setLanguage(newLanguage);
    }
  };
};

export default useTranslation;'''
    
    def _generate_language_selector_component(self) -> str:
        """Generate language selector component"""
        return '''import React from 'react';
import { useI18n } from './I18nProvider';
import { 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel,
  Box,
  Typography
} from '@mui/material';
import { Language as LanguageIcon } from '@mui/icons-material';

export const LanguageSelector = ({ 
  variant = 'standard',
  showLabel = true,
  showIcon = true,
  size = 'medium'
}) => {
  const { language, setLanguage } = useI18n();
  
  // Available languages - in a real app, this would come from the API
  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Español' },
    { code: 'fr', name: 'Français' },
    { code: 'de', name: 'Deutsch' }
  ];
  
  const handleChange = (event) => {
    setLanguage(event.target.value);
  };
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 120 }}>
      {showIcon && <LanguageIcon sx={{ mr: 1 }} />}
      <FormControl fullWidth size={size}>
        {showLabel && <InputLabel>Language</InputLabel>}
        <Select
          value={language}
          onChange={handleChange}
          variant={variant}
          label={showLabel ? "Language" : undefined}
        >
          {languages.map((lang) => (
            <MenuItem key={lang.code} value={lang.code}>
              {lang.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};

export default LanguageSelector;'''
    
    def _generate_trans_component(self) -> str:
        """Generate Trans component for rendering translations"""
        return '''import React from 'react';
import { useI18n } from './I18nProvider';

export const Trans = ({ 
  i18nKey, 
  values = {}, 
  components = {},
  fallback = null,
  ...props 
}) => {
  const { t } = useI18n();
  
  if (!i18nKey) {
    return fallback || null;
  }
  
  const translation = t(i18nKey, values);
  
  // Simple interpolation of components
  // In a real implementation, this would be more sophisticated
  let result = translation;
  
  // Replace component placeholders like {{componentName}}
  Object.keys(components).forEach(componentName => {
    const placeholder = `{{${componentName}}}`;
    if (result.includes(placeholder)) {
      result = result.replace(placeholder, components[componentName]);
    }
  });
  
  return <span {...props}>{result}</span>;
};

export default Trans;'''
    
    def _generate_languages_endpoint(self) -> str:
        """Generate endpoint for getting available languages"""
        return '''from flask import jsonify
from .i18n_services import I18nManager

def get_available_languages():
    """Get list of available languages"""
    try:
        i18n_manager = I18nManager()
        languages = i18n_manager.get_available_languages()
        return jsonify({
            'success': True,
            'languages': languages
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add to your Flask app:
# @app.route('/api/i18n/languages', methods=['GET'])
# def api_get_languages():
#     return get_available_languages()'''
    
    def _generate_translation_endpoint(self) -> str:
        """Generate endpoint for getting translations"""
        return '''from flask import jsonify, request
from .i18n_services import I18nManager

def get_translations(language):
    """Get translations for a specific language"""
    try:
        i18n_manager = I18nManager()
        # In a real implementation, load translations from storage
        # For demo, we'll return a sample set
        sample_translations = {
            'welcome_to_our_application': {
                'en': 'Welcome to our application',
                'es': 'Bienvenido a nuestra aplicación',
                'fr': 'Bienvenue dans notre application',
                'de': 'Willkommen in unserer Anwendung'
            },
            'login': {
                'en': 'Login',
                'es': 'Iniciar sesión',
                'fr': 'Connexion',
                'de': 'Anmelden'
            },
            'logout': {
                'en': 'Logout',
                'es': 'Cerrar sesión',
                'fr': 'Déconnexion',
                'de': 'Abmelden'
            }
        }
        
        # Extract translations for the requested language
        result = {}
        for key, translations in sample_translations.items():
            result[key] = translations.get(language, translations.get('en', key))
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

# Add to your Flask app:
# @app.route('/api/i18n/translations/<language>', methods=['GET'])
# def api_get_translations(language):
#     return get_translations(language)'''
    
    def _generate_set_language_endpoint(self) -> str:
        """Generate endpoint for setting language"""
        return '''from flask import jsonify, request

def set_language():
    """Set the current language"""
    try:
        data = request.get_json()
        language = data.get('language')
        
        if not language:
            return jsonify({
                'success': False,
                'error': 'Language is required'
            }), 400
        
        # In a real implementation, you would validate the language
        # and possibly store the user's preference
        
        return jsonify({
            'success': True,
            'message': f'Language set to {language}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add to your Flask app:
# @app.route('/api/i18n/language', methods=['POST'])
# def api_set_language():
#     return set_language()'''
    
    def _generate_export_translations_endpoint(self) -> str:
        """Generate endpoint for exporting translations"""
        return '''from flask import jsonify, request
from .i18n_services import I18nManager

def export_translations():
    """Export all translations"""
    try:
        i18n_manager = I18nManager()
        # In a real implementation, this would export actual translations
        # For demo, we'll return a sample structure
        sample_export = {
            'welcome_to_our_application': {
                'default': 'Welcome to our application',
                'translations': {
                    'es': 'Bienvenido a nuestra aplicación',
                    'fr': 'Bienvenue dans notre application',
                    'de': 'Willkommen in unserer Anwendung'
                },
                'context': 'Main application welcome message'
            },
            'login': {
                'default': 'Login',
                'translations': {
                    'es': 'Iniciar sesión',
                    'fr': 'Connexion',
                    'de': 'Anmelden'
                },
                'context': 'Login button text'
            }
        }
        
        format_type = request.args.get('format', 'json')
        
        if format_type == 'json':
            return jsonify(sample_export)
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported format'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add to your Flask app:
# @app.route('/api/i18n/export', methods=['GET'])
# def api_export_translations():
#     return export_translations()'''