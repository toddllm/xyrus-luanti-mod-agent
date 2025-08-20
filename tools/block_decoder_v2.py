#!/usr/bin/env python3
"""
Concrete example of decoding a Luanti/Minetest MapBlock from the database
Shows the exact binary format and node type mappings
"""

import struct
import sqlite3
import zstandard as zstd
from io import BytesIO

def decode_mapblock_position(pos_int):
    """Decode the integer position to (x,y,z) coordinates"""
    # SQLite stores position as a single 64-bit integer
    x = (pos_int & 0xfff) - 2048
    y = ((pos_int >> 12) & 0xfff) - 2048  
    z = ((pos_int >> 24) & 0xfff) - 2048
    return x, y, z

def read_u8(stream):
    return struct.unpack('B', stream.read(1))[0]

def read_u16(stream):
    return struct.unpack('>H', stream.read(2))[0]

def read_u32(stream):
    return struct.unpack('>I', stream.read(4))[0]

def read_string16(stream):
    """Read a 16-bit length-prefixed string"""
    length = read_u16(stream)
    return stream.read(length).decode('utf-8')

def decode_name_id_mapping(stream):
    """Decode the NameIdMapping from the stream"""
    num_mappings = read_u16(stream)
    mapping = {}
    
    for i in range(num_mappings):
        node_id = read_u16(stream)
        node_name = read_string16(stream)
        mapping[node_id] = node_name
    
    return mapping

def decode_compressed_block(data_blob):
    """Decode a ZSTD-compressed MapBlock and show its structure"""
    
    # First byte is the version
    version = data_blob[0]
    print(f"Block format version: {version}")
    
    if version < 29:
        print("This decoder only handles version 29+ blocks")
        return None, None
    
    # For version 29+, decompress the entire stream first
    try:
        dctx = zstd.ZstdDecompressor()
        decompressed = dctx.decompress(data_blob[1:])  # Skip version byte
        stream = BytesIO(decompressed)
    except Exception as e:
        print(f"ZSTD decompression error: {e}")
        return None, None
    
    # Read block header
    flags = read_u8(stream)
    is_underground = bool(flags & 0x01)
    is_generated = not bool(flags & 0x08)
    
    print(f"Flags: 0x{flags:02x} (underground={is_underground}, generated={is_generated})")
    
    # Read lighting complete
    lighting_complete = read_u16(stream)
    print(f"Lighting complete: 0x{lighting_complete:04x}")
    
    # Read timestamp (only in disk format)
    timestamp = read_u32(stream)
    print(f"Timestamp: {timestamp}")
    
    # Read NameIdMapping
    print("\n=== NameIdMapping ===")
    name_id_map = decode_name_id_mapping(stream)
    print(f"Number of node types in this block: {len(name_id_map)}")
    
    for node_id, node_name in sorted(name_id_map.items()):
        print(f"  {node_id:3d} → {node_name}")
    
    # Read content and param widths
    content_width = read_u8(stream)
    params_width = read_u8(stream)
    print(f"\nContent width: {content_width} bytes, Params width: {params_width} bytes")
    
    if content_width not in [1, 2] or params_width != 2:
        print(f"ERROR: Invalid widths - content_width={content_width}, params_width={params_width}")
        return name_id_map, None
    
    # Read node data (4096 nodes = 16x16x16)
    print("\n=== Node Data ===")
    nodes = []
    node_counts = {}
    
    for i in range(4096):
        # Read content ID
        if content_width == 2:
            content_id = read_u16(stream)
        else:
            content_id = read_u8(stream)
        
        # Read param1 and param2
        param1 = read_u8(stream)
        param2 = read_u8(stream)
        
        nodes.append((content_id, param1, param2))
        
        # Count node types
        if content_id in name_id_map:
            node_name = name_id_map[content_id]
            node_counts[node_name] = node_counts.get(node_name, 0) + 1
    
    # Show node distribution
    print("\nNode distribution in this block:")
    for node_name, count in sorted(node_counts.items(), key=lambda x: -x[1]):
        percentage = (count / 4096) * 100
        print(f"  {node_name:30s}: {count:4d} nodes ({percentage:5.1f}%)")
    
    # Show a slice of the block (Y=1 layer, just above bottom)
    print("\n=== Y=1 Layer (just above bottom) ===")
    print("   X→ 0123456789ABCDEF")
    for z in range(16):
        row = []
        for x in range(16):
            idx = z * 256 + 1 * 16 + x  # y=1
            content_id, _, _ = nodes[idx]
            if content_id in name_id_map:
                node_name = name_id_map[content_id]
                # Use symbols for visualization
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
                elif "tree" in node_name or "wood" in node_name:
                    symbol = "W"
                elif "leaves" in node_name:
                    symbol = "L"
                else:
                    symbol = node_name[0].upper()
            else:
                symbol = "?"
            row.append(symbol)
        print(f"Z{z:2d} " + "".join(row))
    
    return name_id_map, nodes

def find_interesting_blocks(db_path, limit=10):
    """Find blocks that have interesting content (not just stone/air)"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # First, let's just get ANY blocks with reasonable size
    cursor.execute("""
        SELECT pos, data 
        FROM blocks 
        WHERE length(data) BETWEEN 500 AND 2000
        ORDER BY RANDOM() 
        LIMIT ?
    """, (limit,))
    
    results = cursor.fetchall()
    
    if not results:
        # If no blocks in that range, just get any blocks
        cursor.execute("""
            SELECT pos, data 
            FROM blocks 
            WHERE length(data) > 100
            ORDER BY RANDOM() 
            LIMIT ?
        """, (limit,))
        results = cursor.fetchall()
    
    conn.close()
    return results

if __name__ == "__main__":
    # Path to your world's map database
    db_path = "/var/games/minetest-server/.minetest/worlds/world/map.sqlite"
    
    print("Luanti/Minetest MapBlock Decoder - Version 2")
    print("This shows the exact binary format and node mappings\n")
    
    blocks = find_interesting_blocks(db_path, limit=3)
    
    for i, (pos_int, data_blob) in enumerate(blocks):
        x, y, z = decode_mapblock_position(pos_int)
        print(f"\n{'='*60}")
        print(f"BLOCK #{i+1}: Position ({x}, {y}, {z})")
        print(f"World coordinates: ({x*16} to {x*16+15}, {y*16} to {y*16+15}, {z*16} to {z*16+15})")
        print(f"Compressed size: {len(data_blob)} bytes")
        print(f"{'='*60}")
        
        try:
            decode_compressed_block(data_blob)
        except Exception as e:
            print(f"Error decoding block: {e}")
            import traceback
            traceback.print_exc()