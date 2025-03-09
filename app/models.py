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
    "string[]": (List[str], ...),
    "number[]": (List[float], ...),
    "boolean[]": (List[bool], ...),
    "object[]": (List[dict], ...),
}

class ComponentValueModel(BaseModel):
    """Base model for component values."""
    value: Any

def create_component_model(component: Dict[str, Any]) -> Optional[Type[BaseModel]]:
    """
    Dynamically creates a Pydantic model for a component based on its configuration.
    
    Args:
        component: A dictionary containing the component configuration.
        
    Returns:
        A Pydantic BaseModel class for the component or None if the component has no output.
    """
    # Extract component name, ID, and output type
    component_name = component.get("componentName", "UnknownComponent")
    component_id = component.get("componentID", "unknown-id")
    output_type = component.get("output", {}).get("type", "none")
    
    # Skip creating models for components with output type "none"
    if output_type == "none":
        return None
    
    # Get the Python type for the output type
    python_type = type_mapping.get(output_type, (str, ...))[0]
    
    # Create a model with a value field of the appropriate type
    model_name = f"{component_name.replace(' ', '')}Model"
    return create_model(model_name, value=(python_type, ...))

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
            
        if component_name and component_id:
            # Get the Python type for the output type
            python_type = type_mapping.get(output_type, (str, ...))[0]
            # Create a model for this component with the correct type
            component_model = create_model(
                f"{component_name}Value",
                value=(python_type, ...),
                __base__=BaseModel
            )
            # Use componentID as the field name
            field_definitions[component_id] = (component_model, ...)
    
    # Create and return the model, even if empty
    model_name = f"{template_name.capitalize()}Model"
    return create_model(model_name, **field_definitions) 