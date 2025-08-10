# Signal Moderation Bot - Complete Solution
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    openjdk-17-jre-headless \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install signal-cli-rest-api
RUN wget -O /tmp/signal-cli-rest-api.tar.gz \
    https://github.com/bbernhard/signal-cli-rest-api/releases/latest/download/signal-cli-rest-api-0.74-linux-amd64.tar.gz \
    && tar -xzf /tmp/signal-cli-rest-api.tar.gz -C /opt/ \
    && ln -s /opt/signal-cli-rest-api /usr/local/bin/signal-cli-rest-api \
    && rm /tmp/signal-cli-rest-api.tar.gz

# Set up Python environment
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY signal_service.py .
COPY templates/ ./templates/

# Create signal-cli data directory and copy data
RUN mkdir -p /home/.local/share/signal-cli
COPY signal-cli-data/ /home/.local/share/signal-cli/

# Set proper permissions
RUN chown -R 1000:1000 /home/.local/share/signal-cli
RUN chmod -R 755 /home/.local/share/signal-cli

# Create startup script
COPY start.sh .
RUN chmod +x start.sh

# Expose ports
EXPOSE 8080 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start both signal-cli-rest-api and web interface
CMD ["./start.sh"]

