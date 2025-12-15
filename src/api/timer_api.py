"""
Timer API Endpoints
REST API endpoints for managing countdown timers.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from ..services.timer_service import timer_service
from ..models.timer import create_timer

logger = logging.getLogger(__name__)
timer_api = Blueprint('timer_api', __name__, url_prefix='/api/timers')

@timer_api.route('', methods=['POST'])
def create_timer_endpoint():
    """Create a new timer"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'title', 'duration']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create timer
        timer_id = timer_service.create_timer(
            user_id=data['user_id'],
            title=data['title'],
            duration=int(data['duration']),
            notification_enabled=data.get('notification_enabled', True),
            notification_message=data.get('notification_message'),
            repeat=data.get('repeat', False),
            tags=data.get('tags')
        )
        
        return jsonify({
            'success': True,
            'timer_id': timer_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating timer: {e}")
        return jsonify({'error': 'Failed to create timer'}), 500

@timer_api.route('/<timer_id>', methods=['GET'])
def get_timer_endpoint(timer_id):
    """Get a timer by ID"""
    try:
        timer = timer_service.get_timer(timer_id)
        if not timer:
            return jsonify({'error': 'Timer not found'}), 404
        
        # Convert timer to dict for JSON serialization
        timer_dict = {
            'id': timer.id,
            'user_id': timer.user_id,
            'title': timer.title,
            'duration': timer.duration,
            'remaining_time': timer.remaining_time,
            'status': timer.status,
            'created_at': timer.created_at.isoformat() if timer.created_at else None,
            'started_at': timer.started_at.isoformat() if timer.started_at else None,
            'completed_at': timer.completed_at.isoformat() if timer.completed_at else None,
            'notification_enabled': timer.notification_enabled,
            'notification_message': timer.notification_message,
            'repeat': timer.repeat,
            'tags': timer.tags
        }
        
        return jsonify(timer_dict), 200
        
    except Exception as e:
        logger.error(f"Error getting timer: {e}")
        return jsonify({'error': 'Failed to get timer'}), 500

@timer_api.route('/user/<user_id>', methods=['GET'])
def get_user_timers_endpoint(user_id):
    """Get all timers for a user"""
    try:
        limit = int(request.args.get('limit', 50))
        timers = timer_service.get_user_timers(user_id, limit)
        
        # Convert timers to dicts for JSON serialization
        timers_list = []
        for timer in timers:
            timers_list.append({
                'id': timer.id,
                'user_id': timer.user_id,
                'title': timer.title,
                'duration': timer.duration,
                'remaining_time': timer.remaining_time,
                'status': timer.status,
                'created_at': timer.created_at.isoformat() if timer.created_at else None,
                'started_at': timer.started_at.isoformat() if timer.started_at else None,
                'completed_at': timer.completed_at.isoformat() if timer.completed_at else None,
                'notification_enabled': timer.notification_enabled,
                'notification_message': timer.notification_message,
                'repeat': timer.repeat,
                'tags': timer.tags
            })
        
        return jsonify(timers_list), 200
        
    except Exception as e:
        logger.error(f"Error getting user timers: {e}")
        return jsonify({'error': 'Failed to get user timers'}), 500

@timer_api.route('/<timer_id>/status', methods=['PUT'])
def update_timer_status_endpoint(timer_id):
    """Update timer status"""
    try:
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Missing status field'}), 400
        
        success = timer_service.update_timer_status(timer_id, data['status'])
        if not success:
            return jsonify({'error': 'Failed to update timer status'}), 500
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Error updating timer status: {e}")
        return jsonify({'error': 'Failed to update timer status'}), 500

@timer_api.route('/<timer_id>/time', methods=['PUT'])
def update_timer_time_endpoint(timer_id):
    """Update timer remaining time"""
    try:
        data = request.get_json()
        
        if 'remaining_time' not in data:
            return jsonify({'error': 'Missing remaining_time field'}), 400
        
        success = timer_service.update_remaining_time(timer_id, int(data['remaining_time']))
        if not success:
            return jsonify({'error': 'Failed to update timer time'}), 500
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Error updating timer time: {e}")
        return jsonify({'error': 'Failed to update timer time'}), 500

@timer_api.route('/<timer_id>', methods=['DELETE'])
def delete_timer_endpoint(timer_id):
    """Delete a timer"""
    try:
        success = timer_service.delete_timer(timer_id)
        if not success:
            return jsonify({'error': 'Failed to delete timer'}), 500
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Error deleting timer: {e}")
        return jsonify({'error': 'Failed to delete timer'}), 500