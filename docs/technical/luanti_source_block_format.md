# Luanti Block Format - Source Code Analysis

Based on analysis of the Luanti source code at https://github.com/toddllm/luanti

## Block Serialization Format (Version 29+)

### Database Storage
- **Table**: `blocks` with columns `pos` (INT) and `data` (BLOB)
- **Position encoding**: Single integer encoding 3D block coordinates
- **Data**: ZSTD compressed binary data

### Compressed Block Structure

```
[Version Byte]          // Current version: 29
[Flags Byte]            // Bit 0: is_underground, Bit 1: !isAir, Bit 3: !generated
[Lighting Complete]     // u16: lighting status
[Timestamp]            // u32: last modification time (disk only)
[NameIdMapping]        // Node name to ID mappings
[Node Data]            // Bulk node data
[Node Metadata]        // Chest contents, sign text, etc.
[Static Objects]       // Entities, dropped items
```

### NameIdMapping Format
Maps node IDs (u16) to node names (strings like "air", "default:stone"):

```
[Version]              // u8: 0
[Count]                // u16: number of mappings
For each mapping:
  [ID]                 // u16: node ID
  [Name Length]        // u16: string length
  [Name]               // string: node name (e.g., "default:stone")
```

### Node Data Format
- **Content width**: 1 or 2 bytes per node ID
- **Params width**: 2 bytes (param1: light, param2: rotation/etc)
- **4096 nodes** per block (16×16×16)

### Key Classes (from source)

1. **MapBlock** (`mapblock.cpp`):
   - `serialize()`: Compresses and writes block to database
   - `deSerialize()`: Reads and decompresses block from database
   - Version 29+ uses ZSTD compression

2. **NameIdMapping** (`nameidmapping.cpp`):
   - Maps between numeric IDs and string names
   - Serialized with each block for disk storage
   - Allows dynamic node registration

3. **NodeMetadata** (`nodemetadata.cpp`):
   - Stores per-node metadata (chest inventories, etc.)
   - Key-value pairs per node position

## Example: Air Block Analysis

Small blocks (44 bytes) that are mostly air:
```
1D 28B52FFD 0058150100A000FF000001000000036169720202000F000A000004
^^ ^^^^^^^^
|  ZSTD magic
Version/flags

After decompression contains:
- NameIdMapping with "air" -> ID mapping
- 4096 nodes all set to air ID
```

## Node Types

Node types are NOT hardcoded but dynamically registered:
- Core nodes defined in `builtin/game/register.lua`
- Game nodes in `games/minetest_game/mods/*/init.lua`
- Mod nodes in mod directories

Common node examples:
- `air` - Empty space
- `default:stone` - Basic stone
- `default:dirt` - Dirt block
- `default:chest` - Chest with inventory

## Accessing Block Data Programmatically

```cpp
// Pseudocode based on source
MapBlock block;
std::stringstream compressed_data(blob_from_database);
block.deSerialize(compressed_data, version, true);

// Access nodes
for (int i = 0; i < MAP_BLOCKSIZE * MAP_BLOCKSIZE * MAP_BLOCKSIZE; i++) {
    MapNode node = block.getNodeNoCheck(i);
    std::string name = nodedef->get(node).name;
}
```

## Summary

The Luanti block format is a sophisticated system that:
1. Compresses all block data with ZSTD
2. Stores node type mappings per block (allowing dynamic node types)
3. Includes metadata, lighting, and entity data
4. Uses version numbers for backward compatibility
5. Efficiently packs 4096 nodes into compressed blobs

The "air" blocks we saw are minimal because they contain:
- Simple NameIdMapping (just "air")
- All nodes set to the same ID
- No metadata or entities