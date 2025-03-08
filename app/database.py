import logging
import os
import json
from typing import Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, JSON, MetaData, Table
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

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()

# Dictionary to store dynamic models
dynamic_tables = {}

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

def create_dynamic_table(template_name: str):
    """
    Creates a dynamic SQLAlchemy table for a template.
    
    Args:
        template_name: The name of the template.
        
    Returns:
        A SQLAlchemy Table object for the template.
    """
    # Create a table name from the template name
    table_name = f"{template_name.lower()}_submissions"
    
    # Check if table already exists in our dictionary
    if table_name in dynamic_tables:
        return dynamic_tables[table_name]
    
    logger.info(f"Creating dynamic table: {table_name}")
    
    # Create a table
    table = Table(
        table_name,
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('submission_id', String, unique=True, index=True),
        Column('data', JSON),
        extend_existing=True
    )
    
    # Store the table in our dictionary
    dynamic_tables[table_name] = table
    
    # Create the table if it doesn't exist
    if not engine.dialect.has_table(engine, table_name):
        table.create(bind=engine)
        logger.info(f"Created table: {table_name}")
    
    return table

def initialize_db():
    """
    Initializes the database by creating all tables.
    """
    try:
        # Load templates from templates.json
        with open("templates.json", "r") as f:
            templates_data = json.load(f)
        
        # Create tables for each template
        for template_name in templates_data.keys():
            create_dynamic_table(template_name)
        
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise 