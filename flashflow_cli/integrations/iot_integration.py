"""
IoT Integration for FlashFlow Laravel Frontend
Provides API endpoints and integration points for IoT device management
"""

import json
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from ..services.iot_service import iot_service

def register_iot_routes(app: Flask):
    """
    Register IoT API routes with Flask app
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.route('/api/v1/iot/devices', methods=['GET'])
    def iot_list_devices():
        """List all IoT devices"""
        try:
            devices = iot_service.list_devices()
            return jsonify({
                "success": True,
                "data": devices
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/iot/devices', methods=['POST'])
    def iot_register_device():
        """Register a new IoT device"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'device_type']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Register device
            device_id = iot_service.register_device(
                name=data['name'],
                device_type=data['device_type'],
                protocol=data.get('protocol', 'MQTT')
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
    
    @app.route('/api/v1/iot/devices/<device_id>', methods=['GET'])
    def iot_get_device(device_id):
        """Get a specific IoT device"""
        try:
            device = iot_service.get_device(device_id)
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
    
    @app.route('/api/v1/iot/devices/<device_id>/status', methods=['PUT'])
    def update_device_status(device_id):
        """Update device status"""
        try:
            data = request.get_json()
            
            if 'status' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing required field: status"
                }), 400
            
            success = iot_service.update_device_status(device_id, data['status'])
            if success:
                return jsonify({
                    "success": True,
                    "message": "Device status updated successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to update device status"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/iot/devices/<device_id>/commands', methods=['POST'])
    def send_command(device_id):
        """Send command to device"""
        try:
            data = request.get_json()
            
            if 'command' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing required field: command"
                }), 400
            
            command_id = iot_service.send_command(
                device_id=device_id,
                command=data['command'],
                parameters=data.get('parameters', {})
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "command_id": command_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/iot/devices/<device_id>/telemetry', methods=['POST'])
    def record_telemetry(device_id):
        """Record telemetry data from device"""
        try:
            data = request.get_json()
            
            if 'data' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing required field: data"
                }), 400
            
            success = iot_service.record_telemetry(device_id, data['data'])
            if success:
                return jsonify({
                    "success": True,
                    "message": "Telemetry recorded successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to record telemetry"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/iot/devices/<device_id>/telemetry', methods=['GET'])
    def get_telemetry(device_id):
        """Get telemetry data for device"""
        try:
            limit = int(request.args.get('limit', 100))
            telemetry = iot_service.get_telemetry(device_id, limit)
            
            return jsonify({
                "success": True,
                "data": telemetry
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/iot/devices/<device_id>', methods=['DELETE'])
    def iot_delete_device(device_id):
        """Delete an IoT device"""
        try:
            success = iot_service.delete_device(device_id)
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


def get_iot_dashboard_data() -> Dict[str, Any]:
    """
    Get data for IoT dashboard
    
    Returns:
        dict: Dashboard data including device statistics
    """
    try:
        devices = iot_service.list_devices()
        
        # Calculate statistics
        total_devices = len(devices)
        active_devices = len([d for d in devices if d["status"] == "active"])
        registered_devices = len([d for d in devices if d["status"] == "registered"])
        
        # Group by device type
        device_types = {}
        for device in devices:
            device_type = device.get("device_type", "unknown")
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        return {
            "total_devices": total_devices,
            "active_devices": active_devices,
            "registered_devices": registered_devices,
            "device_types": device_types
        }
    except Exception as e:
        return {
            "error": str(e)
        }