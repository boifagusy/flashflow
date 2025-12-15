"""
Default UI Service for FlashFlow
Generates default UI components and pages when none are explicitly defined
"""

from typing import Dict, Any, List
from ..core import FlashFlowIR


class DefaultUIService:
    """Service for generating default UI components and pages"""
    
    def __init__(self):
        pass
    
    def generate_default_pages(self, ir: FlashFlowIR):
        """Generate default CRUD pages for models that don't have explicit page definitions"""
        # For each model, check if there are explicit pages defined for it
        for model_name, model_def in ir.models.items():
            # Check if any pages already reference this model
            model_has_pages = False
            for page_path, page_def in ir.pages.items():
                # Check if page has components that reference this model
                if 'body' in page_def:
                    for component in page_def['body']:
                        if isinstance(component, dict):
                            # Check list components
                            if component.get('component') == 'list' and component.get('data_source') == model_name:
                                model_has_pages = True
                                break
                            # Check form components
                            if component.get('component') == 'form' and component.get('data_source') == model_name:
                                model_has_pages = True
                                break
                            # Check card components
                            if component.get('component') == 'card' and component.get('data_source') == model_name:
                                model_has_pages = True
                                break
                
                # Also check if page has direct model reference
                if page_def.get('model') == model_name:
                    model_has_pages = True
                    break
            
            # If no explicit pages found for this model, generate default CRUD pages
            if not model_has_pages:
                self._generate_crud_pages_for_model(ir, model_name, model_def)
    
    def _generate_crud_pages_for_model(self, ir: FlashFlowIR, model_name: str, model_def: Dict[str, Any]):
        """Generate default CRUD pages for a model"""
        model_slug = model_name.lower()
        
        # Generate list page
        list_page_path = f"/{model_slug}s"
        list_page = {
            'title': f"{model_name} List",
            'path': list_page_path,
            'layout': 'main',
            'body': [
                {
                    'component': 'list',
                    'data_source': model_name,
                    'fields': self._get_default_list_fields(model_def),
                    'actions': ['create', 'edit', 'delete']
                }
            ]
        }
        ir.add_page(list_page_path, list_page)
        
        # Generate create form page
        create_page_path = f"/{model_slug}s/create"
        create_page = {
            'title': f"Create {model_name}",
            'path': create_page_path,
            'layout': 'main',
            'body': [
                {
                    'component': 'form',
                    'data_source': model_name,
                    'fields': self._get_default_form_fields(model_def),
                    'submit_text': f"Create {model_name}",
                    'cancel_action': 'back'
                }
            ]
        }
        ir.add_page(create_page_path, create_page)
        
        # Generate edit form page
        edit_page_path = f"/{model_slug}s/{{id}}/edit"
        edit_page = {
            'title': f"Edit {model_name}",
            'path': edit_page_path,
            'layout': 'main',
            'body': [
                {
                    'component': 'form',
                    'data_source': model_name,
                    'fields': self._get_default_form_fields(model_def),
                    'submit_text': f"Update {model_name}",
                    'cancel_action': 'back'
                }
            ]
        }
        ir.add_page(edit_page_path, edit_page)
        
        # Generate view/detail page
        view_page_path = f"/{model_slug}s/{{id}}"
        view_page = {
            'title': f"View {model_name}",
            'path': view_page_path,
            'layout': 'main',
            'body': [
                {
                    'component': 'card',
                    'data_source': model_name,
                    'fields': self._get_default_view_fields(model_def),
                    'actions': ['edit', 'delete']
                }
            ]
        }
        ir.add_page(view_page_path, view_page)
    
    def _get_default_list_fields(self, model_def: Dict[str, Any]) -> List[str]:
        """Get default fields to display in list views"""
        fields = []
        model_fields = model_def.get('fields', {})
        
        # Always include ID if present
        if 'id' in model_fields:
            fields.append('id')
        
        # Include the first few fields (up to 5) that are not ID
        field_count = 0
        for field_name, field_def in model_fields.items():
            if field_name != 'id' and field_count < 5:
                fields.append(field_name)
                field_count += 1
        
        # If we don't have enough fields, include ID if not already included
        if len(fields) < 2 and 'id' not in fields:
            fields.append('id')
            
        return fields
    
    def _get_default_form_fields(self, model_def: Dict[str, Any]) -> List[str]:
        """Get default fields to include in forms"""
        fields = []
        model_fields = model_def.get('fields', {})
        
        # Include all fields except ID (which is typically auto-generated)
        for field_name, field_def in model_fields.items():
            if field_name != 'id':
                fields.append(field_name)
                
        return fields
    
    def _get_default_view_fields(self, model_def: Dict[str, Any]) -> List[str]:
        """Get default fields to display in view/detail pages"""
        fields = []
        model_fields = model_def.get('fields', {})
        
        # Include all fields
        for field_name, field_def in model_fields.items():
            fields.append(field_name)
            
        return fields


# Global instance
default_ui_service = DefaultUIService()