"""
AutoML Service for FlashFlow
Provides automated machine learning pipeline capabilities
"""

import json
import os
from typing import Dict, Any, List
import uuid
from datetime import datetime


class AutoMLService:
    """Service for managing automated machine learning pipelines"""
    
    def __init__(self, storage_path: str = "storage/automl"):
        """
        Initialize AutoML service
        
        Args:
            storage_path (str): Path to store AutoML pipeline data
        """
        self.storage_path = storage_path
        self.pipelines_file = os.path.join(storage_path, "pipelines.json")
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        
        # Initialize pipelines file if it doesn't exist
        if not os.path.exists(self.pipelines_file):
            with open(self.pipelines_file, 'w') as f:
                json.dump({"pipelines": []}, f)
    
    def create_pipeline(self, name: str, dataset_path: str, 
                       target_column: str, algorithm: str = "auto") -> str:
        """
        Create a new AutoML pipeline
        
        Args:
            name (str): Name of the pipeline
            dataset_path (str): Path to the dataset
            target_column (str): Target column for prediction
            algorithm (str): Algorithm to use (default: auto)
            
        Returns:
            str: Pipeline ID
        """
        pipeline_id = str(uuid.uuid4())
        pipeline = {
            "id": pipeline_id,
            "name": name,
            "dataset_path": dataset_path,
            "target_column": target_column,
            "algorithm": algorithm,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metrics": {},
            "model_path": None
        }
        
        # Load existing pipelines
        with open(self.pipelines_file, 'r') as f:
            data = json.load(f)
        
        # Add new pipeline
        data["pipelines"].append(pipeline)
        
        # Save updated pipelines
        with open(self.pipelines_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return pipeline_id
    
    def get_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Get pipeline by ID
        
        Args:
            pipeline_id (str): Pipeline ID
            
        Returns:
            dict: Pipeline data
        """
        with open(self.pipelines_file, 'r') as f:
            data = json.load(f)
        
        for pipeline in data["pipelines"]:
            if pipeline["id"] == pipeline_id:
                return pipeline
        
        raise ValueError(f"Pipeline with ID {pipeline_id} not found")
    
    def list_pipelines(self) -> List[Dict[str, Any]]:
        """
        List all pipelines
        
        Returns:
            list: List of all pipelines
        """
        with open(self.pipelines_file, 'r') as f:
            data = json.load(f)
        
        return data["pipelines"]
    
    def update_pipeline_status(self, pipeline_id: str, status: str, 
                              metrics: Dict[str, Any] = None) -> bool:
        """
        Update pipeline status
        
        Args:
            pipeline_id (str): Pipeline ID
            status (str): New status
            metrics (dict): Evaluation metrics
            
        Returns:
            bool: True if updated successfully
        """
        with open(self.pipelines_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for pipeline in data["pipelines"]:
            if pipeline["id"] == pipeline_id:
                pipeline["status"] = status
                pipeline["updated_at"] = datetime.now().isoformat()
                if metrics:
                    pipeline["metrics"] = metrics
                updated = True
                break
        
        if updated:
            with open(self.pipelines_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def run_pipeline(self, pipeline_id: str) -> bool:
        """
        Run AutoML pipeline (simulated)
        
        Args:
            pipeline_id (str): Pipeline ID
            
        Returns:
            bool: True if pipeline started successfully
        """
        # In a real implementation, this would trigger the actual AutoML process
        # For now, we'll just update the status to "running"
        success = self.update_pipeline_status(pipeline_id, "running")
        if success:
            # Simulate completion after some processing
            # In reality, this would involve actual ML training
            self.update_pipeline_status(
                pipeline_id, 
                "completed", 
                {
                    "accuracy": 0.92,
                    "precision": 0.89,
                    "recall": 0.91,
                    "f1_score": 0.90
                }
            )
        return success
    
    def delete_pipeline(self, pipeline_id: str) -> bool:
        """
        Delete pipeline
        
        Args:
            pipeline_id (str): Pipeline ID
            
        Returns:
            bool: True if deleted successfully
        """
        with open(self.pipelines_file, 'r') as f:
            data = json.load(f)
        
        original_count = len(data["pipelines"])
        data["pipelines"] = [
            p for p in data["pipelines"] if p["id"] != pipeline_id
        ]
        
        if len(data["pipelines"]) < original_count:
            with open(self.pipelines_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False


# Global instance
automl_service = AutoMLService()