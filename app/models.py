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
    # Extract component name and attributes
    component_name = component.get("componentName", "UnknownComponent")
    attributes = component.get("attributes", [])
    
    # Create field definitions for the model
    field_definitions = {
        "style": (Optional[str], None),
        "componentID": (str, Field(..., description="Unique identifier for the component within the template"))
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

def create_template_model(template_name: str, component_list: List[str], component_models: Dict[str, BaseModel]) -> BaseModel:
    """
    Dynamically creates a Pydantic model for a template based on its components.
    
    Args:
        template_name: The name of the template.
        component_list: A list of component names in the template.
        component_models: A dictionary mapping component names to their models.
        
    Returns:
        A Pydantic BaseModel class for the template.
    """
    # Create field definitions for the template model
    field_definitions = {}
    
    # Add each component as a field in the template model
    for component_name in component_list:
        if component_name in component_models:
            field_definitions[component_name] = (component_models[component_name], ...)
    
    # Create and return the model
    model_name = f"{template_name.capitalize()}Model"
    return create_model(model_name, **field_definitions) 