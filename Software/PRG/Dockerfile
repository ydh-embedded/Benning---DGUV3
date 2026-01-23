FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_hexagon.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_hexagon.txt

# Copy application
COPY src/ src/
COPY .env .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "src/main.py"]
