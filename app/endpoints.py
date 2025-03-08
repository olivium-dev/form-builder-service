import logging
import uuid
from typing import Dict, Any, Callable
from fastapi import Depends, Path, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text, insert, select

from app.database import get_db, create_dynamic_table
from app.config import load_config

logger = logging.getLogger(__name__)

# Load templates data
templates_data = load_config("templates.json")

def create_post_endpoint(template_name: str, model: BaseModel) -> Callable:
    """
    Creates a POST endpoint handler for a specific template.
    
    Args:
        template_name: The name of the template.
        model: The Pydantic model for the template.
        
    Returns:
        A function that handles POST requests for the template.
    """
    # Get or create the table for this template
    table = create_dynamic_table(template_name)
    
    async def post_endpoint(form_data: model, db: Session = Depends(get_db)):
        """
        Handles form submission for a specific template.
        
        Args:
            form_data: The form data to be submitted.
            db: The database session.
            
        Returns:
            A dictionary with a success message and the submitted data.
        """
        try:
            # Generate a unique ID for the submission
            submission_id = str(uuid.uuid4())
            
            # Convert form data to a dictionary
            data_dict = form_data.model_dump()
            
            # Get the template components
            template_components = templates_data.get(template_name, [])
            
            # Create a mapping from componentID to componentName
            id_to_name_map = {
                comp.get("componentID"): comp.get("componentName")
                for comp in template_components
                if comp.get("componentID") and comp.get("componentName")
            }
            
            # Transform the data to use componentName as keys and extract only the values
            transformed_data = {}
            for component_id, component_data in data_dict.items():
                if component_id in id_to_name_map:
                    component_name = id_to_name_map[component_id]
                    # Store only the value, not the entire component data
                    transformed_data[component_name] = component_data.get("value")
            
            # Insert the data into the database using the table
            stmt = insert(table).values(submission_id=submission_id, data=transformed_data)
            db.execute(stmt)
            db.commit()
            
            logger.info(f"Saved {template_name} submission with ID: {submission_id}")
            
            # Return success response with simplified data
            response_data = {}
            for component_id, component_data in data_dict.items():
                if component_id in id_to_name_map:
                    # Include only the value in the response
                    response_data[component_id] = {"value": component_data.get("value")}
            
            return {
                "message": f"{template_name} submitted successfully",
                "submission_id": submission_id,
                "data": response_data
            }
        except Exception as e:
            logger.error(f"Error saving {template_name} submission: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error saving submission: {str(e)}")
    
    return post_endpoint

def create_get_endpoint(template_name: str, model: BaseModel) -> Callable:
    """
    Creates a GET endpoint handler for a specific template.
    
    Args:
        template_name: The name of the template.
        model: The Pydantic model for the template.
        
    Returns:
        A function that handles GET requests for the template.
    """
    # Get or create the table for this template
    table = create_dynamic_table(template_name)
    
    async def get_endpoint(form_id: str = Path(..., description="Unique identifier for the form submission"), 
                          db: Session = Depends(get_db)):
        """
        Retrieves a form submission by ID.
        
        Args:
            form_id: The unique identifier for the form submission.
            db: The database session.
            
        Returns:
            A dictionary with the retrieved form data.
        """
        try:
            # Query the database for the submission using the table
            stmt = select(table.c.data).where(table.c.submission_id == form_id)
            result = db.execute(stmt).fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail=f"{template_name} submission with ID {form_id} not found")
            
            # Extract the data from the result
            data = result[0]
            
            # Get the template components
            template_components = templates_data.get(template_name, [])
            
            # Create a mapping from componentName to componentID
            name_to_id_map = {
                comp.get("componentName"): comp.get("componentID")
                for comp in template_components
                if comp.get("componentID") and comp.get("componentName")
            }
            
            # Transform the data to use componentID as keys and wrap values in the expected format
            transformed_data = {}
            for component_name, value in data.items():
                if component_name in name_to_id_map:
                    component_id = name_to_id_map[component_name]
                    # Wrap the value in a dictionary with a "value" key
                    transformed_data[component_id] = {"value": value}
            
            logger.info(f"Retrieved {template_name} submission with ID: {form_id}")
            
            # Return the data
            return {
                "message": f"Retrieved {template_name} form",
                "submission_id": form_id,
                "data": transformed_data
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving {template_name} submission: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving submission: {str(e)}")
    
    return get_endpoint 