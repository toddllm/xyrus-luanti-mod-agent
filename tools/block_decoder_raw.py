#!/usr/bin/env python3
"""
Raw block decoder - let's understand the exact format
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

def analyze_raw_block(data_blob):
    """Analyze the raw block data to understand format"""
    print(f"Total size: {len(data_blob)} bytes")
    print(f"First 20 bytes (hex): {data_blob[:20].hex()}")
    print(f"First 20 bytes (dec): {list(data_blob[:20])}")
    
    # Check version
    version = data_blob[0]
    print(f"\nVersion byte: {version}")
    
    if version == 29:
        print("This is a version 29 block (ZSTD compressed)")
        
        # Try different decompression approaches
        print("\n--- Trying different ZSTD decompression methods ---")
        
        # Method 1: Direct decompression of everything after version
        try:
            dctx = zstd.ZstdDecompressor()
            result = dctx.decompress(data_blob[1:])
            print(f"Method 1 SUCCESS: Decompressed to {len(result)} bytes")
            print(f"First 20 decompressed bytes: {list(result[:20])}")
            return result
        except Exception as e:
            print(f"Method 1 failed: {e}")
        
        # Method 2: Use max_output_size
        try:
            dctx = zstd.ZstdDecompressor()
            result = dctx.decompress(data_blob[1:], max_output_size=65536)
            print(f"Method 2 SUCCESS: Decompressed to {len(result)} bytes")
            print(f"First 20 decompressed bytes: {list(result[:20])}")
            return result
        except Exception as e:
            print(f"Method 2 failed: {e}")
        
        # Method 3: Check if it's already a valid ZSTD frame
        print(f"\nZSTD frame magic check:")
        if len(data_blob) > 5:
            # ZSTD magic number is 0xFD2FB528 (little endian)
            magic = struct.unpack('<I', data_blob[1:5])[0]
            print(f"Magic at offset 1: 0x{magic:08x}")
            if magic == 0x28B52FFD:
                print("Valid ZSTD magic number found!")
        
        # Method 4: Try with streaming
        try:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(data_blob[1:]) as reader:
                result = reader.read()
            print(f"Method 4 SUCCESS: Decompressed to {len(result)} bytes")
            return result
        except Exception as e:
            print(f"Method 4 failed: {e}")
    
    return None

def examine_blocks(db_path):
    """Examine some blocks to understand format"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get a variety of block sizes
    cursor.execute("""
        SELECT pos, data, length(data) as size
        FROM blocks 
        WHERE size > 100
        ORDER BY size
        LIMIT 5
    """)
    
    blocks = cursor.fetchall()
    conn.close()
    
    print("Examining blocks of different sizes...\n")
    
    for i, (pos_int, data_blob, size) in enumerate(blocks):
        x, y, z = decode_mapblock_position(pos_int)
        print(f"\n{'='*60}")
        print(f"Block #{i+1}: Position ({x}, {y}, {z}), Size: {size} bytes")
        print(f"{'='*60}")
        
        decompressed = analyze_raw_block(data_blob)
        
        if decompressed:
            print(f"\n--- Analyzing decompressed data ---")
            print(f"Total decompressed size: {len(decompressed)} bytes")
            
            # Parse the decompressed data
            pos = 0
            
            # Read flags
            flags = decompressed[pos]
            pos += 1
            print(f"Flags: 0x{flags:02x}")
            print(f"  Underground: {bool(flags & 0x01)}")
            print(f"  Generated: {not bool(flags & 0x08)}")
            
            # Read lighting complete (u16)
            if pos + 2 <= len(decompressed):
                lighting = struct.unpack('>H', decompressed[pos:pos+2])[0]
                pos += 2
                print(f"Lighting complete: 0x{lighting:04x}")
            
            # Read timestamp (u32)
            if pos + 4 <= len(decompressed):
                timestamp = struct.unpack('>I', decompressed[pos:pos+4])[0]
                pos += 4
                print(f"Timestamp: {timestamp}")
            
            print(f"\nPosition in stream: {pos}")
            print(f"Next 20 bytes: {list(decompressed[pos:pos+20])}")
            
            # The NameIdMapping might come after content/param widths
            # Let's read content_width and params_width first
            if pos + 2 <= len(decompressed):
                content_width = decompressed[pos]
                params_width = decompressed[pos + 1]
                print(f"\nContent width: {content_width}, Params width: {params_width}")
                pos += 2
                
                # Now try to read the NameIdMapping
                if pos + 2 <= len(decompressed):
                    num_mappings = struct.unpack('>H', decompressed[pos:pos+2])[0]
                    pos += 2
                    print(f"\nNameIdMapping count: {num_mappings}")
                    
                    # Try to read first few mappings
                    for j in range(min(5, num_mappings)):
                        if pos + 2 <= len(decompressed):
                            node_id = struct.unpack('>H', decompressed[pos:pos+2])[0]
                            pos += 2
                            
                            if pos + 2 <= len(decompressed):
                                name_len = struct.unpack('>H', decompressed[pos:pos+2])[0]
                                pos += 2
                                
                                if pos + name_len <= len(decompressed):
                                    name = decompressed[pos:pos+name_len].decode('utf-8', errors='replace')
                                    pos += name_len
                                    print(f"  {node_id} → {name}")
                
                # Show what comes after the mappings
                print(f"\nAfter mappings, position: {pos}")
                print(f"Next bytes: {list(decompressed[pos:pos+20])}")
                
                # Calculate expected node data size
                node_size = content_width + 2  # content + param1 + param2
                total_node_data = 4096 * node_size
                print(f"\nExpected node data size: {total_node_data} bytes")
                print(f"Remaining data: {len(decompressed) - pos} bytes")

if __name__ == "__main__":
    db_path = "/var/games/minetest-server/.minetest/worlds/world/map.sqlite"
    examine_blocks(db_path)