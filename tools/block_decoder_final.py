#!/usr/bin/env python3
"""
Final working Luanti/Minetest block decoder
Shows the exact node type mappings in blocks
"""

import struct
import sqlite3
import zstandard as zstd

def decode_mapblock_position(pos_int):
    """Decode the integer position to (x,y,z) coordinates"""
    x = (pos_int & 0xfff) - 2048
    y = ((pos_int >> 12) & 0xfff) - 2048  
    z = ((pos_int >> 24) & 0xfff) - 2048
    return x, y, z

def read_string16(data, pos):
    """Read a 16-bit length-prefixed string"""
    if pos + 2 > len(data):
        return None, pos
    length = struct.unpack('>H', data[pos:pos+2])[0]
    pos += 2
    if pos + length > len(data):
        return None, pos
    string = data[pos:pos+length].decode('utf-8', errors='replace')
    return string, pos + length

def decode_block(data_blob):
    """Decode a complete MapBlock"""
    
    # Check version
    version = data_blob[0]
    if version != 29:
        print(f"Unsupported version: {version}")
        return None
    
    # Decompress with max_output_size
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(data_blob[1:], max_output_size=65536)
    
    pos = 0
    
    # Read flags
    flags = decompressed[pos]
    pos += 1
    is_underground = bool(flags & 0x01)
    is_generated = not bool(flags & 0x08)
    
    # Read lighting complete
    lighting_complete = struct.unpack('>H', decompressed[pos:pos+2])[0]
    pos += 2
    
    # Read timestamp
    timestamp = struct.unpack('>I', decompressed[pos:pos+4])[0]
    pos += 4
    
    # Read NameIdMapping - starts right after timestamp
    # First read the count
    num_mappings = struct.unpack('>H', decompressed[pos:pos+2])[0]
    pos += 2
    
    name_id_map = {}
    print(f"\n=== NameIdMapping ({num_mappings} entries) ===")
    
    for i in range(num_mappings):
        # Read node ID
        if pos + 2 > len(decompressed):
            break
        node_id = struct.unpack('>H', decompressed[pos:pos+2])[0]
        pos += 2
        
        # Read node name
        node_name, pos = read_string16(decompressed, pos)
        if node_name is None:
            break
            
        name_id_map[node_id] = node_name
        print(f"  {node_id:3d} → {node_name}")
    
    # Now read content_width and params_width
    content_width = decompressed[pos]
    params_width = decompressed[pos + 1]
    pos += 2
    
    print(f"\nContent width: {content_width} bytes, Params width: {params_width} bytes")
    
    # Read node data
    node_counts = {}
    nodes = []
    
    for i in range(4096):
        # Read content ID
        if content_width == 2:
            if pos + 2 > len(decompressed):
                break
            content_id = struct.unpack('>H', decompressed[pos:pos+2])[0]
            pos += 2
        else:
            content_id = decompressed[pos]
            pos += 1
        
        # Read param1 and param2
        param1 = decompressed[pos]
        param2 = decompressed[pos + 1]
        pos += 2
        
        nodes.append((content_id, param1, param2))
        
        # Count node types
        if content_id in name_id_map:
            node_name = name_id_map[content_id]
            node_counts[node_name] = node_counts.get(node_name, 0) + 1
    
    # Show distribution
    print("\n=== Node Distribution ===")
    for node_name, count in sorted(node_counts.items(), key=lambda x: -x[1]):
        percentage = (count / 4096) * 100
        print(f"  {node_name:30s}: {count:4d} nodes ({percentage:5.1f}%)")
    
    # Show a 2D slice at Y=8 (middle height)
    print("\n=== Y=8 Layer (middle) ===")
    print("   X→ 0123456789ABCDEF")
    for z in range(16):
        row = []
        for x in range(16):
            idx = z * 256 + 8 * 16 + x  # y=8
            if idx < len(nodes):
                content_id, _, _ = nodes[idx]
                if content_id in name_id_map:
                    node_name = name_id_map[content_id]
                    # Symbols for common nodes
                    if node_name == "air":
                        symbol = "."
                    elif "stone" in node_name:
                        symbol = "#"
                    elif "water" in node_name:
                        symbol = "~"
                    elif "dirt" in node_name:
                        symbol = "D"
                    elif "grass" in node_name:
                        symbol = "G"
                    elif "tree" in node_name or "wood" in node_name:
                        symbol = "W"
                    elif "leaves" in node_name:
                        symbol = "L"
                    elif "sand" in node_name:
                        symbol = "S"
                    elif "lava" in node_name:
                        symbol = "!"
                    else:
                        symbol = node_name[0].upper()
                else:
                    symbol = "?"
            else:
                symbol = " "
        row.append(symbol)
        print(f"Z{z:2d} " + "".join(row))
    
    return name_id_map, nodes

def main():
    db_path = "/var/games/minetest-server/.minetest/worlds/world/map.sqlite"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get some larger blocks that likely have more variety
    cursor.execute("""
        SELECT pos, data 
        FROM blocks 
        WHERE length(data) > 200
        ORDER BY RANDOM() 
        LIMIT 3
    """)
    
    blocks = cursor.fetchall()
    conn.close()
    
    print("Luanti/Minetest MapBlock Decoder - Final Version")
    print("Showing node type mappings in world blocks\n")
    
    for i, (pos_int, data_blob) in enumerate(blocks):
        x, y, z = decode_mapblock_position(pos_int)
        print(f"\n{'='*60}")
        print(f"BLOCK #{i+1}: Position ({x}, {y}, {z})")
        print(f"World coordinates: ({x*16} to {x*16+15}, {y*16} to {y*16+15}, {z*16} to {z*16+15})")
        print(f"Compressed size: {len(data_blob)} bytes")
        print(f"{'='*60}")
        
        try:
            decode_block(data_blob)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()