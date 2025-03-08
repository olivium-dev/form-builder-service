import logging
import uuid
from typing import Dict, Any, Callable
from fastapi import Depends, Path, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db

logger = logging.getLogger(__name__)

def create_post_endpoint(template_name: str, model: BaseModel) -> Callable:
    """
    Creates a POST endpoint handler for a specific template.
    
    Args:
        template_name: The name of the template.
        model: The Pydantic model for the template.
        
    Returns:
        A function that handles POST requests for the template.
    """
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
            
            # Create a table name from the template name
            table_name = f"{template_name.lower()}_submissions"
            
            # Insert the data into the database
            db.execute(
                f"INSERT INTO {table_name} (submission_id, data) VALUES (:submission_id, :data)",
                {"submission_id": submission_id, "data": data_dict}
            )
            db.commit()
            
            logger.info(f"Saved {template_name} submission with ID: {submission_id}")
            
            # Return success response
            return {
                "message": f"{template_name} submitted successfully",
                "submission_id": submission_id,
                "data": data_dict
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
            # Create a table name from the template name
            table_name = f"{template_name.lower()}_submissions"
            
            # Query the database for the submission
            result = db.execute(
                f"SELECT data FROM {table_name} WHERE submission_id = :submission_id",
                {"submission_id": form_id}
            ).fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail=f"{template_name} submission with ID {form_id} not found")
            
            # Extract the data from the result
            data = result[0]
            
            logger.info(f"Retrieved {template_name} submission with ID: {form_id}")
            
            # Return the data
            return {
                "message": f"Retrieved {template_name} form",
                "submission_id": form_id,
                "data": data
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving {template_name} submission: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving submission: {str(e)}")
    
    return get_endpoint 