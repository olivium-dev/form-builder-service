import logging
import argparse
from fastapi import FastAPI
import uvicorn

from app.config import load_config
from app.models import create_component_model, create_template_model
from app.endpoints import create_post_endpoint, create_get_endpoint
from app.database import initialize_db
from app.template_endpoints import (
    get_all_templates, 
    get_template_by_name, 
    get_all_components, 
    get_component_by_name,
    get_template_schema
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define configuration file paths
COMPONENTS_CONFIG_FILE = "components_config.json"
TEMPLATES_FILE = "templates.json"

# Load configuration files
components_config = load_config(COMPONENTS_CONFIG_FILE)
templates_data = load_config(TEMPLATES_FILE)

# Create dynamic component models from components_config.json
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

# Create dynamic template models from templates.json
template_models = {}
for template_name, template_components in templates_data.items():
    try:
        # Extract component names from the template components
        component_names = [comp.get("componentName") for comp in template_components if comp.get("componentName")]
        
        # Create template model using the component names
        model = create_template_model(template_name, component_names, component_models)
        template_models[template_name] = model
        logger.info(f"Created template model for: {template_name}")
    except Exception as e:
        logger.error(f"Failed to create template model for {template_name}: {e}")
        raise

# Initialize FastAPI application
app = FastAPI(
    title="Form Builder Microservice",
    description="A dynamic, configuration-driven form builder service with PostgreSQL database.",
    version="1.0.0",
)

# Initialize the database
@app.on_event("startup")
async def startup_event():
    initialize_db()
    logger.info("Database initialized on startup")

# Register template-related endpoints
@app.get("/templates", summary="Get all templates", tags=["Templates"])
async def get_templates():
    """
    Get all available templates with their component definitions.
    """
    return get_all_templates()

@app.get("/templates/{template_name}", summary="Get template by name", tags=["Templates"])
async def get_template(template_name: str):
    """
    Get a specific template by name.
    """
    return get_template_by_name(template_name)

@app.get("/templates/{template_name}/schema", summary="Get template schema", tags=["Templates"])
async def get_schema(template_name: str):
    """
    Get the schema for a specific template.
    """
    return get_template_schema(template_name)

@app.get("/components", summary="Get all components", tags=["Components"])
async def get_components():
    """
    Get all available components.
    """
    return get_all_components()

@app.get("/components/{component_name}", summary="Get component by name", tags=["Components"])
async def get_component(component_name: str):
    """
    Get a specific component by name.
    """
    return get_component_by_name(component_name)

# Dynamically register endpoints for each template
for template_name, model in template_models.items():
    post_path = f"/forms/{template_name}"
    get_path = f"/forms/{template_name}/{{form_id}}"

    app.post(
        post_path,
        response_model=dict,  # Using dict as response_model since we're returning a message and data
        summary=f"Submit {template_name} form",
        tags=["Forms"]
    )(create_post_endpoint(template_name, model))

    app.get(
        get_path,
        response_model=dict,  # Using dict as response_model for the same reason
        summary=f"Retrieve {template_name} form by ID",
        tags=["Forms"]
    )(create_get_endpoint(template_name, model))

    logger.info(f"Registered endpoints for template: {template_name} (POST: {post_path}, GET: {get_path})")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Form Builder Microservice")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    args = parser.parse_args()
    
    # Run the application
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=False) 