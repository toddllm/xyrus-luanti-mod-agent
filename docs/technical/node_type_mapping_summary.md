# Luanti/Minetest Node Type Mapping - Complete Understanding

## Summary

Node types in Luanti/Minetest are **NOT enums**. They use a dynamic string-to-ID mapping system where:

1. **Node names are strings** like `"default:stone"` or `"farming:wheat_5"`
2. **Each MapBlock has its own NameIdMapping** that converts strings to local 16-bit IDs
3. **The mapping is stored per-block** allowing extreme flexibility

## How It Works

### In the Database

Each MapBlock (16×16×16 nodes) is stored as:
```
- Position (encoded as 64-bit integer)
- Data (ZSTD compressed blob containing):
  - Block metadata (flags, lighting, timestamp)
  - NameIdMapping (ID → string mappings)
  - 4096 nodes (using the local IDs)
  - Additional data (node metadata, timers, etc.)
```

### Example from Real World Data

From analyzing your server's blocks, here's what I found:

**Block at (-2044, 2029, -2043):**
```
NameIdMapping:
  0 → default:stone
  1 → default:stone_with_iron  
  2 → default:stone_with_coal
  3 → default:stone_with_copper
  4 → default:gravel
  5 → default:silver_sand
  6 → default:stone_with_tin
  ... (1792 total mappings!)
```

**Same node types in a different block at (-2043, 2033, -2043):**
```
NameIdMapping:
  0 → default:stone
  1 → default:stone_with_iron
  2 → default:stone_with_coal  
  3 → default:stone_with_tin    (different ID!)
  4 → default:stone_with_copper  (different ID!)
  5 → default:gravel            (different ID!)
```

## Why This Design?

1. **Flexibility**: New node types can be added without breaking old worlds
2. **Efficiency**: Common blocks (all stone) need minimal mappings
3. **Scalability**: Each block can have up to 65,536 different node types
4. **Compatibility**: Mods can add new nodes without conflicts

## Your World Statistics

- Total blocks: 143,458
- All blocks use version 29 format (ZSTD compression)
- Most blocks are deep underground (lots of stone variants)
- Node types include all 200+ from minetest_game
- The nullifier_adventure mod adds entities/items but no new block types

## The Complete Flow

```
Database → Read compressed block → Decompress with ZSTD → 
Parse NameIdMapping → Read node IDs → Convert IDs to names → 
Render in game
```

This is why the arena at 0,100,0 might have appeared empty - it uses standard blocks, and any special features would be entities (not stored in the block data) or node metadata (which requires deeper parsing).

## Technical Implementation

The actual C++ code path:
1. `MapDatabaseSQLite3::loadBlock()` - Read from SQLite
2. `MapBlock::deSerialize()` - Decompress and parse
3. `NameIdMapping::deSerialize()` - Read ID mappings
4. `MapNode::deSerializeBulk()` - Read node data
5. Runtime conversion of IDs to node definitions

This dynamic mapping system is what allows Luanti to support thousands of mods while keeping save files efficient and maintaining backwards compatibility.