# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if needed)
# RUN apt-get update && apt-get install -y \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p audio exports

# Expose port
EXPOSE 8001

# Run with uvicorn
