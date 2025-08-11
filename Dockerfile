FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Java for signal-cli-rest-api
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    wget \
    supervisor \
    openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Download and setup signal-cli-rest-api JAR (use a working version)
RUN mkdir -p /opt/signal-cli-rest-api && \
    cd /opt/signal-cli-rest-api && \
    wget -O signal-cli-rest-api.jar https://github.com/bbernhard/signal-cli-rest-api/releases/download/0.93/signal-cli-rest-api-0.93-fat.jar

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt requests

# Copy application files
COPY app.py .
COPY templates/ templates/

# Copy signal-cli data to the correct location
COPY signal-cli-data/ /home/.local/share/signal-cli/

# Set proper permissions for signal-cli data
RUN chmod -R 755 /home/.local/share/signal-cli

# Create logs directory
RUN mkdir -p /app/logs

# Create supervisor configuration to run both services
RUN echo '[supervisord]' > /etc/supervisor/conf.d/supervisord.conf && \
    echo 'nodaemon=true' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo '' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo '[program:signal-cli-rest-api]' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'command=java -jar /opt/signal-cli-rest-api/signal-cli-rest-api.jar' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'directory=/opt/signal-cli-rest-api' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'environment=MODE=json-rpc,GIN_MODE=release,PORT=8080' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'stdout_logfile=/var/log/signal-cli-rest-api.log' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'stderr_logfile=/var/log/signal-cli-rest-api.log' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo '' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo '[program:flask-app]' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'command=python app.py' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'directory=/app' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'environment=PORT=5000' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'stdout_logfile=/var/log/flask-app.log' >> /etc/supervisor/conf.d/supervisord.conf && \
    echo 'stderr_logfile=/var/log/flask-app.log' >> /etc/supervisor/conf.d/supervisord.conf

# Expose ports (Railway will use 8080 for external access)
EXPOSE 8080 5000

# Health check for signal-cli-rest-api
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/v1/about || exit 1

# Start both services with supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

