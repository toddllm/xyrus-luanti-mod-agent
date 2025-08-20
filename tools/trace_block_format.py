#!/usr/bin/env python3
"""
Trace through block format byte by byte
"""

import struct
import sqlite3
import zstandard as zstd

def trace_block(data_blob):
    """Trace through block format step by step"""
    
    print(f"Compressed block size: {len(data_blob)} bytes")
    print(f"Version byte: {data_blob[0]}")
    
    # Decompress
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(data_blob[1:], max_output_size=65536)
    print(f"Decompressed size: {len(decompressed)} bytes")
    
    pos = 0
    print("\n--- Tracing decompressed data ---")
    
    # 1. Flags
    flags = decompressed[pos]
    print(f"Pos {pos}: Flags = 0x{flags:02x}")
    pos += 1
    
    # 2. Lighting complete (u16 big-endian)  
    lighting = struct.unpack('>H', decompressed[pos:pos+2])[0]
    print(f"Pos {pos}: Lighting complete = 0x{lighting:04x}")
    pos += 2
    
    # 3. Timestamp (u32 big-endian)
    timestamp = struct.unpack('>I', decompressed[pos:pos+4])[0]
    print(f"Pos {pos}: Timestamp = {timestamp}")
    pos += 4
    
    # 4. NameIdMapping
    print(f"\nPos {pos}: Start of NameIdMapping")
    print(f"  Next 20 bytes: {list(decompressed[pos:pos+20])}")
    
    # NameIdMapping starts with count (u16)
    num_mappings = struct.unpack('>H', decompressed[pos:pos+2])[0]
    print(f"  Number of mappings: {num_mappings}")
    pos += 2
    
    # Each mapping is: u16 id, u16 namelen, name
    for i in range(min(num_mappings, 5)):  # Show first 5
        if pos + 2 > len(decompressed):
            break
        node_id = struct.unpack('>H', decompressed[pos:pos+2])[0]
        pos += 2
        
        if pos + 2 > len(decompressed):
            break
        name_len = struct.unpack('>H', decompressed[pos:pos+2])[0]
        pos += 2
        
        if pos + name_len > len(decompressed):
            break
        name = decompressed[pos:pos+name_len].decode('utf-8', errors='replace')
        pos += name_len
        
        print(f"  Mapping {i}: ID {node_id} → '{name}'")
    
    if num_mappings > 5:
        # Skip remaining mappings
        for i in range(5, num_mappings):
            if pos + 2 > len(decompressed):
                break
            node_id = struct.unpack('>H', decompressed[pos:pos+2])[0]
            pos += 2
            
            if pos + 2 > len(decompressed):
                break
            name_len = struct.unpack('>H', decompressed[pos:pos+2])[0]
            pos += 2
            pos += name_len
    
    print(f"\nPos {pos}: After NameIdMapping")
    print(f"  Next 10 bytes: {list(decompressed[pos:pos+10])}")
    
    # 5. Content width and params width
    if pos + 2 <= len(decompressed):
        content_width = decompressed[pos]
        params_width = decompressed[pos + 1]
        print(f"  Content width: {content_width}")
        print(f"  Params width: {params_width}")
        pos += 2
        
        # Calculate expected node data size
        node_data_size = 4096 * (content_width + params_width)
        print(f"\nExpected node data: {node_data_size} bytes")
        print(f"Remaining in buffer: {len(decompressed) - pos} bytes")
        
        # Sample first few nodes
        print("\nFirst few nodes:")
        bytes_per_node = content_width + params_width
        for i in range(min(5, 4096)):
            if pos + bytes_per_node > len(decompressed):
                break
            node_data = decompressed[pos:pos+bytes_per_node]
            if content_width == 2:
                content_id = struct.unpack('>H', node_data[0:2])[0]
            else:
                content_id = node_data[0]
            param1 = node_data[content_width]
            param2 = node_data[content_width + 1]
            print(f"  Node {i}: content_id={content_id}, param1={param1}, param2={param2}")
            pos += bytes_per_node

# Main
db_path = "/var/games/minetest-server/.minetest/worlds/world/map.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get a specific interesting block
cursor.execute("""
    SELECT pos, data 
    FROM blocks 
    WHERE length(data) BETWEEN 400 AND 800
    ORDER BY RANDOM()
    LIMIT 1
""")

pos_int, data_blob = cursor.fetchone()
conn.close()

x = (pos_int & 0xfff) - 2048
y = ((pos_int >> 12) & 0xfff) - 2048  
z = ((pos_int >> 24) & 0xfff) - 2048

print(f"Analyzing block at ({x}, {y}, {z})")
print("="*50)
trace_block(data_blob)