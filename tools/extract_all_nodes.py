#!/usr/bin/env python3
"""
Extract all node types by looking for strings in block data
"""

import sqlite3
import re
from collections import defaultdict

def extract_node_names(data):
    """Extract potential node names from binary data"""
    nodes = set()
    
    # Look for patterns like "default:stone", "air", etc.
    # Node names are typically lowercase with optional mod prefix
    pattern = rb'[a-z_]+(?::[a-z_]+)?'
    
    # Find all matches
    for match in re.finditer(pattern, data):
        name = match.group().decode('utf-8', errors='ignore')
        # Filter reasonable node names
        if len(name) >= 3 and len(name) <= 30:
            if name == 'air' or ':' in name:
                nodes.add(name)
    
    return nodes

def main():
    db_path = "/var/games/minetest-server/.minetest/worlds/world/map.sqlite"
    
    print("Extracting all node types from Luanti world...")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get total blocks
    cursor.execute("SELECT COUNT(*) FROM blocks")
    total_blocks = cursor.fetchone()[0]
    print(f"Total blocks: {total_blocks:,}")
    print()
    
    all_nodes = defaultdict(int)
    blocks_with_nodes = defaultdict(int)
    
    # Sample blocks of different sizes
    size_ranges = [
        (0, 100, "tiny"),
        (100, 500, "small"),
        (500, 1000, "medium"),
        (1000, 2000, "large"),
        (2000, 10000, "huge")
    ]
    
    for min_size, max_size, category in size_ranges:
        print(f"Analyzing {category} blocks ({min_size}-{max_size} bytes)...")
        
        cursor.execute("""
            SELECT pos, data 
            FROM blocks 
            WHERE LENGTH(data) >= ? AND LENGTH(data) < ?
            LIMIT 1000
        """, (min_size, max_size))
        
        count = 0
        for pos, data in cursor:
            nodes = extract_node_names(data)
            count += 1
            
            for node in nodes:
                all_nodes[node] += 1
                blocks_with_nodes[node] += 1
        
        print(f"  Analyzed {count} blocks")
    
    # Also get some specific positions
    print("\nAnalyzing blocks near spawn...")
    cursor.execute("""
        SELECT pos, data, LENGTH(data) as size
        FROM blocks 
        WHERE pos >= 0 AND pos < 10000000
        LIMIT 100
    """)
    
    for pos, data, size in cursor:
        nodes = extract_node_names(data)
        for node in nodes:
            all_nodes[node] += 1
    
    conn.close()
    
    # Print results
    print("\n" + "=" * 60)
    print(f"FOUND {len(all_nodes)} UNIQUE NODE TYPES")
    print("=" * 60)
    
    # Group by mod
    mod_nodes = defaultdict(list)
    for node in all_nodes:
        if ':' in node:
            mod, name = node.split(':', 1)
            mod_nodes[mod].append(node)
        else:
            mod_nodes['builtin'].append(node)
    
    # Print by mod
    for mod in sorted(mod_nodes.keys()):
        nodes = sorted(mod_nodes[mod])
        print(f"\n{mod.upper()} MOD ({len(nodes)} nodes):")
        print("-" * 40)
        
        for node in nodes:
            count = all_nodes[node]
            print(f"  {node:<30} (found in {count} blocks)")
    
    # Special analysis for nullifier_adventure
    print("\n" + "=" * 60)
    print("NULLIFIER ADVENTURE NODES:")
    print("=" * 60)
    
    nullifier_nodes = [n for n in all_nodes if n.startswith('nullifier_adventure:')]
    if nullifier_nodes:
        for node in sorted(nullifier_nodes):
            print(f"  {node}")
    else:
        print("  No nullifier_adventure nodes found in sampled blocks")
        
    # Look for largest blocks
    print("\n" + "=" * 60)
    print("LARGEST BLOCKS (likely complex areas):")
    print("=" * 60)
    
    cursor = conn.cursor() 
    cursor.execute("""
        SELECT pos, LENGTH(data) as size
        FROM blocks
        ORDER BY size DESC
        LIMIT 10
    """)
    
    for pos, size in cursor:
        print(f"  Position {pos}: {size:,} bytes")

if __name__ == "__main__":
    main()