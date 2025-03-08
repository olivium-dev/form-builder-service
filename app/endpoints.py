import uuid
import logging
from fastapi import Path, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db, create_dynamic_table

logger = logging.getLogger(__name__)

def create_post_endpoint(template_name: str, model: BaseModel):
    """
    Factory function to create a POST endpoint handler for a given template.
    """
    # Create a dynamic table for this template
    db_model = create_dynamic_table(template_name, model.__fields__)
    
    async def post_endpoint(form_data: model, db: Session = Depends(get_db)):
        try:
            # Generate a unique submission ID
            submission_id = str(uuid.uuid4())
            
            # Create a new database record
            db_record = db_model(
                submission_id=submission_id,
                data=form_data.dict()
            )
            
            # Add and commit to the database
            db.add(db_record)
            db.commit()
            db.refresh(db_record)
            
            logger.info(f"Saved {template_name} submission with ID: {submission_id}")
            
            return {
                "message": f"{template_name} submitted successfully",
                "submission_id": submission_id,
                "data": form_data.dict(),
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving {template_name} submission: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error saving form submission: {str(e)}")
    
    return post_endpoint

def create_get_endpoint(template_name: str, model: BaseModel):
    """
    Factory function to create a GET endpoint handler for a given template.
    """
    # Create a dynamic table for this template
    db_model = create_dynamic_table(template_name, model.__fields__)
    
    async def get_endpoint(form_id: str = Path(..., description="Unique identifier for the form submission"), 
                          db: Session = Depends(get_db)):
        try:
            # Query the database for the submission
            submission = db.query(db_model).filter(db_model.submission_id == form_id).first()
            
            if not submission:
                raise HTTPException(status_code=404, detail=f"{template_name} submission with ID {form_id} not found")
            
            logger.info(f"Retrieved {template_name} submission with ID: {form_id}")
            
            return {
                "message": f"Retrieved {template_name} form",
                "submission_id": form_id,
                "data": submission.data,
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving {template_name} submission: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving form submission: {str(e)}")
    
    return get_endpoint 