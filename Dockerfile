# Use official Python 3.9 image
FROM python:3.9-slim

# Install system dependencies for the judge engine (g++, gcc, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port (FastAPI default)
EXPOSE 8000

# Command to run the application
# We use uvicorn with host 0.0.0.0 to make it accessible inside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
