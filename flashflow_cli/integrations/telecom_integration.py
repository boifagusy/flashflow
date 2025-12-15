"""
Telecommunications Integration for FlashFlow Laravel Frontend
Provides API endpoints and integration points for telecommunications equipment
"""

import json
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from ..services.telecom_service import telecom_service

def register_telecom_routes(app: Flask):
    """
    Register Telecommunications API routes with Flask app
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.route('/api/v1/telecom/equipment', methods=['GET'])
    def list_equipment():
        """List all telecommunications equipment"""
        try:
            equipment = telecom_service.list_equipment()
            return jsonify({
                "success": True,
                "data": equipment
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/telecom/equipment', methods=['POST'])
    def register_equipment():
        """Register new telecommunications equipment"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'equipment_type', 'vendor', 'model']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Register equipment
            equipment_id = telecom_service.register_equipment(
                name=data['name'],
                equipment_type=data['equipment_type'],
                vendor=data['vendor'],
                model=data['model']
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "equipment_id": equipment_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/telecom/equipment/<equipment_id>', methods=['GET'])
    def get_equipment(equipment_id):
        """Get equipment by ID"""
        try:
            equipment = telecom_service.get_equipment(equipment_id)
            return jsonify({
                "success": True,
                "data": equipment
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
    
    @app.route('/api/v1/telecom/equipment/<equipment_id>/status', methods=['PUT'])
    def update_equipment_status(equipment_id):
        """Update equipment status"""
        try:
            data = request.get_json()
            
            if 'status' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing required field: status"
                }), 400
            
            success = telecom_service.update_equipment_status(
                equipment_id=equipment_id,
                status=data['status'],
                ip_address=data.get('ip_address')
            )
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Equipment status updated successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to update equipment status"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/telecom/networks', methods=['POST'])
    def create_network():
        """Create a new network"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'network_type']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            network_id = telecom_service.create_network(
                name=data['name'],
                network_type=data['network_type'],
                frequency_band=data.get('frequency_band', '2.4GHz')
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "network_id": network_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/telecom/networks/<network_id>', methods=['GET'])
    def get_network(network_id):
        """Get network by ID"""
        try:
            network = telecom_service.get_network(network_id)
            return jsonify({
                "success": True,
                "data": network
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
    
    @app.route('/api/v1/telecom/networks', methods=['GET'])
    def list_networks():
        """List all networks"""
        try:
            networks = telecom_service.list_networks()
            return jsonify({
                "success": True,
                "data": networks
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/telecom/networks/<network_id>/equipment/<equipment_id>', methods=['POST'])
    def add_equipment_to_network(network_id, equipment_id):
        """Add equipment to network"""
        try:
            success = telecom_service.add_equipment_to_network(network_id, equipment_id)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Equipment added to network successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to add equipment to network"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/telecom/connections', methods=['POST'])
    def establish_connection():
        """Establish a connection between two entities"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['source_id', 'destination_id']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            connection_id = telecom_service.establish_connection(
                source_id=data['source_id'],
                destination_id=data['destination_id'],
                connection_type=data.get('connection_type', 'data')
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "connection_id": connection_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/telecom/equipment/<equipment_id>/signal', methods=['POST'])
    def monitor_signal(equipment_id):
        """Monitor signal from equipment"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['signal_strength', 'signal_quality']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            success = telecom_service.monitor_signal(
                equipment_id=equipment_id,
                signal_strength=float(data['signal_strength']),
                signal_quality=float(data['signal_quality'])
            )
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Signal monitored successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to monitor signal"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/telecom/equipment/<equipment_id>/signal', methods=['GET'])
    def get_signal_history(equipment_id):
        """Get signal history for equipment"""
        try:
            limit = int(request.args.get('limit', 100))
            signal_history = telecom_service.get_signal_history(equipment_id, limit)
            
            return jsonify({
                "success": True,
                "data": signal_history
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/telecom/networks/<network_id>/topology', methods=['GET'])
    def get_network_topology(network_id):
        """Get network topology information"""
        try:
            topology = telecom_service.get_network_topology(network_id)
            
            return jsonify({
                "success": True,
                "data": topology
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/telecom/equipment/<equipment_id>', methods=['DELETE'])
    def delete_equipment(equipment_id):
        """Delete equipment"""
        try:
            success = telecom_service.delete_equipment(equipment_id)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Equipment deleted successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Equipment not found"
                }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500


def get_telecom_dashboard_data() -> Dict[str, Any]:
    """
    Get data for Telecommunications dashboard
    
    Returns:
        dict: Dashboard data including network statistics
    """
    try:
        equipment = telecom_service.list_equipment()
        networks = telecom_service.list_networks()
        
        # Calculate statistics
        total_equipment = len(equipment)
        active_equipment = len([e for e in equipment if e["status"] == "active"])
        registered_equipment = len([e for e in equipment if e["status"] == "registered"])
        
        total_networks = len(networks)
        equipment_types = {}
        network_types = {}
        
        # Group equipment by type
        for eq in equipment:
            eq_type = eq.get("equipment_type", "unknown")
            equipment_types[eq_type] = equipment_types.get(eq_type, 0) + 1
        
        # Group networks by type
        for network in networks:
            net_type = network.get("network_type", "unknown")
            network_types[net_type] = network_types.get(net_type, 0) + 1
        
        return {
            "total_equipment": total_equipment,
            "active_equipment": active_equipment,
            "registered_equipment": registered_equipment,
            "total_networks": total_networks,
            "equipment_types": equipment_types,
            "network_types": network_types
        }
    except Exception as e:
        return {
            "error": str(e)
        }