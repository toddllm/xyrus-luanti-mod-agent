#!/bin/bash
# Complete signs testing script with proper server management

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LUANTI_DIR="/home/tdeshane/luanti"
TEST_PORT=50000
LOG_FILE="$LUANTI_DIR/devkorth_test_server.log"

echo "=== Signs Fix Complete Test Script ==="
echo "Starting at $(date)"

# Function to stop test server
stop_test_server() {
    echo "Stopping test server on port $TEST_PORT..."
    pkill -f "port $TEST_PORT" 2>/dev/null
    sleep 2
}

# Function to start test server
start_test_server() {
    echo "Starting test server on port $TEST_PORT..."
    cd "$LUANTI_DIR"
    
    # Clear old log
    > "$LOG_FILE"
    
    # Start server in background with world's config
    nohup /usr/lib/minetest/minetestserver \
        --world "$LUANTI_DIR/devkorth_test_world" \
        --config "$LUANTI_DIR/devkorth_test_world/minetest.conf" \
        --logfile "$LOG_FILE" \
        > /dev/null 2>&1 &
    
    # Wait for server to start
    echo "Waiting for server to start..."
    for i in {1..10}; do
        if grep -q "listening on" "$LOG_FILE" 2>/dev/null; then
            echo "Server started successfully!"
            return 0
        fi
        sleep 1
    done
    
    echo "Warning: Server may not have started properly"
    return 1
}

# Function to check if signs_fix loaded
check_mod_loaded() {
    echo "Checking if signs_fix mod loaded..."
    if grep -q "\[signs_fix\].*Loaded" "$LOG_FILE"; then
        echo "✓ signs_fix mod loaded successfully"
        grep "\[signs_fix\]" "$LOG_FILE" | tail -5
        return 0
    else
        echo "✗ signs_fix mod not found in logs"
        return 1
    fi
}

# Function to run automation test
run_automation() {
    echo "Running automation test..."
    cd "$LUANTI_DIR/luanti-voyager/scripts"
    python3 test_sign_50000.py 2>&1 | tee "$SCRIPT_DIR/automation_output.txt"
    
    # Check if test completed
    if grep -q "Test completed" "$SCRIPT_DIR/automation_output.txt"; then
        echo "✓ Automation test completed"
        return 0
    else
        echo "✗ Automation test may have failed"
        return 1
    fi
}

# Function to check results
check_results() {
    echo "Checking test results in server log..."
    echo "Signs_fix activity:"
    grep -E "\[signs_fix\].*update_sign_text|on_receive_fields|Entity|texture" "$LOG_FILE" | tail -20
    
    # Count important events
    local callbacks=$(grep -c "on_receive_fields" "$LOG_FILE")
    local updates=$(grep -c "update_sign_text" "$LOG_FILE")
    local entities=$(grep -c "Entity created" "$LOG_FILE")
    
    echo ""
    echo "Summary:"
    echo "  Callbacks triggered: $callbacks"
    echo "  Sign updates: $updates"
    echo "  Entities created: $entities"
    
    if [ "$callbacks" -gt 0 ] && [ "$updates" -gt 0 ]; then
        echo "✓ Test PASSED - callbacks and updates detected"
        return 0
    else
        echo "✗ Test FAILED - no sign activity detected"
        return 1
    fi
}

# Main execution
echo ""
echo "Step 1: Stop any existing test server"
stop_test_server

echo ""
echo "Step 2: Start fresh test server"
if ! start_test_server; then
    echo "Failed to start server"
    exit 1
fi

echo ""
echo "Step 3: Verify mod loaded"
if ! check_mod_loaded; then
    echo "Mod loading issue detected"
fi

echo ""
echo "Step 4: Run automation test"
if ! run_automation; then
    echo "Automation may have issues"
fi

echo ""
echo "Step 5: Check results"
sleep 2  # Give time for logs to flush
check_results

echo ""
echo "=== Test Complete at $(date) ==="
echo "Full log available at: $LOG_FILE"
echo ""
echo "To view live logs: tail -f $LOG_FILE | grep signs_fix"