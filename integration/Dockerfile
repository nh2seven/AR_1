FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default to port 8007 if not specified
ENV INTEGRATION_API_PORT=8007

# Expose the port
EXPOSE ${INTEGRATION_API_PORT}

# Run the API server
CMD ["python", "integration_api.py"]