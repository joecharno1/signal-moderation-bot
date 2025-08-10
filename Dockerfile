FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Java for signal-cli
RUN apt-get update && apt-get install -y \
    sqlite3 \
        curl \
            wget \
                supervisor \
                    openjdk-17-jre-headless \
                        && rm -rf /var/lib/apt/lists/*

                        # Download signal-cli (not the REST API wrapper, but the actual signal-cli)
                        RUN wget -O /tmp/signal-cli.tar.gz \
                            https://github.com/AsamK/signal-cli/releases/download/v0.13.18/signal-cli-0.13.18-Linux.tar.gz && \
                                tar -xzf /tmp/signal-cli.tar.gz -C /opt && \
                                    mv /opt/signal-cli-* /opt/signal-cli && \
                                        rm /tmp/signal-cli.tar.gz

                                        # Copy requirements and install Python dependencies
                                        COPY requirements.txt .
                                        RUN pip install --no-cache-dir -r requirements.txt

                                        # Copy application files
                                        COPY signal_service.py .
                                        COPY app.py .
                                        COPY templates/ templates/

                                        # Copy signal-cli data to the correct location
                                        COPY signal-cli-data/ /home/.local/share/signal-cli/

                                        # Create a simple startup script
                                        RUN echo '#!/bin/bash' > /app/start.sh && \
                                            echo 'cd /app' >> /app/start.sh && \
                                                echo 'export SIGNAL_CLI_CONFIG_DIR=/home/.local/share/signal-cli' >> /app/start.sh && \
                                                    echo 'export PORT=${PORT:-8080}' >> /app/start.sh && \
                                                        echo 'python app.py &' >> /app/start.sh && \
                                                            echo 'wait' >> /app/start.sh && \
                                                                chmod +x /app/start.sh

                                                                # Create logs directory
                                                                RUN mkdir -p /app/logs /var/log

                                                                # Set proper permissions for signal-cli data
                                                                RUN chmod -R 755 /home/.local/share/signal-cli

                                                                # Expose port
                                                                EXPOSE 8080

                                                                # Health check
                                                                HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
                                                                    CMD curl -f http://localhost:8080/health || exit 1

                                                                    # Start the application
                                                                    CMD ["/app/start.sh"]
