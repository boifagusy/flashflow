"""
Scientific Instruments Integration for FlashFlow Laravel Frontend
Provides API endpoints and integration points for scientific instruments
"""

import json
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from ..services.scientific_service import scientific_service

def register_scientific_routes(app: Flask):
    """
    Register Scientific Instruments API routes with Flask app
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.route('/api/v1/scientific/instruments', methods=['GET'])
    def list_instruments():
        """List all scientific instruments"""
        try:
            instruments = scientific_service.list_instruments()
            return jsonify({
                "success": True,
                "data": instruments
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/scientific/instruments', methods=['POST'])
    def register_instrument():
        """Register a new scientific instrument"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'instrument_type', 'vendor', 'model']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Register instrument
            instrument_id = scientific_service.register_instrument(
                name=data['name'],
                instrument_type=data['instrument_type'],
                vendor=data['vendor'],
                model=data['model']
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "instrument_id": instrument_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/scientific/instruments/<instrument_id>', methods=['GET'])
    def get_instrument(instrument_id):
        """Get instrument by ID"""
        try:
            instrument = scientific_service.get_instrument(instrument_id)
            return jsonify({
                "success": True,
                "data": instrument
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
    
    @app.route('/api/v1/scientific/instruments/<instrument_id>/status', methods=['PUT'])
    def update_instrument_status(instrument_id):
        """Update instrument status"""
        try:
            data = request.get_json()
            
            if 'status' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing required field: status"
                }), 400
            
            success = scientific_service.update_instrument_status(instrument_id, data['status'])
            if success:
                return jsonify({
                    "success": True,
                    "message": "Instrument status updated successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to update instrument status"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/scientific/experiments', methods=['POST'])
    def create_experiment():
        """Create a new experiment"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'description', 'researcher', 'project']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            experiment_id = scientific_service.create_experiment(
                name=data['name'],
                description=data['description'],
                researcher=data['researcher'],
                project=data['project']
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "experiment_id": experiment_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/scientific/experiments/<experiment_id>', methods=['GET'])
    def get_experiment(experiment_id):
        """Get experiment by ID"""
        try:
            experiment = scientific_service.get_experiment(experiment_id)
            return jsonify({
                "success": True,
                "data": experiment
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
    
    @app.route('/api/v1/scientific/experiments/<experiment_id>/instruments/<instrument_id>', methods=['POST'])
    def add_instrument_to_experiment(experiment_id, instrument_id):
        """Add instrument to experiment"""
        try:
            success = scientific_service.add_instrument_to_experiment(experiment_id, instrument_id)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Instrument added to experiment successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to add instrument to experiment"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/scientific/experiments/<experiment_id>/start', methods=['POST'])
    def start_experiment(experiment_id):
        """Start an experiment"""
        try:
            success = scientific_service.start_experiment(experiment_id)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Experiment started successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to start experiment"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/scientific/experiments/<experiment_id>/measurements', methods=['POST'])
    def record_measurement(experiment_id):
        """Record a measurement"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['instrument_id', 'measurement_type', 'value', 'unit']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            measurement_id = scientific_service.record_measurement(
                experiment_id=experiment_id,
                instrument_id=data['instrument_id'],
                measurement_type=data['measurement_type'],
                value=float(data['value']),
                unit=data['unit'],
                metadata=data.get('metadata', {})
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "measurement_id": measurement_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/scientific/experiments/<experiment_id>/measurements', methods=['GET'])
    def get_measurements(experiment_id):
        """Get measurements for experiment"""
        try:
            limit = int(request.args.get('limit', 100))
            measurements = scientific_service.get_measurements(
                experiment_id=experiment_id,
                limit=limit
            )
            
            return jsonify({
                "success": True,
                "data": measurements
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/scientific/instruments/<instrument_id>/calibrate', methods=['POST'])
    def calibrate_instrument(instrument_id):
        """Calibrate an instrument"""
        try:
            data = request.get_json()
            
            calibration_id = scientific_service.calibrate_instrument(instrument_id, data)
            
            return jsonify({
                "success": True,
                "data": {
                    "calibration_id": calibration_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/scientific/instruments/<instrument_id>/calibrations', methods=['GET'])
    def get_calibration_history(instrument_id):
        """Get calibration history for instrument"""
        try:
            calibrations = scientific_service.get_calibration_history(instrument_id)
            
            return jsonify({
                "success": True,
                "data": calibrations
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/scientific/measurements/analyze', methods=['POST'])
    def analyze_data():
        """Perform basic data analysis on measurements"""
        try:
            data = request.get_json()
            
            if 'measurement_ids' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing required field: measurement_ids"
                }), 400
            
            analysis = scientific_service.analyze_data(data['measurement_ids'])
            
            return jsonify({
                "success": True,
                "data": analysis
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/scientific/experiments/<experiment_id>/export', methods=['GET'])
    def export_data(experiment_id):
        """Export experiment data"""
        try:
            format = request.args.get('format', 'json')
            export_content = scientific_service.export_data(experiment_id, format)
            
            return jsonify({
                "success": True,
                "data": {
                    "content": export_content,
                    "format": format
                }
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/scientific/instruments/<instrument_id>', methods=['DELETE'])
    def delete_instrument(instrument_id):
        """Delete instrument"""
        try:
            success = scientific_service.delete_instrument(instrument_id)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Instrument deleted successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Instrument not found"
                }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500


def get_scientific_dashboard_data() -> Dict[str, Any]:
    """
    Get data for Scientific Instruments dashboard
    
    Returns:
        dict: Dashboard data including experiment statistics
    """
    try:
        instruments = scientific_service.list_instruments()
        
        # Calculate statistics
        total_instruments = len(instruments)
        active_instruments = len([i for i in instruments if i["status"] == "active"])
        registered_instruments = len([i for i in instruments if i["status"] == "registered"])
        
        # Group by instrument type
        instrument_types = {}
        for instrument in instruments:
            inst_type = instrument.get("instrument_type", "unknown")
            instrument_types[inst_type] = instrument_types.get(inst_type, 0) + 1
        
        return {
            "total_instruments": total_instruments,
            "active_instruments": active_instruments,
            "registered_instruments": registered_instruments,
            "instrument_types": instrument_types
        }
    except Exception as e:
        return {
            "error": str(e)
        }