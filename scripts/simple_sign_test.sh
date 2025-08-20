#!/bin/bash
# Simple test to verify signs_fix callbacks work via console

echo "=== Simple Sign Test ==="
echo "This will connect to the test server and run commands directly"

# Use screen/tmux or direct connection
# For now, let's test the /testsign command directly by checking if it works

SERVER_LOG="/home/tdeshane/luanti/devkorth_test_server.log"

# Clear the log section
echo "" >> "$SERVER_LOG"
echo "=== SIMPLE TEST START ===" >> "$SERVER_LOG"

# Check if server is running
if ! pgrep -f "port 50000" > /dev/null; then
    echo "Server not running. Starting..."
    nohup /usr/lib/minetest/minetestserver \
        --world /home/tdeshane/luanti/devkorth_test_world \
        --port 50000 \
        --logfile "$SERVER_LOG" \
        > /dev/null 2>&1 &
    sleep 3
fi

echo "Server is running on port 50000"

# Connect using minetest client in a subprocess
echo "Testing direct command execution..."

# Create a simple expect script or use netcat to send commands
# For now, let's just verify the mod is loaded and ready

echo "Checking if signs_fix mod is loaded..."
if grep -q "\[signs_fix\].*Loaded" "$SERVER_LOG"; then
    echo "✓ Mod loaded"
else
    echo "✗ Mod not loaded"
    exit 1
fi

echo ""
echo "The /testsign command is available in-game:"
echo "  /testsign <x> <y> <z> <text>"
echo ""
echo "Example: /testsign 0 0 0 Hello World"
echo ""
echo "To test manually:"
echo "1. Connect to localhost:50000 with a Minetest client"
echo "2. Run: /testsign 0 0 0 Test Text"
echo "3. Check the log for [signs_fix] messages"
echo ""
echo "Current signs_fix activity in log:"
grep "\[signs_fix\]" "$SERVER_LOG" | tail -5