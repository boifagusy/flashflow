"""
POS Integration for FlashFlow Laravel Frontend
Provides API endpoints and integration points for Point-of-Sale systems
"""

import json
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from ..services.pos_service import pos_service

def register_pos_routes(app: Flask):
    """
    Register POS API routes with Flask app
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.route('/api/v1/pos/terminals', methods=['GET'])
    def list_terminals():
        """List all POS terminals"""
        try:
            terminals = pos_service.list_terminals()
            return jsonify({
                "success": True,
                "data": terminals
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/pos/terminals', methods=['POST'])
    def register_terminal():
        """Register a new POS terminal"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'terminal_type']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Register terminal
            terminal_id = pos_service.register_terminal(
                name=data['name'],
                terminal_type=data['terminal_type'],
                location=data.get('location', 'default')
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "terminal_id": terminal_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/pos/terminals/<terminal_id>', methods=['GET'])
    def get_terminal(terminal_id):
        """Get a specific POS terminal"""
        try:
            terminal = pos_service.get_terminal(terminal_id)
            return jsonify({
                "success": True,
                "data": terminal
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
    
    @app.route('/api/v1/pos/terminals/<terminal_id>/status', methods=['PUT'])
    def update_terminal_status(terminal_id):
        """Update terminal status"""
        try:
            data = request.get_json()
            
            if 'status' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing required field: status"
                }), 400
            
            success = pos_service.update_terminal_status(terminal_id, data['status'])
            if success:
                return jsonify({
                    "success": True,
                    "message": "Terminal status updated successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to update terminal status"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/pos/inventory', methods=['POST'])
    def add_inventory_item():
        """Add an inventory item"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['sku', 'name', 'price']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            success = pos_service.add_inventory_item(
                sku=data['sku'],
                name=data['name'],
                price=float(data['price']),
                category=data.get('category', 'general'),
                stock_quantity=int(data.get('stock_quantity', 0))
            )
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Inventory item added successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to add inventory item"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/pos/inventory/<sku>', methods=['GET'])
    def get_inventory_item(sku):
        """Get inventory item by SKU"""
        try:
            item = pos_service.get_inventory_item(sku)
            return jsonify({
                "success": True,
                "data": item
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
    
    @app.route('/api/v1/pos/inventory', methods=['GET'])
    def list_inventory():
        """List all inventory items"""
        try:
            items = pos_service.list_inventory()
            return jsonify({
                "success": True,
                "data": items
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/pos/inventory/<sku>/stock', methods=['PUT'])
    def update_stock(sku):
        """Update stock quantity for an item"""
        try:
            data = request.get_json()
            
            if 'quantity_change' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing required field: quantity_change"
                }), 400
            
            success = pos_service.update_stock(sku, int(data['quantity_change']))
            if success:
                return jsonify({
                    "success": True,
                    "message": "Stock updated successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to update stock"
                }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/pos/transactions', methods=['POST'])
    def process_transaction():
        """Process a transaction"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['terminal_id', 'items', 'payment_method', 'total_amount']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }), 400
            
            transaction_id = pos_service.process_transaction(
                terminal_id=data['terminal_id'],
                items=data['items'],
                payment_method=data['payment_method'],
                total_amount=float(data['total_amount'])
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "transaction_id": transaction_id
                }
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/pos/transactions/<transaction_id>', methods=['GET'])
    def get_transaction(transaction_id):
        """Get transaction by ID"""
        try:
            transaction = pos_service.get_transaction(transaction_id)
            return jsonify({
                "success": True,
                "data": transaction
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
    
    @app.route('/api/v1/pos/transactions', methods=['GET'])
    def list_transactions():
        """List recent transactions"""
        try:
            limit = int(request.args.get('limit', 100))
            transactions = pos_service.list_transactions(limit)
            
            return jsonify({
                "success": True,
                "data": transactions
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/pos/transactions/<transaction_id>/receipt', methods=['GET'])
    def generate_receipt(transaction_id):
        """Generate receipt for transaction"""
        try:
            format = request.args.get('format', 'text')
            receipt = pos_service.generate_receipt(transaction_id, format)
            
            return jsonify({
                "success": True,
                "data": {
                    "receipt": receipt
                }
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/pos/barcode/<barcode>', methods=['GET'])
    def scan_barcode(barcode):
        """Scan barcode and return item info"""
        try:
            item = pos_service.scan_barcode(barcode)
            
            return jsonify({
                "success": True,
                "data": item
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/v1/pos/terminals/<terminal_id>', methods=['DELETE'])
    def delete_terminal(terminal_id):
        """Delete a POS terminal"""
        try:
            success = pos_service.delete_terminal(terminal_id)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Terminal deleted successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Terminal not found"
                }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500


def get_pos_dashboard_data() -> Dict[str, Any]:
    """
    Get data for POS dashboard
    
    Returns:
        dict: Dashboard data including sales statistics
    """
    try:
        terminals = pos_service.list_terminals()
        transactions = pos_service.list_transactions(1000)  # Get last 1000 transactions
        inventory = pos_service.list_inventory()
        
        # Calculate statistics
        total_terminals = len(terminals)
        active_terminals = len([t for t in terminals if t["status"] == "active"])
        
        # Calculate sales statistics
        total_sales = sum(t["total_amount"] for t in transactions)
        total_transactions = len(transactions)
        avg_transaction_value = total_sales / total_transactions if total_transactions > 0 else 0
        
        # Inventory statistics
        total_inventory_items = len(inventory)
        low_stock_items = len([i for i in inventory if i["stock_quantity"] < 10])
        
        # Payment method distribution
        payment_methods = {}
        for transaction in transactions:
            method = transaction.get("payment_method", "unknown")
            payment_methods[method] = payment_methods.get(method, 0) + 1
        
        return {
            "total_terminals": total_terminals,
            "active_terminals": active_terminals,
            "total_sales": round(total_sales, 2),
            "total_transactions": total_transactions,
            "avg_transaction_value": round(avg_transaction_value, 2),
            "total_inventory_items": total_inventory_items,
            "low_stock_items": low_stock_items,
            "payment_methods": payment_methods
        }
    except Exception as e:
        return {
            "error": str(e)
        }