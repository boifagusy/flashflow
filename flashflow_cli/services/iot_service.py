"""
IoT Device Management Service for FlashFlow
Provides IoT device registration, management, and monitoring capabilities
"""

import json
import os
from typing import Dict, Any, List
import uuid
from datetime import datetime
import hashlib


class IoTDevice:
    """Represents an IoT device"""
    
    def __init__(self, device_id: str, name: str, device_type: str, 
                 protocol: str = "MQTT", status: str = "registered"):
        self.device_id = device_id
        self.name = name
        self.device_type = device_type
        self.protocol = protocol
        self.status = status
        self.registered_at = datetime.now().isoformat()
        self.last_seen = None
        self.telemetry_data = []
        self.commands = []
        self.security_token = self._generate_token()
    
    def _generate_token(self) -> str:
        """Generate a security token for the device"""
        token_data = f"{self.device_id}{self.registered_at}{uuid.uuid4()}"
        return hashlib.sha256(token_data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert device to dictionary"""
        return {
            "device_id": self.device_id,
            "name": self.name,
            "device_type": self.device_type,
            "protocol": self.protocol,
            "status": self.status,
            "registered_at": self.registered_at,
            "last_seen": self.last_seen,
            "security_token": self.security_token
        }


class IoTService:
    """Service for managing IoT devices"""
    
    def __init__(self, storage_path: str = "storage/iot"):
        """
        Initialize IoT service
        
        Args:
            storage_path (str): Path to store IoT device data
        """
        self.storage_path = storage_path
        self.devices_file = os.path.join(storage_path, "devices.json")
        self.telemetry_file = os.path.join(storage_path, "telemetry.json")
        self.commands_file = os.path.join(storage_path, "commands.json")
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        
        # Initialize files if they don't exist
        for file_path in [self.devices_file, self.telemetry_file, self.commands_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({"data": []}, f)
    
    def register_device(self, name: str, device_type: str, 
                       protocol: str = "MQTT") -> str:
        """
        Register a new IoT device
        
        Args:
            name (str): Device name
            device_type (str): Device type (sensor, actuator, gateway, etc.)
            protocol (str): Communication protocol (MQTT, HTTP, CoAP, etc.)
            
        Returns:
            str: Device ID
        """
        device_id = str(uuid.uuid4())
        device = IoTDevice(device_id, name, device_type, protocol)
        
        # Load existing devices
        with open(self.devices_file, 'r') as f:
            data = json.load(f)
        
        # Add new device
        data["data"].append(device.to_dict())
        
        # Save updated devices
        with open(self.devices_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return device_id
    
    def get_device(self, device_id: str) -> Dict[str, Any]:
        """
        Get device by ID
        
        Args:
            device_id (str): Device ID
            
        Returns:
            dict: Device data
        """
        with open(self.devices_file, 'r') as f:
            data = json.load(f)
        
        for device in data["data"]:
            if device["device_id"] == device_id:
                return device
        
        raise ValueError(f"Device with ID {device_id} not found")
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """
        List all devices
        
        Returns:
            list: List of all devices
        """
        with open(self.devices_file, 'r') as f:
            data = json.load(f)
        
        return data["data"]
    
    def update_device_status(self, device_id: str, status: str) -> bool:
        """
        Update device status
        
        Args:
            device_id (str): Device ID
            status (str): New status
            
        Returns:
            bool: True if updated successfully
        """
        with open(self.devices_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for device in data["data"]:
            if device["device_id"] == device_id:
                device["status"] = status
                device["last_seen"] = datetime.now().isoformat()
                updated = True
                break
        
        if updated:
            with open(self.devices_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def send_command(self, device_id: str, command: str, 
                    parameters: Dict[str, Any] = None) -> str:
        """
        Send command to device
        
        Args:
            device_id (str): Device ID
            command (str): Command to send
            parameters (dict): Command parameters
            
        Returns:
            str: Command ID
        """
        command_id = str(uuid.uuid4())
        command_record = {
            "command_id": command_id,
            "device_id": device_id,
            "command": command,
            "parameters": parameters or {},
            "timestamp": datetime.now().isoformat(),
            "status": "sent"
        }
        
        # Load existing commands
        with open(self.commands_file, 'r') as f:
            data = json.load(f)
        
        # Add new command
        data["data"].append(command_record)
        
        # Save updated commands
        with open(self.commands_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return command_id
    
    def record_telemetry(self, device_id: str, data: Dict[str, Any]) -> bool:
        """
        Record telemetry data from device
        
        Args:
            device_id (str): Device ID
            data (dict): Telemetry data
            
        Returns:
            bool: True if recorded successfully
        """
        telemetry_record = {
            "device_id": device_id,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Load existing telemetry
        with open(self.telemetry_file, 'r') as f:
            telemetry_data = json.load(f)
        
        # Add new telemetry record
        telemetry_data["data"].append(telemetry_record)
        
        # Save updated telemetry
        with open(self.telemetry_file, 'w') as f:
            json.dump(telemetry_data, f, indent=2)
        
        # Update device last seen
        self.update_device_status(device_id, "active")
        
        return True
    
    def get_telemetry(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get telemetry data for device
        
        Args:
            device_id (str): Device ID
            limit (int): Maximum number of records to return
            
        Returns:
            list: Telemetry data
        """
        with open(self.telemetry_file, 'r') as f:
            data = json.load(f)
        
        # Filter telemetry for this device
        device_telemetry = [t for t in data["data"] if t["device_id"] == device_id]
        
        # Return most recent records up to limit
        return device_telemetry[-limit:] if len(device_telemetry) > limit else device_telemetry
    
    def delete_device(self, device_id: str) -> bool:
        """
        Delete device
        
        Args:
            device_id (str): Device ID
            
        Returns:
            bool: True if deleted successfully
        """
        with open(self.devices_file, 'r') as f:
            data = json.load(f)
        
        original_count = len(data["data"])
        data["data"] = [
            d for d in data["data"] if d["device_id"] != device_id
        ]
        
        if len(data["data"]) < original_count:
            with open(self.devices_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False


# Global instance
iot_service = IoTService()