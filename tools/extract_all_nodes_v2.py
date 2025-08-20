#!/usr/bin/env python3
"""
Extract all node types by analyzing block data more carefully
"""

import sqlite3
import re
from collections import defaultdict

def extract_node_names(data):
    """Extract node names - looking for specific patterns"""
    nodes = set()
    
    # Look for strings that match node naming conventions
    # Must start with lowercase letter, can contain underscores
    # Optional mod prefix with colon
    
    # Convert to string for easier searching (ignore decode errors)
    text = data.decode('latin-1', errors='ignore')
    
    # Pattern for node names
    patterns = [
        # Builtin nodes
        r'\b(air|ignore)\b',
        # Default mod nodes
        r'\bdefault:[a-z_]+\b',
        # Other mod nodes
        r'\b[a-z][a-z0-9_]*:[a-z][a-z0-9_]*\b',
        # Specific mods we know about
        r'\b(?:farming|doors|stairs|beds|bucket|bones|butterflies|carts|creative|default|dye|fire|flowers|screwdriver|vessels|walls|wool|xpanes):[a-z_]+\b',
        # Nullifier adventure
        r'\bnullifier_adventure:[a-z_]+\b'
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            node = match.group()
            if 3 <= len(node) <= 50:  # Reasonable length
                nodes.add(node)
    
    return nodes

def main():
    db_path = "/var/games/minetest-server/.minetest/worlds/world/map.sqlite"
    
    print("Extracting node types from Luanti world blocks...")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get total blocks
    cursor.execute("SELECT COUNT(*) FROM blocks")
    total_blocks = cursor.fetchone()[0]
    print(f"Total blocks in world: {total_blocks:,}")
    print()
    
    all_nodes = defaultdict(int)
    block_sizes = defaultdict(int)
    processed = 0
    
    # Process ALL blocks (or a large sample)
    cursor.execute("SELECT data, LENGTH(data) as size FROM blocks")
    
    print("Processing blocks...")
    for data, size in cursor:
        # Track block sizes
        if size < 100:
            block_sizes['tiny'] += 1
        elif size < 500:
            block_sizes['small'] += 1
        elif size < 1000:
            block_sizes['medium'] += 1
        elif size < 2000:
            block_sizes['large'] += 1
        else:
            block_sizes['huge'] += 1
        
        # Extract nodes
        nodes = extract_node_names(data)
        for node in nodes:
            all_nodes[node] += 1
        
        processed += 1
        if processed % 10000 == 0:
            print(f"  Processed {processed:,} / {total_blocks:,} blocks...")
            if processed >= 50000:  # Limit to 50k for speed
                break
    
    # Get some of the largest blocks specifically
    print("\nAnalyzing largest blocks...")
    cursor.execute("""
        SELECT data, LENGTH(data) as size 
        FROM blocks 
        ORDER BY size DESC 
        LIMIT 100
    """)
    
    for data, size in cursor:
        nodes = extract_node_names(data)
        for node in nodes:
            all_nodes[node] += 1
    
    conn.close()
    
    # Filter out obvious false positives
    filtered_nodes = {}
    for node, count in all_nodes.items():
        # Keep if it's a known pattern or appears in multiple blocks
        if ':' in node or node in ['air', 'ignore'] or count > 2:
            # Additional filtering
            parts = node.split(':')
            if len(parts) <= 2:  # Not too many colons
                if len(parts) == 1 or (len(parts[0]) < 20 and len(parts[1]) < 30):
                    filtered_nodes[node] = count
    
    # Print results
    print("\n" + "=" * 60)
    print(f"ANALYSIS COMPLETE - Found {len(filtered_nodes)} node types")
    print("=" * 60)
    
    print(f"\nBlock size distribution (sample of {processed:,} blocks):")
    for size, count in sorted(block_sizes.items()):
        print(f"  {size}: {count:,} blocks")
    
    # Group by mod
    mod_nodes = defaultdict(list)
    for node in filtered_nodes:
        if ':' in node:
            mod = node.split(':', 1)[0]
            mod_nodes[mod].append(node)
        else:
            mod_nodes['builtin'].append(node)
    
    print(f"\nNode types by mod ({len(mod_nodes)} mods):")
    print("=" * 60)
    
    # Sort mods by number of nodes
    for mod in sorted(mod_nodes.keys(), key=lambda m: len(mod_nodes[m]), reverse=True):
        nodes = sorted(mod_nodes[mod])
        print(f"\n{mod.upper()} ({len(nodes)} nodes):")
        
        # Print first 20 nodes for each mod
        for i, node in enumerate(nodes[:20]):
            count = filtered_nodes[node]
            print(f"  {node:<35} found in {count:>5} blocks")
        
        if len(nodes) > 20:
            print(f"  ... and {len(nodes) - 20} more")
    
    # Special focus on game mods
    print("\n" + "=" * 60)
    print("DETAILED NODE LISTING")
    print("=" * 60)
    
    # All default nodes
    default_nodes = [n for n in filtered_nodes if n.startswith('default:')]
    if default_nodes:
        print(f"\nDEFAULT mod nodes ({len(default_nodes)} total):")
        for node in sorted(default_nodes):
            print(f"  {node}")
    
    # All farming nodes
    farming_nodes = [n for n in filtered_nodes if n.startswith('farming:')]
    if farming_nodes:
        print(f"\nFARMING mod nodes ({len(farming_nodes)} total):")
        for node in sorted(farming_nodes):
            print(f"  {node}")
    
    # Nullifier adventure nodes
    nullifier_nodes = [n for n in filtered_nodes if 'nullifier' in n]
    if nullifier_nodes:
        print(f"\nNULLIFIER ADVENTURE nodes ({len(nullifier_nodes)} total):")
        for node in sorted(nullifier_nodes):
            print(f"  {node}")
    else:
        print("\nNo nullifier_adventure nodes found in sampled blocks")

if __name__ == "__main__":
    main()