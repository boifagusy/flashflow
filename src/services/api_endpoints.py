"""
API Endpoints for User Activity and Notifications
================================================

Flask API endpoints for tracking user activities and managing notifications.
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import logging

from .user_activity_service import user_activity_service
from .notification_service import notification_service

logger = logging.getLogger(__name__)

def register_api_endpoints(app: Flask):
    """Register API endpoints for user activity tracking and notifications"""
    
    @app.route('/api/activity/track', methods=['POST'])
    def track_user_activity():
        """Track a user activity"""
        try:
            data = request.get_json()
            
            activity_id = user_activity_service.track_activity(
                user_id=data.get('user_id'),
                activity_type=data.get('activity_type'),
                session_id=data.get('session_id'),
                metadata=data.get('metadata'),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                referrer=data.get('referrer'),
                page_url=data.get('page_url')
            )
            
            return jsonify({
                'success': True,
                'activity_id': activity_id
            })
            
        except Exception as e:
            logger.error(f"Failed to track user activity: {e}")
            return jsonify({'error': 'Failed to track activity'}), 500
    
    @app.route('/api/session/start', methods=['POST'])
    def start_user_session():
        """Start a user session"""
        try:
            data = request.get_json()
            
            session_id = user_activity_service.start_session(
                user_id=data.get('user_id'),
                ip_address=request.remote_addr,
                device_info=data.get('device_info')
            )
            
            return jsonify({
                'success': True,
                'session_id': session_id
            })
            
        except Exception as e:
            logger.error(f"Failed to start user session: {e}")
            return jsonify({'error': 'Failed to start session'}), 500
    
    @app.route('/api/session/end/<session_id>', methods=['POST'])
    def end_user_session(session_id):
        """End a user session"""
        try:
            success = user_activity_service.end_session(session_id)
            
            return jsonify({
                'success': success
            })
            
        except Exception as e:
            logger.error(f"Failed to end user session: {e}")
            return jsonify({'error': 'Failed to end session'}), 500
    
    @app.route('/api/analytics/user/<user_id>', methods=['GET'])
    def get_user_analytics(user_id):
        """Get user analytics"""
        try:
            analytics = user_activity_service.get_user_analytics(user_id)
            
            return jsonify({
                'success': True,
                'analytics': {
                    'user_id': analytics.user_id,
                    'total_sessions': analytics.total_sessions,
                    'total_activities': analytics.total_activities,
                    'last_activity': analytics.last_activity.isoformat() if analytics.last_activity else None,
                    'avg_session_duration': analytics.avg_session_duration,
                    'most_visited_pages': analytics.most_visited_pages,
                    'favorite_features': analytics.favorite_features,
                    'engagement_score': analytics.engagement_score
                }
            })
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return jsonify({'error': 'Failed to get analytics'}), 500
    
    @app.route('/api/notifications/send', methods=['POST'])
    def send_notification():
        """Send a notification"""
        try:
            data = request.get_json()
            
            notification_id = notification_service.send_notification(
                user_id=data.get('user_id'),
                title=data.get('title'),
                message=data.get('message'),
                notification_type=data.get('notification_type'),
                channel=data.get('channel'),
                data=data.get('data'),
                priority=data.get('priority', 'normal'),
                scheduled_at=datetime.fromisoformat(data['scheduled_at']) if data.get('scheduled_at') else None,
                device_tokens=data.get('device_tokens')
            )
            
            return jsonify({
                'success': True,
                'notification_id': notification_id
            })
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return jsonify({'error': 'Failed to send notification'}), 500
    
    @app.route('/api/notifications/preferences', methods=['POST'])
    def update_notification_preference():
        """Update notification preferences"""
        try:
            data = request.get_json()
            
            success = notification_service.update_notification_preference(
                user_id=data.get('user_id'),
                notification_type=data.get('notification_type'),
                channel=data.get('channel'),
                enabled=data.get('enabled', True)
            )
            
            return jsonify({
                'success': success
            })
            
        except Exception as e:
            logger.error(f"Failed to update notification preference: {e}")
            return jsonify({'error': 'Failed to update preference'}), 500
    
    @app.route('/api/notifications/preferences/<user_id>/<notification_type>/<channel>', methods=['GET'])
    def get_notification_preference(user_id, notification_type, channel):
        """Get a specific notification preference"""
        try:
            # This would need to be implemented in the notification service
            # For now, we'll return a default response
            return jsonify({
                'success': True,
                'enabled': True
            })
            
        except Exception as e:
            logger.error(f"Failed to get notification preference: {e}")
            return jsonify({'error': 'Failed to get preference'}), 500
    
    @app.route('/api/notifications/user/<user_id>', methods=['GET'])
    def get_user_notifications(user_id):
        """Get notifications for a user"""
        try:
            limit = int(request.args.get('limit', 50))
            notifications = notification_service.get_user_notifications(user_id, limit)
            
            return jsonify({
                'success': True,
                'notifications': notifications
            })
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return jsonify({'error': 'Failed to get notifications'}), 500
    
    @app.route('/api/notifications/read/<notification_id>', methods=['POST'])
    def mark_notification_as_read(notification_id):
        """Mark a notification as read"""
        try:
            success = notification_service.mark_notification_as_read(notification_id)
            
            return jsonify({
                'success': success
            })
            
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")
            return jsonify({'error': 'Failed to mark notification as read'}), 500
    
    @app.route('/api/devices/register', methods=['POST'])
    def register_device_token():
        """Register a device token for push notifications"""
        try:
            data = request.get_json()
            
            device_token_id = notification_service.register_device_token(
                user_id=data.get('user_id'),
                token=data.get('token'),
                platform=data.get('platform'),
                device_info=data.get('device_info')
            )
            
            return jsonify({
                'success': True,
                'device_token_id': device_token_id
            })
            
        except Exception as e:
            logger.error(f"Failed to register device token: {e}")
            return jsonify({'error': 'Failed to register device token'}), 500
    
    logger.info("User activity and notification API endpoints registered")