from collections import Counter
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel, create_model

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
    Dynamically creates a Pydantic model for a UI component.
    The model includes a 'style' field and fields for each attribute.
    """
    model_fields = {}

    # Process the 'style' field if defined
    if "style" in component and isinstance(component["style"], dict):
        style_type = component["style"].get("type", "string").lower()
        model_fields["style"] = type_mapping.get(style_type, (str, ...))
    
    # Process attributes if defined
    if "attributes" in component and isinstance(component["attributes"], list):
        for attr in component["attributes"]:
            attr_name = attr.get("name")
            attr_type_str = attr.get("type", "string").lower()
            if attr_name:
                model_fields[attr_name] = type_mapping.get(attr_type_str, (str, ...))
    
    # Generate a model name based on the component name
    model_name = component.get("componentName", "UnnamedComponent").replace(" ", "") + "Model"
    return create_model(model_name, **model_fields)

def create_template_model(template_name: str, component_list: List[str], component_models: Dict[str, BaseModel]) -> BaseModel:
    """
    Dynamically creates a Pydantic model for a form template.
    Each template is defined as a list of component names.
    Duplicate component names are handled by appending an index.
    """
    fields = {}
    counter = Counter(component_list)
    occurrence: Dict[str, int] = {}

    for comp in component_list:
        if comp not in component_models:
            raise ValueError(f"Component '{comp}' is not defined in the components configuration.")
        occurrence[comp] = occurrence.get(comp, 0) + 1
        field_name = comp.replace(" ", "")
        if counter[comp] > 1:
            field_name = f"{field_name}_{occurrence[comp]}"
        fields[field_name] = (component_models[comp], ...)
    
    model_name = template_name[0].upper() + template_name[1:] + "Template"
    return create_model(model_name, **fields) 