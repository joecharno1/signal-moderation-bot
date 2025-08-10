FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
        curl \
            && rm -rf /var/lib/apt/lists/*

            # Copy requirements and install Python dependencies
            COPY requirements.txt .
            RUN pip install --no-cache-dir -r requirements.txt

            # Copy application files
            COPY signal_service.py .
            COPY app.py .
            COPY templates/ templates/

            # Copy signal-cli data
            COPY signal-cli-data/ /home/.local/share/signal-cli/

            # Create logs directory
            RUN mkdir -p /app/logs

            # Expose port
            EXPOSE 5000

            # Health check
            HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
                CMD curl -f http://localhost:5000/health || exit 1

                # Run the application
                CMD ["python", "app.py"]
