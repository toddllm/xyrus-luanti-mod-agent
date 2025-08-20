#!/usr/bin/env python3
"""
Concrete example of decoding a Luanti/Minetest MapBlock from the database
This shows the exact binary format and how node types are mapped
"""

import struct
import sqlite3
import zstandard as zstd
from io import BytesIO

def decode_mapblock_position(pos_int):
    """Decode the integer position to (x,y,z) coordinates"""
    # SQLite stores position as a single 64-bit integer
    # Decode according to Minetest's getBlockAsInteger function
    x = (pos_int & 0xfff) - 2048
    y = ((pos_int >> 12) & 0xfff) - 2048  
    z = ((pos_int >> 24) & 0xfff) - 2048
    return x, y, z

def read_string16(stream):
    """Read a 16-bit length-prefixed string"""
    length = struct.unpack('>H', stream.read(2))[0]
    return stream.read(length).decode('utf-8')

def decode_compressed_block(data_blob):
    """Decode a ZSTD-compressed MapBlock and show its structure"""
    # Version 29+ uses ZSTD compression
    
    # First byte should be version (29 or higher)
    version = data_blob[0]
    print(f"Block format version: {version}")
    
    if version >= 29:
        # The entire blob (including version byte) is fed to decompressor as a stream
        # This matches the C++ code which reads the stream progressively
        try:
            dctx = zstd.ZstdDecompressor()
            # Create a stream from the data after version byte
            compressed_stream = BytesIO(data_blob[1:])
            reader = dctx.stream_reader(compressed_stream)
            
            # Read all decompressed data
            decompressed = reader.read()
            stream = BytesIO(decompressed)
        except Exception as e:
            print(f"ZSTD decompression failed: {e}")
            # Try alternative: decompress the whole thing
            dctx = zstd.ZstdDecompressor()
            decompressed = dctx.decompress(data_blob[1:])
            stream = BytesIO(decompressed)
        
        # Read the actual data version (post-compression)
        data_version = struct.unpack('B', stream.read(1))[0]
        print(f"Data version: {data_version}")
        
        # Read block flags
        flags = struct.unpack('B', stream.read(1))[0]
        is_underground = bool(flags & 0x01)
        print(f"Is underground: {is_underground}")
        
        # Read lighting info
        lighting_complete = struct.unpack('>H', stream.read(2))[0]
        print(f"Lighting complete: 0x{lighting_complete:04x}")
        
        # Read content width and param width
        content_width = struct.unpack('B', stream.read(1))[0]
        param_width = struct.unpack('B', stream.read(1))[0]
        print(f"Content width: {content_width} bytes, Param width: {param_width} bytes")
        
        # Read NameIdMapping
        print("\n=== NameIdMapping ===")
        name_id_map = {}
        
        # Version 29+ has different format
        if data_version >= 29:
            # Read number of mappings
            num_mappings = struct.unpack('>H', stream.read(2))[0]
            print(f"Number of node types in this block: {num_mappings}")
            
            for i in range(num_mappings):
                node_id = struct.unpack('>H', stream.read(2))[0]
                node_name = read_string16(stream)
                name_id_map[node_id] = node_name
                print(f"  {node_id:3d} → {node_name}")
        
        # Read node data (4096 nodes = 16x16x16)
        print("\n=== Node Data ===")
        nodes = []
        node_counts = {}
        
        for i in range(4096):
            # Read content ID (2 bytes for content_width=2)
            if content_width == 2:
                content_id = struct.unpack('>H', stream.read(2))[0]
            else:
                content_id = struct.unpack('B', stream.read(1))[0]
            
            # Skip param1 and param2 for this example
            stream.read(2)  # param1 + param2
            
            nodes.append(content_id)
            
            # Count node types
            if content_id in name_id_map:
                node_name = name_id_map[content_id]
                node_counts[node_name] = node_counts.get(node_name, 0) + 1
        
        # Show node distribution
        print("\nNode distribution in this block:")
        for node_name, count in sorted(node_counts.items(), key=lambda x: -x[1]):
            percentage = (count / 4096) * 100
            print(f"  {node_name:30s}: {count:4d} nodes ({percentage:5.1f}%)")
        
        # Show a slice of the block (Y=0 layer)
        print("\n=== Y=0 Layer (bottom) ===")
        print("X→")
        for z in range(16):
            row = []
            for x in range(16):
                idx = z * 256 + 0 * 16 + x  # y=0
                content_id = nodes[idx]
                if content_id in name_id_map:
                    node_name = name_id_map[content_id]
                    # Use first letter or symbol
                    if node_name == "air":
                        symbol = "."
                    elif "stone" in node_name:
                        symbol = "#"
                    elif "dirt" in node_name:
                        symbol = "D"
                    elif "grass" in node_name:
                        symbol = "G"
                    elif "water" in node_name:
                        symbol = "~"
                    else:
                        symbol = node_name[0].upper()
                else:
                    symbol = "?"
                row.append(symbol)
            print(f"Z{z:2d} " + "".join(row))
        
        return name_id_map, nodes

def analyze_world_blocks(db_path, limit=5):
    """Analyze several blocks from the world to show variety"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get some interesting blocks (not just all air)
    cursor.execute("""
        SELECT pos, data 
        FROM blocks 
        WHERE length(data) > 100  -- Skip very small (likely all-air) blocks
        ORDER BY RANDOM() 
        LIMIT ?
    """, (limit,))
    
    for i, (pos_blob, data_blob) in enumerate(cursor.fetchall()):
        x, y, z = decode_mapblock_position(pos_blob)
        print(f"\n{'='*60}")
        print(f"BLOCK #{i+1}: Position ({x}, {y}, {z})")
        print(f"World coordinates: ({x*16} to {x*16+15}, {y*16} to {y*16+15}, {z*16} to {z*16+15})")
        print(f"Compressed size: {len(data_blob)} bytes")
        print(f"{'='*60}")
        
        try:
            decode_compressed_block(data_blob)
        except Exception as e:
            print(f"Error decoding block: {e}")
    
    conn.close()

if __name__ == "__main__":
    # Path to your world's map database
    db_path = "/var/games/minetest-server/.minetest/worlds/world/map.sqlite"
    
    print("Luanti/Minetest MapBlock Decoder")
    print("This shows the exact binary format of blocks in the database\n")
    
    analyze_world_blocks(db_path, limit=3)