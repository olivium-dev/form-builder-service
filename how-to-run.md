# How to Run the Form Builder Microservice

This document provides step-by-step instructions for setting up and running the Form Builder Microservice.

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/olivium-dev/form-builder-service.git
cd form-builder-service
```

### 2. Set Up a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory with the following content (adjust as needed):

```
DATABASE_URL=postgresql+psycopg2://postgres:newpassword@db-alrahma.cnism90ipjjx.us-east-2.rds.amazonaws.com:5432/formbuilder?sslmode=require
ROOT_PATH=/formbuilder
```

You can copy from the `.env.example` file if needed:

```bash
cp .env.example .env
# Then edit the .env file with your specific database credentials
```

### 5. Run the Application

```bash
# Run the application with uvicorn
python -m app.main --host 0.0.0.0 --port 8000
```

### 6. Access the Application

- Local development: http://localhost:8000
- Swagger UI documentation: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## Docker Setup

If you prefer to use Docker:

### 1. Build the Docker Image

```bash
docker build -t form-builder .
```

### 2. Run the Docker Container

```bash
docker run -d -p 8000:8000 --name form-builder-container \
  -e DATABASE_URL="postgresql+psycopg2://postgres:newpassword@db-alrahma.cnism90ipjjx.us-east-2.rds.amazonaws.com:5432/formbuilder?sslmode=require" \
  -e ROOT_PATH="/formbuilder" \
  form-builder
```

### 3. Access the Dockerized Application

- Local development: http://localhost:8000
- Swagger UI documentation: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## Deployment to Production

For deployment to the production server, you can use the GitHub workflow:

1. Push your changes to the GitHub repository
2. Go to the GitHub repository's Actions tab
3. Run the "Deploy to EC2 (RAHMAH)" workflow manually

The deployed service will be available at: https://al-rahmah.com/formbuilder/

## API Documentation

Once the service is running, you can access the Swagger UI documentation at:
- Local: http://localhost:8000/docs
- Production: https://al-rahmah.com/formbuilder/docs

## Configuration Files

The service is configured using two main JSON files:

1. `components_config.json`: Defines individual UI components with their attributes
2. `templates.json`: Defines form templates with their component configurations

## Troubleshooting

### Swagger UI Not Loading

If the Swagger UI is not loading correctly, ensure that:
- The `ROOT_PATH` environment variable is set correctly
- The service is running and accessible
- You're using the correct URL for the documentation

### Database Connection Issues

If you encounter database connection issues:
- Verify that the `DATABASE_URL` in your `.env` file is correct
- Ensure that the database server is running and accessible
- Check that the database user has the necessary permissions 