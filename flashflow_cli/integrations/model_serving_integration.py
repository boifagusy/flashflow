"""
Model Serving Integration for FlashFlow Laravel Frontend
Provides API endpoints and integration points for Model Serving functionality
"""

import json
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from ..services.model_serving_service import ModelServingService

# Initialize Model Serving service
model_serving_service = ModelServingService()

def register_model_serving_routes(app: Flask):
    """
    Register Model Serving API routes with Flask app
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.route('/api/v1/models', methods=['GET'])
    def list_deployments():
        """List all model deployments"""
        try:
            deployments = model_serving_service.list_deployments()
            return jsonify({
                "success": True,
                "data": deployments
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/models', methods=['POST'])
    def deploy_model():
        """Deploy a new model"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'model_path']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Deploy model
            deployment_id = model_serving_service.deploy_model(
                name=data['name'],
                model_path=data['model_path'],
                framework=data.get('framework', 'sklearn'),
                version=data.get('version', '1.0')
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "deployment_id": deployment_id,
                    "endpoint": f"/api/v1/models/{deployment_id}/predict"
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/models/<deployment_id>', methods=['GET'])
    def get_deployment(deployment_id):
        """Get a specific model deployment"""
        try:
            deployment = model_serving_service.get_deployment(deployment_id)
            return jsonify({
                "success": True,
                "data": deployment
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
    
    @app.route('/api/v1/models/<deployment_id>/predict', methods=['POST'])
    def predict(deployment_id):
        """Make predictions using a deployed model"""
        try:
            input_data = request.get_json()
            
            # Make prediction
            result = model_serving_service.predict(deployment_id, input_data)
            
            if "error" in result:
                return jsonify({
                    "success": False,
                    "error": result["error"]
                }), 500
            else:
                return jsonify({
                    "success": True,
                    "data": result
                })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/models/<deployment_id>', methods=['DELETE'])
    def undeploy_model(deployment_id):
        """Undeploy a model"""
        try:
            success = model_serving_service.undeploy_model(deployment_id)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Model undeployed successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Model deployment not found"
                }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500


def get_model_serving_dashboard_data() -> Dict[str, Any]:
    """
    Get data for Model Serving dashboard
    
    Returns:
        dict: Dashboard data including deployment statistics
    """
    try:
        deployments = model_serving_service.list_deployments()
        
        # Calculate statistics
        total_deployments = len(deployments)
        active_deployments = len([d for d in deployments if d["status"] == "deployed"])
        
        # Framework distribution
        framework_distribution = {}
        for deployment in deployments:
            framework = deployment.get("framework", "unknown")
            framework_distribution[framework] = framework_distribution.get(framework, 0) + 1
        
        return {
            "total_deployments": total_deployments,
            "active_deployments": active_deployments,
            "framework_distribution": framework_distribution
        }
    except Exception as e:
        return {
            "error": str(e)
        }