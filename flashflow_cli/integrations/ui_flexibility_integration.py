"""
UI Flexibility Integration for FlashFlow
Provides Flask endpoints for UI flexibility features
"""

from flask import Blueprint, jsonify, request
from ..services.ui_flexibility_service import ui_flexibility_service


def register_ui_flexibility_routes(app):
    """Register UI flexibility routes with the Flask app"""
    
    ui_bp = Blueprint('ui_flexibility', __name__)
    
    @ui_bp.route('/api/ui/themes', methods=['GET'])
    def get_themes():
        """Get available themes"""
        themes = {
            "light": "Light Theme",
            "dark": "Dark Theme"
        }
        return jsonify(themes)
    
    @ui_bp.route('/api/ui/themes/<theme_name>', methods=['GET'])
    def get_theme_details(theme_name):
        """Get details for a specific theme"""
        # In a real implementation, this would return theme details
        theme_details = {
            "name": theme_name,
            "description": f"{theme_name.capitalize()} theme for FlashFlow applications"
        }
        return jsonify(theme_details)
    
    @ui_bp.route('/api/ui/components', methods=['POST'])
    def generate_component():
        """Generate a flexible UI component"""
        data = request.get_json()
        
        component_type = data.get('type')
        props = data.get('props', {})
        
        if not component_type:
            return jsonify({"error": "Component type is required"}), 400
        
        try:
            html = ui_flexibility_service.generate_flexible_component(component_type, props)
            return jsonify({"html": html})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @ui_bp.route('/api/ui/tokens', methods=['GET'])
    def get_tokens():
        """Get available design tokens"""
        # This would return available design tokens
        tokens = {
            "colors": ["primary", "secondary", "success", "warning", "danger"],
            "spacing": ["xs", "sm", "md", "lg", "xl"],
            "typography": ["fontFamily", "fontSize", "fontWeight"]
        }
        return jsonify(tokens)
    
    @ui_bp.route('/api/ui/tokens/<token_path>', methods=['GET'])
    def get_token_value(token_path):
        """Get value of a specific design token"""
        value = ui_flexibility_service.get_design_token(token_path)
        if value is None:
            return jsonify({"error": f"Token '{token_path}' not found"}), 404
        return jsonify({"value": value})
    
    # Register the blueprint with the app
    app.register_blueprint(ui_bp, url_prefix='/api/ui')


# For backward compatibility
register_routes = register_ui_flexibility_routes