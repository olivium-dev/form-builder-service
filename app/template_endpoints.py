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
    Get all available templates.
    
    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary of template names and their component definitions
    """
    return templates_data

def get_template_by_name(template_name: str):
    """
    Get a specific template by name.
    
    Args:
        template_name: The name of the template to retrieve
        
    Returns:
        List[Dict[str, Any]]: List of component definitions for the template
    """
    if template_name not in templates_data:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
    
    return templates_data[template_name]

def get_template_schema(template_name: str):
    """
    Get the schema for a specific template.
    
    Args:
        template_name: The name of the template to retrieve
        
    Returns:
        Dict[str, Any]: Schema definition for the template
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
        
        # Find the component definition in components_config
        component_def = next((c for c in components_config if c.get("componentName") == component_name), None)
        
        if not component_def:
            continue
        
        # Get the output type
        output_type = "none"
        if "output" in component_def and "type" in component_def["output"]:
            output_type = component_def["output"]["type"]
        
        # Skip components with output type "none"
        if output_type == "none":
            continue
        
        # Determine if the component is required based on validations
        is_required = False
        if "validations" in component_def:
            for validation in component_def["validations"]:
                if validation.get("type") == "required":
                    is_required = True
                    break
        
        # Add component to the schema
        components.append({
            "name": component_name,
            "type": output_type,
            "required": is_required,
            "componentID": component_id,
            "attributes": component_def.get("attributes", [])
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
    Get all available components.
    
    Returns:
        List[Dict[str, Any]]: List of all component definitions
    """
    return components_config

def get_component_by_name(component_name: str):
    """
    Get a specific component by name.
    
    Args:
        component_name: The name of the component to retrieve
        
    Returns:
        Dict[str, Any]: Component definition
    """
    component = next((c for c in components_config if c.get("componentName") == component_name), None)
    
    if not component:
        raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
    
    return component 