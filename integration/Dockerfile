FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY integration_api.py .
COPY server_allocation_adapter.py .
COPY lab_utilization_adapter.py .
COPY .env .

# Run the application
CMD ["python", "integration_api.py"]