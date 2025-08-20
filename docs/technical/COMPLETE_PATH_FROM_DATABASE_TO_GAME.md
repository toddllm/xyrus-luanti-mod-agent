# Complete Path: From Database to Game - Every Step

## Starting Point: Player at Position (1234, 56, -789)

### STEP 1: Game Needs Node
```cpp
// src/client/game.cpp
void Game::handlePointingAtNode(const PointedThing &pointed)
{
    v3s16 nodepos = pointed.node_undersurface;  // (1234, 56, -789)
    MapNode n = map->getNode(nodepos);
}
```

### STEP 2: Map::getNode() Called
```cpp
// src/map.cpp
MapNode Map::getNode(v3s16 p)
{
    v3s16 blockpos = getNodeBlockPos(p);
    MapBlock *block = getBlockNoCreateNoEx(blockpos);
    if (!block)
        throw InvalidPositionException();
    
    v3s16 relpos = p - blockpos * MAP_BLOCKSIZE;
    return block->getNodeNoCheck(relpos);
}
```

### STEP 3: Calculate Block Position
```cpp
// src/map.h
inline v3s16 getNodeBlockPos(v3s16 p)
{
    return v3s16(
        floor(p.X / MAP_BLOCKSIZE),  // MAP_BLOCKSIZE = 16
        floor(p.Y / MAP_BLOCKSIZE),
        floor(p.Z / MAP_BLOCKSIZE)
    );
}

// CALCULATION:
// (1234, 56, -789) / 16 = (77.125, 3.5, -49.3125)
// floor() = (77, 3, -50)
// Block position = (77, 3, -50)
```

### STEP 4: Get Block from Cache or Database
```cpp
// src/map.cpp
MapBlock *Map::getBlockNoCreateNoEx(v3s16 p)
{
    // First check cache
    MapBlock *block = m_blocks_cache.lookup(p);
    if (block)
        return block;
    
    // Not in cache, load from database
    block = loadBlock(p);
    if (block)
        m_blocks_cache.insert(p, block);
    
    return block;
}
```

### STEP 5: Load Block from Database
```cpp
// src/map.cpp
MapBlock *ServerMap::loadBlock(v3s16 blockpos)
{
    std::string blob;
    if (!dbase->loadBlock(blockpos, &blob))
        return nullptr;
    
    MapBlock *block = new MapBlock(this, blockpos);
    std::istringstream is(blob, std::ios_base::binary);
    u8 version = readU8(is);
    block->deSerialize(is, version, true);
    
    return block;
}
```

### STEP 6: Database Query
```cpp
// src/database/database-sqlite3.cpp
bool MapDatabaseSQLite3::loadBlock(const v3s16 &pos, std::string *block)
{
    verifyDatabase();
    
    // Convert position to database key
    s64 key = getBlockAsInteger(pos);
    
    sqlite3_bind_int64(m_stmt_read, 1, key);
    
    if (sqlite3_step(m_stmt_read) == SQLITE_ROW) {
        const char *data = (char *) sqlite3_column_blob(m_stmt_read, 0);
        size_t len = sqlite3_column_bytes(m_stmt_read, 0);
        
        block->assign(data, len);
        
        sqlite3_reset(m_stmt_read);
        return true;
    }
    
    sqlite3_reset(m_stmt_read);
    return false;
}

// Position encoding function
static s64 getBlockAsInteger(const v3s16 &pos)
{
    return (u64)(pos.Z + 2048) << 24 |
           (u64)(pos.Y + 2048) << 12 |
           (u64)(pos.X + 2048);
}

// CALCULATION:
// pos = (77, 3, -50)
// key = (-50 + 2048) << 24 | (3 + 2048) << 12 | (77 + 2048)
// key = 1998 << 24 | 2051 << 12 | 2125
// key = 33520667730509
```

### STEP 7: SQLite Executes Query
```sql
-- Actual SQL executed
SELECT data FROM blocks WHERE pos = 33520667730509;

-- Returns BLOB: 1D 28 B5 2F FD 00 58 DD 02 00 34 03 09 FF...
-- Size: 621 bytes
```

### STEP 8: Deserialize Block - Version Check
```cpp
// src/mapblock.cpp
void MapBlock::deSerialize(std::istream &is, u8 version, bool disk)
{
    if (!ser_ver_supported_read(version))
        throw VersionMismatchException("ERROR: MapBlock format not supported");
    
    m_is_air_expired = true;
    
    if (version <= 21) {
        deSerialize_pre22(is, version, disk);
        return;
    }
    
    // Version 22+ continues...
```

### STEP 9: Decompress ZSTD Data
```cpp
// src/mapblock.cpp (continued)
    // For version >= 29
    std::stringstream in_raw(std::ios_base::binary | std::ios_base::in | std::ios_base::out);
    if (version >= 29)
        decompress(is, in_raw, version);
    std::istream &real_is = version >= 29 ? in_raw : is;

// src/serialization.cpp
void decompress(std::istream &is, std::ostream &os, u8 version)
{
    if (version >= 29) {
        decompressZstd(is, os);
        return;
    }
    // older versions...
}

void decompressZstd(std::istream &is, std::ostream &os)
{
    thread_local std::unique_ptr<ZSTD_DStream, ZSTD_Deleter> stream(ZSTD_createDStream());
    
    ZSTD_initDStream(stream.get());
    
    const size_t bufsize = 16384;
    char output_buffer[bufsize];
    char input_buffer[bufsize];
    
    ZSTD_outBuffer output = {output_buffer, bufsize, 0};
    ZSTD_inBuffer input = {input_buffer, 0, 0};
    
    size_t ret;
    do {
        if (input.pos == input.size) {
            is.read(input_buffer, bufsize);
            input.size = is.gcount();
            input.pos = 0;
        }
        
        ret = ZSTD_decompressStream(stream.get(), &output, &input);
        
        if (output.pos) {
            os.write(output_buffer, output.pos);
            output.pos = 0;
        }
    } while (ret != 0);
}

// RESULT: Decompressed data ~16KB
```

### STEP 10: Parse Block Header
```cpp
// src/mapblock.cpp
    // Read flags
    u8 flags = readU8(real_is);
    is_underground = (flags & 0x01) != 0;
    m_day_night_diff = (flags & 0x02) != 0;
    m_generated = (flags & 0x08) == 0;
    
    // Read lighting_complete
    if (version < 27)
        m_lighting_complete = 0xFFFF;
    else
        m_lighting_complete = readU16(real_is);
    
    // EXAMPLE DATA:
    // flags = 0x01 (underground=true, generated=true)
    // lighting_complete = 0xFFFF
```

### STEP 11: Read NameIdMapping
```cpp
// src/mapblock.cpp
    NameIdMapping nimap;
    if (disk && version >= 29) {
        // Read timestamp
        setTimestampNoChangedFlag(readU32(real_is));
        m_disk_timestamp = m_timestamp;
        
        // Read name-id mapping
        nimap.deSerialize(real_is);
    }

// src/nameidmapping.cpp
void NameIdMapping::deSerialize(std::istream &is)
{
    u16 count = readU16(is);
    m_id_to_name.clear();
    m_name_to_id.clear();
    
    for (u16 i = 0; i < count; i++) {
        u16 id = readU16(is);
        std::string name = deSerializeString16(is);
        m_id_to_name[id] = name;
        m_name_to_id[name] = id;
    }
}

// EXAMPLE DATA READ:
// count = 7
// 0 -> "default:stone"
// 1 -> "default:stone_with_iron"
// 2 -> "default:stone_with_coal"
// 3 -> "default:stone_with_copper"
// 4 -> "default:gravel"
// 5 -> "default:silver_sand"
// 6 -> "default:stone_with_tin"
```

### STEP 12: Read Node Data Format
```cpp
// src/mapblock.cpp
    u8 content_width = readU8(real_is);
    u8 params_width = readU8(real_is);
    
    if (content_width != 1 && content_width != 2)
        throw SerializationError("MapBlock::deSerialize(): invalid content_width");
    if (params_width != 2)
        throw SerializationError("MapBlock::deSerialize(): invalid params_width");
    
    // EXAMPLE: content_width = 2, params_width = 2
```

### STEP 13: Read All 4096 Nodes
```cpp
// src/mapblock.cpp
    MapNode::deSerializeBulk(real_is, version, data, nodecount,
        content_width, params_width);

// src/mapnode.cpp
void MapNode::deSerializeBulk(std::istream &is, int version,
    MapNode *nodes, u32 nodecount,
    u8 content_width, u8 params_width)
{
    if (version >= 24) {
        for (u32 i = 0; i < nodecount; i++) {
            if (content_width == 2) {
                nodes[i].param0 = readU16(is);
            } else {
                nodes[i].param0 = readU8(is);
            }
            nodes[i].param1 = readU8(is);
            nodes[i].param2 = readU8(is);
        }
    }
    // older versions...
}

// READS 4096 nodes, each with:
// - param0 (content_id): 2 bytes
// - param1 (light): 1 byte  
// - param2 (rotation): 1 byte
// Total: 4096 * 4 = 16384 bytes
```

### STEP 14: Apply Name-ID Mappings
```cpp
// src/mapblock.cpp
    if (disk) {
        // Correct ids in the block to match nodedef based on names
        correctBlockNodeIds(&nimap, data, m_gamedef);
    }

// src/mapblock.cpp
static void correctBlockNodeIds(const NameIdMapping *nimap, MapNode *nodes,
    IGameDef *gamedef)
{
    const NodeDefManager *nodedef = gamedef->ndef();
    
    std::unordered_set<content_t> unnamed_contents;
    std::unordered_set<std::string> unallocatable_contents;
    
    for (u32 i = 0; i < MapBlock::nodecount; i++) {
        content_t local_id = nodes[i].param0;
        std::string name;
        
        if (!nimap->getName(local_id, name)) {
            unnamed_contents.insert(local_id);
            continue;
        }
        
        content_t global_id;
        if (!nodedef->getId(name, global_id)) {
            global_id = gamedef->allocateUnknownNodeId(name);
            if (global_id == CONTENT_IGNORE) {
                unallocatable_contents.insert(name);
                continue;
            }
        }
        
        nodes[i].param0 = global_id;
    }
}
```

### STEP 15: Get Node from Block
```cpp
// Back to src/map.cpp - Map::getNode()
    v3s16 relpos = p - blockpos * MAP_BLOCKSIZE;
    return block->getNodeNoCheck(relpos);

// src/mapblock.h
MapNode getNodeNoCheck(v3s16 p) {
    return getNodeNoCheck(p.X, p.Y, p.Z);
}

MapNode getNodeNoCheck(s16 x, s16 y, s16 z) {
    return data[z * zstride + y * ystride + x];
}

// Where:
// zstride = 16 * 16 = 256
// ystride = 16
// 
// CALCULATION:
// relpos = (1234, 56, -789) - (77*16, 3*16, -50*16)
// relpos = (1234, 56, -789) - (1232, 48, -800)
// relpos = (2, 8, 11)
//
// index = 11 * 256 + 8 * 16 + 2
// index = 2816 + 128 + 2
// index = 2946
//
// node = data[2946]
// node.param0 = 2 (content_id from local mapping)
// node.param1 = 0
// node.param2 = 0
```

### STEP 16: Get Node Properties
```cpp
// src/client/game.cpp
    MapNode n = map->getNode(nodepos);
    const ContentFeatures &features = ndef->get(n);
    
// src/nodedef.cpp
const ContentFeatures &NodeDefManager::get(const MapNode &n) const
{
    return get(n.getContent());
}

const ContentFeatures &NodeDefManager::get(content_t c) const
{
    if (c < m_content_features.size())
        return m_content_features[c];
    else
        return m_content_features[CONTENT_UNKNOWN];
}

// RESULT:
// content_id 2 was "default:stone_with_coal" in block mapping
// Global registry returns full ContentFeatures:
// - name = "default:stone_with_coal"
// - drawtype = NDT_NORMAL
// - tiles = {"default_stone.png^default_mineral_coal.png"}
// - groups = {cracky = 3}
// - drop = "default:coal_lump"
// - sounds = stone sound table
// etc...
```

### STEP 17: Use Node Properties
```cpp
// Now the game can:
// - Render the texture
// - Play sounds when hit
// - Drop coal when mined
// - Calculate mining time based on groups
// - Show name in HUD
// etc.
```

## Complete Data Flow Summary

```
World Position (1234, 56, -789)
    |
    v
Block Position (77, 3, -50)
    |
    v
Database Key 33520667730509
    |
    v
SQLite Query Returns 621 bytes
    |
    v
Version Check: 29
    |
    v
ZSTD Decompress to ~16KB
    |
    v
Parse Header (flags, lighting)
    |
    v
Read NameIdMapping (7 entries)
    |
    v
Read 4096 Nodes (16KB)
    |
    v
Calculate Node Index 2946
    |
    v
Get Local Content ID: 2
    |
    v
Map to Name: "default:stone_with_coal"
    |
    v
Get Global Content ID & Properties
    |
    v
Render/Use Node
```

This is the COMPLETE path from database to game!