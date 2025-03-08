# Form Builder Microservice - Source Code Documentation

This document details the source code structure and the step-by-step process to build a Form Builder microservice using a configuration-driven approach. The microservice dynamically creates Pydantic models and RESTful endpoints based on two JSON configuration files—one for individual UI components and another for form templates. These dynamic models are then automatically integrated with FastAPI to generate up-to-date OpenAPI (Swagger) documentation.

---

## Table of Contents
- [Overview](#overview)
- [File Structure](#file-structure)
- [Configuration Files](#configuration-files)
  - [components_config.json](#components_configjson)
  - [templates_config.json](#templates_configjson)
- [Dynamic Model Generation](#dynamic-model-generation)
- [Dynamic Endpoint Registration](#dynamic-endpoint-registration)
- [Code Walkthrough](#code-walkthrough)
- [Source Code Checklist](#source-code-checklist)

---

## Overview

The microservice is designed to be highly flexible:
- **Configuration-Driven:** The service uses JSON configuration files to define UI components and form templates.  
- **Dynamic Model Creation:** Based on the configuration, the service creates Pydantic models on startup using `create_model`.
- **Automatic Endpoint Registration:** It generates API endpoints (e.g., POST for form submissions, GET for retrieval) automatically, ensuring that any changes in the configuration files are directly reflected in the API and its Swagger documentation.
- **OpenAPI Integration:** FastAPI’s integration with Pydantic ensures that the OpenAPI schema is automatically updated with the dynamically generated models and routes.

---

## File Structure

A typical project structure may look like this:
form-builder-microservice/ │ ├── main.py # Main application file with dynamic model & endpoint generation ├── components_config.json # JSON file defining available UI components and their attributes ├── templates_config.json # JSON file defining form templates (list of components per template) ├── requirements.txt # Python dependencies for the microservice └── README.md # This documentation file

csharp
Copy

---

## Configuration Files

### components_config.json

This JSON file defines each UI component. A sample entry includes:
- **componentName:** The name of the component (e.g., "Header", "Text Input").
- **description:** A short description of the component’s purpose.
- **style:** An object that describes the CSS style properties.
- **attributes:** An array of objects where each object defines an attribute (name, type, description).
- **output:** Specifies the type and description of the output produced by the component.
- **validations:** An array for validation rules (if any).

**Example:**
```json
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
    "componentName": "Label",
    "description": "A text element used for headings, descriptions, or instructions.",
    "style": {
      "type": "string",
      "description": "CSS style string or class reference for the label."
    },
    "attributes": [
      {
        "name": "text",
        "type": "string",
        "description": "The content of the label."
      }
    ],
    "output": {
      "type": "none",
      "description": "No output data is collected from a label."
    },
    "validations": []
  },
  {
    "componentName": "Horizontal Separator",
    "description": "A thin line or rule used to visually separate different sections.",
    "style": {
      "type": "string",
      "description": "CSS style string or class reference for the separator."
    },
    "attributes": [
      {
        "name": "color",
        "type": "string",
        "description": "Color of the separator line."
      },
      {
        "name": "thickness",
        "type": "number",
        "description": "Line thickness in pixels."
      },
      {
        "name": "margin",
        "type": "object",
        "description": "Spacing around the separator (e.g., top/bottom)."
      }
    ],
    "output": {
      "type": "none",
      "description": "No output data is collected from a separator."
    },
    "validations": []
  },
  {
    "componentName": "Single Selection",
    "description": "A set of radio options from which the user can pick exactly one.",
    "style": {
      "type": "string",
      "description": "CSS style string or class reference for the single selection component."
    },
    "attributes": [
      {
        "name": "options",
        "type": "array",
        "description": "List of selectable items, each with { id: string, label: string }."
      },
      {
        "name": "layout",
        "type": "string",
        "description": "Defines how options are displayed (e.g., 'vertical', 'horizontal')."
      },
      {
        "name": "defaultSelection",
        "type": "string",
        "description": "ID of the initially selected option (if any)."
      }
    ],
    "output": {
      "type": "string",
      "description": "ID of the selected option."
    },
    "validations": [
      {
        "type": "required",
        "description": "User must select one option if this field is mandatory."
      }
    ]
  },
  {
    "componentName": "Text Input",
    "description": "A single-line text field for entering information (e.g. name, email).",
    "style": {
      "type": "string",
      "description": "CSS style string or class reference for the text input."
    },
    "attributes": [
      {
        "name": "label",
        "type": "string",
        "description": "Label text displayed above or beside the input."
      },
      {
        "name": "placeholder",
        "type": "string",
        "description": "Hint text displayed when the field is empty."
      },
      {
        "name": "inputType",
        "type": "string",
        "description": "Specifies the type (e.g., 'text', 'email', 'password')."
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
      },
      {
        "type": "maxLength",
        "description": "Text cannot exceed the specified length."
      },
      {
        "type": "pattern",
        "description": "Optional pattern/format validation (e.g., email)."
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
  },
  {
    "componentName": "Phone Input",
    "description": "An input for phone numbers, including country-code selection and verification.",
    "style": {
      "type": "string",
      "description": "CSS style string or class reference for the phone input."
    },
    "attributes": [
      {
        "name": "countryCodes",
        "type": "array",
        "description": "List of supported country codes, each with { id: string, label: string, code: string }."
      },
      {
        "name": "defaultCountryCode",
        "type": "string",
        "description": "ID of the pre-selected country code."
      },
      {
        "name": "verificationMethod",
        "type": "string",
        "description": "Preferred method for verification (e.g., 'sms', 'whatsapp')."
      }
    ],
    "output": {
      "type": "string",
      "description": "The full phone number (country code + local number)."
    },
    "validations": [
      {
        "type": "required",
        "description": "Phone number must be provided if mandatory."
      },
      {
        "type": "phoneFormat",
        "description": "Must be a valid phone format (e.g., E.164)."
      }
    ]
  },
  {
    "componentName": "Photo Upload Grid",
    "description": "A grid of placeholders to upload and display profile pictures, with reorder/remove functionality.",
    "style": {
      "type": "string",
      "description": "CSS style string or class reference for the photo upload grid."
    },
    "attributes": [
      {
        "name": "maxImages",
        "type": "number",
        "description": "Maximum number of images allowed."
      },
      {
        "name": "allowReorder",
        "type": "boolean",
        "description": "Enables reordering of uploaded images."
      },
      {
        "name": "allowRemove",
        "type": "boolean",
        "description": "Allows removal of an uploaded image."
      },
      {
        "name": "imageVisibilityToggle",
        "type": "boolean",
        "description": "If true, users can toggle visibility of each photo."
      }
    ],
    "output": {
      "type": "array",
      "description": "An array of image file paths or URIs (strings)."
    },
    "validations": [
      {
        "type": "allowedFileTypes",
        "description": "Permitted file formats (e.g., JPG, PNG)."
      },
      {
        "type": "maxFileSize",
        "description": "Max file size per image."
      },
      {
        "type": "minImages",
        "description": "Minimum number of images required."
      },
      {
        "type": "maxImages",
        "description": "Maximum number of images allowed."
      }
    ]
  },
  {
    "componentName": "Multi Selection",
    "description": "Allows the user to pick multiple options from a list, optionally with a search bar.",
    "style": {
      "type": "string",
      "description": "CSS style string or class reference for the multi selection component."
    },
    "attributes": [
      {
        "name": "options",
        "type": "array",
        "description": "List of selectable items, each with { id: string, label: string }."
      },
      {
        "name": "showSearchBar",
        "type": "boolean",
        "description": "If true, a search bar is shown for filtering options."
      },
      {
        "name": "maxSelection",
        "type": "number",
        "description": "Maximum number of items the user can select."
      }
    ],
    "output": {
      "type": "array",
      "description": "An array of selected option IDs (strings)."
    },
    "validations": [
      {
        "type": "required",
        "description": "At least one selection is required if mandatory."
      },
      {
        "type": "maxSelection",
        "description": "Cannot select more items than the defined limit."
      }
    ]
  },
  {
    "componentName": "Slider with Label",
    "description": "A track bar for selecting a numeric value, accompanied by a label (e.g. 'Distance: 10km').",
    "style": {
      "type": "string",
      "description": "CSS style string or class reference for the slider component."
    },
    "attributes": [
      {
        "name": "label",
        "type": "string",
        "description": "Descriptive text displayed alongside the slider."
      },
      {
        "name": "minValue",
        "type": "number",
        "description": "The slider’s minimum allowed value."
      },
      {
        "name": "maxValue",
        "type": "number",
        "description": "The slider’s maximum allowed value."
      },
      {
        "name": "step",
        "type": "number",
        "description": "Increment steps for the slider."
      },
      {
        "name": "defaultValue",
        "type": "number",
        "description": "The initial slider position."
      }
    ],
    "output": {
      "type": "number",
      "description": "The numeric value the user has selected."
    },
    "validations": [
      {
        "type": "required",
        "description": "A value must be selected if the field is mandatory."
      },
      {
        "type": "range",
        "description": "Selected value must be within minValue and maxValue."
      },
      {
        "type": "step",
        "description": "Value must align with the defined step increments."
      }
    ]
  }
]

  // Additional component definitions ...
]
templates_config.json
This file defines form templates by listing the components that make up each template. Each template is essentially a named collection of component names.

Example:

json
Copy
{
  "loginForm": ["Header", "Text Input", "Password Input", "Button"],
  "registrationForm": ["Header", "Text Input", "Text Input", "Date Input", "Button"]
}
Dynamic Model Generation
The microservice uses a dynamic model creation approach:

Load Configurations:
At startup, the application loads components_config.json and templates_config.json.

Type Mapping:
A mapping dictionary translates string types (e.g., "string", "number", "boolean") from the configuration into Python types.

Dynamic Component Models:
Using Pydantic’s create_model, a dynamic model is generated for each component, encapsulating its style, attributes, output, and validations.

Template Models:
For each template, the service dynamically builds a model that aggregates the component models specified in the template. This allows each form template to have its own schema based on its constituent components.

Dynamic Endpoint Registration
The dynamic endpoint registration mechanism works as follows:

Endpoint Factory Functions:
Factory functions (for example, create_post_endpoint and create_get_endpoint) are defined to generate endpoint functions dynamically. These functions:

Accept a model (generated from the configuration).
Process incoming JSON data using the dynamic model.
Handle persistence logic if needed (e.g., converting UUIDs or managing database interactions).
Loop over Templates:
The application loops over the templates defined in templates_config.json. For each template:

A POST endpoint is registered to handle form submissions.
A GET endpoint is registered to retrieve form data.
FastAPI Integration:
Because these endpoints use dynamically generated Pydantic models, FastAPI automatically updates its OpenAPI schema and Swagger UI documentation to reflect these endpoints.

Code Walkthrough
Configuration Loading:
In main.py, the code loads the JSON configuration files:

python
Copy
with open("components_config.json") as f:
    components_config = json.load(f)

with open("templates_config.json") as f:
    templates_config = json.load(f)
Type Mapping Dictionary:
A dictionary maps configuration string types to Python types:

python
Copy
type_mapping = {
    "string": (str, ...),
    "number": (float, ...),
    "boolean": (bool, ...),
    "object": (dict, ...),
    "array": (list, ...),
    // Extend as necessary
}
Dynamic Component Model Creation:
For each component in components_config.json, a dynamic model is created:

python
Copy
from pydantic import create_model

component_models = {}
for component in components_config:
    fields = {}
    # Process style, attributes, and output fields based on the mapping
    # For example, map the 'style' field:
    style_type = component["style"]["type"].lower()
    fields["style"] = type_mapping.get(style_type, (str, ...))
    # Process attributes and add them to fields
    for attr in component["attributes"]:
        attr_type = attr["type"].lower()
        fields[attr["name"]] = type_mapping.get(attr_type, (str, ...))
    # Create the component model
    model = create_model(component["componentName"] + "Model", **fields)
    component_models[component["componentName"]] = model
Dynamic Template Model Creation:
For each template in templates_config.json, a model is generated that aggregates its components:

python
Copy
template_models = {}
for template_name, component_list in templates_config.items():
    fields = {}
    for comp_name in component_list:
        # Each component is represented as a nested model
        fields[comp_name] = (component_models[comp_name], ...)
    # Create the template model
    template_model = create_model(template_name.capitalize() + "Template", **fields)
    template_models[template_name] = template_model
Endpoint Factory Functions:
Define functions to create endpoints dynamically:

python
Copy
def create_post_endpoint(template_name: str, model):
    async def post_endpoint(form_data: model):
        # Process the form submission (e.g., convert types, persist data)
        return {"message": f"{template_name} submitted", "data": form_data.dict()}
    return post_endpoint

def create_get_endpoint(template_name: str, model):
    async def get_endpoint(form_id: str):
        # Retrieve form data based on form_id
        return {"form_id": form_id, "template": template_name}
    return get_endpoint
Registering Endpoints:
Loop over each template model and register the endpoints with FastAPI:

python
Copy
from fastapi import FastAPI, Path

app = FastAPI()

for template_name, model in template_models.items():
    app.post(f"/forms/{template_name}", response_model=model)(
        create_post_endpoint(template_name, model)
    )
    app.get(f"/forms/{template_name}/{{form_id}}", response_model=model)(
        create_get_endpoint(template_name, model)
    )
These endpoints automatically appear in the Swagger documentation generated by FastAPI.

Source Code Checklist
Step	Task Description	Completed
1	Create and configure components_config.json: Define all UI components with their style, attributes, output, and validations.	[ ]
2	Create and configure templates_config.json: Define form templates as collections of component names.	[ ]
3	Implement configuration file loading: Write code to read and parse the JSON configuration files at startup.	[ ]
4	Setup type mapping: Create a dictionary that maps configuration types (string, number, boolean, etc.) to Python types.	[ ]
5	Dynamic Component Model Creation: Use Pydantic’s create_model to dynamically generate a model for each component based on its configuration.	[ ]
6	Dynamic Template Model Creation: Create models for each form template by aggregating the component models defined in the configuration.	[ ]
7	Define endpoint factory functions: Write functions to create POST and GET endpoint handlers that use the dynamic models.	[ ]
8	Register endpoints dynamically: Loop over the template models to register endpoints with FastAPI using decorators.	[ ]
9	Ensure OpenAPI integration: Verify that the dynamic models and endpoints are automatically incorporated into FastAPI’s OpenAPI (Swagger) documentation.	[ ]
css
Copy
