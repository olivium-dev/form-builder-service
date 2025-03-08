# Form Builder Microservice

A dynamic, configuration-driven form builder service built with FastAPI and Pydantic.

## Overview

This microservice dynamically creates Pydantic models and RESTful endpoints based on JSON configuration files:
- `components_config.json`: Defines individual UI components with their attributes
- `templates.json`: Defines form templates with their component configurations

The service automatically generates OpenAPI (Swagger) documentation for all endpoints.

## Project Structure

```
form-builder-microservice/
├── app/
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration loader for JSON files
│   ├── models.py           # Dynamic model generation for components and templates
│   ├── endpoints.py        # Endpoint factory functions for POST/GET handlers
│   └── main.py             # Main application file; loads configs, registers endpoints
├── components_config.json  # JSON file defining UI components
├── templates.json          # JSON file defining form templates with component configurations
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Service

```
python -m app.main
```

The service will be available at http://localhost:8000

## API Documentation

Once the service is running, you can access the Swagger UI documentation at:
http://localhost:8000/docs

## Configuration

### Components Configuration

The `components_config.json` file defines UI components with their attributes, style, and validations.

### Templates Configuration

The `templates.json` file defines form templates as collections of component configurations.

## Adding New Components or Templates

1. To add a new component, add its definition to `components_config.json`
2. To create a new form template, add an entry to `templates.json` with component configurations
3. Restart the service to apply changes

## License

MIT 