#!/bin/bash

# Xyrus Standalone Startup Script

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set environment variables
export HOST="0.0.0.0"
export PORT="8088"

# Kill any existing process on port 8088
lsof -ti:8088 | xargs -r kill -9 2>/dev/null

echo "Starting Xyrus Mod Agent on http://localhost:8088"
echo "Admin panel: http://localhost:8088/admin"

# Start the application
python app.py