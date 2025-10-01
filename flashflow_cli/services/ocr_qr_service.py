"""
FlashFlow OCR and QR Code Scanning Service
Provides OCR text recognition and QR/barcode scanning capabilities
"""

import base64
import json
import os
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path

class OCRService:
    """OCR text recognition service with multiple provider support"""
    
    def __init__(self):
        self.providers = {
            'tesseract': self._init_tesseract,
            'easyocr': self._init_easyocr,
            'paddleocr': self._init_paddleocr,
            'google_vision': self._init_google_vision
        }
        self.active_provider = None
        self.provider_config = {}
    
    def _init_tesseract(self, config: Dict) -> bool:
        """Initialize Tesseract OCR"""
        try:
            import pytesseract
            from PIL import Image
            
            # Set tesseract path if provided
            if 'tesseract_path' in config:
                pytesseract.pytesseract.tesseract_cmd = config['tesseract_path']
            
            self.provider_config['tesseract'] = {
                'languages': config.get('languages', ['eng']),
                'config': config.get('config', '--psm 6'),
                'timeout': config.get('timeout', 30)
            }
            return True
        except ImportError:
            return False
    
    def _init_easyocr(self, config: Dict) -> bool:
        """Initialize EasyOCR"""
        try:
            import easyocr
            
            languages = config.get('languages', ['en'])
            gpu = config.get('gpu', False)
            
            self.provider_config['easyocr'] = {
                'reader': easyocr.Reader(languages, gpu=gpu),
                'detail': config.get('detail', 1),
                'paragraph': config.get('paragraph', False)
            }
            return True
        except ImportError:
            return False
    
    def _init_paddleocr(self, config: Dict) -> bool:
        """Initialize PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            
            self.provider_config['paddleocr'] = {
                'ocr': PaddleOCR(
                    use_angle_cls=config.get('use_angle_cls', True),
                    lang=config.get('lang', 'en'),
                    use_gpu=config.get('use_gpu', False)
                ),
                'cls': config.get('cls', True)
            }
            return True
        except ImportError:
            return False
    
    def _init_google_vision(self, config: Dict) -> bool:
        """Initialize Google Cloud Vision API"""
        try:
            from google.cloud import vision
            
            # Set credentials if provided
            if 'credentials_path' in config:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['credentials_path']
            
            self.provider_config['google_vision'] = {
                'client': vision.ImageAnnotatorClient(),
                'features': config.get('features', ['TEXT_DETECTION'])
            }
            return True
        except ImportError:
            return False
    
    def setup_provider(self, provider_name: str, config: Dict = None) -> bool:
        """Setup OCR provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Unsupported OCR provider: {provider_name}")
        
        config = config or {}
        success = self.providers[provider_name](config)
        
        if success:
            self.active_provider = provider_name
            return True
        return False
    
    def extract_text(self, image_path: str, options: Dict = None) -> Dict:
        """Extract text from image"""
        if not self.active_provider:
            raise RuntimeError("No OCR provider configured")
        
        options = options or {}
        
        try:
            if self.active_provider == 'tesseract':
                return self._extract_tesseract(image_path, options)
            elif self.active_provider == 'easyocr':
                return self._extract_easyocr(image_path, options)
            elif self.active_provider == 'paddleocr':
                return self._extract_paddleocr(image_path, options)
            elif self.active_provider == 'google_vision':
                return self._extract_google_vision(image_path, options)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0,
                'words': [],
                'blocks': []
            }
    
    def _extract_tesseract(self, image_path: str, options: Dict) -> Dict:
        """Extract text using Tesseract"""
        import pytesseract
        from PIL import Image
        
        config = self.provider_config['tesseract']
        
        with Image.open(image_path) as img:
            # Extract text
            text = pytesseract.image_to_string(
                img,
                lang='+'.join(config['languages']),
                config=config['config'],
                timeout=config['timeout']
            )
            
            # Get detailed data
            data = pytesseract.image_to_data(
                img,
                lang='+'.join(config['languages']),
                config=config['config'],
                output_type=pytesseract.Output.DICT
            )
            
            # Process words and confidence
            words = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:
                    words.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'bbox': [
                            data['left'][i],
                            data['top'][i],
                            data['left'][i] + data['width'][i],
                            data['top'][i] + data['height'][i]
                        ]
                    })
            
            avg_confidence = sum(w['confidence'] for w in words) / len(words) if words else 0
            
            return {
                'success': True,
                'text': text.strip(),
                'confidence': avg_confidence,
                'words': words,
                'blocks': [],
                'provider': 'tesseract'
            }
    
    def _extract_easyocr(self, image_path: str, options: Dict) -> Dict:
        """Extract text using EasyOCR"""
        config = self.provider_config['easyocr']
        reader = config['reader']
        
        results = reader.readtext(
            image_path,
            detail=config['detail'],
            paragraph=config['paragraph']
        )
        
        words = []
        all_text = []
        
        for result in results:
            if config['detail']:
                bbox, text, confidence = result
                words.append({
                    'text': text,
                    'confidence': confidence * 100,
                    'bbox': [int(coord) for point in bbox for coord in point]
                })
                all_text.append(text)
            else:
                all_text.append(result)
        
        avg_confidence = sum(w['confidence'] for w in words) / len(words) if words else 0
        
        return {
            'success': True,
            'text': ' '.join(all_text),
            'confidence': avg_confidence,
            'words': words,
            'blocks': [],
            'provider': 'easyocr'
        }
    
    def _extract_paddleocr(self, image_path: str, options: Dict) -> Dict:
        """Extract text using PaddleOCR"""
        config = self.provider_config['paddleocr']
        ocr = config['ocr']
        
        result = ocr.ocr(image_path, cls=config['cls'])
        
        words = []
        all_text = []
        
        if result and result[0]:
            for line in result[0]:
                if line:
                    bbox, (text, confidence) = line
                    words.append({
                        'text': text,
                        'confidence': confidence * 100,
                        'bbox': [int(coord) for point in bbox for coord in point]
                    })
                    all_text.append(text)
        
        avg_confidence = sum(w['confidence'] for w in words) / len(words) if words else 0
        
        return {
            'success': True,
            'text': ' '.join(all_text),
            'confidence': avg_confidence,
            'words': words,
            'blocks': [],
            'provider': 'paddleocr'
        }
    
    def _extract_google_vision(self, image_path: str, options: Dict) -> Dict:
        """Extract text using Google Cloud Vision"""
        from google.cloud import vision
        
        config = self.provider_config['google_vision']
        client = config['client']
        
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(f"Google Vision API error: {response.error.message}")
        
        texts = response.text_annotations
        words = []
        full_text = ""
        
        if texts:
            full_text = texts[0].description
            
            for text in texts[1:]:  # Skip the first one (full text)
                vertices = text.bounding_poly.vertices
                bbox = [
                    min(v.x for v in vertices),
                    min(v.y for v in vertices),
                    max(v.x for v in vertices),
                    max(v.y for v in vertices)
                ]
                
                words.append({
                    'text': text.description,
                    'confidence': 95,  # Google doesn't provide word-level confidence
                    'bbox': bbox
                })
        
        return {
            'success': True,
            'text': full_text,
            'confidence': 95,
            'words': words,
            'blocks': [],
            'provider': 'google_vision'
        }


class QRCodeService:
    """QR code and barcode scanning service"""
    
    def __init__(self):
        self.providers = {
            'pyzbar': self._init_pyzbar,
            'opencv': self._init_opencv,
            'zxing': self._init_zxing
        }
        self.active_provider = None
        self.provider_config = {}
    
    def _init_pyzbar(self, config: Dict) -> bool:
        """Initialize pyzbar for QR/barcode scanning"""
        try:
            from pyzbar import pyzbar
            from PIL import Image
            
            self.provider_config['pyzbar'] = {
                'symbols': config.get('symbols', None)  # None means all symbols
            }
            return True
        except ImportError:
            return False
    
    def _init_opencv(self, config: Dict) -> bool:
        """Initialize OpenCV QR detector"""
        try:
            import cv2
            
            self.provider_config['opencv'] = {
                'detector': cv2.QRCodeDetector()
            }
            return True
        except ImportError:
            return False
    
    def _init_zxing(self, config: Dict) -> bool:
        """Initialize ZXing via pyzxing"""
        try:
            from pyzxing import BarCodeReader
            
            self.provider_config['zxing'] = {
                'reader': BarCodeReader()
            }
            return True
        except ImportError:
            return False
    
    def setup_provider(self, provider_name: str, config: Dict = None) -> bool:
        """Setup QR code provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Unsupported QR provider: {provider_name}")
        
        config = config or {}
        success = self.providers[provider_name](config)
        
        if success:
            self.active_provider = provider_name
            return True
        return False
    
    def scan_codes(self, image_path: str, options: Dict = None) -> Dict:
        """Scan QR codes and barcodes from image"""
        if not self.active_provider:
            raise RuntimeError("No QR code provider configured")
        
        options = options or {}
        
        try:
            if self.active_provider == 'pyzbar':
                return self._scan_pyzbar(image_path, options)
            elif self.active_provider == 'opencv':
                return self._scan_opencv(image_path, options)
            elif self.active_provider == 'zxing':
                return self._scan_zxing(image_path, options)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'codes': []
            }
    
    def _scan_pyzbar(self, image_path: str, options: Dict) -> Dict:
        """Scan codes using pyzbar"""
        from pyzbar import pyzbar
        from PIL import Image
        
        config = self.provider_config['pyzbar']
        
        with Image.open(image_path) as img:
            decoded_objects = pyzbar.decode(img, symbols=config['symbols'])
        
        codes = []
        for obj in decoded_objects:
            codes.append({
                'data': obj.data.decode('utf-8'),
                'type': obj.type,
                'quality': obj.quality if hasattr(obj, 'quality') else None,
                'bbox': [obj.rect.left, obj.rect.top, 
                        obj.rect.left + obj.rect.width, 
                        obj.rect.top + obj.rect.height],
                'polygon': [[p.x, p.y] for p in obj.polygon] if obj.polygon else None
            })
        
        return {
            'success': True,
            'codes': codes,
            'count': len(codes),
            'provider': 'pyzbar'
        }
    
    def _scan_opencv(self, image_path: str, options: Dict) -> Dict:
        """Scan QR codes using OpenCV"""
        import cv2
        
        config = self.provider_config['opencv']
        detector = config['detector']
        
        img = cv2.imread(image_path)
        data, points, _ = detector.detectAndDecode(img)
        
        codes = []
        if data:
            # Convert points to bbox
            if points is not None and len(points) > 0:
                pts = points[0]
                x_coords = [p[0] for p in pts]
                y_coords = [p[1] for p in pts]
                bbox = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
                polygon = [[int(p[0]), int(p[1])] for p in pts]
            else:
                bbox = None
                polygon = None
            
            codes.append({
                'data': data,
                'type': 'QRCODE',
                'quality': None,
                'bbox': bbox,
                'polygon': polygon
            })
        
        return {
            'success': True,
            'codes': codes,
            'count': len(codes),
            'provider': 'opencv'
        }
    
    def _scan_zxing(self, image_path: str, options: Dict) -> Dict:
        """Scan codes using ZXing"""
        config = self.provider_config['zxing']
        reader = config['reader']
        
        result = reader.decode(image_path)
        codes = []
        
        if result:
            for code in result:
                codes.append({
                    'data': code.get('raw', ''),
                    'type': code.get('format', 'UNKNOWN'),
                    'quality': None,
                    'bbox': code.get('points', None),
                    'polygon': None
                })
        
        return {
            'success': True,
            'codes': codes,
            'count': len(codes),
            'provider': 'zxing'
        }


class FlashFlowOCRQRService:
    """Unified OCR and QR code service for FlashFlow"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.ocr = OCRService()
        self.qr = QRCodeService()
        self.setup_defaults()
    
    def setup_defaults(self):
        """Setup default providers"""
        # Try to setup OCR provider in order of preference
        ocr_providers = ['tesseract', 'easyocr', 'paddleocr']
        for provider in ocr_providers:
            if self.ocr.setup_provider(provider, self.config.get('ocr', {})):
                break
        
        # Try to setup QR provider in order of preference
        qr_providers = ['pyzbar', 'opencv', 'zxing']
        for provider in qr_providers:
            if self.qr.setup_provider(provider, self.config.get('qr', {})):
                break
    
    def process_image(self, image_path: str, operations: List[str] = None) -> Dict:
        """Process image with OCR and/or QR scanning"""
        operations = operations or ['ocr', 'qr']
        results = {}
        
        if 'ocr' in operations:
            results['ocr'] = self.ocr.extract_text(image_path)
        
        if 'qr' in operations:
            results['qr'] = self.qr.scan_codes(image_path)
        
        return {
            'success': True,
            'image_path': image_path,
            'operations': operations,
            'results': results,
            'timestamp': json.dumps(None, default=str)
        }
    
    def process_base64(self, base64_data: str, operations: List[str] = None, 
                      image_format: str = 'png') -> Dict:
        """Process base64 encoded image"""
        # Decode base64 and save to temporary file
        image_data = base64.b64decode(base64_data)
        
        with tempfile.NamedTemporaryFile(suffix=f'.{image_format}', delete=False) as tmp_file:
            tmp_file.write(image_data)
            tmp_path = tmp_file.name
        
        try:
            result = self.process_image(tmp_path, operations)
            result['input_type'] = 'base64'
            return result
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    def get_provider_info(self) -> Dict:
        """Get information about active providers"""
        return {
            'ocr_provider': self.ocr.active_provider,
            'qr_provider': self.qr.active_provider,
            'available_ocr': list(self.ocr.providers.keys()),
            'available_qr': list(self.qr.providers.keys())
        }