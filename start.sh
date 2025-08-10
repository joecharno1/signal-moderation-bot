#!/bin/bash

# Start signal-cli-rest-api in background
signal-cli-rest-api \
  -signal-cli-config /home/.local/share/signal-cli \
  -host 0.0.0.0 \
  -port 8080 \
  -mode json-rpc &

# Wait for signal-cli to start
sleep 5

# Start Flask web interface
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app

