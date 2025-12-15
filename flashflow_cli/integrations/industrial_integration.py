"""
Industrial Systems Integration for FlashFlow Laravel Frontend
Provides API endpoints and integration points for industrial control systems
"""

import json
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from ..services.industrial_service import industrial_service

def register_industrial_routes(app: Flask):
    """
    Register Industrial Systems API routes with Flask app
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.route('/api/v1/industrial/devices', methods=['GET'])
    def industrial_list_devices():
        """List all industrial devices"""
        try:
            devices = industrial_service.list_devices()
            return jsonify({
                "success": True,
                "data": devices
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/industrial/devices', methods=['POST'])
    def industrial_register_device():
        """Register a new industrial device"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'protocol', 'ip_address', 'port']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Register device
            device_id = industrial_service.register_device(
                name=data['name'],
                protocol=data['protocol'],
                ip_address=data['ip_address'],
                port=int(data['port'])
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "device_id": device_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/industrial/devices/<device_id>', methods=['GET'])
    def industrial_get_device(device_id):
        """Get a specific industrial device"""
        try:
            device = industrial_service.get_device(device_id)
            return jsonify({
                "success": True,
                "data": device
            })
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/industrial/devices/<device_id>/tags', methods=['POST'])
    def add_tag(device_id):
        """Add a tag to device"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['tag_name', 'tag_address', 'data_type']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            success = industrial_service.add_tag(
                device_id=device_id,
                tag_name=data['tag_name'],
                tag_address=data['tag_address'],
                data_type=data['data_type']
            )
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Tag added successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to add tag"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/industrial/devices/<device_id>/tags/<tag_name>/read', methods=['GET'])
    def read_tag(device_id, tag_name):
        """Read tag value from device"""
        try:
            value = industrial_service.read_tag(device_id, tag_name)
            
            return jsonify({
                "success": True,
                "data": {
                    "device_id": device_id,
                    "tag_name": tag_name,
                    "value": value
                }
            })
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/industrial/devices/<device_id>/tags/<tag_name>/write', methods=['POST'])
    def write_tag(device_id, tag_name):
        """Write tag value to device"""
        try:
            data = request.get_json()
            
            if 'value' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing required field: value"
                }), 400
            
            success = industrial_service.write_tag(device_id, tag_name, data['value'])
            if success:
                return jsonify({
                    "success": True,
                    "message": "Tag written successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to write tag"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/industrial/devices/<device_id>/data', methods=['POST'])
    def record_data(device_id):
        """Record data point from device"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['tag_name', 'value']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            success = industrial_service.record_data(
                device_id=device_id,
                tag_name=data['tag_name'],
                value=data['value']
            )
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Data recorded successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to record data"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/industrial/alarms', methods=['POST'])
    def create_alarm():
        """Create an alarm"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['device_id', 'tag_name', 'condition', 'severity', 'message']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            alarm_id = industrial_service.create_alarm(
                device_id=data['device_id'],
                tag_name=data['tag_name'],
                condition=data['condition'],
                severity=data['severity'],
                message=data['message']
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "alarm_id": alarm_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/industrial/alarms/<alarm_id>/acknowledge', methods=['POST'])
    def acknowledge_alarm(alarm_id):
        """Acknowledge an alarm"""
        try:
            success = industrial_service.acknowledge_alarm(alarm_id)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Alarm acknowledged successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to acknowledge alarm"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/industrial/alarms/active', methods=['GET'])
    def get_active_alarms():
        """Get all active alarms"""
        try:
            alarms = industrial_service.get_active_alarms()
            return jsonify({
                "success": True,
                "data": alarms
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/industrial/devices/<device_id>', methods=['DELETE'])
    def industrial_delete_device(device_id):
        """Delete an industrial device"""
        try:
            success = industrial_service.delete_device(device_id)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Device deleted successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Device not found"
                }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500


def get_industrial_dashboard_data() -> Dict[str, Any]:
    """
    Get data for Industrial Systems dashboard
    
    Returns:
        dict: Dashboard data including device statistics
    """
    try:
        devices = industrial_service.list_devices()
        
        # Calculate statistics
        total_devices = len(devices)
        connected_devices = len([d for d in devices if d["status"] == "connected"])
        registered_devices = len([d for d in devices if d["status"] == "registered"])
        
        # Group by protocol
        protocols = {}
        for device in devices:
            protocol = device.get("protocol", "unknown")
            protocols[protocol] = protocols.get(protocol, 0) + 1
        
        # Get active alarms
        active_alarms = industrial_service.get_active_alarms()
        
        return {
            "total_devices": total_devices,
            "connected_devices": connected_devices,
            "registered_devices": registered_devices,
            "protocols": protocols,
            "active_alarms": len(active_alarms)
        }
    except Exception as e:
        return {
            "error": str(e)
        }