FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV DATABASE_URL=postgresql+psycopg2://postgres:newpassword@db-alrahma.cnism90ipjjx.us-east-2.rds.amazonaws.com:5432/formbuilder?sslmode=require

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "app.main", "--host", "0.0.0.0", "--port", "8000"] 