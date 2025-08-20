#!/usr/bin/env python3
"""
Extract all node types from Luanti world blocks
"""

import sqlite3
import zstandard as zstd
import struct
from collections import defaultdict
import sys

def read_u8(data, pos):
    return data[pos], pos + 1

def read_u16(data, pos):
    return struct.unpack('>H', data[pos:pos+2])[0], pos + 2

def read_u32(data, pos):
    return struct.unpack('>I', data[pos:pos+4])[0], pos + 4

def read_string16(data, pos):
    length, pos = read_u16(data, pos)
    string = data[pos:pos+length].decode('utf-8', errors='ignore')
    return string, pos + length

def decode_nameid_mapping(data, pos):
    """Decode NameIdMapping from block data"""
    mapping = {}
    
    # Version
    version, pos = read_u8(data, pos)
    if version != 0:
        return mapping, pos
    
    # Count
    count, pos = read_u16(data, pos)
    
    # Read mappings
    for i in range(count):
        node_id, pos = read_u16(data, pos)
        node_name, pos = read_string16(data, pos)
        mapping[node_id] = node_name
    
    return mapping, pos

def analyze_block(compressed_data):
    """Analyze a single compressed block"""
    try:
        # Skip if too small
        if len(compressed_data) < 10:
            return None
            
        # First byte is version (0x1D = 29)
        version = compressed_data[0]
        
        # Check for ZSTD magic number at position 1
        if compressed_data[1:5] != b'\x28\xb5\x2f\xfd':
            return None
            
        # Decompress (skip version byte)
        dctx = zstd.ZstdDecompressor()
        decompressed = dctx.decompress(compressed_data[1:])
        
        pos = 0
        
        # Read flags
        flags, pos = read_u8(decompressed, pos)
        is_underground = (flags & 0x01) != 0
        is_not_air = (flags & 0x02) != 0
        
        # Read lighting complete (u16)
        lighting, pos = read_u16(decompressed, pos)
        
        # Read timestamp (u32) - only in disk format
        timestamp, pos = read_u32(decompressed, pos)
        
        # Read NameIdMapping
        node_mapping, pos = decode_nameid_mapping(decompressed, pos)
        
        return {
            'is_underground': is_underground,
            'is_not_air': is_not_air,
            'timestamp': timestamp,
            'node_types': node_mapping
        }
        
    except Exception as e:
        return None

def main():
    db_path = "/var/games/minetest-server/.minetest/worlds/world/map.sqlite"
    
    print("Analyzing Luanti world blocks...")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get total blocks
    cursor.execute("SELECT COUNT(*) FROM blocks")
    total_blocks = cursor.fetchone()[0]
    print(f"Total blocks in world: {total_blocks:,}")
    print()
    
    # Analyze blocks
    node_types = defaultdict(int)
    block_types = defaultdict(int)
    underground_count = 0
    air_only_count = 0
    failed_count = 0
    sample_blocks = []
    
    # Process blocks in batches
    batch_size = 1000
    processed = 0
    
    cursor.execute("SELECT pos, data FROM blocks")
    
    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
            
        for pos, data in rows:
            result = analyze_block(data)
            
            if result:
                # Count node types
                for node_id, node_name in result['node_types'].items():
                    node_types[node_name] += 1
                
                # Categorize blocks
                if len(result['node_types']) == 1 and 'air' in result['node_types'].values():
                    air_only_count += 1
                    block_types['air_only'] += 1
                elif result['is_underground']:
                    underground_count += 1
                    block_types['underground'] += 1
                else:
                    block_types['surface'] += 1
                
                # Save some examples
                if len(sample_blocks) < 10 and len(result['node_types']) > 3:
                    sample_blocks.append({
                        'pos': pos,
                        'size': len(data),
                        'nodes': result['node_types']
                    })
            else:
                failed_count += 1
            
            processed += 1
            
        # Progress
        if processed % 10000 == 0:
            print(f"Processed {processed:,} / {total_blocks:,} blocks...")
    
    conn.close()
    
    # Print results
    print()
    print("Block Analysis Results")
    print("=" * 60)
    print(f"Successfully analyzed: {processed - failed_count:,} blocks")
    print(f"Failed to analyze: {failed_count:,} blocks")
    print()
    
    print("Block Categories:")
    for category, count in sorted(block_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count:,} ({count/total_blocks*100:.1f}%)")
    print()
    
    print(f"All Node Types Found ({len(node_types)} total):")
    print("-" * 60)
    
    # Group by mod
    mod_nodes = defaultdict(list)
    for node_name in sorted(node_types.keys()):
        if ':' in node_name:
            mod, name = node_name.split(':', 1)
            mod_nodes[mod].append(node_name)
        else:
            mod_nodes['builtin'].append(node_name)
    
    # Print by mod
    for mod in sorted(mod_nodes.keys()):
        print(f"\n{mod}:")
        for node in sorted(mod_nodes[mod]):
            count = node_types[node]
            print(f"  {node} (in {count} blocks)")
    
    print()
    print("Sample Complex Blocks:")
    print("-" * 60)
    for i, block in enumerate(sample_blocks[:5]):
        print(f"\nBlock {i+1} (pos={block['pos']}, size={block['size']} bytes):")
        print("  Nodes:", ', '.join(block['nodes'].values()))

if __name__ == "__main__":
    # Check if zstandard is installed
    try:
        import zstandard
    except ImportError:
        print("Installing required zstandard library...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "zstandard"])
        import zstandard
    
    main()