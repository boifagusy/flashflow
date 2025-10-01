"""
FlashFlow OCR and QR Code Integration
Adds OCR and QR scanning support to FlashFlow parser and generators
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from .ocr_qr_service import FlashFlowOCRQRService

class OCRQRIntegration:
    """Integration layer for OCR and QR functionality in FlashFlow"""
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.service = None
        self.config = {}
    
    def setup_service(self, config: Dict = None) -> bool:
        """Setup OCR/QR service with configuration"""
        try:
            self.config = config or self._load_config()
            self.service = FlashFlowOCRQRService(self.config)
            return True
        except Exception as e:
            print(f"Failed to setup OCR/QR service: {e}")
            return False
    
    def _load_config(self) -> Dict:
        """Load OCR/QR configuration from FlashFlow project"""
        config_path = Path(self.project_path) / "flashflow.json"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                project_config = json.load(f)
                return project_config.get('ocr_qr', {})
        
        return {}
    
    def generate_ocr_component(self, component_config: Dict) -> str:
        """Generate OCR component code"""
        component_name = component_config.get('name', 'OCRComponent')
        
        return f"""
// FlashFlow OCR Component
import React, {{ useState, useRef }} from 'react';

export const {component_name} = ({{ onTextExtracted, className = '' }}) => {{
    const [isProcessing, setIsProcessing] = useState(false);
    const [extractedText, setExtractedText] = useState('');
    const [confidence, setConfidence] = useState(0);
    const fileInputRef = useRef(null);
    
    const handleFileSelect = async (event) => {{
        const file = event.target.files[0];
        if (!file) return;
        
        setIsProcessing(true);
        
        try {{
            const formData = new FormData();
            formData.append('image', file);
            
            const response = await fetch('/api/ocr/extract', {{
                method: 'POST',
                body: formData
            }});
            
            const result = await response.json();
            
            if (result.success) {{
                setExtractedText(result.text);
                setConfidence(result.confidence);
                onTextExtracted?.(result);
            }}
        }} catch (error) {{
            console.error('OCR error:', error);
        }} finally {{
            setIsProcessing(false);
        }}
    }};
    
    return (
        <div className={{`ocr-component ${{className}}`}}>
            <div onClick={{() => fileInputRef.current?.click()}}>
                <input
                    ref={{fileInputRef}}
                    type="file"
                    accept="image/*"
                    onChange={{handleFileSelect}}
                    style={{{{ display: 'none' }}}}
                />
                
                {{isProcessing ? (
                    <div>Extracting text...</div>
                ) : (
                    <div>Click to upload image for OCR</div>
                )}}
            </div>
            
            {{extractedText && (
                <div>
                    <div>Confidence: {{Math.round(confidence)}}%</div>
                    <textarea value={{extractedText}} readOnly rows={{8}} />
                </div>
            )}}
        </div>
    );
}};
"""
    
    def generate_qr_component(self, component_config: Dict) -> str:
        """Generate QR code scanning component"""
        component_name = component_config.get('name', 'QRScannerComponent')
        
        return f"""
// FlashFlow QR Scanner Component
import React, {{ useState, useRef }} from 'react';

export const {component_name} = ({{ onCodeScanned, className = '' }}) => {{
    const [scannedCodes, setScannedCodes] = useState([]);
    const fileInputRef = useRef(null);
    
    const handleFileSelect = async (event) => {{
        const file = event.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('image', file);
        
        try {{
            const response = await fetch('/api/qr/scan', {{
                method: 'POST',
                body: formData
            }});
            
            const result = await response.json();
            
            if (result.success) {{
                setScannedCodes(result.codes);
                result.codes.forEach(code => onCodeScanned?.(code));
            }}
        }} catch (error) {{
            console.error('QR scan error:', error);
        }}
    }};
    
    return (
        <div className={{`qr-scanner ${{className}}`}}>
            <button onClick={{() => fileInputRef.current?.click()}}>
                Scan QR Code
            </button>
            
            <input
                ref={{fileInputRef}}
                type="file"
                accept="image/*"
                onChange={{handleFileSelect}}
                style={{{{ display: 'none' }}}}
            />
            
            {{scannedCodes.length > 0 && (
                <div>
                    {{scannedCodes.map((code, index) => (
                        <div key={{index}}>
                            <strong>{{code.type}}:</strong> {{code.data}}
                        </div>
                    ))}}
                </div>
            )}}
        </div>
    );
}};
"""
    
    def generate_backend_routes(self) -> str:
        """Generate backend API routes for OCR/QR"""
        return '''
# FlashFlow OCR/QR API Routes
from flask import request, jsonify
from werkzeug.utils import secure_filename
import tempfile
import os

@app.route('/api/ocr/extract', methods=['POST'])
def ocr_extract():
    """Extract text from uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp_file:
            file.save(tmp_file.name)
            
            # Process with OCR service
            from flashflow_cli.services.ocr_qr_service import FlashFlowOCRQRService
            service = FlashFlowOCRQRService()
            result = service.process_image(tmp_file.name, ['ocr'])
            
            # Cleanup
            os.unlink(tmp_file.name)
            
            if result['results']['ocr']['success']:
                return jsonify({
                    'success': True,
                    'text': result['results']['ocr']['text'],
                    'confidence': result['results']['ocr']['confidence'],
                    'words': result['results']['ocr']['words'],
                    'provider': result['results']['ocr']['provider']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result['results']['ocr']['error']
                })
                
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/qr/scan', methods=['POST'])
def qr_scan():
    """Scan QR codes from uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp_file:
            file.save(tmp_file.name)
            
            # Process with QR service
            from flashflow_cli.services.ocr_qr_service import FlashFlowOCRQRService
            service = FlashFlowOCRQRService()
            result = service.process_image(tmp_file.name, ['qr'])
            
            # Cleanup
            os.unlink(tmp_file.name)
            
            if result['results']['qr']['success']:
                return jsonify({
                    'success': True,
                    'codes': result['results']['qr']['codes'],
                    'count': result['results']['qr']['count'],
                    'provider': result['results']['qr']['provider']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result['results']['qr']['error']
                })
                
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
'''