"""
Media Engine Services for FlashFlow
Provides comprehensive media handling including upload, processing, optimization, and management
"""

import os
import json
import hashlib
import shutil
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from PIL import Image, ImageOps
import logging

logger = logging.getLogger(__name__)

@dataclass
class MediaFile:
    """Media file data structure"""
    id: str
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    media_type: str  # image, video, audio, document
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class MediaVariant:
    """Media variant (different sizes/formats)"""
    id: str
    parent_id: str
    variant_type: str  # thumbnail, small, medium, large, original
    file_path: str
    width: int
    height: int
    file_size: int
    format: str

class MediaProcessor:
    """Media processing and optimization"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        self.supported_video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        self.supported_audio_formats = ['.mp3', '.wav', '.ogg', '.m4a']
        
        # Image sizes configuration
        self.image_variants = {
            'thumbnail': (150, 150),
            'small': (300, 300),
            'medium': (600, 600),
            'large': (1200, 1200)
        }
    
    def process_image(self, file_path: str, output_dir: str) -> List[MediaVariant]:
        """Process image and generate variants"""
        variants = []
        
        try:
            with Image.open(file_path) as img:
                # Get original dimensions
                original_width, original_height = img.size
                file_size = os.path.getsize(file_path)
                
                # Generate variants
                for variant_type, (max_width, max_height) in self.image_variants.items():
                    try:
                        # Calculate new dimensions maintaining aspect ratio
                        img_copy = img.copy()
                        img_copy.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                        
                        # Generate variant filename
                        base_name = os.path.splitext(os.path.basename(file_path))[0]
                        variant_filename = f"{base_name}_{variant_type}.jpg"
                        variant_path = os.path.join(output_dir, variant_filename)
                        
                        # Save variant
                        img_copy.save(variant_path, 'JPEG', quality=85, optimize=True)
                        
                        # Create variant object
                        variant = MediaVariant(
                            id=self._generate_id(variant_path),
                            parent_id=self._generate_id(file_path),
                            variant_type=variant_type,
                            file_path=variant_path,
                            width=img_copy.width,
                            height=img_copy.height,
                            file_size=os.path.getsize(variant_path),
                            format='JPEG'
                        )
                        variants.append(variant)
                        
                    except Exception as e:
                        logger.error(f"Failed to create {variant_type} variant: {e}")
                        continue
                
                logger.info(f"Generated {len(variants)} image variants")
                return variants
                
        except Exception as e:
            logger.error(f"Failed to process image {file_path}: {e}")
            return []
    
    def optimize_image(self, file_path: str, quality: int = 85) -> bool:
        """Optimize image for web"""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Save optimized
                img.save(file_path, 'JPEG', quality=quality, optimize=True)
                logger.info(f"Optimized image: {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to optimize image {file_path}: {e}")
            return False
    
    def get_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract image metadata"""
        metadata = {}
        
        try:
            with Image.open(file_path) as img:
                metadata.update({
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'has_transparency': img.mode in ('RGBA', 'LA', 'P')
                })
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    if exif:
                        metadata['exif'] = exif
                
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
        
        return metadata
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for media content"""
        return hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()

class MediaStorage:
    """Media file storage management"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.storage_type = self.config.get('type', 'local')
        self.base_path = self.config.get('path', 'media')
        self.max_file_size = self.config.get('max_file_size', 10 * 1024 * 1024)  # 10MB
        
        # Create storage directories
        self._setup_storage()
    
    def _setup_storage(self):
        """Setup storage directories"""
        directories = ['uploads', 'images', 'videos', 'audio', 'documents', 'thumbnails']
        
        for directory in directories:
            dir_path = os.path.join(self.base_path, directory)
            os.makedirs(dir_path, exist_ok=True)
    
    def store_file(self, file_data: bytes, filename: str, content_type: str) -> MediaFile:
        """Store uploaded file"""
        try:
            # Validate file
            if len(file_data) > self.max_file_size:
                raise ValueError(f"File size exceeds maximum limit: {self.max_file_size}")
            
            # Determine media type and storage directory
            media_type = self._get_media_type(filename, content_type)
            storage_dir = os.path.join(self.base_path, f"{media_type}s")
            
            # Generate unique filename
            file_id = hashlib.md5(file_data + filename.encode()).hexdigest()
            file_extension = os.path.splitext(filename)[1].lower()
            stored_filename = f"{file_id}{file_extension}"
            file_path = os.path.join(storage_dir, stored_filename)
            
            # Store file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Create media file object
            media_file = MediaFile(
                id=file_id,
                filename=stored_filename,
                original_filename=filename,
                file_path=file_path,
                file_size=len(file_data),
                mime_type=content_type,
                media_type=media_type,
                created_at=datetime.now()
            )
            
            logger.info(f"Stored media file: {filename} -> {stored_filename}")
            return media_file
            
        except Exception as e:
            logger.error(f"Failed to store file {filename}: {e}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """Delete stored file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """Get public URL for file"""
        # For local storage, return relative path
        if self.storage_type == 'local':
            return file_path.replace(self.base_path, '/media')
        
        # For cloud storage, implement provider-specific URL generation
        return file_path
    
    def _get_media_type(self, filename: str, content_type: str) -> str:
        """Determine media type from filename and content type"""
        extension = os.path.splitext(filename)[1].lower()
        
        if content_type.startswith('image/') or extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return 'image'
        elif content_type.startswith('video/') or extension in ['.mp4', '.avi', '.mov', '.mkv']:
            return 'video'
        elif content_type.startswith('audio/') or extension in ['.mp3', '.wav', '.ogg']:
            return 'audio'
        else:
            return 'document'

class MediaManager:
    """Main media management class"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.storage = MediaStorage(config.get('storage', {}))
        self.processor = MediaProcessor(config.get('processing', {}))
        self.media_registry = {}  # In-memory registry (use database in production)
    
    def upload_media(self, file_data: bytes, filename: str, content_type: str) -> MediaFile:
        """Upload and process media file"""
        try:
            # Store original file
            media_file = self.storage.store_file(file_data, filename, content_type)
            
            # Process based on media type
            if media_file.media_type == 'image':
                self._process_image(media_file)
            elif media_file.media_type == 'video':
                self._process_video(media_file)
            
            # Register media file
            self.media_registry[media_file.id] = media_file
            
            logger.info(f"Successfully uploaded media: {media_file.id}")
            return media_file
            
        except Exception as e:
            logger.error(f"Failed to upload media {filename}: {e}")
            raise
    
    def _process_image(self, media_file: MediaFile):
        """Process uploaded image"""
        try:
            # Extract metadata
            metadata = self.processor.get_image_metadata(media_file.file_path)
            media_file.width = metadata.get('width')
            media_file.height = metadata.get('height')
            media_file.metadata = metadata
            
            # Optimize original image
            self.processor.optimize_image(media_file.file_path)
            
            # Generate variants
            output_dir = os.path.dirname(media_file.file_path)
            variants = self.processor.process_image(media_file.file_path, output_dir)
            
            # Store variants in metadata
            if not media_file.metadata:
                media_file.metadata = {}
            media_file.metadata['variants'] = [asdict(v) for v in variants]
            
        except Exception as e:
            logger.error(f"Failed to process image {media_file.id}: {e}")
    
    def _process_video(self, media_file: MediaFile):
        """Process uploaded video (placeholder)"""
        try:
            # Video processing would require ffmpeg or similar
            # For now, just extract basic metadata
            media_file.metadata = {
                'processed': False,
                'requires_ffmpeg': True
            }
            
        except Exception as e:
            logger.error(f"Failed to process video {media_file.id}: {e}")
    
    def get_media(self, media_id: str) -> Optional[MediaFile]:
        """Get media file by ID"""
        return self.media_registry.get(media_id)
    
    def list_media(self, media_type: Optional[str] = None, limit: int = 100) -> List[MediaFile]:
        """List media files with optional filtering"""
        media_files = list(self.media_registry.values())
        
        if media_type:
            media_files = [m for m in media_files if m.media_type == media_type]
        
        return media_files[:limit]
    
    def delete_media(self, media_id: str) -> bool:
        """Delete media file and its variants"""
        try:
            media_file = self.media_registry.get(media_id)
            if not media_file:
                return False
            
            # Delete original file
            self.storage.delete_file(media_file.file_path)
            
            # Delete variants if they exist
            if media_file.metadata and 'variants' in media_file.metadata:
                for variant_data in media_file.metadata['variants']:
                    self.storage.delete_file(variant_data['file_path'])
            
            # Remove from registry
            del self.media_registry[media_id]
            
            logger.info(f"Deleted media: {media_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete media {media_id}: {e}")
            return False
    
    def get_media_url(self, media_id: str, variant: Optional[str] = None) -> Optional[str]:
        """Get public URL for media file or variant"""
        media_file = self.media_registry.get(media_id)
        if not media_file:
            return None
        
        if variant and media_file.metadata and 'variants' in media_file.metadata:
            # Find specific variant
            for variant_data in media_file.metadata['variants']:
                if variant_data['variant_type'] == variant:
                    return self.storage.get_file_url(variant_data['file_path'])
        
        # Return original file URL
        return self.storage.get_file_url(media_file.file_path)
    
    def get_media_stats(self) -> Dict[str, Any]:
        """Get media statistics"""
        stats = {
            'total_files': len(self.media_registry),
            'by_type': {},
            'total_size': 0
        }
        
        for media_file in self.media_registry.values():
            # Count by type
            media_type = media_file.media_type
            if media_type not in stats['by_type']:
                stats['by_type'][media_type] = 0
            stats['by_type'][media_type] += 1
            
            # Add to total size
            stats['total_size'] += media_file.file_size
        
        return stats

def create_media_manager(config: Dict[str, Any] = None) -> MediaManager:
    """Factory function to create media manager"""
    return MediaManager(config)