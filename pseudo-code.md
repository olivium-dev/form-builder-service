File: app/__init__.py
python
Copy
# app/__init__.py
# (This file can be left empty or used for package-level initialization.)
File: app/config.py
python
Copy
# app/config.py
import json
import logging

logger = logging.getLogger(__name__)

def load_config(file_path: str):
    """
    Load a JSON configuration file and return its data.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            logger.info(f"Loaded configuration from {file_path}")
            return config_data
    except Exception as e:
        logger.error(f"Error loading config file {file_path}: {e}")
        raise RuntimeError(f"Error loading config file {file_path}: {e}")
File: app/models.py
python
Copy
# app/models.py
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
File: app/endpoints.py
python
Copy
# app/endpoints.py
from fastapi import Path
from pydantic import BaseModel

def create_post_endpoint(template_name: str, model: BaseModel):
    """
    Factory function to create a POST endpoint handler for a given template.
    """
    async def post_endpoint(form_data: model):
        # In production, add persistence or additional processing as required.
        return {
            "message": f"{template_name} submitted successfully",
            "data": form_data.dict(),
        }
    return post_endpoint

def create_get_endpoint(template_name: str, model: BaseModel):
    """
    Factory function to create a GET endpoint handler for a given template.
    """
    async def get_endpoint(form_id: str = Path(..., description="Unique identifier for the form submission")):
        # In production, replace this with retrieval logic.
        dummy_data = {field: None for field in model.__fields__.keys()}
        dummy_data["id"] = form_id
        return {
            "message": f"Retrieved {template_name} form",
            "data": dummy_data,
        }
    return get_endpoint
File: app/main.py
python
Copy
# app/main.py
import logging
from fastapi import FastAPI
import uvicorn

from app.config import load_config
from app.models import create_component_model, create_template_model
from app.endpoints import create_post_endpoint, create_get_endpoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define configuration file paths
COMPONENTS_CONFIG_FILE = "components_config.json"
TEMPLATES_CONFIG_FILE = "templates_config.json"

# Load configuration files
components_config = load_config(COMPONENTS_CONFIG_FILE)
templates_config = load_config(TEMPLATES_CONFIG_FILE)

# Create dynamic component models
component_models = {}
for comp in components_config:
    comp_name = comp.get("componentName")
    if not comp_name:
        logger.warning("A component without a componentName encountered; skipping.")
        continue
    try:
        model = create_component_model(comp)
        component_models[comp_name] = model
        logger.info(f"Created model for component: {comp_name}")
    except Exception as e:
        logger.error(f"Failed to create model for component {comp_name}: {e}")
        raise

# Create dynamic template models
template_models = {}
for template_name, comp_list in templates_config.items():
    try:
        model = create_template_model(template_name, comp_list, component_models)
        template_models[template_name] = model
        logger.info(f"Created template model for: {template_name}")
    except Exception as e:
        logger.error(f"Failed to create template model for {template_name}: {e}")
        raise

# Initialize FastAPI application
app = FastAPI(
    title="Form Builder Microservice",
    description="A dynamic, configuration-driven form builder service.",
    version="1.0.0",
)

# Dynamically register endpoints for each template
for template_name, model in template_models.items():
    post_path = f"/forms/{template_name}"
    get_path = f"/forms/{template_name}/{{form_id}}"

    app.post(
        post_path,
        response_model=model,
        summary=f"Submit {template_name} form"
    )(create_post_endpoint(template_name, model))

    app.get(
        get_path,
        response_model=model,
        summary=f"Retrieve {template_name} form by ID"
    )(create_get_endpoint(template_name, model))

    logger.info(f"Registered endpoints for template: {template_name} (POST: {post_path}, GET: {get_path})")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
File: components_config.json
json
Copy
[
  {
    "componentName": "Header",
    "description": "A top area containing the screen’s title or heading.",
    "style": {
      "type": "string",
      "description": "CSS style string or class reference for the header."
    },
    "attributes": [
      {
        "name": "titleText",
        "type": "string",
        "description": "The text displayed in the header."
      },
      {
        "name": "alignment",
        "type": "string",
        "description": "Specifies how the header text is aligned (e.g., 'center', 'left')."
      }
    ],
    "output": {
      "type": "none",
      "description": "This component does not produce output data."
    },
    "validations": []
  },
  {
    "componentName": "Text Input",
    "description": "A single-line text field for entering information.",
    "style": {
      "type": "string",
      "description": "CSS style string or class reference for the text input."
    },
    "attributes": [
      {
        "name": "placeholder",
        "type": "string",
        "description": "Placeholder text for the input field."
      },
      {
        "name": "maxLength",
        "type": "number",
        "description": "Maximum number of characters allowed."
      }
    ],
    "output": {
      "type": "string",
      "description": "The user-entered text."
    },
    "validations": [
      {
        "type": "required",
        "description": "Field must be filled if mandatory."
      }
    ]
  },
  {
    "componentName": "Date Input",
    "description": "A component to select a date (e.g. birthday).",
    "style": {
      "type": "string",
      "description": "CSS style string or class reference for the date input."
    },
    "attributes": [
      {
        "name": "label",
        "type": "string",
        "description": "Label text describing the date field."
      },
      {
        "name": "minDate",
        "type": "string",
        "description": "Earliest allowable date (e.g., '1900-01-01' in ISO format)."
      },
      {
        "name": "maxDate",
        "type": "string",
        "description": "Latest allowable date (e.g., '2100-12-31' in ISO format)."
      }
    ],
    "output": {
      "type": "string",
      "description": "The selected date in a standardized format (e.g., ISO)."
    },
    "validations": [
      {
        "type": "required",
        "description": "Date must be provided if mandatory."
      },
      {
        "type": "validDate",
        "description": "Must be a valid calendar date within allowed range."
      }
    ]
  }
]
File: templates_config.json
json
Copy
{
  "loginForm": ["Header", "Text Input"],
  "registrationForm": ["Header", "Text Input", "Date Input"]
}
File: requirements.txt
ini
Copy
fastapi==0.109.2
uvicorn==0.27.1
pydantic==2.6.1
Project Structure
graphql
Copy
form-builder-microservice/
├── app/
│   ├── __init__.py         # Package initialization (can be empty)
│   ├── config.py           # Configuration loader for JSON files
│   ├── models.py           # Dynamic model generation for components and templates
│   ├── endpoints.py        # Endpoint factory functions for POST/GET handlers
│   └── main.py             # Main application file; loads configs, registers endpoints, and starts FastAPI
├── components_config.json  # JSON file defining UI components
├── templates_config.json   # JSON file defining form templates (list of component names)
├── requirements.txt        # Python dependencies list
└── README.md               # Project documentation (if needed)