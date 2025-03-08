import os
import logging
from typing import Dict, Any, Type
from sqlalchemy import Column, String, JSON, Integer, MetaData, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()

# Dictionary to store dynamically created models
dynamic_models: Dict[str, Type[Base]] = {}

def get_db():
    """
    Get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_dynamic_table(template_name: str, component_fields: Dict[str, Any]):
    """
    Dynamically create a table for a template.
    
    Args:
        template_name: The name of the template
        component_fields: Dictionary of component fields
    
    Returns:
        SQLAlchemy model class for the template
    """
    table_name = f"{template_name.lower()}_submissions"
    logger.info(f"Creating dynamic table: {table_name}")
    
    # Check if table already exists
    if table_name in dynamic_models:
        return dynamic_models[table_name]
    
    # Create a model class directly using declarative base
    class DynamicModel(Base):
        __tablename__ = table_name
        
        id = Column(Integer, primary_key=True, index=True)
        submission_id = Column(String, unique=True, index=True)
        data = Column(JSON)  # Store the entire form data as JSON
    
    # Set the model name
    DynamicModel.__name__ = f"{template_name.capitalize()}Submission"
    
    # Store the model in our dictionary
    dynamic_models[table_name] = DynamicModel
    
    # Create the table in the database if it doesn't exist
    if not engine.dialect.has_table(engine.connect(), table_name):
        Base.metadata.create_all(bind=engine, tables=[DynamicModel.__table__])
        logger.info(f"Created table {table_name} in the database")
    
    return DynamicModel

def initialize_db():
    """
    Initialize the database by creating all tables.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized") 