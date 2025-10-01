"""
Media Integration for FlashFlow
Provides media engine integration with React components and Flask routes
"""

import os
import json
from typing import Dict, Any, List, Optional
from ..services.media_services import MediaManager, MediaFile
import logging

logger = logging.getLogger(__name__)

class MediaIntegration:
    """Main media integration class for FlashFlow"""
    
    def __init__(self):
        self.media_manager = None
        self.generated_components = {}
        self.generated_routes = {}
    
    def initialize(self, config: Dict[str, Any] = None):
        """Initialize media services"""
        try:
            media_config = config or {
                'storage': {'type': 'local', 'path': 'media'},
                'processing': {'quality': 85}
            }
            self.media_manager = MediaManager(media_config)
            
            logger.info("Media integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize media integration: {e}")
            return False
    
    def generate_react_components(self) -> Dict[str, str]:
        """Generate React components for media management"""
        components = {}
        
        try:
            # Media upload component
            components['MediaUpload'] = self._generate_media_upload_component()
            
            # Media gallery component
            components['MediaGallery'] = self._generate_media_gallery_component()
            
            # Media viewer component
            components['MediaViewer'] = self._generate_media_viewer_component()
            
            # Image editor component
            components['ImageEditor'] = self._generate_image_editor_component()
            
            # Media manager component
            components['MediaManager'] = self._generate_media_manager_component()
            
            # Media hooks
            components['useMedia'] = self._generate_media_hooks()
            
            self.generated_components = components
            logger.info(f"Generated {len(components)} media React components")
            return components
            
        except Exception as e:
            logger.error(f"Failed to generate React components: {e}")
            return {}
    
    def generate_flask_routes(self) -> Dict[str, str]:
        """Generate Flask routes for media API"""
        routes = {}
        
        try:
            # Media upload endpoint
            routes['media_upload'] = self._generate_media_upload_endpoint()
            
            # Media management endpoint
            routes['media_management'] = self._generate_media_management_endpoint()
            
            # Media serving endpoint
            routes['media_serving'] = self._generate_media_serving_endpoint()
            
            self.generated_routes = routes
            logger.info(f"Generated {len(routes)} media Flask routes")
            return routes
            
        except Exception as e:
            logger.error(f"Failed to generate Flask routes: {e}")
            return {}
    
    def _generate_media_upload_component(self) -> str:
        """Generate media upload component"""
        return '''import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box, Typography, LinearProgress, Alert, Chip, IconButton, Card, CardContent
} from '@mui/material';
import { CloudUpload, Delete, Image, VideoFile, AudioFile, Description } from '@mui/icons-material';

export const MediaUpload = ({ onUpload, maxFiles = 10, acceptedTypes = ['image/*', 'video/*'] }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    setUploading(true);
    setError(null);
    
    try {
      const uploadPromises = acceptedFiles.map(async (file, index) => {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/media/upload', {
          method: 'POST',
          body: formData,
        });
        
        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        setUploadProgress(((index + 1) / acceptedFiles.length) * 100);
        
        return result;
      });
      
      const results = await Promise.all(uploadPromises);
      setUploadedFiles(prev => [...prev, ...results]);
      
      if (onUpload) {
        onUpload(results);
      }
      
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    maxFiles,
    disabled: uploading
  });

  const getFileIcon = (mimeType) => {
    if (mimeType.startsWith('image/')) return <Image />;
    if (mimeType.startsWith('video/')) return <VideoFile />;
    if (mimeType.startsWith('audio/')) return <AudioFile />;
    return <Description />;
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <Box>
      <Card
        {...getRootProps()}
        sx={{
          border: 2,
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          borderStyle: 'dashed',
          p: 3,
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper'
        }}
      >
        <input {...getInputProps()} />
        <CloudUpload sx={{ fontSize: 48, color: 'grey.500', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop files here...' : 'Drag & drop files here, or click to select'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Accepted: {acceptedTypes.join(', ')} • Max {maxFiles} files
        </Typography>
      </Card>

      {uploading && (
        <Box mt={2}>
          <Typography variant="body2" gutterBottom>
            Uploading... {uploadProgress.toFixed(0)}%
          </Typography>
          <LinearProgress variant="determinate" value={uploadProgress} />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {uploadedFiles.length > 0 && (
        <Box mt={2}>
          <Typography variant="h6" gutterBottom>
            Uploaded Files ({uploadedFiles.length})
          </Typography>
          {uploadedFiles.map((file, index) => (
            <Card key={index} sx={{ mb: 1 }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', py: 1 }}>
                {getFileIcon(file.mime_type)}
                <Box ml={2} flex={1}>
                  <Typography variant="body2">{file.original_filename}</Typography>
                  <Box display="flex" gap={1} mt={0.5}>
                    <Chip label={file.media_type} size="small" />
                    <Chip label={`${(file.file_size / 1024).toFixed(1)} KB`} size="small" variant="outlined" />
                  </Box>
                </Box>
                <IconButton onClick={() => removeFile(index)} size="small">
                  <Delete />
                </IconButton>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default MediaUpload;'''
    
    def _generate_media_gallery_component(self) -> str:
        """Generate media gallery component"""
        return '''import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardMedia, CardContent, Typography, Box, Chip, IconButton,
  Dialog, DialogContent, DialogActions, Button, TextField, MenuItem
} from '@mui/material';
import { Visibility, Download, Delete, Edit } from '@mui/icons-material';

export const MediaGallery = ({ mediaType = 'all', onMediaSelect }) => {
  const [media, setMedia] = useState([]);
  const [selectedMedia, setSelectedMedia] = useState(null);
  const [viewerOpen, setViewerOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchMedia();
  }, [mediaType, filter]);

  const fetchMedia = async () => {
    try {
      const params = new URLSearchParams();
      if (mediaType !== 'all') params.append('type', mediaType);
      if (filter !== 'all') params.append('filter', filter);
      
      const response = await fetch(`/api/media?${params}`);
      const data = await response.json();
      setMedia(data.media || []);
    } catch (error) {
      console.error('Failed to fetch media:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMediaClick = (mediaItem) => {
    if (onMediaSelect) {
      onMediaSelect(mediaItem);
    } else {
      setSelectedMedia(mediaItem);
      setViewerOpen(true);
    }
  };

  const handleDelete = async (mediaId, event) => {
    event.stopPropagation();
    
    if (window.confirm('Are you sure you want to delete this media?')) {
      try {
        await fetch(`/api/media/${mediaId}`, { method: 'DELETE' });
        fetchMedia(); // Refresh the gallery
      } catch (error) {
        console.error('Failed to delete media:', error);
      }
    }
  };

  const getMediaThumbnail = (mediaItem) => {
    if (mediaItem.media_type === 'image') {
      return `/api/media/${mediaItem.id}/thumbnail`;
    } else if (mediaItem.media_type === 'video') {
      return '/static/video-thumbnail.png'; // Placeholder
    }
    return '/static/file-thumbnail.png'; // Placeholder
  };

  if (loading) {
    return <Typography>Loading media...</Typography>;
  }

  return (
    <Box>
      <Box mb={2} display="flex" justifyContent="between" alignItems="center">
        <Typography variant="h6">
          Media Gallery ({media.length} items)
        </Typography>
        <TextField
          select
          label="Filter"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          size="small"
          sx={{ minWidth: 120 }}
        >
          <MenuItem value="all">All Media</MenuItem>
          <MenuItem value="image">Images</MenuItem>
          <MenuItem value="video">Videos</MenuItem>
          <MenuItem value="audio">Audio</MenuItem>
        </TextField>
      </Box>

      <Grid container spacing={2}>
        {media.map((mediaItem) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={mediaItem.id}>
            <Card
              sx={{ cursor: 'pointer', '&:hover': { boxShadow: 6 } }}
              onClick={() => handleMediaClick(mediaItem)}
            >
              <CardMedia
                component="img"
                height={200}
                image={getMediaThumbnail(mediaItem)}
                alt={mediaItem.original_filename}
                sx={{ objectFit: 'cover' }}
              />
              <CardContent sx={{ p: 1 }}>
                <Typography variant="body2" noWrap title={mediaItem.original_filename}>
                  {mediaItem.original_filename}
                </Typography>
                <Box display="flex" justifyContent="space-between" alignItems="center" mt={1}>
                  <Chip 
                    label={mediaItem.media_type} 
                    size="small" 
                    color="primary" 
                    variant="outlined"
                  />
                  <Box>
                    <IconButton size="small" onClick={(e) => handleDelete(mediaItem.id, e)}>
                      <Delete fontSize="small" />
                    </IconButton>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Media Viewer Dialog */}
      <Dialog
        open={viewerOpen}
        onClose={() => setViewerOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogContent>
          {selectedMedia && (
            <Box>
              {selectedMedia.media_type === 'image' && (
                <img
                  src={`/api/media/${selectedMedia.id}`}
                  alt={selectedMedia.original_filename}
                  style={{ width: '100%', height: 'auto' }}
                />
              )}
              {selectedMedia.media_type === 'video' && (
                <video
                  controls
                  style={{ width: '100%', height: 'auto' }}
                  src={`/api/media/${selectedMedia.id}`}
                />
              )}
              <Typography variant="h6" mt={2}>
                {selectedMedia.original_filename}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {selectedMedia.media_type} • {(selectedMedia.file_size / 1024).toFixed(1)} KB
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewerOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MediaGallery;'''
    
    def _generate_media_viewer_component(self) -> str:
        """Generate media viewer component"""
        return '''import React from 'react';
import { Box, Typography, Chip } from '@mui/material';

export const MediaViewer = ({ mediaId, mediaType, alt, width = '100%', height = 'auto' }) => {
  if (!mediaId) {
    return (
      <Box 
        display="flex" 
        alignItems="center" 
        justifyContent="center" 
        height={200}
        bgcolor="grey.100"
      >
        <Typography color="textSecondary">No media selected</Typography>
      </Box>
    );
  }

  const renderMedia = () => {
    switch (mediaType) {
      case 'image':
        return (
          <img
            src={`/api/media/${mediaId}`}
            alt={alt}
            style={{ width, height, objectFit: 'contain' }}
          />
        );
      case 'video':
        return (
          <video
            controls
            style={{ width, height }}
            src={`/api/media/${mediaId}`}
          >
            Your browser does not support video playback.
          </video>
        );
      case 'audio':
        return (
          <audio
            controls
            style={{ width }}
            src={`/api/media/${mediaId}`}
          >
            Your browser does not support audio playback.
          </audio>
        );
      default:
        return (
          <Box p={2} textAlign="center">
            <Typography>Preview not available for this media type</Typography>
            <Chip label={mediaType} size="small" />
          </Box>
        );
    }
  };

  return <Box>{renderMedia()}</Box>;
};

export default MediaViewer;'''
    
    def _generate_image_editor_component(self) -> str:
        """Generate image editor component"""
        return '''import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  Slider, Typography, Box, ButtonGroup
} from '@mui/material';
import { Crop, Brightness6, Contrast, Palette } from '@mui/icons-material';

export const ImageEditor = ({ open, onClose, imageId, onSave }) => {
  const [brightness, setBrightness] = useState(100);
  const [contrast, setContrast] = useState(100);
  const [saturation, setSaturation] = useState(100);

  const handleSave = async () => {
    try {
      const response = await fetch(`/api/media/${imageId}/edit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brightness,
          contrast,
          saturation
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        if (onSave) onSave(result);
        onClose();
      }
    } catch (error) {
      console.error('Failed to save image edits:', error);
    }
  };

  const resetFilters = () => {
    setBrightness(100);
    setContrast(100);
    setSaturation(100);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Image Editor</DialogTitle>
      <DialogContent>
        <Box mb={3}>
          <img
            src={`/api/media/${imageId}`}
            alt="Edit preview"
            style={{
              width: '100%',
              height: 'auto',
              filter: `brightness(${brightness}%) contrast(${contrast}%) saturate(${saturation}%)`
            }}
          />
        </Box>
        
        <Box mb={2}>
          <Typography gutterBottom><Brightness6 sx={{ mr: 1 }} />Brightness</Typography>
          <Slider
            value={brightness}
            onChange={(e, value) => setBrightness(value)}
            min={0}
            max={200}
            step={1}
            valueLabelDisplay="auto"
          />
        </Box>
        
        <Box mb={2}>
          <Typography gutterBottom><Contrast sx={{ mr: 1 }} />Contrast</Typography>
          <Slider
            value={contrast}
            onChange={(e, value) => setContrast(value)}
            min={0}
            max={200}
            step={1}
            valueLabelDisplay="auto"
          />
        </Box>
        
        <Box mb={2}>
          <Typography gutterBottom><Palette sx={{ mr: 1 }} />Saturation</Typography>
          <Slider
            value={saturation}
            onChange={(e, value) => setSaturation(value)}
            min={0}
            max={200}
            step={1}
            valueLabelDisplay="auto"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={resetFilters}>Reset</Button>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} variant="contained">Save</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ImageEditor;'''
    
    def _generate_media_manager_component(self) -> str:
        """Generate media manager component"""
        return '''import React, { useState } from 'react';
import { Box, Tabs, Tab, Paper } from '@mui/material';
import MediaUpload from './MediaUpload';
import MediaGallery from './MediaGallery';

export const MediaManager = ({ onMediaSelect }) => {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <Paper>
      <Tabs value={activeTab} onChange={(e, value) => setActiveTab(value)}>
        <Tab label="Upload" />
        <Tab label="Gallery" />
      </Tabs>
      
      <Box p={3}>
        {activeTab === 0 && (
          <MediaUpload onUpload={() => setActiveTab(1)} />
        )}
        {activeTab === 1 && (
          <MediaGallery onMediaSelect={onMediaSelect} />
        )}
      </Box>
    </Paper>
  );
};

export default MediaManager;'''
    
    def _generate_media_hooks(self) -> str:
        """Generate media hooks"""
        return '''import { useState, useEffect } from 'react';

export const useMedia = () => {
  const [media, setMedia] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchMedia = async (type = null) => {
    setLoading(true);
    try {
      const params = type ? `?type=${type}` : '';
      const response = await fetch(`/api/media${params}`);
      const data = await response.json();
      setMedia(data.media || []);
    } catch (error) {
      console.error('Failed to fetch media:', error);
    } finally {
      setLoading(false);
    }
  };

  const uploadMedia = async (files) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    const response = await fetch('/api/media/upload', {
      method: 'POST',
      body: formData
    });
    
    return response.json();
  };

  const deleteMedia = async (mediaId) => {
    await fetch(`/api/media/${mediaId}`, { method: 'DELETE' });
    fetchMedia(); // Refresh
  };

  return { media, loading, fetchMedia, uploadMedia, deleteMedia };
};

export default useMedia;'''
    
    def _generate_media_upload_endpoint(self) -> str:
        """Generate media upload endpoint"""
        return '''from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

media_upload_bp = Blueprint('media_upload', __name__)

@media_upload_bp.route('/upload', methods=['POST'])
def upload_media():
    """Upload media files"""
    try:
        from flashflow_cli.integrations.media_integration import get_media_manager
        
        media_manager = get_media_manager()
        if not media_manager:
            return jsonify({'error': 'Media system not initialized'}), 500
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file data
        file_data = file.read()
        filename = secure_filename(file.filename)
        content_type = file.content_type or 'application/octet-stream'
        
        # Upload and process
        media_file = media_manager.upload_media(file_data, filename, content_type)
        
        return jsonify({
            'id': media_file.id,
            'filename': media_file.filename,
            'original_filename': media_file.original_filename,
            'file_size': media_file.file_size,
            'mime_type': media_file.mime_type,
            'media_type': media_file.media_type,
            'width': media_file.width,
            'height': media_file.height,
            'url': f'/api/media/{media_file.id}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

def register_upload_routes(app):
    app.register_blueprint(media_upload_bp, url_prefix='/api/media')'''
    
    def _generate_media_management_endpoint(self) -> str:
        """Generate media management endpoint"""
        return '''from flask import Blueprint, request, jsonify

media_mgmt_bp = Blueprint('media_mgmt', __name__)

@media_mgmt_bp.route('', methods=['GET'])
def list_media():
    """List media files"""
    try:
        from flashflow_cli.integrations.media_integration import get_media_manager
        
        media_manager = get_media_manager()
        if not media_manager:
            return jsonify({'error': 'Media system not initialized'}), 500
        
        media_type = request.args.get('type')
        limit = int(request.args.get('limit', 100))
        
        media_files = media_manager.list_media(media_type, limit)
        
        return jsonify({
            'media': [
                {
                    'id': m.id,
                    'filename': m.filename,
                    'original_filename': m.original_filename,
                    'file_size': m.file_size,
                    'mime_type': m.mime_type,
                    'media_type': m.media_type,
                    'width': m.width,
                    'height': m.height,
                    'created_at': m.created_at.isoformat() if m.created_at else None,
                    'url': f'/api/media/{m.id}'
                } for m in media_files
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to list media: {str(e)}'}), 500

@media_mgmt_bp.route('/<media_id>', methods=['DELETE'])
def delete_media(media_id):
    """Delete media file"""
    try:
        from flashflow_cli.integrations.media_integration import get_media_manager
        
        media_manager = get_media_manager()
        if not media_manager:
            return jsonify({'error': 'Media system not initialized'}), 500
        
        success = media_manager.delete_media(media_id)
        
        if success:
            return jsonify({'message': 'Media deleted successfully'})
        else:
            return jsonify({'error': 'Media not found'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete media: {str(e)}'}), 500

def register_management_routes(app):
    app.register_blueprint(media_mgmt_bp, url_prefix='/api/media')'''
    
    def _generate_media_serving_endpoint(self) -> str:
        """Generate media serving endpoint"""
        return '''from flask import Blueprint, send_file, request, jsonify
import os

media_serve_bp = Blueprint('media_serve', __name__)

@media_serve_bp.route('/<media_id>')
def serve_media(media_id):
    """Serve media file"""
    try:
        from flashflow_cli.integrations.media_integration import get_media_manager
        
        media_manager = get_media_manager()
        if not media_manager:
            return jsonify({'error': 'Media system not initialized'}), 500
        
        variant = request.args.get('variant')  # thumbnail, small, medium, large
        
        # Get media file
        media_file = media_manager.get_media(media_id)
        if not media_file:
            return jsonify({'error': 'Media not found'}), 404
        
        # Determine file path
        if variant and media_file.metadata and 'variants' in media_file.metadata:
            # Find variant
            for variant_data in media_file.metadata['variants']:
                if variant_data['variant_type'] == variant:
                    file_path = variant_data['file_path']
                    break
            else:
                file_path = media_file.file_path  # Fallback to original
        else:
            file_path = media_file.file_path
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on disk'}), 404
        
        return send_file(file_path, mimetype=media_file.mime_type)
        
    except Exception as e:
        return jsonify({'error': f'Failed to serve media: {str(e)}'}), 500

def register_serving_routes(app):
    app.register_blueprint(media_serve_bp, url_prefix='/api/media')'''

# Global functions for Flask integration
_integration_instance = None

def initialize_media_integration(config: Dict[str, Any] = None):
    """Initialize global media integration"""
    global _integration_instance
    _integration_instance = MediaIntegration()
    return _integration_instance.initialize(config)

def get_media_manager():
    """Get media manager from global integration"""
    if _integration_instance:
        return _integration_instance.media_manager
    return None

def get_generated_components():
    """Get generated React components"""
    if _integration_instance:
        return _integration_instance.generate_react_components()
    return {}

def get_generated_routes():
    """Get generated Flask routes"""
    if _integration_instance:
        return _integration_instance.generate_flask_routes()
    return {}