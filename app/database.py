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
    Dependency for FastAPI to get a database session.
    
    Yields:
        A database session that is automatically closed when the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_dynamic_table(template_name: str, component_fields: Dict[str, Any]):
    """
    Creates a dynamic SQLAlchemy model and table for a template.
    
    Args:
        template_name: The name of the template.
        component_fields: A dictionary of component fields.
        
    Returns:
        A SQLAlchemy model class for the template.
    """
    # Create a table name from the template name
    table_name = f"{template_name.lower()}_submissions"
    
    logger.info(f"Creating dynamic table: {table_name}")
    
    # Define a dynamic model class
    class DynamicModel(Base):
        __tablename__ = table_name
        
        id = Column(Integer, primary_key=True, index=True)
        submission_id = Column(String, unique=True, index=True)
        data = Column(JSON)  # Store the entire form data as JSON
        
        def __repr__(self):
            return f"<{template_name.capitalize()}Submission(id={self.id}, submission_id={self.submission_id})>"
    
    # Create the table if it doesn't exist
    if not engine.dialect.has_table(engine, table_name):
        DynamicModel.__table__.create(bind=engine)
        logger.info(f"Created table: {table_name}")
    
    return DynamicModel

def initialize_db():
    """
    Initializes the database by creating all tables.
    """
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise 