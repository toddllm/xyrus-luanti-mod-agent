#!/usr/bin/env python3
"""
Complete working decoder showing exact binary format
"""

import struct
import sqlite3
import zstandard as zstd

def decode_position(pos_int):
    """Decode 64-bit integer position to (x,y,z)"""
    # Extract components using bit operations
    x = (pos_int & 0xfff) - 2048
    y = ((pos_int >> 12) & 0xfff) - 2048  
    z = ((pos_int >> 24) & 0xfff) - 2048
    return x, y, z

def encode_position(x, y, z):
    """Encode (x,y,z) to 64-bit integer"""
    return ((z + 2048) << 24) | ((y + 2048) << 12) | (x + 2048)

def read_u8(data, pos):
    return data[pos], pos + 1

def read_u16(data, pos):
    return struct.unpack('>H', data[pos:pos+2])[0], pos + 2

def read_u32(data, pos):
    return struct.unpack('>I', data[pos:pos+4])[0], pos + 4

def read_string16(data, pos):
    length, pos = read_u16(data, pos)
    string = data[pos:pos+length].decode('utf-8')
    return string, pos + length

def decode_complete_block(pos_int, data_blob):
    """Decode a block showing complete binary format"""
    
    x, y, z = decode_position(pos_int)
    print(f"\n=== MAPBLOCK AT ({x}, {y}, {z}) ===")
    print(f"Database key: {pos_int}")
    print(f"World coordinates: ({x*16} to {x*16+15}, {y*16} to {y*16+15}, {z*16} to {z*16+15})")
    
    # 1. Outer format
    print(f"\n--- Compressed Data ---")
    print(f"Total size: {len(data_blob)} bytes")
    version = data_blob[0]
    print(f"Version: {version}")
    
    if version != 29:
        print("Not version 29!")
        return
    
    # Check ZSTD magic
    if len(data_blob) > 4:
        magic = struct.unpack('<I', data_blob[1:5])[0]
        print(f"ZSTD magic: 0x{magic:08x} (should be 0x28B52FFD)")
    
    # 2. Decompress
    dctx = zstd.ZstdDecompressor()
    try:
        # Try normal decompression first
        decompressed = dctx.decompress(data_blob[1:])
    except:
        # Fall back to max_output_size
        decompressed = dctx.decompress(data_blob[1:], max_output_size=65536)
    
    print(f"\n--- Decompressed Data ---")
    print(f"Decompressed size: {len(decompressed)} bytes")
    print(f"First 32 bytes: {' '.join(f'{b:02X}' for b in decompressed[:32])}")
    
    # 3. Parse decompressed data
    pos = 0
    
    # Flags
    flags, pos = read_u8(decompressed, pos)
    print(f"\n--- Block Header ---")
    print(f"Flags: 0x{flags:02x}")
    print(f"  is_underground: {bool(flags & 0x01)}")
    print(f"  is_generated: {not bool(flags & 0x08)}")
    
    # Lighting
    lighting, pos = read_u16(decompressed, pos)
    print(f"Lighting complete: 0x{lighting:04x}")
    
    # Check if this is disk format (has timestamp)
    test_u32, _ = read_u32(decompressed, pos)
    has_timestamp = (test_u32 != 0x00000000 or test_u32 == 0xFFFFFFFF)
    
    if has_timestamp:
        timestamp, pos = read_u32(decompressed, pos)
        print(f"Timestamp: {timestamp} (0x{timestamp:08x})")
    
    # NameIdMapping
    print(f"\n--- NameIdMapping ---")
    print(f"Position in stream: {pos}")
    
    # Try to read mapping count
    mapping_count, test_pos = read_u16(decompressed, pos)
    
    # Check if this looks valid
    if mapping_count == 0 or mapping_count > 1000:
        # Might be content_width/params_width instead
        print(f"Invalid mapping count: {mapping_count}, checking for alternate format...")
        
        # Skip the bad count
        pos += 2
        
        # Try reading content/params width
        content_width, pos = read_u8(decompressed, pos)
        params_width, pos = read_u8(decompressed, pos)
        print(f"Content width: {content_width}, Params width: {params_width}")
        
        # Now try mapping count again
        mapping_count, pos = read_u16(decompressed, pos)
    else:
        pos = test_pos
    
    print(f"Mapping count: {mapping_count}")
    
    # Read mappings
    name_id_map = {}
    for i in range(min(mapping_count, 10)):  # Show first 10
        node_id, pos = read_u16(decompressed, pos)
        node_name, pos = read_string16(decompressed, pos)
        name_id_map[node_id] = node_name
        print(f"  {node_id:4d} -> \"{node_name}\"")
    
    if mapping_count > 10:
        print(f"  ... and {mapping_count - 10} more mappings")
        # Skip remaining
        for i in range(10, mapping_count):
            node_id, pos = read_u16(decompressed, pos)
            node_name, pos = read_string16(decompressed, pos)
            name_id_map[node_id] = node_name
    
    # Content/params width (if not already read)
    if 'content_width' not in locals():
        content_width, pos = read_u8(decompressed, pos)
        params_width, pos = read_u8(decompressed, pos)
        print(f"\n--- Node Format ---")
        print(f"Content width: {content_width} bytes")
        print(f"Params width: {params_width} bytes")
    
    # Node data
    print(f"\n--- Node Data ---")
    print(f"Position in stream: {pos}")
    print(f"Expected node data size: {4096 * (content_width + params_width)} bytes")
    print(f"Remaining in buffer: {len(decompressed) - pos} bytes")
    
    # Read first few nodes as examples
    if params_width == 2:  # Valid format
        print(f"\nFirst 10 nodes:")
        for i in range(min(10, 4096)):
            if content_width == 2:
                content_id, pos = read_u16(decompressed, pos)
            else:
                content_id, pos = read_u8(decompressed, pos)
            
            param1, pos = read_u8(decompressed, pos)
            param2, pos = read_u8(decompressed, pos)
            
            # Calculate position within block
            node_x = i % 16
            node_y = (i // 16) % 16
            node_z = i // 256
            
            node_name = name_id_map.get(content_id, f"unknown_{content_id}")
            print(f"  Node[{i:4d}] at ({node_x:2d},{node_y:2d},{node_z:2d}): "
                  f"content={content_id:3d} ({node_name}), "
                  f"param1={param1:3d}, param2={param2:3d}")
    
    return name_id_map

# Main
def main():
    db_path = "/var/games/minetest-server/.minetest/worlds/world/map.sqlite"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get a specific block for detailed analysis
    # Let's get block at (0, 0, 0) if it exists
    test_pos = encode_position(0, 0, 0)
    cursor.execute("SELECT pos, data FROM blocks WHERE pos = ?", (test_pos,))
    result = cursor.fetchone()
    
    if not result:
        # Get any block with reasonable size
        cursor.execute("""
            SELECT pos, data 
            FROM blocks 
            WHERE length(data) BETWEEN 300 AND 1000
            ORDER BY RANDOM()
            LIMIT 1
        """)
        result = cursor.fetchone()
    
    conn.close()
    
    if result:
        pos_int, data_blob = result
        decode_complete_block(pos_int, data_blob)
    else:
        print("No suitable blocks found")

if __name__ == "__main__":
    main()