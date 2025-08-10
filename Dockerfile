FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Java for Signal-CLI
RUN apt-get update && apt-get install -y \
    sqlite3 \
        curl \
            wget \
                openjdk-17-jre-headless \
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

                    # Download signal-cli-rest-api JAR
                    RUN wget -O /app/signal-cli-rest-api.jar \
                        https://github.com/bbernhard/signal-cli-rest-api/releases/download/0.94/signal-cli-rest-api-0.94-fat.jar

                        # Create startup script that runs both services
                        RUN echo '#!/bin/bash\n\
                        set -e\n\
                        \n\
                        echo "Starting Signal-CLI REST API..."\n\
                        java -jar /app/signal-cli-rest-api.jar \\\n\
                          --signal-cli-config-dir=/home/.local/share/signal-cli \\\n\
                            --server.port=8080 \\\n\
                              --logging.level.root=INFO &\n\
                              \n\
                              echo "Waiting for Signal-CLI to be ready..."\n\
                              for i in {1..30}; do\n\
                                if curl -f http://localhost:8080/v1/about >/dev/null 2>&1; then\n\
                                    echo "Signal-CLI is ready!"\n\
                                        break\n\
                                          fi\n\
                                            echo "Waiting for Signal-CLI... ($i/30)"\n\
                                              sleep 2\n\
                                              done\n\
                                              \n\
                                              echo "Starting Flask app..."\n\
                                              export SIGNAL_API_URL=http://localhost:8080\n\
                                              export DATABASE_PATH=/home/.local/share/signal-cli/data/+15614121835.d/account.db\n\
                                              python app.py\n\
                                              ' > /app/start.sh && chmod +x /app/start.sh

                                              # Set proper permissions for signal-cli data
                                              RUN chmod -R 755 /home/.local/share/signal-cli

                                              # Expose ports
                                              EXPOSE 5000 8080

                                              # Health check
                                              HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
                                                  CMD curl -f http://localhost:5000/health || exit 1

                                                  # Start both services
                                                  CMD ["./start.sh"]
