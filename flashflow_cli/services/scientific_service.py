"""
Scientific Instruments Service for FlashFlow
Provides laboratory equipment connectivity and scientific data acquisition
"""

import json
import os
from typing import Dict, Any, List
import uuid
from datetime import datetime
import hashlib
import math


class ScientificService:
    """Service for managing scientific instruments and data acquisition"""
    
    def __init__(self, storage_path: str = "storage/scientific"):
        """
        Initialize Scientific service
        
        Args:
            storage_path (str): Path to store scientific data
        """
        self.storage_path = storage_path
        self.instruments_file = os.path.join(storage_path, "instruments.json")
        self.experiments_file = os.path.join(storage_path, "experiments.json")
        self.measurements_file = os.path.join(storage_path, "measurements.json")
        self.calibrations_file = os.path.join(storage_path, "calibrations.json")
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        
        # Initialize files if they don't exist
        for file_path in [self.instruments_file, self.experiments_file, 
                         self.measurements_file, self.calibrations_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({"data": []}, f)
    
    def register_instrument(self, name: str, instrument_type: str,
                           vendor: str, model: str) -> str:
        """
        Register a new scientific instrument
        
        Args:
            name (str): Instrument name
            instrument_type (str): Instrument type (spectrometer, microscope, etc.)
            vendor (str): Instrument vendor
            model (str): Instrument model
            
        Returns:
            str: Instrument ID
        """
        instrument_id = str(uuid.uuid4())
        instrument = {
            "instrument_id": instrument_id,
            "name": name,
            "instrument_type": instrument_type,
            "vendor": vendor,
            "model": model,
            "status": "registered",
            "registered_at": datetime.now().isoformat(),
            "last_used": None,
            "serial_number": None,
            "calibration_due": None,
            "supported_measurements": []
        }
        
        # Load existing instruments
        with open(self.instruments_file, 'r') as f:
            data = json.load(f)
        
        # Add new instrument
        data["data"].append(instrument)
        
        # Save updated instruments
        with open(self.instruments_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return instrument_id
    
    def get_instrument(self, instrument_id: str) -> Dict[str, Any]:
        """
        Get instrument by ID
        
        Args:
            instrument_id (str): Instrument ID
            
        Returns:
            dict: Instrument data
        """
        with open(self.instruments_file, 'r') as f:
            data = json.load(f)
        
        for instrument in data["data"]:
            if instrument["instrument_id"] == instrument_id:
                return instrument
        
        raise ValueError(f"Instrument with ID {instrument_id} not found")
    
    def list_instruments(self) -> List[Dict[str, Any]]:
        """
        List all instruments
        
        Returns:
            list: List of all instruments
        """
        with open(self.instruments_file, 'r') as f:
            data = json.load(f)
        
        return data["data"]
    
    def update_instrument_status(self, instrument_id: str, status: str) -> bool:
        """
        Update instrument status
        
        Args:
            instrument_id (str): Instrument ID
            status (str): New status
            
        Returns:
            bool: True if updated successfully
        """
        with open(self.instruments_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for instrument in data["data"]:
            if instrument["instrument_id"] == instrument_id:
                instrument["status"] = status
                instrument["last_used"] = datetime.now().isoformat()
                updated = True
                break
        
        if updated:
            with open(self.instruments_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def create_experiment(self, name: str, description: str,
                         researcher: str, project: str) -> str:
        """
        Create a new experiment
        
        Args:
            name (str): Experiment name
            description (str): Experiment description
            researcher (str): Researcher name
            project (str): Project name
            
        Returns:
            str: Experiment ID
        """
        experiment_id = str(uuid.uuid4())
        experiment = {
            "experiment_id": experiment_id,
            "name": name,
            "description": description,
            "researcher": researcher,
            "project": project,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "instruments": [],
            "measurements": []
        }
        
        # Load existing experiments
        with open(self.experiments_file, 'r') as f:
            data = json.load(f)
        
        # Add new experiment
        data["data"].append(experiment)
        
        # Save updated experiments
        with open(self.experiments_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return experiment_id
    
    def get_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get experiment by ID
        
        Args:
            experiment_id (str): Experiment ID
            
        Returns:
            dict: Experiment data
        """
        with open(self.experiments_file, 'r') as f:
            data = json.load(f)
        
        for experiment in data["data"]:
            if experiment["experiment_id"] == experiment_id:
                return experiment
        
        raise ValueError(f"Experiment with ID {experiment_id} not found")
    
    def add_instrument_to_experiment(self, experiment_id: str, instrument_id: str) -> bool:
        """
        Add instrument to experiment
        
        Args:
            experiment_id (str): Experiment ID
            instrument_id (str): Instrument ID
            
        Returns:
            bool: True if added successfully
        """
        with open(self.experiments_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for experiment in data["data"]:
            if experiment["experiment_id"] == experiment_id:
                if instrument_id not in experiment["instruments"]:
                    experiment["instruments"].append(instrument_id)
                    updated = True
                break
        
        if updated:
            with open(self.experiments_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def start_experiment(self, experiment_id: str) -> bool:
        """
        Start an experiment
        
        Args:
            experiment_id (str): Experiment ID
            
        Returns:
            bool: True if started successfully
        """
        with open(self.experiments_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for experiment in data["data"]:
            if experiment["experiment_id"] == experiment_id:
                experiment["status"] = "running"
                experiment["started_at"] = datetime.now().isoformat()
                updated = True
                break
        
        if updated:
            with open(self.experiments_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def record_measurement(self, experiment_id: str, instrument_id: str,
                          measurement_type: str, value: float,
                          unit: str, metadata: Dict[str, Any] = None) -> str:
        """
        Record a measurement
        
        Args:
            experiment_id (str): Experiment ID
            instrument_id (str): Instrument ID
            measurement_type (str): Type of measurement
            value (float): Measurement value
            unit (str): Measurement unit
            metadata (dict): Additional metadata
            
        Returns:
            str: Measurement ID
        """
        measurement_id = str(uuid.uuid4())
        measurement = {
            "measurement_id": measurement_id,
            "experiment_id": experiment_id,
            "instrument_id": instrument_id,
            "measurement_type": measurement_type,
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Load existing measurements
        with open(self.measurements_file, 'r') as f:
            data = json.load(f)
        
        # Add new measurement
        data["data"].append(measurement)
        
        # Save updated measurements
        with open(self.measurements_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update instrument last used
        self.update_instrument_status(instrument_id, "active")
        
        # Add measurement to experiment
        self._add_measurement_to_experiment(experiment_id, measurement_id)
        
        return measurement_id
    
    def _add_measurement_to_experiment(self, experiment_id: str, measurement_id: str) -> bool:
        """
        Add measurement to experiment
        
        Args:
            experiment_id (str): Experiment ID
            measurement_id (str): Measurement ID
            
        Returns:
            bool: True if added successfully
        """
        with open(self.experiments_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for experiment in data["data"]:
            if experiment["experiment_id"] == experiment_id:
                if measurement_id not in experiment["measurements"]:
                    experiment["measurements"].append(measurement_id)
                    updated = True
                break
        
        if updated:
            with open(self.experiments_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def get_measurements(self, experiment_id: str = None, 
                        instrument_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get measurements with optional filtering
        
        Args:
            experiment_id (str): Filter by experiment ID
            instrument_id (str): Filter by instrument ID
            limit (int): Maximum number of records to return
            
        Returns:
            list: Measurements
        """
        with open(self.measurements_file, 'r') as f:
            data = json.load(f)
        
        measurements = data["data"]
        
        # Apply filters
        if experiment_id:
            measurements = [m for m in measurements if m["experiment_id"] == experiment_id]
        
        if instrument_id:
            measurements = [m for m in measurements if m["instrument_id"] == instrument_id]
        
        # Return most recent records up to limit
        return measurements[-limit:] if len(measurements) > limit else measurements
    
    def calibrate_instrument(self, instrument_id: str, calibration_data: Dict[str, Any]) -> str:
        """
        Calibrate an instrument
        
        Args:
            instrument_id (str): Instrument ID
            calibration_data (dict): Calibration data
            
        Returns:
            str: Calibration ID
        """
        calibration_id = str(uuid.uuid4())
        calibration = {
            "calibration_id": calibration_id,
            "instrument_id": instrument_id,
            "calibration_data": calibration_data,
            "calibrated_at": datetime.now().isoformat(),
            "calibrated_by": calibration_data.get("technician", "unknown"),
            "next_calibration_due": calibration_data.get("next_due")
        }
        
        # Load existing calibrations
        with open(self.calibrations_file, 'r') as f:
            data = json.load(f)
        
        # Add new calibration
        data["data"].append(calibration)
        
        # Save updated calibrations
        with open(self.calibrations_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update instrument calibration info
        self._update_instrument_calibration(instrument_id, calibration)
        
        return calibration_id
    
    def _update_instrument_calibration(self, instrument_id: str, calibration: Dict[str, Any]) -> bool:
        """
        Update instrument calibration information
        
        Args:
            instrument_id (str): Instrument ID
            calibration (dict): Calibration data
            
        Returns:
            bool: True if updated successfully
        """
        with open(self.instruments_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for instrument in data["data"]:
            if instrument["instrument_id"] == instrument_id:
                instrument["calibration_due"] = calibration.get("next_calibration_due")
                updated = True
                break
        
        if updated:
            with open(self.instruments_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def get_calibration_history(self, instrument_id: str) -> List[Dict[str, Any]]:
        """
        Get calibration history for instrument
        
        Args:
            instrument_id (str): Instrument ID
            
        Returns:
            list: Calibration history
        """
        with open(self.calibrations_file, 'r') as f:
            data = json.load(f)
        
        return [c for c in data["data"] if c["instrument_id"] == instrument_id]
    
    def analyze_data(self, measurement_ids: List[str]) -> Dict[str, Any]:
        """
        Perform basic data analysis on measurements
        
        Args:
            measurement_ids (list): List of measurement IDs to analyze
            
        Returns:
            dict: Analysis results
        """
        measurements = []
        for measurement_id in measurement_ids:
            # In a real implementation, we would fetch each measurement
            # For now, we'll simulate by generating random data
            import random
            random.seed(hash(measurement_id))
            measurements.append({
                "id": measurement_id,
                "value": random.uniform(0, 100)
            })
        
        if not measurements:
            return {"error": "No measurements provided"}
        
        values = [m["value"] for m in measurements]
        
        # Calculate basic statistics
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)
        
        return {
            "count": len(values),
            "mean": round(mean, 4),
            "std_dev": round(std_dev, 4),
            "min": min(values),
            "max": max(values),
            "range": max(values) - min(values)
        }
    
    def export_data(self, experiment_id: str, format: str = "csv") -> str:
        """
        Export experiment data
        
        Args:
            experiment_id (str): Experiment ID
            format (str): Export format (csv, json, etc.)
            
        Returns:
            str: Export file path or content
        """
        experiment = self.get_experiment(experiment_id)
        measurements = self.get_measurements(experiment_id=experiment_id)
        
        if format == "json":
            export_data = {
                "experiment": experiment,
                "measurements": measurements
            }
            return json.dumps(export_data, indent=2)
        elif format == "csv":
            # Create CSV content
            csv_content = "Measurement ID,Experiment ID,Instrument ID,Type,Value,Unit,Timestamp\n"
            for measurement in measurements:
                csv_content += f"{measurement['measurement_id']},{measurement['experiment_id']},{measurement['instrument_id']},{measurement['measurement_type']},{measurement['value']},{measurement['unit']},{measurement['timestamp']}\n"
            return csv_content
        else:
            return f"Export format {format} not supported"
    
    def delete_instrument(self, instrument_id: str) -> bool:
        """
        Delete instrument
        
        Args:
            instrument_id (str): Instrument ID
            
        Returns:
            bool: True if deleted successfully
        """
        with open(self.instruments_file, 'r') as f:
            data = json.load(f)
        
        original_count = len(data["data"])
        data["data"] = [
            d for d in data["data"] if d["instrument_id"] != instrument_id
        ]
        
        if len(data["data"]) < original_count:
            with open(self.instruments_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False


# Global instance
scientific_service = ScientificService()