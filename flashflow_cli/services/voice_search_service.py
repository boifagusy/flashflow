"""
FlashFlow Voice Search and Speech Recognition Service
Provides voice input, speech recognition, and voice search capabilities
"""

import json
import tempfile
import os
import wave
import io
import re
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import threading
import time


class VoiceCommandRegistry:
    """Registry for voice commands and pattern matching"""
    
    def __init__(self):
        self.commands = {}
        self.patterns = {}
    
    def register_command(self, name: str, patterns: List[str], description: str, parameters: Dict = None):
        """Register a voice command with patterns"""
        self.commands[name] = {
            'name': name,
            'patterns': patterns,
            'description': description,
            'parameters': parameters or {}
        }
        
        # Compile patterns for matching
        for pattern in patterns:
            regex_pattern = pattern.replace('*', '(.+)')
            self.patterns[re.compile(regex_pattern, re.IGNORECASE)] = name
    
    def match_command(self, text: str) -> Optional[Dict]:
        """Match input text to registered commands"""
        for pattern, command_name in self.patterns.items():
            match = pattern.match(text.strip())
            if match:
                return {
                    'command': command_name,
                    'matches': match.groups(),
                    'confidence': 0.9,
                    'original_text': text
                }
        return None
    
    def get_all_commands(self) -> Dict:
        """Get all registered commands"""
        return self.commands


class VoiceIntentClassifier:
    """Classify voice input into intents and extract entities"""
    
    def __init__(self):
        self.intent_patterns = {
            'search': [r'search for (.+)', r'find (.+)', r'look for (.+)', r'show me (.+)'],
            'navigation': [r'go to (.+)', r'navigate to (.+)', r'open (.+)', r'take me to (.+)'],
            'action': [r'create (.+)', r'delete (.+)', r'update (.+)', r'edit (.+)'],
            'query': [r'what is (.+)', r'how (.+)', r'when (.+)', r'where (.+)'],
            'help': [r'help', r'how to (.+)', r'show help', r'what can (.+)']
        }
        
        self.entity_patterns = {
            'product': [r'\b(phone|laptop|computer|tablet|headphones|camera)\b'],
            'color': [r'\b(red|blue|green|yellow|black|white|gray|purple)\b'],
            'price': [r'\$([0-9,]+(?:\.[0-9]{2})?)', r'under ([0-9,]+)', r'less than ([0-9,]+)'],
            'number': [r'\b([0-9]+)\b'],
            'size': [r'\b(small|medium|large|xl|xxl)\b']
        }
    
    def classify_intent(self, text: str) -> Optional[Dict]:
        """Classify the intent of the voice input"""
        text = text.lower().strip()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return {
                        'intent': intent,
                        'confidence': 0.8,
                        'text': text,
                        'pattern_matched': pattern
                    }
        
        return {
            'intent': 'unknown',
            'confidence': 0.1,
            'text': text,
            'pattern_matched': None
        }
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract entities from voice input"""
        entities = []
        text = text.lower()
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'type': entity_type,
                        'value': match.group(1) if match.groups() else match.group(0),
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.9
                    })
        
        return entities


class RealTimeVoiceProcessor:
    """Real-time voice processing and activity detection"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 16000)
        self.chunk_size = self.config.get('chunk_size', 1024)
        self.silence_threshold = self.config.get('silence_threshold', 500)
        self.silence_duration = self.config.get('silence_duration', 1.0)
        self.is_listening = False
        self.audio_buffer = []
        
    def _detect_voice_activity(self, audio_data: Dict) -> bool:
        """Detect if audio contains voice activity"""
        audio_level = audio_data.get('audio_level', 0)
        return audio_level > self.silence_threshold
    
    def start_processing(self, callback: callable):
        """Start real-time voice processing"""
        self.is_listening = True
        
        def process_audio():
            while self.is_listening:
                # Simulate audio processing
                audio_data = {'audio_level': 600}  # Simulated
                if self._detect_voice_activity(audio_data):
                    callback({'status': 'voice_detected', 'data': audio_data})
                time.sleep(0.1)
        
        thread = threading.Thread(target=process_audio)
        thread.daemon = True
        thread.start()
    
    def stop_processing(self):
        """Stop real-time voice processing"""
        self.is_listening = False

class SpeechRecognitionService:
    """Speech recognition service with multiple provider support"""
    
    def __init__(self):
        self.providers = {
            'google': self._init_google_speech,
            'azure': self._init_azure_speech,
            'whisper': self._init_whisper,
            'vosk': self._init_vosk,
            'sphinx': self._init_sphinx
        }
        self.active_provider = None
        self.provider_config = {}
        self.is_listening = False
        self.audio_thread = None
        
        # Initialize provider configurations
        self.google_config = {
            'language': 'en-US',
            'timeout': 5,
            'phrase_timeout': 1,
            'api_key': None
        }
        
        self.azure_config = {
            'speech_key': None,
            'service_region': 'eastus',
            'language': 'en-US',
            'timeout': 5
        }
        
        self.whisper_config = {
            'model_size': 'base',
            'device': 'auto',
            'language': 'en',
            'temperature': 0.0
        }
        
        self.vosk_config = {
            'model_path': None,
            'sample_rate': 16000,
            'chunk_size': 4096
        }
        
        self.sphinx_config = {
            'language': 'en-US',
            'timeout': 5
        }
    
    def _init_google_speech(self, config: Dict) -> bool:
        """Initialize Google Speech-to-Text"""
        try:
            import speech_recognition as sr
            
            self.provider_config['google'] = {
                'recognizer': sr.Recognizer(),
                'microphone': sr.Microphone(),
                'language': config.get('language', 'en-US'),
                'timeout': config.get('timeout', 5),
                'phrase_timeout': config.get('phrase_timeout', 1),
                'api_key': config.get('api_key', None)
            }
            
            # Adjust for ambient noise
            with self.provider_config['google']['microphone'] as source:
                self.provider_config['google']['recognizer'].adjust_for_ambient_noise(source, duration=1)
            
            return True
        except ImportError:
            return False
    
    def _init_azure_speech(self, config: Dict) -> bool:
        """Initialize Azure Speech Services"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            speech_key = config.get('speech_key')
            service_region = config.get('service_region', 'eastus')
            
            if not speech_key:
                return False
            
            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
            speech_config.speech_recognition_language = config.get('language', 'en-US')
            
            self.provider_config['azure'] = {
                'speech_config': speech_config,
                'audio_config': speechsdk.audio.AudioConfig(use_default_microphone=True),
                'timeout': config.get('timeout', 5)
            }
            return True
        except ImportError:
            return False
    
    def _init_whisper(self, config: Dict) -> bool:
        """Initialize OpenAI Whisper"""
        try:
            import whisper
            import torch
            
            model_size = config.get('model_size', 'base')
            device = config.get('device', 'auto')
            
            if device == 'auto':
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
            
            model = whisper.load_model(model_size, device=device)
            
            self.provider_config['whisper'] = {
                'model': model,
                'language': config.get('language', 'en'),
                'device': device,
                'temperature': config.get('temperature', 0.0)
            }
            return True
        except ImportError:
            return False
    
    def _init_vosk(self, config: Dict) -> bool:
        """Initialize Vosk offline speech recognition"""
        try:
            import vosk
            import pyaudio
            
            model_path = config.get('model_path')
            if not model_path or not os.path.exists(model_path):
                return False
            
            model = vosk.Model(model_path)
            rec = vosk.KaldiRecognizer(model, 16000)
            
            self.provider_config['vosk'] = {
                'model': model,
                'recognizer': rec,
                'sample_rate': 16000,
                'chunk_size': config.get('chunk_size', 4096)
            }
            return True
        except ImportError:
            return False
    
    def _init_sphinx(self, config: Dict) -> bool:
        """Initialize CMU Sphinx (PocketSphinx)"""
        try:
            import speech_recognition as sr
            
            self.provider_config['sphinx'] = {
                'recognizer': sr.Recognizer(),
                'microphone': sr.Microphone(),
                'language': config.get('language', 'en-US'),
                'timeout': config.get('timeout', 5)
            }
            return True
        except ImportError:
            return False
    
    def setup_provider(self, provider_name: str, config: Dict = None) -> bool:
        """Setup speech recognition provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Unsupported speech provider: {provider_name}")
        
        config = config or {}
        success = self.providers[provider_name](config)
        
        if success:
            self.active_provider = provider_name
            return True
        return False
    
    def get_available_providers(self) -> List[str]:
        """Get list of available speech recognition providers"""
        available = []
        
        # Test each provider to see if it's available
        for provider_name in self.providers.keys():
            try:
                if provider_name == 'google' or provider_name == 'sphinx':
                    import speech_recognition
                    available.append(provider_name)
                elif provider_name == 'azure':
                    import azure.cognitiveservices.speech
                    available.append(provider_name)
                elif provider_name == 'whisper':
                    import whisper
                    available.append(provider_name)
                elif provider_name == 'vosk':
                    import vosk
                    available.append(provider_name)
            except ImportError:
                continue
        
        # Always include web_speech_api as it's browser-based
        available.append('web_speech_api')
        
        return available
    
    def recognize_from_audio(self, audio_data: Union[str, bytes], options: Dict = None) -> Dict:
        """Recognize speech from audio data"""
        if not self.active_provider:
            raise RuntimeError("No speech recognition provider configured")
        
        options = options or {}
        
        try:
            if self.active_provider == 'google':
                return self._recognize_google(audio_data, options)
            elif self.active_provider == 'azure':
                return self._recognize_azure(audio_data, options)
            elif self.active_provider == 'whisper':
                return self._recognize_whisper(audio_data, options)
            elif self.active_provider == 'vosk':
                return self._recognize_vosk(audio_data, options)
            elif self.active_provider == 'sphinx':
                return self._recognize_sphinx(audio_data, options)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0,
                'alternatives': [],
                'language': 'unknown'
            }
    
    def start_continuous_recognition(self, callback_func: callable, options: Dict = None) -> bool:
        """Start continuous speech recognition"""
        if self.is_listening:
            return False
        
        self.is_listening = True
        options = options or {}
        
        def recognition_thread():
            while self.is_listening:
                try:
                    result = self.listen_once(options)
                    if result['success'] and result['text'].strip():
                        callback_func(result)
                except Exception as e:
                    callback_func({
                        'success': False,
                        'error': str(e),
                        'text': '',
                        'confidence': 0
                    })
                time.sleep(0.1)  # Small delay to prevent overwhelming the system
        
        self.audio_thread = threading.Thread(target=recognition_thread)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
        return True
    
    def stop_continuous_recognition(self):
        """Stop continuous speech recognition"""
        self.is_listening = False
        if self.audio_thread:
            self.audio_thread.join(timeout=2)
    
    def listen_once(self, options: Dict = None) -> Dict:
        """Listen for speech once and return recognition result"""
        if not self.active_provider:
            raise RuntimeError("No speech recognition provider configured")
        
        options = options or {}
        
        try:
            if self.active_provider in ['google', 'sphinx']:
                return self._listen_speech_recognition(options)
            elif self.active_provider == 'azure':
                return self._listen_azure(options)
            elif self.active_provider == 'vosk':
                return self._listen_vosk(options)
            else:
                return {
                    'success': False,
                    'error': 'Real-time listening not supported for this provider',
                    'text': '',
                    'confidence': 0
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0
            }
    
    def _recognize_google(self, audio_data: Union[str, bytes], options: Dict) -> Dict:
        """Recognize speech using Google Speech-to-Text"""
        import speech_recognition as sr
        
        config = self.provider_config['google']
        recognizer = config['recognizer']
        
        # Handle audio data
        if isinstance(audio_data, str):
            # Audio file path
            with sr.AudioFile(audio_data) as source:
                audio = recognizer.record(source)
        else:
            # Raw audio bytes
            audio = sr.AudioData(audio_data, 16000, 2)
        
        try:
            # Use Google Web Speech API
            if config['api_key']:
                text = recognizer.recognize_google(
                    audio, 
                    key=config['api_key'],
                    language=config['language'],
                    show_all=True
                )
            else:
                text = recognizer.recognize_google(
                    audio, 
                    language=config['language'],
                    show_all=True
                )
            
            if isinstance(text, dict) and 'alternative' in text:
                alternatives = text['alternative']
                if alternatives:
                    best = alternatives[0]
                    return {
                        'success': True,
                        'text': best.get('transcript', ''),
                        'confidence': best.get('confidence', 0.95) * 100,
                        'alternatives': [alt.get('transcript', '') for alt in alternatives[1:5]],
                        'language': config['language'],
                        'provider': 'google'
                    }
            elif isinstance(text, str):
                return {
                    'success': True,
                    'text': text,
                    'confidence': 95,
                    'alternatives': [],
                    'language': config['language'],
                    'provider': 'google'
                }
            
            return {
                'success': False,
                'error': 'No speech detected',
                'text': '',
                'confidence': 0
            }
            
        except sr.UnknownValueError:
            return {
                'success': False,
                'error': 'Could not understand audio',
                'text': '',
                'confidence': 0
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'error': f'Google Speech API error: {e}',
                'text': '',
                'confidence': 0
            }
    
    def _recognize_whisper(self, audio_data: Union[str, bytes], options: Dict) -> Dict:
        """Recognize speech using OpenAI Whisper"""
        config = self.provider_config['whisper']
        model = config['model']
        
        try:
            if isinstance(audio_data, str):
                # Audio file path
                result = model.transcribe(
                    audio_data,
                    language=config['language'],
                    temperature=config['temperature']
                )
            else:
                # Save bytes to temporary file for Whisper
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_path = tmp_file.name
                
                try:
                    result = model.transcribe(
                        tmp_path,
                        language=config['language'],
                        temperature=config['temperature']
                    )
                finally:
                    os.unlink(tmp_path)
            
            return {
                'success': True,
                'text': result['text'].strip(),
                'confidence': 90,  # Whisper doesn't provide confidence scores
                'alternatives': [],
                'language': result.get('language', config['language']),
                'provider': 'whisper'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Whisper error: {e}',
                'text': '',
                'confidence': 0
            }
    
    def _listen_speech_recognition(self, options: Dict) -> Dict:
        """Listen using speech_recognition library"""
        import speech_recognition as sr
        
        config = self.provider_config[self.active_provider]
        recognizer = config['recognizer']
        microphone = config['microphone']
        
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(
                    source, 
                    timeout=config['timeout'],
                    phrase_time_limit=config.get('phrase_timeout', 5)
                )
            
            if self.active_provider == 'google':
                text = recognizer.recognize_google(audio, language=config['language'])
                return {
                    'success': True,
                    'text': text,
                    'confidence': 95,
                    'alternatives': [],
                    'language': config['language'],
                    'provider': 'google'
                }
            elif self.active_provider == 'sphinx':
                text = recognizer.recognize_sphinx(audio)
                return {
                    'success': True,
                    'text': text,
                    'confidence': 80,
                    'alternatives': [],
                    'language': config['language'],
                    'provider': 'sphinx'
                }
                
        except sr.WaitTimeoutError:
            return {
                'success': False,
                'error': 'Listening timeout',
                'text': '',
                'confidence': 0
            }
        except sr.UnknownValueError:
            return {
                'success': False,
                'error': 'Could not understand audio',
                'text': '',
                'confidence': 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0
            }


class VoiceSearchService:
    """Voice search service with query processing and response"""
    
    def __init__(self, speech_service: SpeechRecognitionService = None):
        self.speech_service = speech_service or SpeechRecognitionService()
        self.search_providers = {
            'local': self._search_local,
            'elasticsearch': self._search_elasticsearch,
            'database': self._search_database,
            'api': self._search_api
        }
        self.search_config = {}
        self.voice_commands = {}
        self.nlp_processor = None
        
        # Initialize missing components for testing
        self.command_registry = VoiceCommandRegistry()
        self.intent_classifier = VoiceIntentClassifier()
    
    def setup_search_provider(self, provider_name: str, config: Dict) -> bool:
        """Setup search provider configuration"""
        if provider_name not in self.search_providers:
            return False
        
        self.search_config[provider_name] = config
        return True
    
    def register_voice_command(self, trigger_phrase: str, handler_func: callable, description: str = ""):
        """Register a voice command with trigger phrase"""
        self.voice_commands[trigger_phrase.lower()] = {
            'handler': handler_func,
            'description': description,
            'trigger': trigger_phrase
        }
    
    def process_voice_query(self, audio_data: Union[str, bytes] = None, options: Dict = None) -> Dict:
        """Process voice query and return search results"""
        options = options or {}
        
        # Step 1: Convert speech to text
        if audio_data:
            speech_result = self.speech_service.recognize_from_audio(audio_data, options)
        else:
            # Listen for voice input
            speech_result = self.speech_service.listen_once(options)
        
        if not speech_result['success']:
            return {
                'success': False,
                'error': speech_result['error'],
                'query': '',
                'results': [],
                'speech_result': speech_result
            }
        
        query_text = speech_result['text'].strip()
        
        # Step 2: Process the query
        return self.search_by_text(query_text, {
            'speech_result': speech_result,
            **options
        })
    
    def search_by_text(self, query_text: str, options: Dict = None) -> Dict:
        """Search using text query"""
        options = options or {}
        
        # Check for voice commands first
        command_result = self._check_voice_commands(query_text)
        if command_result:
            return command_result
        
        # Process search query
        processed_query = self._process_query(query_text, options)
        
        # Execute search across configured providers
        search_results = []
        search_providers = options.get('providers', ['local'])
        
        for provider in search_providers:
            if provider in self.search_config:
                try:
                    results = self.search_providers[provider](processed_query, self.search_config[provider])
                    search_results.extend(results)
                except Exception as e:
                    print(f"Search provider {provider} failed: {e}")
        
        # Sort and deduplicate results
        final_results = self._rank_results(search_results, processed_query)
        
        return {
            'success': True,
            'query': query_text,
            'processed_query': processed_query,
            'results': final_results,
            'result_count': len(final_results),
            'speech_result': options.get('speech_result', {}),
            'providers_used': search_providers
        }
    
    def start_voice_assistant(self, callback_func: callable = None) -> bool:
        """Start continuous voice assistant mode"""
        def voice_callback(speech_result):
            if speech_result['success']:
                query_text = speech_result['text'].strip()
                if query_text:
                    search_result = self.search_by_text(query_text, {'speech_result': speech_result})
                    if callback_func:
                        callback_func(search_result)
                    else:
                        print(f"Voice Query: {query_text}")
                        print(f"Results: {len(search_result['results'])} found")
        
        return self.speech_service.start_continuous_recognition(voice_callback)
    
    def stop_voice_assistant(self):
        """Stop continuous voice assistant"""
        self.speech_service.stop_continuous_recognition()
    
    def _check_voice_commands(self, query_text: str) -> Optional[Dict]:
        """Check if query matches registered voice commands"""
        query_lower = query_text.lower().strip()
        
        for trigger, command_info in self.voice_commands.items():
            if trigger in query_lower or query_lower.startswith(trigger):
                try:
                    result = command_info['handler'](query_text)
                    return {
                        'success': True,
                        'query': query_text,
                        'command_triggered': trigger,
                        'command_result': result,
                        'results': [],
                        'type': 'voice_command'
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'error': f"Command execution failed: {e}",
                        'query': query_text,
                        'command_triggered': trigger,
                        'type': 'voice_command'
                    }
        
        return None
    
    def _process_query(self, query_text: str, options: Dict) -> Dict:
        """Process and enhance the search query"""
        # Basic query processing
        processed = {
            'original': query_text,
            'cleaned': query_text.strip().lower(),
            'keywords': query_text.split(),
            'intent': self._detect_intent(query_text),
            'entities': self._extract_entities(query_text)
        }
        
        return processed
    
    def _detect_intent(self, query_text: str) -> str:
        """Detect user intent from query"""
        query_lower = query_text.lower()
        
        if any(word in query_lower for word in ['find', 'search', 'look for', 'show me']):
            return 'search'
        elif any(word in query_lower for word in ['create', 'add', 'new', 'make']):
            return 'create'
        elif any(word in query_lower for word in ['delete', 'remove', 'cancel']):
            return 'delete'
        elif any(word in query_lower for word in ['update', 'edit', 'change', 'modify']):
            return 'update'
        elif any(word in query_lower for word in ['help', 'how to', 'what is']):
            return 'help'
        else:
            return 'search'  # Default intent
    
    def _extract_entities(self, query_text: str) -> List[Dict]:
        """Extract entities from query text"""
        # Basic entity extraction (can be enhanced with NLP libraries)
        entities = []
        
        # Look for common patterns
        words = query_text.split()
        for i, word in enumerate(words):
            if word.lower() in ['user', 'users', 'customer', 'customers']:
                entities.append({'type': 'person', 'value': word, 'position': i})
            elif word.lower() in ['order', 'orders', 'product', 'products']:
                entities.append({'type': 'object', 'value': word, 'position': i})
        
        return entities
    
    def _search_local(self, processed_query: Dict, config: Dict) -> List[Dict]:
        """Search in local data/files"""
        # Basic local search implementation
        return []
    
    def _search_database(self, processed_query: Dict, config: Dict) -> List[Dict]:
        """Search in database"""
        # Database search implementation
        return []
    
    def _search_elasticsearch(self, processed_query: Dict, config: Dict) -> List[Dict]:
        """Search using Elasticsearch"""
        # Elasticsearch implementation
        return []
    
    def _search_api(self, processed_query: Dict, config: Dict) -> List[Dict]:
        """Search using external API"""
        # API search implementation
        return []
    
    def _rank_results(self, results: List[Dict], processed_query: Dict) -> List[Dict]:
        """Rank and deduplicate search results"""
        # Basic ranking by relevance score
        ranked_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
        return ranked_results[:20]  # Return top 20 results
    
    def process_search_query(self, query: str) -> Dict:
        """Process a search query (for testing)"""
        return {
            'success': True,
            'query': query,
            'processed_query': {'original': query, 'cleaned': query.lower()},
            'results': [],
            'result_count': 0
        }
    
    def _get_web_speech_config(self) -> Dict:
        """Get Web Speech API configuration"""
        return {
            'language': 'en-US',
            'continuous': True,
            'interim_results': True,
            'max_alternatives': 3
        }
    
    def _generate_web_speech_js(self) -> str:
        """Generate JavaScript code for Web Speech API"""
        return '''const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = 'en-US';

recognition.onstart = function() {
  console.log('Voice recognition started');
};

recognition.onresult = function(event) {
  const result = event.results[event.results.length - 1];
  const transcript = result[0].transcript;
  console.log('Voice result:', transcript);
};

recognition.onerror = function(event) {
  console.error('Voice recognition error:', event.error);
};

recognition.onend = function() {
  console.log('Voice recognition ended');
};

recognition.start();'''
    
    def _generate_voice_interface_component(self) -> str:
        """Generate voice interface React component"""
        return '''import React, { useState, useEffect } from 'react';

export const VoiceInterface = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      setRecognition(recognitionInstance);
    }
  }, []);

  const startListening = () => {
    if (recognition) {
      recognition.start();
      setIsListening(true);
    }
  };

  const stopListening = () => {
    if (recognition) {
      recognition.stop();
      setIsListening(false);
    }
  };

  return (
    <div className="voice-interface">
      <button onClick={isListening ? stopListening : startListening}>
        {isListening ? 'Stop' : 'Start'} Voice Recognition
      </button>
      <div className="transcript">{transcript}</div>
    </div>
  );
};'''
    
    def _generate_speech_recognition_panel(self) -> str:
        """Generate speech recognition panel component"""
        return '''import React, { useState, useRef } from 'react';

export const SpeechRecognitionPanel = () => {
  const [status, setStatus] = useState('idle');
  const [results, setResults] = useState([]);
  const mediaRecorderRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.start();
      setStatus('recording');
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setStatus('processing');
    }
  };

  return (
    <div className="speech-panel">
      <div className="status">Status: {status}</div>
      <button onClick={status === 'recording' ? stopRecording : startRecording}>
        {status === 'recording' ? 'Stop' : 'Start'} Recording
      </button>
      <div className="results">{JSON.stringify(results)}</div>
    </div>
  );
};'''
    
    def _generate_voice_commands_component(self) -> str:
        """Generate voice commands component"""
        return '''import React, { useState, useEffect } from 'react';

export const VoiceCommands = () => {
  const [commands, setCommands] = useState([]);
  const [activeCommand, setActiveCommand] = useState(null);

  useEffect(() => {
    // Load voice commands from API
    fetch('/api/voice/commands')
      .then(response => response.json())
      .then(data => setCommands(data.commands || []));
  }, []);

  const executeCommand = (command) => {
    setActiveCommand(command);
    // Execute voice command
    fetch('/api/voice/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command })
    });
  };

  return (
    <div className="voice-commands">
      <h3>Available Voice Commands</h3>
      {commands.map((cmd, index) => (
        <div key={index} className="command-item">
          <button onClick={() => executeCommand(cmd)}>
            {cmd.trigger}
          </button>
          <span>{cmd.description}</span>
        </div>
      ))}
    </div>
  );
};'''
    
    def _generate_audio_visualizer_component(self) -> str:
        """Generate audio visualizer component"""
        return '''import React, { useRef, useEffect, useState } from 'react';

export const AudioVisualizer = () => {
  const canvasRef = useRef(null);
  const [audioContext, setAudioContext] = useState(null);
  const [analyser, setAnalyser] = useState(null);

  useEffect(() => {
    const initAudio = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const context = new AudioContext();
        const analyserNode = context.createAnalyser();
        const source = context.createMediaStreamSource(stream);
        
        source.connect(analyserNode);
        setAudioContext(context);
        setAnalyser(analyserNode);
      } catch (error) {
        console.error('Audio initialization failed:', error);
      }
    };

    initAudio();
  }, []);

  useEffect(() => {
    if (analyser && canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const draw = () => {
        analyser.getByteFrequencyData(dataArray);
        
        ctx.fillStyle = 'rgb(0, 0, 0)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        const barWidth = (canvas.width / bufferLength) * 2.5;
        let barHeight;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
          barHeight = dataArray[i] / 2;
          
          ctx.fillStyle = `rgb(${barHeight + 100}, 50, 50)`;
          ctx.fillRect(x, canvas.height - barHeight / 2, barWidth, barHeight);
          
          x += barWidth + 1;
        }
        
        requestAnimationFrame(draw);
      };
      
      draw();
    }
  }, [analyser]);

  return (
    <div className="audio-visualizer">
      <canvas ref={canvasRef} width={800} height={200} />
    </div>
  );
};'''


class FlashFlowVoiceService:
    """Unified voice service for FlashFlow applications"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.speech_service = SpeechRecognitionService()
        self.voice_search = VoiceSearchService(self.speech_service)
        self.setup_defaults()
    
    def setup_defaults(self):
        """Setup default providers and configurations"""
        # Try to setup speech recognition provider
        speech_providers = ['google', 'whisper', 'sphinx']
        for provider in speech_providers:
            if self.speech_service.setup_provider(provider, self.config.get('speech', {})):
                break
        
        # Setup search providers
        search_config = self.config.get('search', {})
        for provider, config in search_config.items():
            self.voice_search.setup_search_provider(provider, config)
    
    def process_voice_input(self, audio_data: Union[str, bytes] = None, options: Dict = None) -> Dict:
        """Process voice input and return comprehensive results"""
        return self.voice_search.process_voice_query(audio_data, options)
    
    def register_command(self, trigger: str, handler: callable, description: str = ""):
        """Register voice command"""
        self.voice_search.register_voice_command(trigger, handler, description)
    
    def start_listening(self, callback: callable = None) -> bool:
        """Start continuous voice listening"""
        return self.voice_search.start_voice_assistant(callback)
    
    def stop_listening(self):
        """Stop voice listening"""
        self.voice_search.stop_voice_assistant()
    
    def get_provider_info(self) -> Dict:
        """Get information about active providers"""
        return {
            'speech_provider': self.speech_service.active_provider,
            'available_speech': list(self.speech_service.providers.keys()),
            'search_providers': list(self.voice_search.search_config.keys()),
            'voice_commands': len(self.voice_search.voice_commands),
            'is_listening': self.speech_service.is_listening
        }