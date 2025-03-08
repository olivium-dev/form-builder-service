import logging
from typing import Dict, List, Any
from fastapi import HTTPException

from app.config import load_config

logger = logging.getLogger(__name__)

# Define configuration file paths
COMPONENTS_CONFIG_FILE = "components_config.json"
TEMPLATES_FILE = "templates.json"

def get_all_templates():
    """
    Get all available templates.
    
    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary of template names and their component definitions
    """
    try:
        templates_data = load_config(TEMPLATES_FILE)
        return templates_data
    except Exception as e:
        logger.error(f"Error loading templates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading templates: {str(e)}")

def get_template_by_name(template_name: str):
    """
    Get a specific template by name.
    
    Args:
        template_name: The name of the template to retrieve
        
    Returns:
        List[Dict[str, Any]]: List of component definitions for the template
    """
    try:
        templates_data = load_config(TEMPLATES_FILE)
        
        if template_name not in templates_data:
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
        
        return templates_data[template_name]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading template '{template_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading template: {str(e)}")

def get_template_schema(template_name: str):
    """
    Get the schema for a specific template.
    
    Args:
        template_name: The name of the template to retrieve
        
    Returns:
        Dict[str, Any]: Schema definition for the template
    """
    try:
        template_components = get_template_by_name(template_name)
        
        # Create a schema object
        schema = {
            "template_name": template_name,
            "components": [],
            "required_fields": []
        }
        
        # Process each component
        for component in template_components:
            comp_name = component.get("componentName")
            if not comp_name:
                continue
                
            # Get output type
            output_type = "none"
            if "output" in component and "type" in component["output"]:
                output_type = component["output"]["type"]
            
            # Check if the component has required validation
            is_required = False
            if "validations" in component:
                for validation in component["validations"]:
                    if validation.get("type") == "required":
                        is_required = True
                        break
            
            # Add to schema
            comp_schema = {
                "name": comp_name,
                "type": output_type,
                "required": is_required,
                "attributes": component.get("attributes", [])
            }
            
            schema["components"].append(comp_schema)
            
            # Add to required fields if necessary
            if is_required and output_type != "none":
                schema["required_fields"].append(comp_name)
        
        return schema
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating schema for template '{template_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating schema: {str(e)}")

def get_all_components():
    """
    Get all available components.
    
    Returns:
        List[Dict[str, Any]]: List of all component definitions
    """
    try:
        components_data = load_config(COMPONENTS_CONFIG_FILE)
        return components_data
    except Exception as e:
        logger.error(f"Error loading components: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading components: {str(e)}")

def get_component_by_name(component_name: str):
    """
    Get a specific component by name.
    
    Args:
        component_name: The name of the component to retrieve
        
    Returns:
        Dict[str, Any]: Component definition
    """
    try:
        components_data = load_config(COMPONENTS_CONFIG_FILE)
        
        for component in components_data:
            if component.get("componentName") == component_name:
                return component
        
        raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading component '{component_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading component: {str(e)}") 