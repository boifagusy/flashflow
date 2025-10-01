"""
Base Generator for FlashFlow
"""

from pathlib import Path
from typing import Dict, Any


class BaseGenerator:
    """Base class for all FlashFlow generators"""
    
    def __init__(self, project_path: str, project_name: str):
        """
        Initialize the base generator.
        
        Args:
            project_path: Path to the project directory
            project_name: Name of the project
        """
        self.project_path = Path(project_path)
        self.project_name = project_name
    
    def generate(self, ir: Dict[str, Any]) -> None:
        """
        Generate code from IR.
        
        Args:
            ir: Intermediate representation of the application
        """
        raise NotImplementedError("Subclasses must implement generate method")