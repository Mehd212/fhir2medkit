# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for pdfminer and cryptography
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY fhir2medkit.py .
COPY test.py .
COPY example/ ./example/

# Set Python path to include current directory
ENV PYTHONPATH=/app

# Default command to run tests
CMD ["python", "test.py"]