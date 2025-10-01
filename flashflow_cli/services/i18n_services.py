"""
i18n Services for FlashFlow
Provides internationalization and localization support with automatic translation and language detection
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
import re
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class TranslationEntry:
    """Represents a single translation entry"""
    key: str
    default_value: str
    translations: Dict[str, str]  # language_code -> translated_text
    context: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class LanguageConfig:
    """Configuration for a language"""
    code: str  # ISO language code (e.g., 'en', 'es', 'fr')
    name: str  # Full name (e.g., 'English', 'Spanish')
    direction: str = 'ltr'  # 'ltr' or 'rtl'
    default: bool = False
    enabled: bool = True

class I18nManager:
    """Main i18n manager for FlashFlow applications"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.translations: Dict[str, TranslationEntry] = {}
        self.languages: List[LanguageConfig] = []
        self.default_language = 'en'
        self.fallback_language = 'en'
        self.supported_languages = ['en']
        self.translation_cache: Dict[str, str] = {}
        self.auto_translate_enabled = self.config.get('auto_translate', True)
        self.translation_providers = self.config.get('providers', ['google_translate'])
        self.translation_api_keys = self.config.get('api_keys', {})
        
        # Initialize with default languages
        self._initialize_default_languages()
    
    def _initialize_default_languages(self):
        """Initialize with default language configurations"""
        default_langs = [
            LanguageConfig('en', 'English', 'ltr', True, True),
            LanguageConfig('es', 'Spanish', 'ltr', False, True),
            LanguageConfig('fr', 'French', 'ltr', False, True),
            LanguageConfig('de', 'German', 'ltr', False, True),
            LanguageConfig('it', 'Italian', 'ltr', False, True),
            LanguageConfig('pt', 'Portuguese', 'ltr', False, True),
            LanguageConfig('ru', 'Russian', 'ltr', False, True),
            LanguageConfig('zh', 'Chinese', 'ltr', False, True),
            LanguageConfig('ja', 'Japanese', 'ltr', False, True),
            LanguageConfig('ar', 'Arabic', 'rtl', False, True),
        ]
        self.languages = default_langs
        self.supported_languages = [lang.code for lang in default_langs if lang.enabled]
        self.default_language = 'en'
        self.fallback_language = 'en'
    
    def configure(self, config: Dict[str, Any]):
        """Configure i18n system with provided settings"""
        self.config = config
        self.auto_translate_enabled = config.get('auto_translate', True)
        self.translation_providers = config.get('providers', ['google_translate'])
        self.translation_api_keys = config.get('api_keys', {})
        self.fallback_language = config.get('fallback_language', 'en')
        
        # Load language configurations if provided
        if 'languages' in config:
            self.languages = []
            for lang_data in config['languages']:
                lang_config = LanguageConfig(**lang_data)
                self.languages.append(lang_config)
                if lang_config.default:
                    self.default_language = lang_config.code
                if lang_config.enabled:
                    self.supported_languages.append(lang_config.code)
        
        logger.info(f"I18n configured with {len(self.supported_languages)} languages")
    
    def add_translation(self, key: str, default_value: str, context: Optional[str] = None) -> bool:
        """Add a new translation entry"""
        try:
            # Check if translation already exists
            if key in self.translations:
                # Update existing entry
                entry = self.translations[key]
                entry.default_value = default_value
                entry.context = context
            else:
                # Create new entry
                entry = TranslationEntry(
                    key=key,
                    default_value=default_value,
                    translations={},
                    context=context
                )
                self.translations[key] = entry
            
            # Auto-translate if enabled
            if self.auto_translate_enabled:
                self._auto_translate_entry(entry)
            
            # Clear cache for this key
            if key in self.translation_cache:
                del self.translation_cache[key]
            
            logger.debug(f"Added translation entry: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add translation for key '{key}': {e}")
            return False
    
    def translate(self, key: str, language: str = None, params: Dict[str, Any] = None) -> str:
        """Translate a key to the specified language"""
        try:
            # Use current language or default
            if not language:
                language = self.default_language
            
            # Check cache first
            cache_key = f"{key}_{language}"
            if cache_key in self.translation_cache:
                result = self.translation_cache[cache_key]
            else:
                # Get translation entry
                if key not in self.translations:
                    logger.warning(f"Translation key '{key}' not found")
                    return key  # Return key as fallback
                
                entry = self.translations[key]
                
                # Try to get translation for requested language
                if language in entry.translations and entry.translations[language]:
                    result = entry.translations[language]
                elif self.fallback_language in entry.translations:
                    result = entry.translations[self.fallback_language]
                    logger.debug(f"Using fallback language for key '{key}'")
                else:
                    result = entry.default_value
                    logger.debug(f"Using default value for key '{key}'")
                
                # Cache the result
                self.translation_cache[cache_key] = result
            
            # Apply parameter substitution if provided
            if params:
                result = self._substitute_params(result, params)
            
            return result
            
        except Exception as e:
            logger.error(f"Translation error for key '{key}': {e}")
            return key  # Return key as ultimate fallback
    
    def _substitute_params(self, text: str, params: Dict[str, Any]) -> str:
        """Substitute parameters in translation text"""
        try:
            # Replace {param} style placeholders
            for key, value in params.items():
                placeholder = f"{{{key}}}"
                text = text.replace(placeholder, str(value))
            return text
        except Exception as e:
            logger.error(f"Parameter substitution error: {e}")
            return text
    
    def _auto_translate_entry(self, entry: TranslationEntry):
        """Auto-translate an entry to all supported languages"""
        try:
            if not self.auto_translate_enabled:
                return
            
            # Translate to all supported languages except default
            for lang_code in self.supported_languages:
                if lang_code != self.default_language and lang_code not in entry.translations:
                    translated = self._translate_text(entry.default_value, lang_code)
                    if translated:
                        entry.translations[lang_code] = translated
            
            logger.debug(f"Auto-translated entry: {entry.key}")
        except Exception as e:
            logger.error(f"Auto-translation failed for entry '{entry.key}': {e}")
    
    def _translate_text(self, text: str, target_language: str) -> Optional[str]:
        """Translate text using configured provider"""
        try:
            # For now, we'll return a mock translation
            # In a real implementation, this would call actual translation APIs
            if target_language == 'es':
                return f"[ES] {text}"
            elif target_language == 'fr':
                return f"[FR] {text}"
            elif target_language == 'de':
                return f"[DE] {text}"
            else:
                return f"[{target_language.upper()}] {text}"
        except Exception as e:
            logger.error(f"Translation failed for '{text}' to {target_language}: {e}")
            return None
    
    def detect_language(self, text: str) -> str:
        """Detect the language of given text"""
        # Simple mock implementation
        # In a real implementation, this would use language detection libraries
        return self.default_language
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """Get list of available languages"""
        return [
            {
                'code': lang.code,
                'name': lang.name,
                'direction': lang.direction,
                'default': lang.default
            }
            for lang in self.languages if lang.enabled
        ]
    
    def set_current_language(self, language_code: str):
        """Set the current language for the application"""
        if language_code in self.supported_languages:
            self.default_language = language_code
            # Clear cache when language changes
            self.translation_cache.clear()
            logger.info(f"Current language set to: {language_code}")
        else:
            logger.warning(f"Unsupported language code: {language_code}")
    
    def export_translations(self, format: str = 'json') -> Union[str, Dict]:
        """Export all translations in specified format"""
        if format.lower() == 'json':
            export_data = {}
            for key, entry in self.translations.items():
                export_data[key] = {
                    'default': entry.default_value,
                    'translations': entry.translations,
                    'context': entry.context
                }
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        else:
            # Return as dictionary
            export_data = {}
            for key, entry in self.translations.items():
                export_data[key] = {
                    'default': entry.default_value,
                    'translations': entry.translations,
                    'context': entry.context
                }
            return export_data
    
    def import_translations(self, data: Union[str, Dict], format: str = 'json'):
        """Import translations from data"""
        try:
            if format.lower() == 'json' and isinstance(data, str):
                import_data = json.loads(data)
            else:
                import_data = data
            
            imported_count = 0
            for key, entry_data in import_data.items():
                entry = TranslationEntry(
                    key=key,
                    default_value=entry_data.get('default', ''),
                    translations=entry_data.get('translations', {}),
                    context=entry_data.get('context')
                )
                self.translations[key] = entry
                imported_count += 1
            
            logger.info(f"Imported {imported_count} translation entries")
            return True
        except Exception as e:
            logger.error(f"Failed to import translations: {e}")
            return False

class I18nExtractor:
    """Extract translatable strings from code"""
    
    def __init__(self):
        self.patterns = [
            r't\(["\']([^"\']+)["\']\)',
            r'translate\(["\']([^"\']+)["\']\)',
            r'i18n\(["\']([^"\']+)["\']\)',
            r'{{\s*t\(["\']([^"\']+)["\']\)\s*}}',
        ]
    
    def extract_from_file(self, file_path: str) -> List[str]:
        """Extract translatable strings from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            strings = []
            for pattern in self.patterns:
                matches = re.findall(pattern, content)
                strings.extend(matches)
            
            # Remove duplicates
            return list(set(strings))
        except Exception as e:
            logger.error(f"Failed to extract strings from {file_path}: {e}")
            return []
    
    def extract_from_directory(self, directory: str, extensions: List[str] = None) -> Dict[str, List[str]]:
        """Extract translatable strings from all files in directory"""
        if extensions is None:
            extensions = ['.js', '.jsx', '.ts', '.tsx', '.py', '.html', '.vue']
        
        results = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    strings = self.extract_from_file(file_path)
                    if strings:
                        results[file_path] = strings
        
        return results