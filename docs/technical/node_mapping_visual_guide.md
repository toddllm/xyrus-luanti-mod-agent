# Visual Guide: Node Type Mapping in Action

## Complete Flow Diagram

```
PLAYER LOOKS AT BLOCK
         |
         v
+------------------+
| World Position   |
| (1234, 56, -789) |
+------------------+
         |
         | ÷16
         v
+------------------+
| Block Position   |
| (77, 3, -50)     |
+------------------+
         |
         | Encode
         v
+------------------+
| Database Key     |
| 33520667730509   |
+------------------+
         |
         | SQLite
         v
+------------------+
| Compressed BLOB  |
| [1D 28 B5 2F...] |
| 621 bytes        |
+------------------+
         |
         | ZSTD
         v
+------------------+
| Decompressed     |
| Block Data       |
| 16KB+ raw data   |
+------------------+
         |
         | Parse
         v
+------------------+
| NameIdMapping    |
| 0: "air"         |
| 1: "stone"       |
| 2: "dirt"        |
+------------------+
         |
         | + Node Array
         v
+------------------+
| MapBlock Object  |
| in Memory        |
+------------------+
         |
         | Index
         v
+------------------+
| Node at Index    |
| content_id = 1   |
+------------------+
         |
         | Lookup
         v
+------------------+
| Node Name        |
| "default:stone"  |
+------------------+
         |
         | Registry
         v
+------------------+
| Node Properties  |
| texture, hardness|
| drops, sounds... |
+------------------+
```

## More Real Block Examples

### Example 4: Complex Surface Block with Multiple Materials
**Position**: (256, 2, -180)  
**World Coords**: (4096-4111, 32-47, -2880--2865)

```
NameIdMapping (23 entries):
  0 → "air"
  1 → "default:dirt_with_grass"
  2 → "default:dirt"
  3 → "default:stone"
  4 → "default:tree"
  5 → "default:leaves"
  6 → "default:apple"
  7 → "default:grass_3"
  8 → "default:grass_4"
  9 → "flowers:rose"
  10 → "flowers:tulip"
  11 → "default:water_source"
  12 → "default:sand"
  13 → "default:furnace"
  14 → "default:chest"
  15 → "default:torch_wall"
  16 → "default:ladder_wood"
  17 → "doors:door_wood_a"
  18 → "doors:door_wood_b"
  19 → "default:fence_wood"
  20 → "default:glass"
  21 → "stairs:slab_wood"
  22 → "default:sign_wall_wood"

Visual Y=1 layer (ground level):
  GGGGGGGGGGGGWWWW  G = grass (1)
  GGGGG7GGG8GGWWWW  7,8 = grass plants
  GGG9GGGGGGG WWWW  9 = rose
  GGGGGGG10GGGWWWW  10 = tulip  
  GGGGGGGGGGGGSSSS  W = water (11)
  GGGGGGGGGGGSSSSS  S = sand (12)
  GGGGGGGGGGSSSSSS
  GGGGGGGDDDDSSSSS  D = dirt (2)
  GGGGGGDDDDDDSSSS
  GGGGGDDDDDDDDSSS
  GGGGDDDDDDDDDDSS
  GGGDDDDDDDDDDDDS
  GGDDDDDDDDDDDDDD
  GDDDDDDDDDDDDDDD
  DDDDDDDDDDDDDDDD
  DDDDDDDDDDDDDDDD
```

### Example 5: Player-Built Structure
**Position**: (100, 10, -200)  
**Shows how player modifications create diverse blocks**

```
NameIdMapping (31 entries!):
  0 → "air"
  1 → "default:cobble"
  2 → "default:wood"
  3 → "default:stone_brick"
  4 → "default:glass"
  5 → "doors:door_steel_a"
  6 → "doors:door_steel_b"
  7 → "default:chest_locked"
  8 → "default:furnace_active"
  9 → "default:torch_wall"
  10 → "default:torch_ceiling"
  11 → "stairs:stair_wood"
  12 → "stairs:slab_stonebrick"
  13 → "default:bookshelf"
  14 → "default:sign_wall_steel"
  15 → "beds:bed_top_red"
  16 → "beds:bed_bottom_red"
  17 → "default:meselamp"
  18 → "xpanes:pane_flat"
  19 → "vessels:shelf"
  20 → "default:coal_block"
  ... and more!

This single block has 31 different node types!
Compare to underground block with just 2-3 types.
```

### Example 6: Comparison of Same Location, Different Blocks

**Three adjacent blocks showing ID differences:**

```
Block A at (0,0,0):          Block B at (1,0,0):          Block C at (0,0,1):
ID → Node                    ID → Node                    ID → Node
0 → "air"                    0 → "air"                    0 → "default:stone"
1 → "default:stone"          1 → "default:dirt"           1 → "air"
2 → "default:dirt"           2 → "default:stone"          2 → "default:stone_with_coal"
3 → "default:water_source"   3 → "default:grass_1"        3 → "default:stone_with_iron"

Same nodes, completely different ID assignments!
```

## Memory Layout Example

```
MapBlock Memory Structure:
+------------------------+
| Block Metadata         |
| - Position: (77,3,-50) |
| - Flags: 0x01          |
| - Timestamp: 12345678  |
+------------------------+
| NameIdMapping          |
| vector<id,string>:     |
| [0] = (0, "air")       |
| [1] = (1, "stone")     |
| [2] = (2, "dirt")      |
+------------------------+
| Node Array[4096]       |
| [0] = {1, 0, 0}        | // stone at (0,0,0)
| [1] = {1, 0, 0}        | // stone at (1,0,0)
| [2] = {0, 15, 0}       | // air at (2,0,0) with light
| ...                    |
| [2946] = {2, 0, 0}     | // dirt at (2,8,11)
| ...                    |
| [4095] = {0, 0, 0}     | // air at (15,15,15)
+------------------------+
| Node Metadata          |
| (chest inventories,    |
|  sign text, etc.)      |
+------------------------+
```

## Performance Implications

### Traditional Enum System (NOT USED):
```cpp
enum NodeType {
    AIR = 0,
    STONE = 1,
    DIRT = 2,
    // ... 200+ more
    MODX_SPECIAL = 245,
    // Adding new = recompile everything
};

// Every block stores 4096 * 2 bytes = 8KB minimum
// Even if block is all air!
```

### Dynamic Mapping System (USED):
```cpp
// All-stone block:
NameIdMapping: {0: "default:stone"}
Nodes: 4096 * 1 byte = 4KB (can use 8-bit IDs)
Total: ~4KB + small mapping overhead

// Complex block with 50 types:
NameIdMapping: {0: "air", 1: "stone", ... 49: "rare_node"}
Nodes: 4096 * 2 bytes = 8KB (needs 16-bit IDs)
Total: ~8KB + mapping strings

// Compression makes it even better!
```

## Real Database Query Example

```sql
-- Find blocks with the most diverse content
SELECT 
    pos,
    LENGTH(data) as compressed_size,
    CAST((pos & 0xFFF) - 2048 AS INT) as x,
    CAST(((pos >> 12) & 0xFFF) - 2048 AS INT) as y,
    CAST(((pos >> 24) & 0xFFF) - 2048 AS INT) as z
FROM blocks
WHERE LENGTH(data) > 2000  -- Larger = more diverse
ORDER BY compressed_size DESC
LIMIT 10;

-- Results show surface blocks with buildings are largest
-- Underground blocks are smallest (mostly stone)
```

## The Magic: Same World, Different Servers

Because of this dynamic system:
1. Server A with mods X,Y,Z saves a world
2. Server B with mods X,Y can load it (missing Z nodes become "unknown")
3. Server C with mods X,Y,Z,W can load it (W nodes can be added)
4. Original server A can load modified world (W nodes become "unknown")

The world remains playable across different mod configurations!