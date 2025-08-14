# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy SSL certificates
COPY certs/bundle.pem /certs/bundle.pem

# Set SSL certificate environment variables
ENV REQUESTS_CA_BUNDLE="/certs/bundle.pem"
ENV SSL_CERT_FILE="/certs/bundle.pem"
ENV CURL_CA_BUNDLE="/certs/bundle.pem"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"] 