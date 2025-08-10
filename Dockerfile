FROM bbernhard/signal-cli-rest-api:latest as signal-cli

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Java for signal-cli
RUN apt-get update && apt-get install -y \
    sqlite3 \
        curl \
            supervisor \
                openjdk-17-jre-headless \
                    && rm -rf /var/lib/apt/lists/*

                    # Copy signal-cli from the official image
                    COPY --from=signal-cli /app /opt/signal-cli-rest-api

                    # Copy requirements and install Python dependencies
                    COPY requirements.txt .
                    RUN pip install --no-cache-dir -r requirements.txt

                    # Copy application files
                    COPY signal_service.py .
                    COPY app.py .
                    COPY templates/ templates/

                    # Copy signal-cli data to the correct location
                    COPY signal-cli-data/ /home/.local/share/signal-cli/

                    # Create supervisor configuration
                    RUN echo '[supervisord]' > /etc/supervisor/conf.d/supervisord.conf && \
                        echo 'nodaemon=true' >> /etc/supervisor/conf.d/supervisord.conf && \
                            echo '' >> /etc/supervisor/conf.d/supervisord.conf && \
                                echo '[program:signal-cli]' >> /etc/supervisor/conf.d/supervisord.conf && \
                                    echo 'command=java -jar /opt/signal-cli-rest-api/signal-cli-rest-api.jar --signal-cli-config-dir=/home/.local/share/signal-cli --server.port=8081' >> /etc/supervisor/conf.d/supervisord.conf && \
                                        echo 'autostart=true' >> /etc/supervisor/conf.d/supervisord.conf && \
                                            echo 'autorestart=true' >> /etc/supervisor/conf.d/supervisord.conf && \
                                                echo 'stderr_logfile=/var/log/signal-cli.err.log' >> /etc/supervisor/conf.d/supervisord.conf && \
                                                    echo 'stdout_logfile=/var/log/signal-cli.out.log' >> /etc/supervisor/conf.d/supervisord.conf && \
                                                        echo '' >> /etc/supervisor/conf.d/supervisord.conf && \
                                                            echo '[program:flask-app]' >> /etc/supervisor/conf.d/supervisord.conf && \
                                                                echo 'command=python app.py' >> /etc/supervisor/conf.d/supervisord.conf && \
                                                                    echo 'directory=/app' >> /etc/supervisor/conf.d/supervisord.conf && \
                                                                        echo 'autostart=true' >> /etc/supervisor/conf.d/supervisord.conf && \
                                                                            echo 'autorestart=true' >> /etc/supervisor/conf.d/supervisord.conf && \
                                                                                echo 'environment=SIGNAL_API_URL="http://localhost:8081",PORT="8080"' >> /etc/supervisor/conf.d/supervisord.conf && \
                                                                                    echo 'stderr_logfile=/var/log/flask-app.err.log' >> /etc/supervisor/conf.d/supervisord.conf && \
                                                                                        echo 'stdout_logfile=/var/log/flask-app.out.log' >> /etc/supervisor/conf.d/supervisord.conf

                                                                                        # Create logs directory
                                                                                        RUN mkdir -p /app/logs /var/log

                                                                                        # Set proper permissions for signal-cli data
                                                                                        RUN chmod -R 755 /home/.local/share/signal-cli

                                                                                        # Expose port
                                                                                        EXPOSE 8080

                                                                                        # Health check
                                                                                        HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
                                                                                            CMD curl -f http://localhost:8080/health || exit 1

                                                                                            # Start supervisor to manage both services
                                                                                            CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
