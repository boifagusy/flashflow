"""
Point-of-Sale (POS) Integration Service for FlashFlow
Provides POS system integration and retail hardware connectivity
"""

import json
import os
from typing import Dict, Any, List
import uuid
from datetime import datetime
import hashlib


class POSService:
    """Service for managing POS systems and retail hardware"""
    
    def __init__(self, storage_path: str = "storage/pos"):
        """
        Initialize POS service
        
        Args:
            storage_path (str): Path to store POS data
        """
        self.storage_path = storage_path
        self.terminals_file = os.path.join(storage_path, "terminals.json")
        self.transactions_file = os.path.join(storage_path, "transactions.json")
        self.inventory_file = os.path.join(storage_path, "inventory.json")
        self.receipts_file = os.path.join(storage_path, "receipts.json")
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        
        # Initialize files if they don't exist
        for file_path in [self.terminals_file, self.transactions_file, 
                         self.inventory_file, self.receipts_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({"data": []}, f)
    
    def register_terminal(self, name: str, terminal_type: str, 
                         location: str = "default") -> str:
        """
        Register a new POS terminal
        
        Args:
            name (str): Terminal name
            terminal_type (str): Terminal type (cash_register, tablet, etc.)
            location (str): Terminal location
            
        Returns:
            str: Terminal ID
        """
        terminal_id = str(uuid.uuid4())
        terminal = {
            "terminal_id": terminal_id,
            "name": name,
            "terminal_type": terminal_type,
            "location": location,
            "status": "registered",
            "registered_at": datetime.now().isoformat(),
            "last_active": None,
            "supported_features": []
        }
        
        # Load existing terminals
        with open(self.terminals_file, 'r') as f:
            data = json.load(f)
        
        # Add new terminal
        data["data"].append(terminal)
        
        # Save updated terminals
        with open(self.terminals_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return terminal_id
    
    def get_terminal(self, terminal_id: str) -> Dict[str, Any]:
        """
        Get terminal by ID
        
        Args:
            terminal_id (str): Terminal ID
            
        Returns:
            dict: Terminal data
        """
        with open(self.terminals_file, 'r') as f:
            data = json.load(f)
        
        for terminal in data["data"]:
            if terminal["terminal_id"] == terminal_id:
                return terminal
        
        raise ValueError(f"Terminal with ID {terminal_id} not found")
    
    def list_terminals(self) -> List[Dict[str, Any]]:
        """
        List all terminals
        
        Returns:
            list: List of all terminals
        """
        with open(self.terminals_file, 'r') as f:
            data = json.load(f)
        
        return data["data"]
    
    def update_terminal_status(self, terminal_id: str, status: str) -> bool:
        """
        Update terminal status
        
        Args:
            terminal_id (str): Terminal ID
            status (str): New status
            
        Returns:
            bool: True if updated successfully
        """
        with open(self.terminals_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for terminal in data["data"]:
            if terminal["terminal_id"] == terminal_id:
                terminal["status"] = status
                terminal["last_active"] = datetime.now().isoformat()
                updated = True
                break
        
        if updated:
            with open(self.terminals_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def add_inventory_item(self, sku: str, name: str, price: float,
                          category: str = "general", stock_quantity: int = 0) -> bool:
        """
        Add an inventory item
        
        Args:
            sku (str): Stock Keeping Unit
            name (str): Item name
            price (float): Item price
            category (str): Item category
            stock_quantity (int): Current stock quantity
            
        Returns:
            bool: True if added successfully
        """
        item = {
            "sku": sku,
            "name": name,
            "price": price,
            "category": category,
            "stock_quantity": stock_quantity,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Load existing inventory
        with open(self.inventory_file, 'r') as f:
            data = json.load(f)
        
        # Check if item already exists
        for existing_item in data["data"]:
            if existing_item["sku"] == sku:
                # Update existing item
                existing_item.update(item)
                break
        else:
            # Add new item
            data["data"].append(item)
        
        # Save updated inventory
        with open(self.inventory_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    
    def get_inventory_item(self, sku: str) -> Dict[str, Any]:
        """
        Get inventory item by SKU
        
        Args:
            sku (str): Stock Keeping Unit
            
        Returns:
            dict: Item data
        """
        with open(self.inventory_file, 'r') as f:
            data = json.load(f)
        
        for item in data["data"]:
            if item["sku"] == sku:
                return item
        
        raise ValueError(f"Inventory item with SKU {sku} not found")
    
    def list_inventory(self) -> List[Dict[str, Any]]:
        """
        List all inventory items
        
        Returns:
            list: List of all inventory items
        """
        with open(self.inventory_file, 'r') as f:
            data = json.load(f)
        
        return data["data"]
    
    def update_stock(self, sku: str, quantity_change: int) -> bool:
        """
        Update stock quantity for an item
        
        Args:
            sku (str): Stock Keeping Unit
            quantity_change (int): Change in quantity (positive or negative)
            
        Returns:
            bool: True if updated successfully
        """
        with open(self.inventory_file, 'r') as f:
            data = json.load(f)
        
        updated = False
        for item in data["data"]:
            if item["sku"] == sku:
                item["stock_quantity"] += quantity_change
                item["updated_at"] = datetime.now().isoformat()
                updated = True
                break
        
        if updated:
            with open(self.inventory_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def process_transaction(self, terminal_id: str, items: List[Dict[str, Any]],
                           payment_method: str, total_amount: float) -> str:
        """
        Process a transaction
        
        Args:
            terminal_id (str): Terminal ID
            items (list): List of items in transaction
            payment_method (str): Payment method (cash, card, etc.)
            total_amount (float): Total transaction amount
            
        Returns:
            str: Transaction ID
        """
        transaction_id = str(uuid.uuid4())
        transaction = {
            "transaction_id": transaction_id,
            "terminal_id": terminal_id,
            "items": items,
            "payment_method": payment_method,
            "total_amount": total_amount,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Load existing transactions
        with open(self.transactions_file, 'r') as f:
            data = json.load(f)
        
        # Add new transaction
        data["data"].append(transaction)
        
        # Save updated transactions
        with open(self.transactions_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update terminal status
        self.update_terminal_status(terminal_id, "active")
        
        # Update inventory stock
        for item in items:
            self.update_stock(item["sku"], -item["quantity"])
        
        return transaction_id
    
    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get transaction by ID
        
        Args:
            transaction_id (str): Transaction ID
            
        Returns:
            dict: Transaction data
        """
        with open(self.transactions_file, 'r') as f:
            data = json.load(f)
        
        for transaction in data["data"]:
            if transaction["transaction_id"] == transaction_id:
                return transaction
        
        raise ValueError(f"Transaction with ID {transaction_id} not found")
    
    def list_transactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List recent transactions
        
        Args:
            limit (int): Maximum number of transactions to return
            
        Returns:
            list: List of recent transactions
        """
        with open(self.transactions_file, 'r') as f:
            data = json.load(f)
        
        # Return most recent transactions up to limit
        transactions = data["data"]
        return transactions[-limit:] if len(transactions) > limit else transactions
    
    def generate_receipt(self, transaction_id: str, format: str = "text") -> str:
        """
        Generate receipt for transaction
        
        Args:
            transaction_id (str): Transaction ID
            format (str): Receipt format (text, html, etc.)
            
        Returns:
            str: Receipt content
        """
        transaction = self.get_transaction(transaction_id)
        
        receipt_id = str(uuid.uuid4())
        receipt_data = {
            "receipt_id": receipt_id,
            "transaction_id": transaction_id,
            "generated_at": datetime.now().isoformat(),
            "format": format
        }
        
        # Load existing receipts
        with open(self.receipts_file, 'r') as f:
            data = json.load(f)
        
        # Add new receipt
        data["data"].append(receipt_data)
        
        # Save updated receipts
        with open(self.receipts_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Generate receipt content based on format
        if format == "text":
            receipt = f"Receipt ID: {receipt_id}\n"
            receipt += f"Transaction ID: {transaction_id}\n"
            receipt += f"Date: {transaction['timestamp']}\n"
            receipt += "=" * 30 + "\n"
            
            for item in transaction["items"]:
                receipt += f"{item['name']}\n"
                receipt += f"  {item['quantity']} x ${item['price']} = ${item['quantity'] * item['price']}\n"
            
            receipt += "=" * 30 + "\n"
            receipt += f"TOTAL: ${transaction['total_amount']}\n"
            receipt += f"Payment Method: {transaction['payment_method']}\n"
            receipt += "\nThank you for your purchase!"
            
            return receipt
        else:
            # For other formats, return a simple placeholder
            return f"Receipt for transaction {transaction_id} in {format} format"
    
    def scan_barcode(self, barcode: str) -> Dict[str, Any]:
        """
        Scan barcode and return item info (simulated)
        
        Args:
            barcode (str): Barcode to scan
            
        Returns:
            dict: Item information
        """
        # In a real implementation, this would interface with a barcode scanner
        # For now, we'll simulate by treating the barcode as an SKU
        try:
            return self.get_inventory_item(barcode)
        except ValueError:
            # If item not found, return a default item
            return {
                "sku": barcode,
                "name": f"Item {barcode}",
                "price": 0.0,
                "category": "unknown",
                "stock_quantity": 0
            }
    
    def delete_terminal(self, terminal_id: str) -> bool:
        """
        Delete terminal
        
        Args:
            terminal_id (str): Terminal ID
            
        Returns:
            bool: True if deleted successfully
        """
        with open(self.terminals_file, 'r') as f:
            data = json.load(f)
        
        original_count = len(data["data"])
        data["data"] = [
            d for d in data["data"] if d["terminal_id"] != terminal_id
        ]
        
        if len(data["data"]) < original_count:
            with open(self.terminals_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False


# Global instance
pos_service = POSService()