from collections import Counter
from typing import Any, Dict, List, Tuple, Optional, Type
from pydantic import BaseModel, create_model, Field

# Mapping from configuration type strings to Python types (with required ellipsis)
type_mapping: Dict[str, Tuple[Any, Any]] = {
    "string": (str, ...),
    "number": (float, ...),
    "boolean": (bool, ...),
    "object": (dict, ...),
    "array": (list, ...),
}

def create_component_model(component: Dict[str, Any]) -> BaseModel:
    """
    Dynamically creates a Pydantic model for a component based on its configuration.
    
    Args:
        component: A dictionary containing the component configuration.
        
    Returns:
        A Pydantic BaseModel class for the component.
    """
    # Extract component name, ID, and attributes
    component_name = component.get("componentName", "UnknownComponent")
    component_id = component.get("componentID", "unknown-id")
    attributes = component.get("attributes", [])
    output_type = component.get("output", {}).get("type", "none")
    
    # Skip creating models for components with output type "none"
    if output_type == "none":
        return None
    
    # Create field definitions for the model
    field_definitions = {
        "value": (Optional[Any], None),  # The actual value of the component
        "style": (Optional[str], None)
    }
    
    # Add attributes from the component configuration
    for attr in attributes:
        attr_name = attr.get("name")
        attr_type = attr.get("type")
        
        if attr_name and attr_type:
            # Map JSON types to Python types
            type_mapping = {
                "string": str,
                "number": float,
                "integer": int,
                "boolean": bool,
                "array": list,
                "object": dict
            }
            
            python_type = type_mapping.get(attr_type, Any)
            field_definitions[attr_name] = (Optional[python_type], None)
    
    # Create and return the model
    model_name = f"{component_name.replace(' ', '')}Model"
    return create_model(model_name, **field_definitions)

def create_template_model(template_name: str, template_components: List[Dict[str, Any]], component_models: Dict[str, BaseModel]) -> BaseModel:
    """
    Dynamically creates a Pydantic model for a template based on its components.
    
    Args:
        template_name: The name of the template.
        template_components: A list of component configurations in the template.
        component_models: A dictionary mapping component names to their models.
        
    Returns:
        A Pydantic BaseModel class for the template.
    """
    # Create field definitions for the template model
    field_definitions = {}
    
    # Add each component as a field in the template model, using componentID as the key
    for component in template_components:
        component_name = component.get("componentName")
        component_id = component.get("componentID")
        output_type = component.get("output", {}).get("type", "none")
        
        # Skip components with output type "none"
        if output_type == "none":
            continue
            
        if component_name in component_models and component_id:
            # Use componentID as the field name
            field_definitions[component_id] = (Optional[component_models[component_name]], None)
    
    # Create and return the model
    model_name = f"{template_name.capitalize()}Model"
    return create_model(model_name, **field_definitions) 