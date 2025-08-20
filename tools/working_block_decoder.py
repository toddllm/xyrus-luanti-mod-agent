#!/usr/bin/env python3
"""
Working Luanti block decoder - understanding the actual format
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

def decode_block_properly(data_blob):
    """Decode block following the actual C++ logic"""
    
    # Outer version
    version = data_blob[0]
    print(f"Outer version: {version}")
    
    if version != 29:
        return None
        
    # For version >= 29, first decompress the whole thing
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(data_blob[1:], max_output_size=65536)
    print(f"Decompressed to {len(decompressed)} bytes")
    
    # Check if this is actually pre-22 format (deSerialize_pre22)
    # Pre-22 format would have different structure
    
    # Let's check what the decompressed data actually contains
    print(f"\nFirst 40 bytes of decompressed data:")
    print(f"Hex: {decompressed[:40].hex()}")
    print(f"Dec: {list(decompressed[:40])}")
    
    # Try parsing as version 29 format
    pos = 0
    
    # Read flags
    flags = decompressed[pos]
    pos += 1
    print(f"\nFlags: 0x{flags:02x}")
    
    # Read lighting_complete
    lighting = struct.unpack('>H', decompressed[pos:pos+2])[0]
    pos += 2
    print(f"Lighting: 0x{lighting:04x}")
    
    # Check if this looks like version 29 format
    # In v29, after flags and lighting comes timestamp
    test_timestamp = struct.unpack('>I', decompressed[pos:pos+4])[0]
    print(f"Next 4 bytes as u32: {test_timestamp}")
    
    # If timestamp looks reasonable (not 0xFFFFFFFF), this is v29 format
    if test_timestamp == 0xFFFFFFFF:
        print("\nThis looks like an uninitialized/new block")
        pos += 4  # Skip timestamp
        
        # Try to read NameIdMapping
        if pos + 2 <= len(decompressed):
            num_mappings = struct.unpack('>H', decompressed[pos:pos+2])[0]
            print(f"NameIdMapping count at pos {pos}: {num_mappings}")
            
            # But wait - if count is 0, the data after might be content_width/params_width
            if num_mappings == 0:
                # Skip the count
                pos += 2
                
                # Read content_width and params_width
                if pos + 2 <= len(decompressed):
                    content_width = decompressed[pos]
                    params_width = decompressed[pos + 1]
                    print(f"Content width: {content_width}, Params width: {params_width}")
                    pos += 2
                    
                    # Now the real NameIdMapping might be here
                    if pos + 2 <= len(decompressed):
                        real_num_mappings = struct.unpack('>H', decompressed[pos:pos+2])[0]
                        print(f"\nActual NameIdMapping count at pos {pos}: {real_num_mappings}")
                        pos += 2
                        
                        # Read the mappings
                        name_id_map = {}
                        for i in range(min(real_num_mappings, 10)):  # Show first 10
                            if pos + 2 > len(decompressed):
                                break
                            node_id = struct.unpack('>H', decompressed[pos:pos+2])[0]
                            pos += 2
                            
                            node_name, pos = read_string16(decompressed, pos)
                            if node_name is None:
                                break
                                
                            name_id_map[node_id] = node_name
                            print(f"  {node_id} → {node_name}")
                        
                        if real_num_mappings > 10:
                            print(f"  ... and {real_num_mappings - 10} more mappings")
                            
                        return name_id_map

def main():
    db_path = "/var/games/minetest-server/.minetest/worlds/world/map.sqlite"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get blocks with varying sizes
    cursor.execute("""
        SELECT pos, data, length(data) as size
        FROM blocks 
        WHERE size > 200
        ORDER BY size DESC
        LIMIT 5
    """)
    
    blocks = cursor.fetchall()
    conn.close()
    
    print("Analyzing different sized blocks to understand format...\n")
    
    for i, (pos_int, data_blob, size) in enumerate(blocks):
        x, y, z = decode_position(pos_int)
        print(f"\n{'='*60}")
        print(f"Block #{i+1}: Position ({x}, {y}, {z}), Size: {size} bytes")
        print(f"{'='*60}")
        
        try:
            result = decode_block_properly(data_blob)
            if result:
                print(f"\nSuccessfully decoded {len(result)} node types!")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()