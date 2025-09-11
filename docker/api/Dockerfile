FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy application code
COPY . .

# Create directories for generated content
RUN mkdir -p /app/generated-bots /app/templates /app/logs /app/tmp

# Set proper permissions
RUN chown -R 1000:1000 /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
CMD ["start"]
