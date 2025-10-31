"""
AutoML Integration for FlashFlow Laravel Frontend
Provides API endpoints and integration points for AutoML functionality
"""

import json
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from ..services.automl_service import AutoMLService

# Initialize AutoML service
automl_service = AutoMLService()

def register_automl_routes(app: Flask):
    """
    Register AutoML API routes with Flask app
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.route('/api/v1/automl/pipelines', methods=['GET'])
    def list_pipelines():
        """List all AutoML pipelines"""
        try:
            pipelines = automl_service.list_pipelines()
            return jsonify({
                "success": True,
                "data": pipelines
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/automl/pipelines', methods=['POST'])
    def create_pipeline():
        """Create a new AutoML pipeline"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'dataset_path', 'target_column']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Create pipeline
            pipeline_id = automl_service.create_pipeline(
                name=data['name'],
                dataset_path=data['dataset_path'],
                target_column=data['target_column'],
                algorithm=data.get('algorithm', 'auto')
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "pipeline_id": pipeline_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/automl/pipelines/<pipeline_id>', methods=['GET'])
    def get_pipeline(pipeline_id):
        """Get a specific AutoML pipeline"""
        try:
            pipeline = automl_service.get_pipeline(pipeline_id)
            return jsonify({
                "success": True,
                "data": pipeline
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
    
    @app.route('/api/v1/automl/pipelines/<pipeline_id>/run', methods=['POST'])
    def run_pipeline(pipeline_id):
        """Run an AutoML pipeline"""
        try:
            success = automl_service.run_pipeline(pipeline_id)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Pipeline started successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to start pipeline"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/automl/pipelines/<pipeline_id>', methods=['DELETE'])
    def delete_pipeline(pipeline_id):
        """Delete an AutoML pipeline"""
        try:
            success = automl_service.delete_pipeline(pipeline_id)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Pipeline deleted successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Pipeline not found"
                }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500


def get_automl_dashboard_data() -> Dict[str, Any]:
    """
    Get data for AutoML dashboard
    
    Returns:
        dict: Dashboard data including pipeline statistics
    """
    try:
        pipelines = automl_service.list_pipelines()
        
        # Calculate statistics
        total_pipelines = len(pipelines)
        completed_pipelines = len([p for p in pipelines if p["status"] == "completed"])
        running_pipelines = len([p for p in pipelines if p["status"] == "running"])
        
        return {
            "total_pipelines": total_pipelines,
            "completed_pipelines": completed_pipelines,
            "running_pipelines": running_pipelines,
            "success_rate": (completed_pipelines / total_pipelines * 100) if total_pipelines > 0 else 0
        }
    except Exception as e:
        return {
            "error": str(e)
        }