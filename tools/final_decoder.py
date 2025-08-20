#!/usr/bin/env python3
"""
Final correct Luanti block decoder
Understanding that the data might be in a different order
"""

import struct
import sqlite3
import zstandard as zstd

def decode_position(pos_int):
    x = (pos_int & 0xfff) - 2048
    y = ((pos_int >> 12) & 0xfff) - 2048  
    z = ((pos_int >> 24) & 0xfff) - 2048
    return x, y, z

def read_string16(data, pos):
    if pos + 2 > len(data):
        return None, pos
    length = struct.unpack('>H', data[pos:pos+2])[0]
    pos += 2
    if pos + length > len(data):
        return None, pos
    string = data[pos:pos+length].decode('utf-8', errors='replace')
    return string, pos + length

def decode_v29_block(data_blob):
    """Decode a version 29 block with proper understanding"""
    
    # Decompress
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(data_blob[1:], max_output_size=65536)
    
    pos = 0
    
    # 1. Flags
    flags = decompressed[pos]
    pos += 1
    is_underground = bool(flags & 0x01)
    is_generated = not bool(flags & 0x08)
    
    print(f"Flags: 0x{flags:02x} (underground={is_underground}, generated={is_generated})")
    
    # 2. Lighting complete
    lighting = struct.unpack('>H', decompressed[pos:pos+2])[0]
    pos += 2
    print(f"Lighting: 0x{lighting:04x}")
    
    # 3. Check what comes next
    # If this is a disk format block, next should be timestamp
    next_u32 = struct.unpack('>I', decompressed[pos:pos+4])[0]
    
    if next_u32 == 0xFFFFFFFF or next_u32 < 100000:
        # This looks like a timestamp
        timestamp = next_u32
        pos += 4
        print(f"Timestamp: {timestamp}")
        
        # 4. NameIdMapping should be next
        # But the count might be after content/params width
        # Let's peek ahead
        peek_pos = pos
        test_count = struct.unpack('>H', decompressed[peek_pos:peek_pos+2])[0]
        
        if test_count == 0:
            # Count is 0, so content_width/params_width come next
            pos += 2  # Skip the 0 count
            
            content_width = decompressed[pos]
            params_width = decompressed[pos + 1]
            pos += 2
            
            print(f"Content width: {content_width}, Params width: {params_width}")
            
            # Now the real NameIdMapping
            num_mappings = struct.unpack('>H', decompressed[pos:pos+2])[0]
            pos += 2
        else:
            # Non-zero count, this IS the NameIdMapping
            num_mappings = test_count
            pos += 2
    else:
        # No timestamp, this must be content_width/params_width
        content_width = decompressed[pos]
        params_width = decompressed[pos + 1]
        pos += 2
        
        print(f"Content width: {content_width}, Params width: {params_width}")
        
        # NameIdMapping
        num_mappings = struct.unpack('>H', decompressed[pos:pos+2])[0]
        pos += 2
    
    # Read the name mappings
    print(f"\n=== NameIdMapping ({num_mappings} entries) ===")
    name_id_map = {}
    
    for i in range(min(num_mappings, 10)):
        if pos + 2 > len(decompressed):
            break
        node_id = struct.unpack('>H', decompressed[pos:pos+2])[0]
        pos += 2
        
        node_name, pos = read_string16(decompressed, pos)
        if node_name:
            name_id_map[node_id] = node_name
            print(f"  {node_id:3d} → {node_name}")
    
    if num_mappings > 10:
        print(f"  ... and {num_mappings - 10} more")
        # Skip the rest
        for i in range(10, num_mappings):
            if pos + 2 > len(decompressed):
                break
            node_id = struct.unpack('>H', decompressed[pos:pos+2])[0]
            pos += 2
            node_name, pos = read_string16(decompressed, pos)
            if node_name:
                name_id_map[node_id] = node_name
    
    # If we haven't read content_width yet, read it now
    if 'content_width' not in locals():
        content_width = decompressed[pos]
        params_width = decompressed[pos + 1]
        pos += 2
        print(f"\nContent width: {content_width}, Params width: {params_width}")
    
    # Now read some nodes
    print(f"\n=== Sample Nodes ===")
    print(f"Position in stream: {pos}")
    print(f"Remaining bytes: {len(decompressed) - pos}")
    
    if params_width == 2:  # Valid params_width
        bytes_per_node = content_width + params_width
        expected_size = 4096 * bytes_per_node
        print(f"Expected node data size: {expected_size} bytes")
        
        # Count node types
        node_counts = {}
        for i in range(4096):
            if pos + bytes_per_node > len(decompressed):
                break
                
            if content_width == 2:
                content_id = struct.unpack('>H', decompressed[pos:pos+2])[0]
                pos += 2
            else:
                content_id = decompressed[pos]
                pos += 1
                
            param1 = decompressed[pos]
            param2 = decompressed[pos + 1]
            pos += 2
            
            if content_id in name_id_map:
                node_name = name_id_map[content_id]
                node_counts[node_name] = node_counts.get(node_name, 0) + 1
        
        # Show distribution
        print("\n=== Node Distribution ===")
        for node_name, count in sorted(node_counts.items(), key=lambda x: -x[1])[:10]:
            percentage = (count / 4096) * 100
            print(f"  {node_name:30s}: {count:4d} nodes ({percentage:5.1f}%)")
    
    return name_id_map

def main():
    db_path = "/var/games/minetest-server/.minetest/worlds/world/map.sqlite"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get a variety of blocks
    cursor.execute("""
        SELECT pos, data, length(data) as size
        FROM blocks 
        WHERE size BETWEEN 500 AND 2000
        ORDER BY RANDOM()
        LIMIT 3
    """)
    
    blocks = cursor.fetchall()
    conn.close()
    
    print("Luanti MapBlock Decoder - Understanding Node Type Mappings")
    print("="*60)
    
    for i, (pos_int, data_blob, size) in enumerate(blocks):
        x, y, z = decode_position(pos_int)
        print(f"\n\nBLOCK #{i+1}: Position ({x}, {y}, {z})")
        print(f"World coordinates: ({x*16} to {x*16+15}, {y*16} to {y*16+15}, {z*16} to {z*16+15})")
        print(f"Compressed size: {size} bytes")
        print("-"*60)
        
        # Check version
        if data_blob[0] == 29:
            try:
                decode_v29_block(data_blob)
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"Unsupported version: {data_blob[0]}")

if __name__ == "__main__":
    main()