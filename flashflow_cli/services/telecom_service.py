"""
Telecommunications Service for FlashFlow
Provides telecommunications equipment integration and 5G infrastructure support
"""

import json
import os
from typing import Dict, Any, List
import uuid
from datetime import datetime
import hashlib


class TelecomService:
    """Service for managing telecommunications equipment and infrastructure"""
    
    def __init__(self, storage_path: str = "storage/telecom"):
        """
        Initialize Telecom service
        
        Args:
            storage_path (str): Path to store telecom data
        """
        self.storage_path = storage_path
        self.equipment_file = os.path.join(storage_path, "equipment.json")
        self.networks_file = os.path.join(storage_path, "networks.json")
        self.connections_file = os.path.join(storage_path, "connections.json")
        self.signals_file = os.path.join(storage_path, "signals.json")
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        
        # Initialize files if they don't exist
        for file_path in [self.equipment_file, self.networks_file, 
                         self.connections_file, self.signals_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({"data": []}, f)
    
    def register_equipment(self, name: str, equipment_type: str, 
                          vendor: str, model: str) -> str:
        """
        Register new telecommunications equipment
        
        Args:
            name (str): Equipment name
            equipment_type (str): Equipment type (base_station, router, switch, etc.)
            vendor (str): Equipment vendor
            model (str): Equipment model
            
        Returns:
            str: Equipment ID
        """
        equipment_id = str(uuid.uuid4())
        equipment = {
            "equipment_id": equipment_id,
            "name": name,
            "equipment_type": equipment_type,
            "vendor": vendor,
            "model": model,
            "status": "registered",
            "registered_at": datetime.now().isoformat(),
            "last_seen": None,
            "ip_address": None,
            "firmware_version": None,
            "supported_protocols": []
        }
        
        # Load existing equipment
        with open(self.equipment_file, 'r') as f:
            data = json.load(f)
        
        # Add new equipment
        data["data"].append(equipment)
        
        # Save updated equipment
        with open(self.equipment_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return equipment_id
    
    def get_equipment(self, equipment_id: str) -> Dict[str, Any]:
        """
        Get equipment by ID
        
        Args:
            equipment_id (str): Equipment ID
            
        Returns:
            dict: Equipment data
        """
        with open(self.equipment_file, 'r') as f:
            data = json.load(f)
        
        for equipment in data["data"]:
            if equipment["equipment_id"] == equipment_id:
                return equipment
        
        raise ValueError(f"Equipment with ID {equipment_id} not found")
    
    def list_equipment(self) -> List[Dict[str, Any]]:
        """
        List all equipment
        
        Returns:
            list: List of all equipment
        """
        with open(self.equipment_file, 'r') as f:
            data = json.load(f)
        
        return data["data"]
    
    def update_equipment_status(self, equipment_id: str, status: str,
                               ip_address: str = None) -> bool:
        """
        Update equipment status
        
        Args:
            equipment_id (str): Equipment ID
            status (str): New status
            ip_address (str): Equipment IP address
            
        Returns:
            bool: True if updated successfully
        """
        with open(self.equipment_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for equipment in data["data"]:
            if equipment["equipment_id"] == equipment_id:
                equipment["status"] = status
                equipment["last_seen"] = datetime.now().isoformat()
                if ip_address:
                    equipment["ip_address"] = ip_address
                updated = True
                break
        
        if updated:
            with open(self.equipment_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def create_network(self, name: str, network_type: str,
                      frequency_band: str = "2.4GHz") -> str:
        """
        Create a new network
        
        Args:
            name (str): Network name
            network_type (str): Network type (5G, 4G, WiFi, etc.)
            frequency_band (str): Frequency band
            
        Returns:
            str: Network ID
        """
        network_id = str(uuid.uuid4())
        network = {
            "network_id": network_id,
            "name": name,
            "network_type": network_type,
            "frequency_band": frequency_band,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "equipment": [],
            "coverage_area": None,
            "capacity": 0
        }
        
        # Load existing networks
        with open(self.networks_file, 'r') as f:
            data = json.load(f)
        
        # Add new network
        data["data"].append(network)
        
        # Save updated networks
        with open(self.networks_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return network_id
    
    def get_network(self, network_id: str) -> Dict[str, Any]:
        """
        Get network by ID
        
        Args:
            network_id (str): Network ID
            
        Returns:
            dict: Network data
        """
        with open(self.networks_file, 'r') as f:
            data = json.load(f)
        
        for network in data["data"]:
            if network["network_id"] == network_id:
                return network
        
        raise ValueError(f"Network with ID {network_id} not found")
    
    def add_equipment_to_network(self, network_id: str, equipment_id: str) -> bool:
        """
        Add equipment to network
        
        Args:
            network_id (str): Network ID
            equipment_id (str): Equipment ID
            
        Returns:
            bool: True if added successfully
        """
        with open(self.networks_file, 'r') as f:
            networks_data = json.load(f)
        
        with open(self.equipment_file, 'r') as f:
            equipment_data = json.load(f)
        
        network_updated = False
        equipment_updated = False
        
        # Add equipment to network
        for network in networks_data["data"]:
            if network["network_id"] == network_id:
                if equipment_id not in network["equipment"]:
                    network["equipment"].append(equipment_id)
                    network["capacity"] += 1
                    network_updated = True
                break
        
        # Update equipment network reference
        for equipment in equipment_data["data"]:
            if equipment["equipment_id"] == equipment_id:
                if "networks" not in equipment:
                    equipment["networks"] = []
                if network_id not in equipment["networks"]:
                    equipment["networks"].append(network_id)
                    equipment_updated = True
                break
        
        if network_updated:
            with open(self.networks_file, 'w') as f:
                json.dump(networks_data, f, indent=2)
        
        if equipment_updated:
            with open(self.equipment_file, 'w') as f:
                json.dump(equipment_data, f, indent=2)
        
        return network_updated or equipment_updated
    
    def establish_connection(self, source_id: str, destination_id: str,
                           connection_type: str = "data") -> str:
        """
        Establish a connection between two entities
        
        Args:
            source_id (str): Source equipment/network ID
            destination_id (str): Destination equipment/network ID
            connection_type (str): Connection type (data, voice, video)
            
        Returns:
            str: Connection ID
        """
        connection_id = str(uuid.uuid4())
        connection = {
            "connection_id": connection_id,
            "source_id": source_id,
            "destination_id": destination_id,
            "connection_type": connection_type,
            "status": "established",
            "established_at": datetime.now().isoformat(),
            "bandwidth": 0,
            "latency": 0,
            "packet_loss": 0
        }
        
        # Load existing connections
        with open(self.connections_file, 'r') as f:
            data = json.load(f)
        
        # Add new connection
        data["data"].append(connection)
        
        # Save updated connections
        with open(self.connections_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return connection_id
    
    def monitor_signal(self, equipment_id: str, signal_strength: float,
                      signal_quality: float) -> bool:
        """
        Monitor signal from equipment
        
        Args:
            equipment_id (str): Equipment ID
            signal_strength (float): Signal strength in dBm
            signal_quality (float): Signal quality percentage
            
        Returns:
            bool: True if recorded successfully
        """
        signal_record = {
            "equipment_id": equipment_id,
            "signal_strength": signal_strength,
            "signal_quality": signal_quality,
            "timestamp": datetime.now().isoformat()
        }
        
        # Load existing signals
        with open(self.signals_file, 'r') as f:
            data = json.load(f)
        
        # Add new signal record
        data["data"].append(signal_record)
        
        # Save updated signals
        with open(self.signals_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update equipment last seen
        self.update_equipment_status(equipment_id, "active")
        
        return True
    
    def get_signal_history(self, equipment_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get signal history for equipment
        
        Args:
            equipment_id (str): Equipment ID
            limit (int): Maximum number of records to return
            
        Returns:
            list: Signal history
        """
        with open(self.signals_file, 'r') as f:
            data = json.load(f)
        
        # Filter signals for this equipment
        equipment_signals = [s for s in data["data"] if s["equipment_id"] == equipment_id]
        
        # Return most recent records up to limit
        return equipment_signals[-limit:] if len(equipment_signals) > limit else equipment_signals
    
    def get_network_topology(self, network_id: str) -> Dict[str, Any]:
        """
        Get network topology information
        
        Args:
            network_id (str): Network ID
            
        Returns:
            dict: Network topology data
        """
        network = self.get_network(network_id)
        
        # Get equipment details
        equipment_details = []
        for equipment_id in network["equipment"]:
            try:
                equipment = self.get_equipment(equipment_id)
                equipment_details.append(equipment)
            except ValueError:
                # Equipment not found, skip
                pass
        
        return {
            "network": network,
            "equipment": equipment_details,
            "connections": self._get_network_connections(network_id)
        }
    
    def _get_network_connections(self, network_id: str) -> List[Dict[str, Any]]:
        """
        Get connections for a network
        
        Args:
            network_id (str): Network ID
            
        Returns:
            list: Network connections
        """
        with open(self.connections_file, 'r') as f:
            data = json.load(f)
        
        # Filter connections for this network
        network_connections = []
        for connection in data["data"]:
            if connection["source_id"] == network_id or connection["destination_id"] == network_id:
                network_connections.append(connection)
        
        return network_connections
    
    def list_networks(self) -> List[Dict[str, Any]]:
        """
        List all networks
        
        Returns:
            list: List of all networks
        """
        with open(self.networks_file, 'r') as f:
            data = json.load(f)
        
        return data["data"]
    
    def delete_equipment(self, equipment_id: str) -> bool:
        """
        Delete equipment
        
        Args:
            equipment_id (str): Equipment ID
            
        Returns:
            bool: True if deleted successfully
        """
        with open(self.equipment_file, 'r') as f:
            data = json.load(f)
        
        original_count = len(data["data"])
        data["data"] = [
            d for d in data["data"] if d["equipment_id"] != equipment_id
        ]
        
        if len(data["data"]) < original_count:
            with open(self.equipment_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False


# Global instance
telecom_service = TelecomService()