"""
Federated Learning Integration for FlashFlow Laravel Frontend
Provides API endpoints and integration points for Federated Learning functionality
"""

import json
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from ..services.federated_learning_service import FederatedLearningService

# Initialize Federated Learning service
federated_service = FederatedLearningService()

def register_federated_routes(app: Flask):
    """
    Register Federated Learning API routes with Flask app
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.route('/api/v1/federated/models', methods=['GET'])
    def list_models():
        """List all federated learning models"""
        try:
            models = federated_service.list_models()
            return jsonify({
                "success": True,
                "data": models
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/federated/models', methods=['POST'])
    def register_model():
        """Register a new federated learning model"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Register model
            model_id = federated_service.register_model(
                name=data['name'],
                framework=data.get('framework', 'pytorch'),
                version=data.get('version', '1.0')
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "model_id": model_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/federated/models/<model_id>', methods=['GET'])
    def get_model(model_id):
        """Get a specific federated learning model"""
        try:
            model = federated_service.get_model(model_id)
            return jsonify({
                "success": True,
                "data": model
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
    
    @app.route('/api/v1/federated/clients', methods=['POST'])
    def register_client():
        """Register a new federated learning client"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['client_id', 'capabilities']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Register client
            success = federated_service.register_client(
                client_id=data['client_id'],
                capabilities=data['capabilities']
            )
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Client registered successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to register client"
                }), 500
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/federated/models/<model_id>/rounds', methods=['POST'])
    def start_training_round(model_id):
        """Start a new federated learning training round"""
        try:
            data = request.get_json()
            
            # Start training round
            round_id = federated_service.start_training_round(
                model_id=model_id,
                num_clients=data.get('num_clients', 5)
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "round_id": round_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500


def get_federated_dashboard_data() -> Dict[str, Any]:
    """
    Get data for Federated Learning dashboard
    
    Returns:
        dict: Dashboard data including model and client statistics
    """
    try:
        models = federated_service.list_models()
        
        # Calculate statistics
        total_models = len(models)
        active_models = len([m for m in models if m["status"] == "training"])
        
        # For client statistics, we would need to load clients
        # This is a simplified implementation
        with open("storage/federated/clients.json", 'r') as f:
            clients_data = json.load(f)
        
        total_clients = len(clients_data["data"])
        active_clients = len([c for c in clients_data["data"] if c["status"] == "active"])
        
        return {
            "total_models": total_models,
            "active_models": active_models,
            "total_clients": total_clients,
            "active_clients": active_clients
        }
    except Exception as e:
        return {
            "error": str(e)
        }