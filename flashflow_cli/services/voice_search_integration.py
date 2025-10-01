"""
FlashFlow Voice Search Integration
Adds voice search and speech recognition to FlashFlow applications
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from .voice_search_service import FlashFlowVoiceService

class VoiceSearchIntegration:
    """Integration layer for voice search functionality in FlashFlow"""
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.service = None
        self.config = {}
    
    def setup_service(self, config: Dict = None) -> bool:
        """Setup voice search service with configuration"""
        try:
            self.config = config or self._load_config()
            self.service = FlashFlowVoiceService(self.config)
            return True
        except Exception as e:
            print(f"Failed to setup voice search service: {e}")
            return False
    
    def _load_config(self) -> Dict:
        """Load voice search configuration from FlashFlow project"""
        config_path = Path(self.project_path) / "flashflow.json"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                project_config = json.load(f)
                return project_config.get('voice_search', {})
        
        return {}
    
    def generate_voice_component(self, component_config: Dict) -> str:
        """Generate voice search component code"""
        component_name = component_config.get('name', 'VoiceSearchComponent')
        
        return f"""
// FlashFlow Voice Search Component
import React, {{ useState, useRef, useEffect }} from 'react';

export const {component_name} = ({{ onVoiceResult, className = '' }}) => {{
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [results, setResults] = useState([]);
    const [error, setError] = useState('');
    
    const recognition = useRef(null);
    
    useEffect(() => {{
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition.current = new SpeechRecognition();
            
            recognition.current.continuous = true;
            recognition.current.interimResults = true;
            recognition.current.lang = 'en-US';
            
            recognition.current.onresult = (event) => {{
                let finalTranscript = '';
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {{
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {{
                        finalTranscript += transcript;
                    }} else {{
                        interimTranscript += transcript;
                    }}
                }}
                
                setTranscript(finalTranscript + interimTranscript);
                
                if (finalTranscript) {{
                    handleVoiceSearch(finalTranscript);
                }}
            }};
            
            recognition.current.onerror = (event) => {{
                setError(`Speech recognition error: ${{event.error}}`);
                setIsListening(false);
            }};
            
            recognition.current.onend = () => {{
                setIsListening(false);
            }};
        }}
        
        return () => {{
            if (recognition.current) {{
                recognition.current.stop();
            }}
        }};
    }}, []);
    
    const startListening = () => {{
        if (recognition.current) {{
            setError('');
            setTranscript('');
            recognition.current.start();
            setIsListening(true);
        }} else {{
            setError('Speech recognition not supported');
        }}
    }};
    
    const stopListening = () => {{
        if (recognition.current) {{
            recognition.current.stop();
        }}
        setIsListening(false);
    }};
    
    const handleVoiceSearch = async (query) => {{
        try {{
            const response = await fetch('/api/voice/search', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{ query }})
            }});
            
            const result = await response.json();
            
            if (result.success) {{
                setResults(result.results);
                onVoiceResult?.(result);
            }} else {{
                setError(result.error);
            }}
        }} catch (error) {{
            setError('Search failed: ' + error.message);
        }}
    }};
    
    return (
        <div className={{`voice-search ${{className}}`}}>
            <div className="voice-controls">
                <button 
                    onClick={{isListening ? stopListening : startListening}}
                    className={{`voice-btn ${{isListening ? 'listening' : ''}}`}}
                >
                    {{isListening ? '🔴 Stop' : '🎤 Start Voice Search'}}
                </button>
            </div>
            
            {{transcript && (
                <div className="transcript">
                    <strong>Transcript:</strong> {{transcript}}
                </div>
            )}}
            
            {{error && (
                <div className="error">
                    {{error}}
                </div>
            )}}
            
            {{results.length > 0 && (
                <div className="search-results">
                    <h4>Search Results:</h4>
                    {{results.map((result, index) => (
                        <div key={{index}} className="result-item">
                            <h5>{{result.title}}</h5>
                            <p>{{result.description}}</p>
                        </div>
                    ))}}
                </div>
            )}}
        </div>
    );
}};
"""
    
    def generate_backend_routes(self) -> str:
        """Generate backend API routes for voice search"""
        return '''
# FlashFlow Voice Search API Routes
from flask import request, jsonify
import tempfile
import os

@app.route('/api/voice/search', methods=['POST'])
def voice_search():
    """Process voice search query"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'success': False, 'error': 'No query provided'})
        
        # Process with voice search service
        from flashflow_cli.services.voice_search_service import FlashFlowVoiceService
        service = FlashFlowVoiceService()
        result = service.voice_search.search_by_text(query)
        
        if result['success']:
            return jsonify({
                'success': True,
                'query': result['query'],
                'results': result['results'],
                'result_count': result['result_count']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/voice/recognize', methods=['POST'])
def voice_recognize():
    """Recognize speech from uploaded audio"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio provided'})
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            file.save(tmp_file.name)
            
            # Process with voice service
            from flashflow_cli.services.voice_search_service import FlashFlowVoiceService
            service = FlashFlowVoiceService()
            result = service.speech_service.recognize_from_audio(tmp_file.name)
            
            # Cleanup
            os.unlink(tmp_file.name)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'text': result['text'],
                    'confidence': result['confidence'],
                    'language': result['language'],
                    'provider': result['provider']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                })
                
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
'''