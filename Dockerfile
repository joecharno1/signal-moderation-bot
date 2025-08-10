# Signal Moderation Bot - Working Solution
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
        wget \
            openjdk-17-jre-headless \
                && rm -rf /var/lib/apt/lists/*

                # Set up Python environment
                WORKDIR /app
                COPY requirements.txt .
                RUN pip install --no-cache-dir -r requirements.txt

                # Copy application files
                COPY app.py .
                COPY signal_service.py .
                COPY templates/ ./templates/

                # Copy working signal-cli data
                COPY signal-cli-data/ /home/.local/share/signal-cli/

                # Set proper permissions
                RUN chmod -R 755 /home/.local/share/signal-cli

                # Install signal-cli-rest-api using working JAR file
                RUN wget -O /tmp/signal-cli-rest-api.jar \
                    https://github.com/bbernhard/signal-cli-rest-api/releases/download/0.94/signal-cli-rest-api-0.94-fat.jar

                    # Copy startup script
                    COPY start.sh .
                    RUN chmod +x start.sh

                    # Expose ports
                    EXPOSE 5000 8080

                    # Set environment variables
                    ENV SIGNAL_CLI_CONFIG_DIR=/home/.local/share/signal-cli
                    ENV PORT=5000

                    # Start the application
                    CMD ["./start.sh"]
