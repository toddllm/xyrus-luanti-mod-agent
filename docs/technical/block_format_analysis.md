# Luanti/Minetest Block Storage Format

## Key Findings from Database Analysis

- The blocks table only contains `pos` (position) and `data` (compressed blob)
- No separate metadata tables - everything is in the compressed block data
- Small blocks (44 bytes) contain mostly air - you can see "air" string in the data
- Data format: `1D 28B52FFD` where `1D` is version/flags and `28B52FFD` is ZSTD magic
- Example air block: contains the string "air" after decompression

## Database Structure

The `map.sqlite` database stores world blocks in a simple table:

```sql
CREATE TABLE `blocks` (
    `pos` INT PRIMARY KEY,
    `data` BLOB
);
```

## Position Encoding

The `pos` field encodes 3D coordinates into a single integer:
- Each block represents a 16×16×16 node cube
- Position is encoded as: `(z * 4096 * 4096) + (y * 4096) + x + offset`
- Coordinates range from -2048 to 2047 in each dimension

## Data Format

The `data` BLOB contains:

1. **Compression**: ZSTD compressed data (identified by magic bytes `0x28B52FFD`)
2. **Contents** (after decompression):
   - **Version byte**: Format version
   - **Flags**: Block properties
   - **Node data**: 4096 nodes (16×16×16)
     - Node ID (2 bytes per node)
     - Param1 (light)
     - Param2 (rotation, etc.)
   - **Node metadata**: Chest contents, signs, etc.
   - **Static objects**: Dropped items, entities
   - **Timestamp**: Last modification

## Sample Block Analysis

```
First bytes (hex): 1D28B52FFD...
- 0x1D = Version/flags
- 0x28B52FFD = ZSTD magic number
- Remaining = Compressed block data
```

## Block Types

Block types are not stored in the database directly. Instead:
- Each node has an ID that maps to registered node types
- Node definitions are in the game/mod code
- Common node IDs:
  - 0 = air
  - 1 = stone
  - 2 = dirt
  - etc.

## Metadata Storage

Node metadata (chest inventories, sign text, etc.) is stored as:
- Count of metadata entries
- For each entry:
  - Position within block (0-4095)
  - Serialized metadata (key-value pairs)

## Raw Data Examples

### Small block (44 bytes - mostly air):
```
Hex: 1D28B52FFD0058150100A000FF000001000000036169720202000F000A000004
     ^^ ^^^^^^^^ (ZSTD header)
                                      ^^^^^^^ "air" in ASCII
```

### Map Generation Parameters
The `map_meta.txt` file contains world generation settings:
- Mapgen: v7 (valleys)
- Features: caves, dungeons, decorations, biomes, ores
- Seed: 13765719009798831817

## Accessing Block Data

To properly read block data, you need:
1. ZSTD decompression library
2. Understanding of the MapBlock serialization format
3. The compressed data contains node names as strings (e.g., "air", "default:stone")

## Summary

- 143,458 blocks in the database
- Each block is a 16×16×16 cube of nodes
- All block data is ZSTD compressed
- Node types are stored as strings within the compressed data
- No separate metadata tables - everything is in the block data