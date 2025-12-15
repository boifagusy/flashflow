"""
Industrial Control Systems Service for FlashFlow
Provides industrial protocol support and SCADA integration capabilities
"""

import json
import os
from typing import Dict, Any, List
import uuid
from datetime import datetime
import struct


class IndustrialDevice:
    """Represents an industrial device"""
    
    def __init__(self, device_id: str, name: str, protocol: str, 
                 ip_address: str, port: int):
        self.device_id = device_id
        self.name = name
        self.protocol = protocol  # Modbus, OPC UA, etc.
        self.ip_address = ip_address
        self.port = port
        self.status = "registered"
        self.registered_at = datetime.now().isoformat()
        self.last_connected = None
        self.tags = []  # Data points/tags in the device
        self.security_config = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert device to dictionary"""
        return {
            "device_id": self.device_id,
            "name": self.name,
            "protocol": self.protocol,
            "ip_address": self.ip_address,
            "port": self.port,
            "status": self.status,
            "registered_at": self.registered_at,
            "last_connected": self.last_connected,
            "tags": self.tags,
            "security_config": self.security_config
        }


class IndustrialService:
    """Service for managing industrial control systems"""
    
    def __init__(self, storage_path: str = "storage/industrial"):
        """
        Initialize Industrial service
        
        Args:
            storage_path (str): Path to store industrial device data
        """
        self.storage_path = storage_path
        self.devices_file = os.path.join(storage_path, "devices.json")
        self.data_file = os.path.join(storage_path, "data.json")
        self.alarms_file = os.path.join(storage_path, "alarms.json")
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        
        # Initialize files if they don't exist
        for file_path in [self.devices_file, self.data_file, self.alarms_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({"data": []}, f)
    
    def register_device(self, name: str, protocol: str, 
                       ip_address: str, port: int) -> str:
        """
        Register a new industrial device
        
        Args:
            name (str): Device name
            protocol (str): Communication protocol (Modbus, OPC UA, etc.)
            ip_address (str): Device IP address
            port (int): Device port
            
        Returns:
            str: Device ID
        """
        device_id = str(uuid.uuid4())
        device = IndustrialDevice(device_id, name, protocol, ip_address, port)
        
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
    
    def add_tag(self, device_id: str, tag_name: str, 
                tag_address: str, data_type: str) -> bool:
        """
        Add a tag to device
        
        Args:
            device_id (str): Device ID
            tag_name (str): Tag name
            tag_address (str): Tag address in device
            data_type (str): Data type (bool, int, float, etc.)
            
        Returns:
            bool: True if added successfully
        """
        with open(self.devices_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for device in data["data"]:
            if device["device_id"] == device_id:
                tag = {
                    "name": tag_name,
                    "address": tag_address,
                    "data_type": data_type,
                    "created_at": datetime.now().isoformat()
                }
                device["tags"].append(tag)
                updated = True
                break
        
        if updated:
            with open(self.devices_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def read_tag(self, device_id: str, tag_name: str) -> Any:
        """
        Read tag value from device (simulated)
        
        Args:
            device_id (str): Device ID
            tag_name (str): Tag name
            
        Returns:
            Any: Tag value
        """
        # In a real implementation, this would communicate with the actual device
        # For now, we'll simulate a value
        import random
        random.seed(hash(f"{device_id}{tag_name}"))
        
        # Get tag info
        device = self.get_device(device_id)
        tag = next((t for t in device["tags"] if t["name"] == tag_name), None)
        
        if not tag:
            raise ValueError(f"Tag {tag_name} not found in device {device_id}")
        
        # Simulate value based on data type
        data_type = tag["data_type"]
        if data_type == "bool":
            return random.choice([True, False])
        elif data_type == "int":
            return random.randint(0, 1000)
        elif data_type == "float":
            return round(random.uniform(0, 100), 2)
        else:
            return f"simulated_value_{random.randint(1, 1000)}"
    
    def write_tag(self, device_id: str, tag_name: str, value: Any) -> bool:
        """
        Write tag value to device (simulated)
        
        Args:
            device_id (str): Device ID
            tag_name (str): Tag name
            value (Any): Value to write
            
        Returns:
            bool: True if written successfully
        """
        # In a real implementation, this would communicate with the actual device
        # For now, we'll just log the write operation
        
        write_record = {
            "device_id": device_id,
            "tag_name": tag_name,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        
        # Load existing data
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        # Add write record
        data["data"].append(write_record)
        
        # Save updated data
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    
    def record_data(self, device_id: str, tag_name: str, value: Any) -> bool:
        """
        Record data point
        
        Args:
            device_id (str): Device ID
            tag_name (str): Tag name
            value (Any): Value to record
            
        Returns:
            bool: True if recorded successfully
        """
        data_record = {
            "device_id": device_id,
            "tag_name": tag_name,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        
        # Load existing data
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        # Add data record
        data["data"].append(data_record)
        
        # Save updated data
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update device last connected
        self._update_device_connection(device_id)
        
        return True
    
    def _update_device_connection(self, device_id: str) -> bool:
        """
        Update device connection timestamp
        
        Args:
            device_id (str): Device ID
            
        Returns:
            bool: True if updated successfully
        """
        with open(self.devices_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for device in data["data"]:
            if device["device_id"] == device_id:
                device["last_connected"] = datetime.now().isoformat()
                device["status"] = "connected"
                updated = True
                break
        
        if updated:
            with open(self.devices_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def create_alarm(self, device_id: str, tag_name: str, 
                     condition: str, severity: str, message: str) -> str:
        """
        Create an alarm
        
        Args:
            device_id (str): Device ID
            tag_name (str): Tag name
            condition (str): Alarm condition
            severity (str): Alarm severity (info, warning, critical)
            message (str): Alarm message
            
        Returns:
            str: Alarm ID
        """
        alarm_id = str(uuid.uuid4())
        alarm = {
            "alarm_id": alarm_id,
            "device_id": device_id,
            "tag_name": tag_name,
            "condition": condition,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Load existing alarms
        with open(self.alarms_file, 'r') as f:
            data = json.load(f)
        
        # Add new alarm
        data["data"].append(alarm)
        
        # Save updated alarms
        with open(self.alarms_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return alarm_id
    
    def acknowledge_alarm(self, alarm_id: str) -> bool:
        """
        Acknowledge an alarm
        
        Args:
            alarm_id (str): Alarm ID
            
        Returns:
            bool: True if acknowledged successfully
        """
        with open(self.alarms_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for alarm in data["data"]:
            if alarm["alarm_id"] == alarm_id:
                alarm["status"] = "acknowledged"
                alarm["acknowledged_at"] = datetime.now().isoformat()
                updated = True
                break
        
        if updated:
            with open(self.alarms_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def get_active_alarms(self) -> List[Dict[str, Any]]:
        """
        Get all active alarms
        
        Returns:
            list: Active alarms
        """
        with open(self.alarms_file, 'r') as f:
            data = json.load(f)
        
        return [alarm for alarm in data["data"] if alarm["status"] == "active"]
    
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
industrial_service = IndustrialService()