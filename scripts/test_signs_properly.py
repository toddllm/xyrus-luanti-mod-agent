#!/usr/bin/env python3
"""
Proper test for signs_fix mod using working UDPLuantiConnection
Joins the game properly before sending commands
"""

import asyncio
import logging
import sys
import os

# Add luanti_voyager to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'luanti-voyager'))

from luanti_voyager import UDPLuantiConnection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_signs():
    """Test signs_fix mod with proper connection"""
    
    # Connect to test server on port 50000 (no password required)
    conn = UDPLuantiConnection(
        host='localhost',
        port=50000,
        username='SignBot',
        password=''  # Empty password for test server
    )
    
    try:
        logging.info("Connecting to test server on port 50000...")
        await conn.connect()
        logging.info(f"Connected successfully! Peer ID: {conn.peer_id}")
        
        # Wait a moment for connection to stabilize
        await asyncio.sleep(2)
        
        # Send initial greeting
        await conn.send_chat_message("SignBot connected for testing signs_fix mod")
        await asyncio.sleep(1)
        
        # Test the /testsign command
        logging.info("Testing /testsign command...")
        await conn.send_chat_message("/testsign 0 5 0 Hello from SignBot")
        await asyncio.sleep(1)
        
        # Test multiple signs
        test_positions = [
            (0, 5, 0, "Test Sign 1"),
            (2, 5, 0, "Test Sign 2"),
            (4, 5, 0, "Multi\\nLine\\nSign"),
            (-2, 5, 0, "Special !@#$%"),
        ]
        
        for x, y, z, text in test_positions:
            logging.info(f"Placing sign at ({x}, {y}, {z}) with text: {text}")
            await conn.send_chat_message(f"/testsign {x} {y} {z} {text}")
            await asyncio.sleep(1)
        
        # Try to interact with a sign (right-click)
        logging.info("Attempting to interact with sign at (0, 5, 0)...")
        # Note: This would need proper packet construction for interaction
        # For now just test the command interface
        
        # Report completion
        await conn.send_chat_message("SignBot testing complete - check server logs for [signs_fix] activity")
        logging.info("Test complete! Check server logs for [signs_fix] messages")
        
        # Keep connection alive briefly to see results
        await asyncio.sleep(3)
        
    except Exception as e:
        logging.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logging.info("Disconnecting...")
        await conn.disconnect()

if __name__ == "__main__":
    asyncio.run(test_signs())