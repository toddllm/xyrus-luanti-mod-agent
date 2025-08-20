#!/bin/bash
# Monitor signs_fix activity in real-time

echo "=== Monitoring signs_fix activity ==="
echo "Watching: /home/tdeshane/luanti/devkorth_test_server.log"
echo "Press Ctrl+C to stop"
echo ""
echo "Waiting for activity..."
echo "================================"

tail -f /home/tdeshane/luanti/devkorth_test_server.log | grep --line-buffered -E "\[signs_fix\]|SignTester|testsign|on_receive_fields|update_sign_text|Entity"