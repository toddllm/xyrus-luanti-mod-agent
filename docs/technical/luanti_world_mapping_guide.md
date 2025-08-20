# Luanti World Mapping: A Developer's Guide

## Overview: How Luanti Stores the World

The world is divided into **MapBlocks** of 16×16×16 nodes. Each MapBlock is stored as a record in the SQLite database with its own node type mappings.

## Example: A Real MapBlock

Let's examine a MapBlock that contains a house with stone walls, wooden floor, glass windows, and a torch:

### 1. The MapBlock Position
```
Position: (5, 0, -10)  // This is in MapBlock coordinates
Real world coordinates: (80 to 95, 0 to 15, -160 to -145)
```

### 2. The NameIdMapping for this block
```cpp
// Inside the compressed block data:
NameIdMapping {
  0: "air"
  1: "default:stone"
  2: "default:wood" 
  3: "default:glass"
  4: "default:torch_wall"
  5: "default:dirt"
  6: "default:dirt_with_grass"
}
```

### 3. The Node Data (simplified view)
```
Layer Y=0 (bottom):
  All nodes = 5 (dirt)
  
Layer Y=1:
  Mostly 6 (dirt_with_grass)
  Some 1 (stone) for house foundation
  
Layer Y=2-4 (house walls):
  Perimeter = 1 (stone)
  Inside = 0 (air)
  One spot = 4 (torch_wall)
  
Layer Y=5 (house ceiling/floor):
  All = 2 (wood)
  
Layer Y=6-15:
  All = 0 (air)
```

### 4. The Actual Binary Storage

The MapBlock is stored in the database as:
```
pos (BLOB): 0x00050000FFFFF6  // Encoded position
data (BLOB): [ZSTD compressed data containing:]
  - Version byte: 29
  - NameIdMapping section
  - 4096 node IDs (16×16×16)
  - Node metadata (if any)
  - Other block data
```

## The Code Path: From Database to Game

### 1. Database Reading
**File: `/home/tdeshane/luanti/luanti_source/src/database/database-sqlite3.cpp`**

```cpp
bool MapDatabaseSQLite3::loadBlock(const v3s16 &pos, std::string *block)
{
    verifyDatabase();
    
    // Convert 3D position to database key
    sqlite3_bind_int64(m_stmt_read, 1, getBlockAsInteger(pos));
    
    if (sqlite3_step(m_stmt_read) == SQLITE_ROW) {
        const char *data = (const char *) sqlite3_column_blob(m_stmt_read, 0);
        size_t len = sqlite3_column_bytes(m_stmt_read, 0);
        
        block->assign(data, len);  // This is compressed data
        
        sqlite3_reset(m_stmt_read);
        return true;
    }
    
    sqlite3_reset(m_stmt_read);
    return false;
}
```

### 2. Block Deserialization
**File: `/home/tdeshane/luanti/luanti_source/src/mapblock.cpp`**

```cpp
void MapBlock::deSerialize(std::istream &is, u8 version, bool disk)
{
    if (version >= 29) {
        // Decompress block data
        std::ostringstream os(std::ios_base::binary);
        decompressZstd(is, os);
        std::istringstream iss(os.str(), std::ios_base::binary);
        
        // Read actual format version
        u8 actual_version = readU8(iss);
        
        // Deserialize using actual version
        deSerialize_pre22(iss, actual_version, disk);
    }
}

void MapBlock::deSerialize_pre22(std::istream &is, u8 version, bool disk)
{
    // Read node data
    if (version >= 29) {
        // Read NameIdMapping
        content_width = readU8(is);  // Should be 2 for 16-bit IDs
        content_t param_width = readU8(is);
        
        // Read the ID-to-name mappings
        m_gamedef->ndef()->deSerialize(nimap, is);
        
        // Example of what's read:
        // nimap[0] = "air"
        // nimap[1] = "default:stone"
        // etc.
        
        // Read all 4096 nodes
        MapNode::deSerializeBulk(is, version, data, 
            nodecount, content_width, param_width);
    }
}
```

### 3. NameIdMapping Management
**File: `/home/tdeshane/luanti/luanti_source/src/nodedef.cpp`**

```cpp
void NodeDefManager::deSerialize(std::istream &is, u16 protocol_version)
{
    u16 count = readU16(is);
    
    for (u16 i = 0; i < count; i++) {
        u16 id = readU16(is);
        std::string name = deSerializeString16(is);
        
        // Map ID to name for this block
        m_name_id_mapping.set(id, name);
    }
}
```

### 4. Node Access in Game
**File: `/home/tdeshane/luanti/luanti_source/src/map.cpp`**

```cpp
MapNode Map::getNode(v3s16 p)
{
    v3s16 blockpos = getNodeBlockPos(p);
    MapBlock *block = getBlockNoCreateNoEx(blockpos);
    
    if (!block)
        throw InvalidPositionException();
    
    v3s16 relpos = p - blockpos * MAP_BLOCKSIZE;
    MapNode node = block->getNodeNoCheck(relpos);
    
    // node.param0 contains the content ID
    // The block's NameIdMapping converts this to a name like "default:stone"
    
    return node;
}
```

## Visual Diagram: Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     map.sqlite Database                      │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐│
│  │ pos: (5,0,-10) │  │ pos: (5,0,-9) │  │ pos: (5,1,-10) ││
│  │ data: [ZSTD]   │  │ data: [ZSTD]   │  │ data: [ZSTD]   ││
│  └────────────────┘  └────────────────┘  └────────────────┘│
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               MapDatabaseSQLite3::loadBlock()               │
│     Reads compressed blob from database by position         │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  MapBlock::deSerialize()                    │
│     1. Decompress with ZSTD                                 │
│     2. Read NameIdMapping:                                  │
│        0→"air", 1→"default:stone", 2→"default:wood"...     │
│     3. Read 4096 node IDs (each is 16-bit)                 │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    MapBlock in Memory                       │
│                                                             │
│  NameIdMapping:              Node Array:                   │
│  ┌─────────────────┐        ┌─┬─┬─┬─┬─┬─┬─┬─┐           │
│  │ 0: "air"        │        │0│0│0│0│0│0│0│0│ (air)      │
│  │ 1: "default:    │        ├─┼─┼─┼─┼─┼─┼─┼─┤           │
│  │    stone"       │        │1│0│0│0│0│0│0│1│ (walls)    │
│  │ 2: "default:    │        ├─┼─┼─┼─┼─┼─┼─┼─┤           │
│  │    wood"        │        │1│0│0│4│0│0│0│1│ (torch)    │
│  │ 3: "default:    │        ├─┼─┼─┼─┼─┼─┼─┼─┤           │
│  │    glass"       │        │2│2│2│2│2│2│2│2│ (floor)    │
│  │ 4: "default:    │        └─┴─┴─┴─┴─┴─┴─┴─┘           │
│  │    torch_wall"  │        (Simplified 2D slice)         │
│  └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Game Engine Usage                         │
│                                                             │
│  getNode(80, 3, -150) → MapNode with content_id = 1       │
│  Block's NameIdMapping: 1 → "default:stone"                │
│  NodeDefManager: "default:stone" → full node properties    │
└─────────────────────────────────────────────────────────────┘
```

## Key Technical Points

1. **Why String-to-ID Mapping?**
   - Flexibility: New node types can be added without breaking saves
   - Efficiency: 16-bit IDs instead of strings in the 4096-node array
   - Modularity: Each block only stores mappings for nodes it uses

2. **Why Per-Block Mapping?**
   - A block with only stone and air needs just 2 mappings
   - A complex block might have 50+ different node types
   - Saves space overall

3. **The Compression**
   - ZSTD compression typically reduces block size by 90%+
   - Most blocks have large areas of the same node (air, stone)
   - Compression ratio depends on block complexity

## Example: Reading a Specific Node

Here's the complete path to read node at world position (83, 2, -155):

```cpp
// 1. Convert world position to block position
v3s16 blockpos = getNodeBlockPos(83, 2, -155);  // = (5, 0, -10)

// 2. Calculate position within block  
v3s16 relpos = (83, 2, -155) - (80, 0, -160);  // = (3, 2, 5)

// 3. Load block from database
MapBlock *block = loadBlock(blockpos);

// 4. Get node from block's 3D array
// Index = z*256 + y*16 + x = 5*256 + 2*16 + 3 = 1315
MapNode node = block->data[1315];

// 5. Get content ID (let's say it's 1)
content_t content = node.getContent();  // = 1

// 6. Use block's NameIdMapping
std::string name = block->getNodeName(1);  // = "default:stone"

// 7. Get full node definition
ContentFeatures def = ndef->get(name);
// def.drawtype, def.tiles, def.groups, etc.
```

## Files to Study

1. **Database Layer**
   - `src/database/database-sqlite3.cpp` - SQLite interface
   - `src/database/database.h` - Database abstraction

2. **Serialization**
   - `src/mapblock.cpp` - Block serialization/deserialization
   - `src/serialization.cpp` - Compression/decompression
   - `src/nodedef.cpp` - Node definition management

3. **World Access**
   - `src/map.cpp` - High-level map access
   - `src/mapnode.cpp` - Individual node representation
   - `src/nameidmapping.cpp` - String↔ID conversion

4. **Constants**
   - `src/constants.h` - MAP_BLOCKSIZE = 16
   - `src/mapblock.h` - Block structure definitions

This is how Luanti efficiently stores and accesses a world with potentially thousands of different node types while keeping save files manageable and maintaining backwards compatibility.