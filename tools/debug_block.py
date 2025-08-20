#!/usr/bin/env python3
"""Debug a single block"""

import sqlite3

db_path = "/var/games/minetest-server/.minetest/worlds/world/map.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get a small block
cursor.execute("SELECT pos, data, LENGTH(data) FROM blocks WHERE LENGTH(data) < 100 LIMIT 1")
pos, data, length = cursor.fetchone()

print(f"Block pos: {pos}")
print(f"Block size: {length} bytes")
print(f"First 32 bytes (hex): {data[:32].hex()}")
print(f"First 32 bytes (raw): {data[:32]}")

# Check each position for ZSTD magic
for i in range(min(10, len(data)-4)):
    chunk = data[i:i+4]
    if chunk == b'\x28\xb5\x2f\xfd':
        print(f"Found ZSTD magic at position {i}")

# Try to find "air" string
if b'air' in data:
    idx = data.index(b'air')
    print(f"Found 'air' at position {idx}")
    print(f"Context: {data[max(0,idx-10):idx+10].hex()}")

conn.close()