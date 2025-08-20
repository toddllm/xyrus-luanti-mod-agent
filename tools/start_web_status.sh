#!/bin/bash

# Start the Luanti server status web interface

echo "Starting Luanti Server Status Web Interface..."
echo "========================================"
echo
echo "The web interface will be available at:"
echo "  http://localhost:8080/"
echo "  http://$(hostname -I | awk '{print $1}'):8080/"
echo
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not installed"
    exit 1
fi

# Start the server
cd /home/tdeshane/luanti
python3 serve_status.py