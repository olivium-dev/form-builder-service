import logging
from typing import Dict, List, Any, Optional
from fastapi import HTTPException

from app.config import load_config

logger = logging.getLogger(__name__)

# Define configuration file paths
COMPONENTS_CONFIG_FILE = "components_config.json"
TEMPLATES_FILE = "templates.json"

components_config = load_config(COMPONENTS_CONFIG_FILE)
templates_data = load_config(TEMPLATES_FILE)

def get_all_templates():
    """
    Returns all templates with their component definitions.
    """
    return templates_data

def get_template_by_name(template_name: str):
    """
    Returns a specific template by name.
    
    Args:
        template_name: The name of the template to retrieve.
        
    Returns:
        The template configuration if found.
        
    Raises:
        HTTPException: If the template is not found.
    """
    if template_name not in templates_data:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
    
    return templates_data[template_name]

def get_template_schema(template_name: str):
    """
    Returns the schema for a specific template.
    
    Args:
        template_name: The name of the template to get the schema for.
        
    Returns:
        A dictionary containing the template schema.
        
    Raises:
        HTTPException: If the template is not found.
    """
    if template_name not in templates_data:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
    
    template_components = templates_data[template_name]
    
    # Extract component types and required fields
    components = []
    required_fields = []
    
    for component in template_components:
        component_name = component.get("componentName")
        component_id = component.get("componentID")
        
        if not component_name or not component_id:
            continue
        
        # Get the output type directly from the template component
        output_type = component.get("output", {}).get("type", "none")
        
        # Skip components with output type "none"
        if output_type == "none":
            continue
        
        # Determine if the component is required based on validations
        is_required = False
        if "validations" in component:
            for validation in component["validations"]:
                if validation.get("type") == "required":
                    is_required = True
                    break
        
        # Add component to the schema with simplified structure
        components.append({
            "name": component_name,
            "type": output_type,
            "required": is_required,
            "componentID": component_id
        })
        
        # Add to required fields if necessary
        if is_required:
            required_fields.append(component_id)
    
    # Construct and return the schema
    return {
        "template_name": template_name,
        "components": components,
        "required_fields": required_fields
    }

def get_all_components():
    """
    Returns all available components.
    """
    return components_config

def get_component_by_name(component_name: str):
    """
    Returns a specific component by name.
    
    Args:
        component_name: The name of the component to retrieve.
        
    Returns:
        The component configuration if found.
        
    Raises:
        HTTPException: If the component is not found.
    """
    component = next((c for c in components_config if c.get("componentName") == component_name), None)
    
    if not component:
        raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
    
    return component 